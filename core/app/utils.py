import boto3
import logging
import re
from base64 import b64decode
from botocore.exceptions import ClientError
from random import sample
from uuid import uuid4
from constants import (
    BRAND_ALIASES,
    CONFIDENCE_THRESHOLD,
    PRODUCTS_TABLE,
    IN_MEMORY_PRODUCTS,
    UserProfile,
)
from decision_engine import generate_decision_summary
from typing import Dict, List, Optional, Set

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

app_logger = logging.getLogger(__name__)


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


def upload_image_to_s3(image_base64: str, bucket: str) -> None:
    """Uploads a base64 encoded image to the S3 bucket and return its key"""
    try:
        image_bytes = b64decode(image_base64)
        key = f"incoming/{uuid4()}.jpg"
        boto3.client("s3").put_object(Bucket=bucket, Key=key, Body=image_bytes)
        return key
    except ClientError as e:
        app_logger.error(
            f"S3 error uploading to {bucket}: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        )
        raise
    except Exception as e:
        app_logger.error(f"Unexpected error uploading to {bucket}: {e}")
        raise


def load_products_from_dynamodb() -> list:
    """
    Scan the entire products table at cold start.
    Returns a list of product dicts in the same shape as IN_MEMORY_PRODUCTS.
    """
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table(PRODUCTS_TABLE)
    products = []

    try:
        response = table.scan()
        products.extend(response.get("Items", []))

        # Handle pagination — scan returns max 1MB per call
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
            products.extend(response.get("Items", []))

        app_logger.info(f"Loaded {len(products)} products from DynamoDB")
    except Exception as e:
        app_logger.error(f"Failed to load products from DynamoDB: {e}")

    return products


def load_products_from_memory() -> list:
    return IN_MEMORY_PRODUCTS


def build_products(
    raw_products: List[Dict[str, str]], aliases: Dict[str, str], stop_words: Set[str]
) -> Dict[str, List[Dict]]:
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
            "cons": item.get("cons", []),
        }
        products_by_brand.setdefault(item["brand"], []).append(product_dict)
    return products_by_brand


def match_product(
    text: str, products_by_brand: Dict[str, List[Dict]], stop_words: Set[str]
) -> Dict:
    norm_text = normalize_text(text, BRAND_ALIASES)
    text_tokens = set(tokenize(norm_text, stop_words))
    best_match = None
    best_score = 0
    for _, items in products_by_brand.items():
        for product in items:
            product_tokens = set(product["search_tokens"])
            score = len(product_tokens & text_tokens) / max(len(product_tokens), 1)
            if score > best_score:
                best_score = score
                best_match = product
    if best_score >= CONFIDENCE_THRESHOLD:
        app_logger.info(f"Best score: {best_score}\nBest match: {best_match}")
        return best_match
    return None


def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
    }


def explain_alternative(matched: Dict, alternative: Dict) -> str:
    parts = []

    # --- Shared goal or different goal --- #
    alt_intent = alternative.get("ingredient_intent", "")
    matched_concerns = set(matched.get("concerns_targeted", []))
    alt_concerns = set(alternative.get("concerns_targeted", []))
    shared_concerns = matched_concerns & alt_concerns

    if shared_concerns:
        parts.append(f"This product targets the same {','.join(shared_concerns)} goal")
    elif alt_intent:
        parts.append(f"but focuses on {alt_intent} instead")

    # --- Texture difference --- #
    matched_texture = matched.get("texture", "")
    alt_texture = alternative.get("texture", "")
    if alt_texture and alt_texture != matched_texture:
        parts.append(f"but {alt_texture} texture")

    # --- Skin type difference --- #
    matched_skin = set(matched.get("skin_types", []))
    alt_skin = set(alternative.get("skin_types", []))
    unique_to_alt = alt_skin - matched_skin
    if unique_to_alt:
        parts.append(
            f"This product is better suited for {', '.join(unique_to_alt)} skin"
        )

    # --- Fallback if nothing meaningful to compare --- #
    if not parts:
        alt_finish = alternative.get("finish", "")
        if alt_finish:
            parts.append(f"{alt_finish} finish")
        parts.append("different formulation approach")

    return " - ".join(parts) if parts else "Alternative formulation"


def build_result(
    matched_product: Dict[str, str],
    user_profile,
    products_by_brand: Dict[str, List[Dict]],
):
    """Shared logic: run decision engine + build alternatives + return result dict."""
    decision_summary = generate_decision_summary(matched_product, user_profile)

    alternatives_pool = [
        p
        for p in products_by_brand.get(matched_product["brand"], [])
        if p["name"] != matched_product["name"]
    ]
    alternatives = sample(alternatives_pool, min(2, len(alternatives_pool)))
    alt_results = [
        {
            "name": alt["name"],
            "why_different": explain_alternative(matched_product, alt),
        }
        for alt in alternatives
    ]

    print(f"decision summary is {decision_summary}")
    return {
        "status": decision_summary["outcome"],
        "brand": matched_product["brand"],
        "product_name": matched_product["name"],
        "product_summary": decision_summary,
        "alternatives": alt_results,
    }


def run_textract_and_match(
    products_by_brand: Dict[str, List[Dict]],
    stop_words: Set[str],
    image_base64: Optional[str] = None,
    key: Optional[str] = None,
    bucket: Optional[str] = None,
) -> Dict:
    """Run Textract on a base64 encoded image file or S3 object and return the matched product or None."""

    if key and image_base64:
        raise RuntimeError("Must specify either an object key or image not both")

    if image_base64:
        document = {"Bytes": b64decode(image_base64)}
    if key:
        document = {"S3Object": {"Bucket": bucket, "Name": key}}

    try:
        response = boto3.client("textract").detect_document_text(Document=document)
    except ClientError as e:
        app_logger.error(
            f"Textract error on document: {e.response['Error']['Code']} - {e.response['Error']['Message']}"
        )
        raise
    except Exception as e:
        app_logger.error(f"Unexpected error calling Textract: {e}")
        raise

    lines = [
        item["Text"]
        for item in response.get("Blocks", [])
        if item["BlockType"] == "LINE"
    ]
    text_from_image = " ".join(lines)
    app_logger.info(f"Detected text: {text_from_image}")
    return match_product(text_from_image, products_by_brand, stop_words)


def parse_user_profile(user_profile_data: dict):
    """Parse a user profile dict into a UserProfile object, or return None."""
    if not user_profile_data:
        return None
    return UserProfile(
        skin_type=user_profile_data.get("skin_type", ""),
        concerns=user_profile_data.get("concerns", []),
        sensitive=user_profile_data.get("sensitive", False),
    )
