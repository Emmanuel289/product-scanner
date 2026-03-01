from constants import UserProfile
from decision_engine import compute_fit_score, recommend


def make_product():
    return {
        "skin_types": ["oily", "combination"],
        "avoid_for": ["dry"],
        "concerns_targeted": ["acne", "excess oil"],
        "concerns_not_ideal": ["dryness"],
        "comedogenic_risk": "low",
        "sensitivity_risk": "low",
    }


def test_oily_skin_scores_high():
    user_profile = UserProfile(skin_type="oily", concerns=[], sensitive=False)
    score = compute_fit_score(make_product(), user_profile)
    assert score == 85, f"Expected 85, got {score}"


def test_dry_skin_scores_low():
    user_profile = UserProfile(skin_type="dry", concerns=[], sensitive=False)
    score = compute_fit_score(make_product(), user_profile)
    assert score == 30, f"Expected 30, got {score}"


def test_matching_concern_increases_score():
    user_profile = UserProfile(skin_type="oily", concerns=[
                               "acne"], sensitive=False)
    score = compute_fit_score(make_product(), user_profile)
    assert score == 90, f"Expected 90, got {score}"


def test_no_profile_returns_none_fit_score():
    summary = recommend(make_product(), user_profile=None)
    assert summary["fit_score"] is None
    assert summary["personalized"] is False


def test_with_profile_returns_real_fit_score():
    user_profile = UserProfile(skin_type="oily", concerns=[], sensitive=False)
    summary = recommend(make_product(), user_profile=user_profile)
    assert summary["fit_score"] == 85
    assert summary["personalized"] is True
