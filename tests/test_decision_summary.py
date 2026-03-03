from constants import (
    Category,
    CoverageType,
    FinishType,
    FitScoreThreshold,
    Outcome,
    RiskLevel,
    SkinType,
    TextureType,
    UserProfile,
)
from decision_engine import generate_decision_summary

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
    "sensitivity_risk": RiskLevel.LOW.value,
}


def test_summary_with_no_user_profile() -> None:
    """Test summary with no user profile."""
    summary = generate_decision_summary(MOCK_PRODUCT)
    assert summary.get("personalized") is False
    assert summary.get("fit_score") is None
    assert not any("your" in r.lower() for r in summary.get("rationale", []))


def test_summary_for_user_with_oily_skin_and_acne() -> None:
    """Test summary for a user with oily skin and acne."""
    user = UserProfile(
        skin_type=SkinType.OILY.value, concerns=["acne"], sensitive=False
    )
    summary = generate_decision_summary(MOCK_PRODUCT, user)
    assert summary.get("personalized") is True
    fit_score = summary.get("fit_score")
    if fit_score >= FitScoreThreshold.GOOD.value:
        assert summary["outcome"] == Outcome.GOOD.value
    elif fit_score >= FitScoreThreshold.MIXED_MATCH.value:
        assert summary["outcome"] == Outcome.MIXED.value
    else:
        assert summary["outcome"] == Outcome.NOT_RECOMMENDED.value


def test_summary_for_user_with_dry_sensitive_skin_and_eczema() -> None:
    """Test summary for a user with dry, sensitive skin, and eczema."""
    user = UserProfile(
        skin_type=SkinType.DRY.value, concerns=["eczema"], sensitive=True
    )
    summary = generate_decision_summary(MOCK_PRODUCT, user)
    assert summary.get("personalized") is True
    fit_score = summary.get("fit_score")
    assert fit_score == 50
    assert summary["outcome"] == Outcome.NOT_RECOMMENDED.value


def test_summary_for_user_with_high_sensitivity_risk() -> None:
    """Test summary for a user with high sensitivity risk."""
    high_sensitivity_product = {
        **MOCK_PRODUCT,
        "sensitivity_risk": RiskLevel.HIGH.value,
    }
    user = UserProfile(skin_type=SkinType.NORMAL.value, concerns=[], sensitive=True)
    summary = generate_decision_summary(high_sensitivity_product, user)
    assert summary["fit_score"] < FitScoreThreshold.MIXED.value
    assert summary["outcome"] == Outcome.NOT_RECOMMENDED.value


def test_summary_for_user_with_concerns_but_no_skin_type() -> None:
    """Test summary for a user with concerns but no skin type provided."""
    user = UserProfile(skin_type=None, concerns=["acne"], sensitive=False)
    summary = generate_decision_summary(MOCK_PRODUCT, user)

    assert summary.get("personalized") is True
    # acne is in concerns_targeted and should be mentioned
    assert any(
        "targets your concerns" in r.lower() for r in summary.get("rationale", [])
    )
    # No skin type means no skin alignment rationale
    assert not any(
        "skin type" in r.lower() and "well aligned" in r.lower()
        for r in summary.get("rationale", [])
    )
