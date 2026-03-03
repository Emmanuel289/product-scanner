import logging
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

app_logger = logging.getLogger(__name__)

# ---- Values that wouldn't change (much) ---- #
STOPWORDS = {
    "new",
    "formula",
    "spf",
    "ml",
    "oz",
    "fl",
    "with",
    "and",
    "the",
    "a",
    "face",
    "body",
    "milk",
}

BRAND_ALIASES = {
    "la roche posay": "la roche-posay",
    "larocheposay": "la roche-posay",
    "rarebeauty": "rare beauty",
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


class FitScoreThreshold(Enum):
    GOOD = 81
    MIXED = 57


class Outcome(Enum):
    GOOD = "✅ Good match"
    MIXED = "⚠️ Mixed match"
    NOT_RECOMMENDED = "❌ Not recommended"


# ---- Model to store the profile of a user ---- #
class UserProfile(BaseModel):
    skin_type: Optional[SkinType]
    concerns: Optional[List]
    sensitive: bool = False
