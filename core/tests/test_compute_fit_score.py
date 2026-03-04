from constants import UserProfile
from decision_engine import compute_fit_score, generate_decision_summary


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
    assert score == 81, f"Expected 81, got {score}"


def test_dry_skin_scores_low():
    user_profile = UserProfile(skin_type="dry", concerns=[], sensitive=False)
    score = compute_fit_score(make_product(), user_profile)
    assert score == 26, f"Expected 26, got {score}"


def test_matching_concern_increases_score():
    user_profile = UserProfile(skin_type="oily", concerns=["acne"], sensitive=False)
    score = compute_fit_score(make_product(), user_profile)
    assert score == 84, f"Expected 84, got {score}"


def test_no_profile_returns_none_fit_score():
    summary = generate_decision_summary(make_product(), user_profile=None)
    assert summary["fit_score"] is None
    assert summary["personalized"] is False


def test_with_profile_returns_real_fit_score():
    user_profile = UserProfile(skin_type="oily", concerns=[], sensitive=False)
    summary = generate_decision_summary(make_product(), user_profile=user_profile)
    assert summary["fit_score"] == 81
    assert summary["personalized"] is True
