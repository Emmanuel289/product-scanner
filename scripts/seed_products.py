import boto3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core", "app"))  # noqa

from constants import (
    Category,
    CoverageType,
    FinishType,
    RiskLevel,
    SkinType,
    TextureType,
    app_logger,
)

TABLE_NAME = "product-scanner-products"

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table(TABLE_NAME)

# ---- The raw source of truth for all the beauty products, categorized by brands (3 brands, 8 products per brand) ---- #
RAW_PRODUCTS = [
    # =========================
    # DIOR
    # =========================
    {
        "brand": "Dior",
        "name": "Dior Forever Skin Glow Foundation",
        "category": Category.FOUNDATION.value,
        "texture": TextureType.LIQUID.value,
        "finish": FinishType.GLOW.value,
        "coverage": CoverageType.MEDIUM.value,
        "best_for": [SkinType.NORMAL.value, SkinType.DRY.value],
        "avoid_for": [SkinType.OILY.value],
        "concerns_targeted": ["hydration", "radiance"],
        "concerns_not_ideal": ["oil control"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Dior",
        "name": "Dior Forever Matte Foundation",
        "category": Category.FOUNDATION.value,
        "texture": TextureType.LIQUID.value,
        "finish": FinishType.MATTE.value,
        "coverage": CoverageType.MEDIUM.value,
        "best_for": [SkinType.OILY.value, SkinType.COMBINATION.value],
        "avoid_for": [SkinType.DRY.value],
        "concerns_targeted": ["oil control", "long wear"],
        "concerns_not_ideal": ["hydration"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Dior",
        "name": "Dior Addict Lip Glow",
        "category": Category.LIP_PRODUCT.value,
        "texture": TextureType.BALM.value,
        "finish": FinishType.GLOW.value,
        "best_for": [SkinType.DRY.value, SkinType.NORMAL.value],
        "avoid_for": [],
        "concerns_targeted": ["hydration", "sheer tint"],
        "concerns_not_ideal": ["full coverage color"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Dior",
        "name": "Dior Rouge Dior Lipstick",
        "category": Category.LIP_PRODUCT.value,
        "texture": TextureType.CREAM.value,
        "finish": FinishType.NATURAL.value,
        "best_for": [SkinType.NORMAL.value],
        "avoid_for": ["very dry"],
        "concerns_targeted": ["pigment", "long wear"],
        "concerns_not_ideal": ["hydration boost"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.MEDIUM.value,
    },
    {
        "brand": "Dior",
        "name": "Dior Backstage Face & Body Foundation",
        "category": Category.FOUNDATION.value,
        "texture": TextureType.LIQUID.value,
        "finish": FinishType.NATURAL.value,
        "coverage": CoverageType.LIGHT.value,
        "best_for": [SkinType.NORMAL.value, SkinType.COMBINATION.value],
        "avoid_for": [],
        "concerns_targeted": ["lightweight wear"],
        "concerns_not_ideal": ["full coverage"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Dior",
        "name": "Dior Capture Totale Super Potent Serum",
        "category": Category.SERUM.value,
        "texture": TextureType.LIQUID.value,
        "best_for": [SkinType.DRY.value, SkinType.NORMAL.value],
        "avoid_for": [],
        "concerns_targeted": ["anti-aging", "firming"],
        "concerns_not_ideal": ["acne treatment"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.MEDIUM.value,
    },
    {
        "brand": "Dior",
        "name": "Dior Hydra Life Fresh Hydration Sorbet Cream",
        "category": Category.MOISTURIZER.value,
        "texture": TextureType.CREAM.value,
        "finish": FinishType.NATURAL.value,
        "best_for": [SkinType.DRY.value, SkinType.NORMAL.value],
        "avoid_for": [],
        "concerns_targeted": ["hydration"],
        "concerns_not_ideal": ["oil control"],
        "comedogenic_risk": RiskLevel.MEDIUM.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Dior",
        "name": "Dior Forever Skin Correct Concealer",
        "category": Category.FOUNDATION.value,
        "texture": TextureType.CREAM.value,
        "finish": FinishType.NATURAL.value,
        "coverage": CoverageType.FULL.value,
        "best_for": [SkinType.NORMAL.value, SkinType.COMBINATION.value],
        "avoid_for": ["very dry"],
        "concerns_targeted": ["coverage", "brightening"],
        "concerns_not_ideal": ["hydration boost"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.MEDIUM.value,
    },
    # =========================
    # RARE BEAUTY
    # =========================
    {
        "brand": "Rare Beauty",
        "name": "Liquid Touch Weightless Foundation",
        "category": Category.FOUNDATION.value,
        "texture": TextureType.LIQUID.value,
        "finish": FinishType.NATURAL.value,
        "coverage": CoverageType.MEDIUM.value,
        "best_for": [SkinType.NORMAL.value, SkinType.COMBINATION.value],
        "avoid_for": [],
        "concerns_targeted": ["lightweight wear"],
        "concerns_not_ideal": ["full glam coverage"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.MEDIUM.value,
    },
    {
        "brand": "Rare Beauty",
        "name": "Positive Light Tinted Moisturizer",
        "category": Category.MOISTURIZER.value,
        "texture": TextureType.LOTION.value,
        "finish": FinishType.GLOW.value,
        "coverage": CoverageType.SHEER.value,
        "best_for": [SkinType.DRY.value, SkinType.NORMAL.value],
        "avoid_for": ["very oily"],
        "concerns_targeted": ["hydration", "light coverage"],
        "concerns_not_ideal": ["oil control"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Rare Beauty",
        "name": "Soft Pinch Liquid Blush",
        "category": Category.LIP_PRODUCT.value,
        "texture": TextureType.LIQUID.value,
        "finish": FinishType.MATTE.value,
        "best_for": [SkinType.NORMAL.value, SkinType.COMBINATION.value],
        "avoid_for": [],
        "concerns_targeted": ["pigment"],
        "concerns_not_ideal": ["hydration"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Rare Beauty",
        "name": "Soft Pinch Tinted Lip Oil",
        "category": Category.LIP_PRODUCT.value,
        "texture": TextureType.LIQUID.value,
        "finish": FinishType.GLOW.value,
        "best_for": [SkinType.DRY.value],
        "avoid_for": [],
        "concerns_targeted": ["hydration", "sheer tint"],
        "concerns_not_ideal": ["matte finish"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Rare Beauty",
        "name": "Always an Optimist Pore Diffusing Primer",
        "category": Category.FOUNDATION.value,
        "texture": TextureType.GEL.value,
        "finish": FinishType.NATURAL.value,
        "best_for": [SkinType.OILY.value, SkinType.COMBINATION.value],
        "avoid_for": ["very dry"],
        "concerns_targeted": ["pore blurring", "oil control"],
        "concerns_not_ideal": ["hydration boost"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.MEDIUM.value,
    },
    {
        "brand": "Rare Beauty",
        "name": "Stay Vulnerable Glossy Lip Balm",
        "category": Category.LIP_PRODUCT.value,
        "texture": TextureType.BALM.value,
        "finish": FinishType.GLOW.value,
        "best_for": [SkinType.DRY.value],
        "avoid_for": [],
        "concerns_targeted": ["hydration"],
        "concerns_not_ideal": ["matte finish"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Rare Beauty",
        "name": "Find Comfort Hydrating Body Lotion",
        "category": Category.MOISTURIZER.value,
        "texture": TextureType.LOTION.value,
        "best_for": [SkinType.DRY.value],
        "avoid_for": [],
        "concerns_targeted": ["hydration"],
        "concerns_not_ideal": ["oil control"],
        "comedogenic_risk": RiskLevel.MEDIUM.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "Rare Beauty",
        "name": "Kind Words Matte Lipstick",
        "category": Category.LIP_PRODUCT.value,
        "texture": TextureType.CREAM.value,
        "finish": FinishType.MATTE.value,
        "best_for": [SkinType.NORMAL.value],
        "avoid_for": ["very dry"],
        "concerns_targeted": ["pigment"],
        "concerns_not_ideal": ["hydration"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.MEDIUM.value,
    },
    # =========================
    # LA ROCHE-POSAY
    # =========================
    {
        "brand": "La Roche-Posay",
        "name": "Toleriane Hydrating Gentle Cleanser",
        "category": Category.CLEANSER.value,
        "texture": TextureType.CREAM.value,
        "best_for": [SkinType.DRY.value, SkinType.SENSITIVE.value],
        "avoid_for": ["very oily"],
        "concerns_targeted": ["barrier repair", "gentle cleansing"],
        "concerns_not_ideal": ["oil stripping"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "La Roche-Posay",
        "name": "Toleriane Double Repair Face Moisturizer",
        "category": Category.MOISTURIZER.value,
        "texture": TextureType.CREAM.value,
        "best_for": [SkinType.DRY.value, SkinType.SENSITIVE.value],
        "avoid_for": [],
        "concerns_targeted": ["barrier repair", "hydration"],
        "concerns_not_ideal": ["oil control"],
        "comedogenic_risk": RiskLevel.MEDIUM.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "La Roche-Posay",
        "name": "Effaclar Purifying Foaming Gel Cleanser",
        "category": Category.CLEANSER.value,
        "texture": TextureType.FOAM.value,
        "best_for": [SkinType.OILY.value, SkinType.ACNE_PRONE.value],
        "avoid_for": [SkinType.DRY.value, SkinType.SENSITIVE.value],
        "concerns_targeted": ["oil control", "acne"],
        "concerns_not_ideal": ["hydration"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.MEDIUM.value,
    },
    {
        "brand": "La Roche-Posay",
        "name": "Effaclar Mat Oil-Free Moisturizer",
        "category": Category.MOISTURIZER.value,
        "texture": TextureType.GEL.value,
        "finish": FinishType.MATTE.value,
        "best_for": [SkinType.OILY.value, SkinType.ACNE_PRONE.value],
        "avoid_for": [SkinType.DRY.value],
        "concerns_targeted": ["oil control"],
        "concerns_not_ideal": ["deep hydration"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.MEDIUM.value,
    },
    {
        "brand": "La Roche-Posay",
        "name": "Effaclar A.I. Targeted Breakout Corrector",
        "category": Category.SERUM.value,
        "texture": TextureType.GEL.value,
        "best_for": [SkinType.ACNE_PRONE.value],
        "avoid_for": ["very sensitive"],
        "concerns_targeted": ["acne"],
        "concerns_not_ideal": ["anti-aging"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.MEDIUM.value,
    },
    {
        "brand": "La Roche-Posay",
        "name": "Hyalu B5 Pure Hyaluronic Acid Serum",
        "category": Category.SERUM.value,
        "texture": TextureType.GEL.value,
        "best_for": [SkinType.DRY.value, SkinType.NORMAL.value],
        "avoid_for": [],
        "concerns_targeted": ["hydration", "plumping"],
        "concerns_not_ideal": ["oil control"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "La Roche-Posay",
        "name": "Cicaplast Baume B5",
        "category": Category.MOISTURIZER.value,
        "texture": TextureType.BALM.value,
        "best_for": [SkinType.DRY.value, SkinType.SENSITIVE.value],
        "avoid_for": ["very oily"],
        "concerns_targeted": ["barrier repair", "soothing"],
        "concerns_not_ideal": ["lightweight wear"],
        "comedogenic_risk": RiskLevel.MEDIUM.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
    {
        "brand": "La Roche-Posay",
        "name": "Anthelios Melt-in Milk Sunscreen SPF 60",
        "category": Category.SUNSCREEN.value,
        "texture": TextureType.LOTION.value,
        "finish": FinishType.NATURAL.value,
        "best_for": [
            SkinType.NORMAL.value,
            SkinType.DRY.value,
            SkinType.SENSITIVE.value,
        ],
        "avoid_for": [],
        "concerns_targeted": ["sun protection"],
        "concerns_not_ideal": ["matte finish"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
]


def seed():
    app_logger.info(f"Seeding {len(RAW_PRODUCTS)} products into {TABLE_NAME}...\n")
    success = 0
    failed = 0

    for product in RAW_PRODUCTS:
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
            # best_for in RAW_PRODUCTS holds skin types — map to skin_types
            "skin_types": product.get("best_for", []),
            "best_for": product.get("best_for", []),
            "avoid_for": product.get("avoid_for", []),
            "concerns_targeted": product.get("concerns_targeted", []),
            "concerns_not_ideal": product.get("concerns_not_ideal", []),
            "comedogenic_risk": product.get("comedogenic_risk", "low"),
            "sensitivity_risk": product.get("sensitivity_risk", "low"),
            # Not in RAW_PRODUCTS yet — placeholder for future enrichment
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
