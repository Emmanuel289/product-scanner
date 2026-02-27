import json
import re
import boto3
from random import sample
from typing import List, Dict, Set

s3_client = boto3.client("s3")
textract_client = boto3.client("textract")

# ---- Constants ---- #
STOPWORDS = {
    "new", "formula", "spf", "ml", "oz",
    "fl", "with", "and", "the", "a",
    "face", "body", "milk"
}

BRAND_ALIASES = {
    "la roche posay": "la roche-posay",
    "larocheposay": "la roche-posay",
    "rarebeauty": "rare beauty"
}

RAW_PRODUCTS = [
    # DIOR
    {"brand": "Dior", "name": "Dior Forever Skin Glow Foundation"},
    {"brand": "Dior", "name": "Dior Forever Matte Foundation"},
    {"brand": "Dior", "name": "Dior Addict Lip Glow"},
    {"brand": "Dior", "name": "Dior Rouge Dior Lipstick"},
    {"brand": "Dior", "name": "Dior Backstage Face & Body Foundation"},
    {"brand": "Dior", "name": "Dior Capture Totale Super Potent Serum"},
    {"brand": "Dior", "name": "Dior Hydra Life Fresh Hydration Sorbet Cream"},
    {"brand": "Dior", "name": "Dior Forever Skin Correct Concealer"},
    # RARE BEAUTY
    {"brand": "Rare Beauty", "name": "Liquid Touch Weightless Foundation"},
    {"brand": "Rare Beauty", "name": "Positive Light Tinted Moisturizer"},
    {"brand": "Rare Beauty", "name": "Soft Pinch Liquid Blush"},
    {"brand": "Rare Beauty", "name": "Soft Pinch Tinted Lip Oil"},
    {"brand": "Rare Beauty", "name": "Always an Optimist Pore Diffusing Primer"},
    {"brand": "Rare Beauty", "name": "Stay Vulnerable Glossy Lip Balm"},
    {"brand": "Rare Beauty", "name": "Find Comfort Hydrating Body Lotion"},
    {"brand": "Rare Beauty", "name": "Kind Words Matte Lipstick"},
    # LA ROCHE-POSAY
    {"brand": "La Roche-Posay", "name": "Toleriane Hydrating Gentle Cleanser"},
    {"brand": "La Roche-Posay", "name": "Toleriane Double Repair Face Moisturizer"},
    {"brand": "La Roche-Posay", "name": "Effaclar Purifying Foaming Gel Cleanser"},
    {"brand": "La Roche-Posay", "name": "Effaclar Mat Oil-Free Moisturizer"},
    {"brand": "La Roche-Posay", "name": "Effaclar A.I. Targeted Breakout Corrector"},
    {"brand": "La Roche-Posay", "name": "Hyalu B5 Pure Hyaluronic Acid Serum"},
    {"brand": "La Roche-Posay", "name": "Cicaplast Baume B5"},
    {"brand": "La Roche-Posay", "name": "Anthelios Melt-in Milk Sunscreen SPF 60"},
]

CONFIDENCE_THRESHOLD = 0.8

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
            "product_id": normalized.replace(" ", "-"),
            "brand": item["brand"],
            "name": item["name"],
            "search_tokens": tokens,
            "skin_types": item.get("skin_types", []),
            "texture": item.get("texture", ""),
            "finish": item.get("finish", ""),
            "ingredient_intent": item.get("ingredient_intent", ""),
            "pros": item.get("pros", []),
            "cons": item.get("cons", [])
        }
        products_by_brand.setdefault(item["brand"], []).append(product_dict)
    return products_by_brand

def match_product(text: str, products_by_brand: Dict[str, List[Dict]], stop_words: Set[str]) -> Dict:
    norm_text = normalize_text(text, BRAND_ALIASES)
    print(f"Normalized text: {norm_text}")
    text_tokens = set(tokenize(norm_text, stop_words))
    print(f"Text in Image tokens -> {text_tokens}")
    best_match = None
    best_score = 0
    for brand, items in products_by_brand.items():
        for product in items:
            product_tokens = set(product["search_tokens"])
            number_of_matching_tokens = len(product_tokens & text_tokens)
            score = number_of_matching_tokens / len(product_tokens)
            print(f"(Product tokens -> {product_tokens}, Match length -> {number_of_matching_tokens} Product Name -> {product['name']}, Score -> {score})")
            if score > best_score:
                best_score = score
                best_match = product
    if best_score >= CONFIDENCE_THRESHOLD:
        return best_match
    return None

# ----- Build products ----- #
PRODUCTS = build_products(RAW_PRODUCTS, BRAND_ALIASES, STOPWORDS)

# ----- Lambda Handler ----- #
def handler(event, context):
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        try:
            response = textract_client.detect_document_text(
                Document={"S3Object": {"Bucket": bucket, "Name": key}}
            )
            lines = [
                item["Text"] for item in response.get("Blocks", [])
                if item["BlockType"] == "LINE"
            ]
            text_from_image = " ".join(lines).lower()
            print("Detected text:", text_from_image)

            # --- Product Matching --- #
            matched_product = match_product(text_from_image, PRODUCTS, STOPWORDS)
            if not matched_product:
                return {"statusCode": 200, "body": json.dumps({
                    "status": "❌ Product Not Found",
                    "message": "We couldn't confidently identify this product."
                })}

            matched_brand = matched_product["brand"]

            # --- Outcome --- #
            if "oily" in matched_product["skin_types"] and "dry" in matched_product["skin_types"]:
                outcome = "⚠️ Mixed match"
            else:
                outcome = "✅ Good match"

            # --- Alternatives --- #
            alternatives_pool = [
                p for p in PRODUCTS[matched_brand] if p["name"] != matched_product["name"]
            ]
            alternatives = sample(alternatives_pool, min(2, len(alternatives_pool)))
            alt_results = [
                {
                    "name": alt["name"],
                    "why_different": f"Different texture ({alt['texture']}) or finish ({alt['finish']})"
                } for alt in alternatives
            ]

            result = {
                "status": outcome,
                "brand": matched_brand,
                "product_name": matched_product["name"],
                "product_summary": {
                    "skin_types": matched_product["skin_types"],
                    "finish": matched_product["finish"],
                    "texture": matched_product["texture"],
                    "ingredient_intent": matched_product["ingredient_intent"],
                    "pros": matched_product["pros"],
                    "cons": matched_product["cons"]
                },
                "alternatives": alt_results
            }
            return {"statusCode": 200, "body": json.dumps(result)}

        except Exception as e:
            print("Error processing document:", str(e))
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}