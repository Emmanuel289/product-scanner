from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

# ---- Values that wouldn't change (much) ---- #
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

CONFIDENCE_THRESHOLD = 0.8


# ---- Enums that control the vocabulary of a product ---- #
class SkinType(Enum):
    DRY = "dry"
    OILY = "oily"
    NORMAL = "normal"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    ACNE_PRONE = "acne-prone"


class Category(Enum):
    FOUNDATION = "foundation"
    CLEANSER = "cleanser"
    MOISTURIZER = "moisturizer"
    SERUM = "serum"
    SUNSCREEN = "sunscreen"
    LIP_PRODUCT = "lip-product"


class FinishType(Enum):
    MATTE = "matte"
    GLOW = "glow"
    NATURAL = "natural"


class TextureType(Enum):
    LIQUID = "liquid"
    CREAM = "cream"
    GEL = "gel"
    FOAM = "foam"
    BALM = "balm"
    LOTION = "lotion"


class CoverageType(Enum):
    SHEER = "sheer"
    LIGHT = "light"
    MEDIUM = "medium"
    FULL = "full"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# ---- The list of products indexed by brands and names (3 brands, 8 products per brand) ---- #
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
        "best_for": [SkinType.NORMAL.value, SkinType.DRY.value, SkinType.SENSITIVE.value],
        "avoid_for": [],
        "concerns_targeted": ["sun protection"],
        "concerns_not_ideal": ["matte finish"],
        "comedogenic_risk": RiskLevel.LOW.value,
        "sensitivity_risk": RiskLevel.LOW.value,
    },
]

# ---- Model to store the profile of a user ---- #


class UserProfile(BaseModel):
    skin_type: Optional[SkinType]
    concerns: Optional[List]
    sensitive: bool = False
