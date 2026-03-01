import base64
import json
import os
import re
import uuid
import boto3
from random import sample
from typing import List, Dict, Set
from constants import CONFIDENCE_THRESHOLD, BRAND_ALIASES, RAW_PRODUCTS, STOPWORDS, UserProfile
from decision_engine import recommend  # deterministic rule engine

SCANNER_BUCKET = os.environ.get("SCANNER_BUCKET", "product-scanner-maximus")
s3_client = boto3.client("s3")
textract_client = boto3.client("textract")


# ----- Helper functions ----- #
def normalize_text(text: str, aliases: dict) -> str:
    text = text.lower()
    for alias, canonical in aliases.items():
        text = text.replace(alias, canonical)
    text = re.sub(r"[^\w\s-]", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text: str, stop_words: set) -> list:
    tokens = text.split()
    return [t for t in tokens if t not in stop_words and len(t) > 2]


def build_products(raw_products: List[Dict[str, str]], aliases: Dict[str, str], stop_words: Set[str]) -> Dict[str, List[Dict]]:
    products_by_brand = {}
    for item in raw_products:
        full_name = f"{item['brand']} {item['name']}"
        normalized = normalize_text(full_name, aliases)
        tokens = tokenize(normalized, stop_words)
        product_dict = {
            # --- Identification --- #
            "product_id": normalized.replace(" ", "-"),
            "brand": item["brand"],
            "name": item["name"],
            "search_tokens": tokens,

            # --- Classification --- #
            "category": item.get("category", ""),
            "texture": item.get("texture", ""),
            "finish": item.get("finish", ""),
            "coverage": item.get("coverage"),
            # Decision intelligence fields
            "best_for": item.get("best_for", []),
            "avoid_for": item.get("avoid_for", []),
            "concerns_targeted": item.get("concerns_targeted", []),
            "concerns_not_ideal": item.get("concerns_not_ideal", []),
            "comedogenic_risk": item.get("comedogenic_risk", "low"),
            "sensitivity_risk": item.get("sensitivity_risk", "low"),
            "skin_types": item.get("skin_types", []),
            "ingredient_intent": item.get("ingredient_intent", ""),
            "pros": item.get("pros", []),
            "cons": item.get("cons", [])
        }
        products_by_brand.setdefault(item["brand"], []).append(product_dict)
    return products_by_brand


def match_product(text: str, products_by_brand: Dict[str, List[Dict]], stop_words: Set[str]) -> Dict:
    norm_text = normalize_text(text, BRAND_ALIASES)
    text_tokens = set(tokenize(norm_text, stop_words))
    best_match = None
    best_score = 0
    for _, items in products_by_brand.items():
        for product in items:
            product_tokens = set(product["search_tokens"])
            score = len(product_tokens & text_tokens) / \
                max(len(product_tokens), 1)
            if score > best_score:
                best_score = score
                best_match = product
    if best_score >= CONFIDENCE_THRESHOLD:
        return best_match
    return None


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST,OPTIONS"
    }


def build_result(matched_product, user_profile):
    """Shared logic: run decision engine + build alternatives + return result dict."""
    decision_summary = recommend(matched_product, user_profile)

    alternatives_pool = [
        p for p in PRODUCTS_BY_BRAND[matched_product["brand"]]
        if p["name"] != matched_product["name"]
    ]
    alternatives = sample(alternatives_pool, min(2, len(alternatives_pool)))
    alt_results = [
        {
            "name": alt["name"],
            "why_different": f"Different texture ({alt['texture']}) or finish ({alt['finish']})"
        } for alt in alternatives
    ]

    return {
        "status": decision_summary["outcome"],
        "brand": matched_product["brand"],
        "product_name": matched_product["name"],
        "product_summary": decision_summary,
        "alternatives": alt_results
    }


def run_textract_and_match(bucket: str, key: str) -> Dict:
    """Run Textract on an S3 object and return the matched product or None."""
    response = textract_client.detect_document_text(
        Document={"S3Object": {"Bucket": bucket, "Name": key}}
    )
    lines = [
        item["Text"] for item in response.get("Blocks", [])
        if item["BlockType"] == "LINE"
    ]
    text_from_image = " ".join(lines)
    print("Detected text:", text_from_image)
    return match_product(text_from_image, PRODUCTS_BY_BRAND, STOPWORDS)


def parse_user_profile(user_profile_data: dict):
    """Parse a user profile dict into a UserProfile object, or return None."""
    if not user_profile_data:
        return None
    return UserProfile(
        skin_type=user_profile_data.get("skin_type", ""),
        concerns=user_profile_data.get("concerns", []),
        sensitive=user_profile_data.get("sensitive", False)
    )


# ----- Build products at cold-start ----- #
PRODUCTS_BY_BRAND = build_products(RAW_PRODUCTS, BRAND_ALIASES, STOPWORDS)


# ----- Lambda Handler ----- #
def handler(event, context):

    # ------------------------------------------------------------------ #
    # HTTP branch — triggered by API Gateway (POST /scan)                 #
    # ------------------------------------------------------------------ #
    if event.get("httpMethod"):

        # --- CORS preflight --- #
        if event["httpMethod"] == "OPTIONS":
            return {"statusCode": 200, "headers": cors_headers(), "body": ""}

        try:
            body = json.loads(event.get("body", "{}"))
            image_b64 = body.get("image_base64")
            user_profile_data = body.get("user_profile")

            if not image_b64:
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps({"error": "image_base64 is required"})
                }

            # --- Upload image to S3 so Textract can read it --- #
            image_bytes = base64.b64decode(image_b64)
            key = f"scans/{uuid.uuid4()}.jpg"
            s3_client.put_object(Bucket=SCANNER_BUCKET,
                                 Key=key, Body=image_bytes)

            # --- Textract + match --- #
            matched_product = run_textract_and_match(SCANNER_BUCKET, key)
            if not matched_product:
                return {
                    "statusCode": 200,
                    "headers": cors_headers(),
                    "body": json.dumps({
                        "status": "❌ Product Not Found",
                        "message": "We couldn't confidently identify this product, so we didn't make a guess."
                    })
                }

            # --- Decision engine --- #
            user_profile = parse_user_profile(user_profile_data)
            result = build_result(matched_product, user_profile)

            return {
                "statusCode": 200,
                "headers": cors_headers(),
                "body": json.dumps(result)
            }

        except Exception as e:
            print("Error in HTTP branch:", str(e))
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": str(e)})
            }

    # ------------------------------------------------------------------ #
    # S3 event branch — triggered directly by S3 event notifications      #
    # ------------------------------------------------------------------ #
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        user_profile_data = record.get("user_profile")

        try:
            matched_product = run_textract_and_match(bucket, key)
            if not matched_product:
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "status": "❌ Product Not Found",
                        "message": "We couldn't confidently identify this product, so we didn't make a guess."
                    })
                }

            user_profile = parse_user_profile(user_profile_data)
            result = build_result(matched_product, user_profile)

            return {"statusCode": 200, "body": json.dumps(result)}

        except Exception as e:
            print("Error in S3 branch:", str(e))
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }
