from core.app.constants import Category, CoverageType, FinishType, RiskLevel, SkinType, TextureType, UserProfile
from core.app.decision_engine import recommend

# --- Mock product ---
MOCK_PRODUCT = {
    "skin_types": [SkinType.OILY.value, SkinType.COMBINATION.value],
    "texture": TextureType.LIQUID.value,
    "finish": FinishType.MATTE.value,
    "ingredient_intent": "oil control",
    "pros": ["long lasting", "controls shine"],
    "cons": ["may feel drying"],
    "category": Category.FOUNDATION.value,
    "coverage": CoverageType.MEDIUM.value,
    "best_for": ["acne", "oil control"],
    "avoid_for": ["very dry"],
    "concerns_targeted": ["acne", "oil control"],
    "concerns_not_ideal": ["eczema"],
    "comedogenic_risk": RiskLevel.LOW.value,
    "sensitivity_risk": RiskLevel.LOW.value
}


def test_recommendation_no_user_profile() -> None:
    """Product recommendation with no user profile."""
    summary = recommend(MOCK_PRODUCT)
    assert summary.get("personalized", None) is False
    # Rationale should not contain any personalized hints
    assert not any("your" in r.lower() for r in summary.get("rationale", []))


def test_recommendation_user_with_oily_skin_and_acne() -> None:
    """Recommendation for user with oily skin and acne concerns."""
    user = UserProfile(
        skin_type=SkinType.OILY.value,
        concerns=["acne"],
        sensitive=False
    )
    summary = recommend(MOCK_PRODUCT, user)
    assert summary.get("personalized", False) is True
    # Rationale list check
    assert any(
        "Not ideal for: very dry" in r for r in summary.get("rationale", []))
    assert any("Targets your concerns" in r for r in summary.get("rationale", []))
    # Outcome should indicate good or caution
    assert any(o in summary.get("outcome", "")
               for o in ["✅ Good match", "⚠️ Mixed match", "⚠️ Use with caution"])


def test_user_with_dry_sensitive_skin_and_eczema() -> None:
    """Recommendation for user with dry, sensitive skin and eczema concerns."""
    user = UserProfile(
        skin_type=SkinType.DRY.value,
        concerns=["eczema"],
        sensitive=True
    )
    summary = recommend(MOCK_PRODUCT, user)
    assert summary.get("personalized", False) is True
    assert any(
        "Not ideal for: very dry" in r for r in summary.get("rationale", []))
    assert not any(concern in user.concerns for concern in summary.get(
        "concerns_targeted", []))
    assert any(o in summary.get("outcome", "")
               for o in ["⚠️ Use with caution", "❌ Not recommended"])


def test_user_with_high_sensitivity_risk() -> None:
    """Recommendation for a product with high sensitivity risk."""
    high_sensitivity_product = MOCK_PRODUCT.copy()
    high_sensitivity_product["sensitivity_risk"] = RiskLevel.HIGH.value
    user = UserProfile(
        skin_type=SkinType.NORMAL.value,
        concerns=[],
        sensitive=True
    )
    summary = recommend(high_sensitivity_product, user)
    assert "Use with caution" in summary.get("outcome", "")
    assert any("sensitivity risk" in r.lower()
               for r in summary.get("rationale", []))


def test_user_with_concerns_but_no_skin_type() -> None:
    """Recommendation when user has concerns but skin type is None."""
    user = UserProfile(
        skin_type=None,
        concerns=["acne"],
        sensitive=False
    )
    summary = recommend(MOCK_PRODUCT, user)
    assert summary.get("personalized", False) is True
    assert any("Targets your concerns" in r for r in summary.get("rationale", []))
