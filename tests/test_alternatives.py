from handler import explain_alternative


def matched():
    return {
        "texture": "liquid",
        "finish": "matte",
        "skin_types": ["oily", "combination"],
        "concerns_targeted": ["acne", "oil control"],
        "ingredient_intent": "oil control",
    }


def test_shared_concern_is_mentioned():
    alt = {
        "texture": "liquid",
        "finish": "matte",
        "skin_types": ["oily", "combination"],
        "concerns_targeted": ["acne", "brightening"],
        "ingredient_intent": "oil control",
    }
    result = explain_alternative(matched(), alt)
    assert "acne" in result
    assert "goal" in result


def test_texture_difference_is_mentioned():
    alt = {
        "texture": "cream",
        "finish": "matte",
        "skin_types": ["oily", "combination"],
        "concerns_targeted": ["acne", "oil control"],
        "ingredient_intent": "oil control",
    }
    result = explain_alternative(matched(), alt)
    assert "cream" in result


def test_unique_skin_type_is_mentioned():
    alt = {
        "texture": "liquid",
        "finish": "matte",
        "skin_types": ["oily", "combination", "sensitive"],
        "concerns_targeted": ["acne", "oil control"],
        "ingredient_intent": "oil control",
    }
    result = explain_alternative(matched(), alt)
    assert "sensitive" in result
    assert "skin" in result


def test_different_goal_uses_alt_intent():
    alt = {
        "texture": "liquid",
        "finish": "matte",
        "skin_types": ["oily", "combination"],
        "concerns_targeted": ["brightening", "dark spots"],
        "ingredient_intent": "brightening",
    }
    result = explain_alternative(matched(), alt)
    assert "brightening" in result
    assert "instead" in result


def test_fallback_when_no_meaningful_difference():
    alt = {
        "texture": "liquid",
        "finish": "satin",
        "skin_types": ["oily", "combination"],
        "concerns_targeted": [],
        "ingredient_intent": "",
    }
    # No shared concerns, no intent, no texture diff, no unique skin types
    # Should fall through to finish + "different formulation approach"
    result = explain_alternative(matched(), alt)
    assert len(result) > 0
    assert result != ""


def test_returns_string_always():
    """explain_alternative should never raise or return None."""
    result = explain_alternative({}, {})
    assert isinstance(result, str)
    assert len(result) > 0


def test_parts_joined_with_dash_separator():
    alt = {
        "texture": "cream",
        "finish": "matte",
        "skin_types": ["oily", "combination"],
        "concerns_targeted": ["acne", "oil control"],
        "ingredient_intent": "oil control",
    }
    result = explain_alternative(matched(), alt)
    assert " - " in result
