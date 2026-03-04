"""
Offline enrichment script — uses Claude to generate ingredient_intent, pros,
and cons for each product in DynamoDB following PRD §14 tone guidelines.

Run with:
    python scripts/enrich_products.py

Flags:
    --dry-run     Print enriched data without writing to DynamoDB
    --brand       Only enrich products for a specific brand
                  e.g. --brand "La Roche-Posay"
"""

import argparse
import json
import os
import sys
import time

import anthropic
import boto3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa

from core.app.constants import PRODUCTS_TABLE
from dotenv import load_dotenv

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(PRODUCTS_TABLE)
load_dotenv("../.env")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ── Prompt ─────────────────────────────────────────────────────────────────────
def build_prompt(product: dict) -> str:
    return f"""You are a beauty product intelligence engine following strict tone guidelines.

Product to enrich:
- Brand: {product["brand"]}
- Name: {product["name"]}
- Category: {product.get("category", "")}
- Texture: {product.get("texture", "")}
- Finish: {product.get("finish", "")}
- Skin types: {", ".join(product.get("skin_types", []))}
- Concerns targeted: {", ".join(product.get("concerns_targeted", []))}
- Concerns not ideal: {", ".join(product.get("concerns_not_ideal", []))}

Generate the following three fields and return ONLY a valid JSON object with no markdown, no explanation, no extra keys:

{{
  "ingredient_intent": "Ingredient Name (plain explanation) + Ingredient Name (plain explanation)",
  "pros": ["pro 1", "pro 2", "pro 3"],
  "cons": ["con 1", "con 2"]
}}

Rules:
- ingredient_intent: list 2-3 key real ingredients in this product. Format each as "Ingredient Name (what it does in plain language)". Join with " + ". Write like a smart friend, not a scientist or doctor. Focus on what it does for the skin, not how it works chemically.
- pros: 2-4 short phrases reflecting what real customers consistently praise about this product
- cons: 1-3 short phrases reflecting real limitations or common criticisms
- Never invent ingredients that are not in this product
- Never use words like "clinically proven", "dermatologist tested", or any marketing language
- Keep every phrase concise — under 8 words each
"""


# ── Claude call ────────────────────────────────────────────────────────────────
def enrich_product(product: dict) -> dict:
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": build_prompt(product)}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


# ── DynamoDB ───────────────────────────────────────────────────────────────────


def load_products(brand_filter: str = None) -> list:
    response = table.scan()
    products = response.get("Items", [])
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        products.extend(response.get("Items", []))

    if brand_filter:
        products = [p for p in products if p["brand"] == brand_filter]

    return products


def write_enrichment(product_id: str, enrichment: dict):
    table.update_item(
        Key={"product_id": product_id},
        UpdateExpression=("SET ingredient_intent = :ii, pros = :p, cons = :c"),
        ExpressionAttributeValues={
            ":ii": enrichment["ingredient_intent"],
            ":p": enrichment["pros"],
            ":c": enrichment["cons"],
        },
    )


# ── Main ───────────────────────────────────────────────────────────────────────
def main(dry_run: bool, brand_filter: str):
    products = load_products(brand_filter)
    print(f"Found {len(products)} products to enrich\n")

    success, failed = 0, 0

    for product in products:
        name = f"{product['brand']} — {product['name']}"
        print(f"  Enriching: {name}")

        try:
            enrichment = enrich_product(product)

            # Preview what will be written
            print(f"ingredient_intent: {enrichment['ingredient_intent']}")
            print(f"pros: {enrichment['pros']}")
            print(f"cons: {enrichment['cons']}")

            if not dry_run:
                write_enrichment(product["product_id"], enrichment)
                print(f"✅ Written to DynamoDB")
            else:
                print(f"🔍 Dry run — not written")

            success += 1

        except Exception as e:
            print(f"❌ Failed: {e}")
            failed += 1

        time.sleep(0.5)

    print(f"\nDone. {success} enriched, {failed} failed.")
    if dry_run:
        print("Re-run without --dry-run to write to DynamoDB.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Enrich products in DynamoDB with Claude"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without writing"
    )
    parser.add_argument("--brand", type=str, default=None, help="Filter by brand name")
    args = parser.parse_args()

    main(dry_run=args.dry_run, brand_filter=args.brand)
