import boto3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa

from core.app.constants import app_logger, IN_MEMORY_PRODUCTS, PRODUCTS_TABLE

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(PRODUCTS_TABLE)


def seed():
    app_logger.info(
        f"Seeding {len(IN_MEMORY_PRODUCTS)} products into {PRODUCTS_TABLE}...\n"
    )
    success = 0
    failed = 0

    for product in IN_MEMORY_PRODUCTS.copy():
        product_id = (
            f"{product['brand'].lower().replace(' ', '-')}"
            f"-{product['name'].lower().replace(' ', '-')}"
        )

        item = {
            "product_id": product_id,
            "brand": product["brand"],
            "name": product["name"],
            "category": product.get("category", ""),
            "texture": product.get("texture", ""),
            "finish": product.get("finish", "") or "",
            "coverage": product.get("coverage", "") or "",
            # best_for in PRODUCTS holds skin types — map to skin_types
            "skin_types": product.get("best_for", []),
            "best_for": product.get("best_for", []),
            "avoid_for": product.get("avoid_for", []),
            "concerns_targeted": product.get("concerns_targeted", []),
            "concerns_not_ideal": product.get("concerns_not_ideal", []),
            "comedogenic_risk": product.get("comedogenic_risk", "low"),
            "sensitivity_risk": product.get("sensitivity_risk", "low"),
            # Not in PRODUCTS yet — placeholder for future enrichment
            "ingredient_intent": product.get("ingredient_intent", ""),
            "pros": product.get("pros", []),
            "cons": product.get("cons", []),
        }

        try:
            table.put_item(Item=item)
            print(f"  ✅  {product['brand']} — {product['name']}")
            success += 1
        except Exception as e:
            print(f"  ❌  {product['brand']} — {product['name']}: {e}")
            failed += 1

    print(f"\nDone. {success} seeded, {failed} failed.")
    if failed:
        print("Re-run after fixing errors above.")


if __name__ == "__main__":
    seed()
