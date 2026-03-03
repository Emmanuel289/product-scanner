# tests/test_lambda.py
import base64
import json
from unittest.mock import patch

import pytest
from handler import handler

# ── Helpers ────────────────────────────────────────────────────────────────────
FAKE_IMAGE = base64.b64encode(b"fake-image-bytes").decode()


def s3_event(key, user_profile=None):
    return {
        "Records": [
            {
                "s3": {
                    "bucket": {"name": "product-scanner-maximus"},
                    "object": {"key": key},
                },
                **({"user_profile": user_profile} if user_profile else {}),
            }
        ]
    }


def http_event(body):
    return {
        "httpMethod": "POST",
        "body": json.dumps(body),
    }


OPTIONS_EVENT = {"httpMethod": "OPTIONS", "body": None}

MOCK_MATCHED_PRODUCT = {
    "product_id": "charlotte-tilbury-flawless-finish-foundation",
    "brand": "Charlotte Tilbury",
    "name": "Flawless Finish Foundation",
    "search_tokens": ["charlotte", "tilbury", "flawless", "finish", "foundation"],
    "category": "foundation",
    "texture": "liquid",
    "finish": "matte",
    "coverage": "medium",
    "best_for": ["oily skin", "combination skin"],
    "avoid_for": ["dry skin"],
    "concerns_targeted": ["acne", "oil control"],
    "concerns_not_ideal": ["dryness"],
    "comedogenic_risk": "low",
    "sensitivity_risk": "low",
    "skin_types": ["oily", "combination"],
    "ingredient_intent": "Niacinamide (reduces pores and controls oil) + SPF 15 (protects from UV damage)",
    "pros": ["Long lasting", "Buildable coverage"],
    "cons": ["Not ideal for dry skin"],
}

MOCK_ALTERNATIVE = {
    "product_id": "charlotte-tilbury-light-wonder-foundation",
    "brand": "Charlotte Tilbury",
    "name": "Light Wonder Foundation",
    "search_tokens": ["charlotte", "tilbury", "light", "wonder", "foundation"],
    "category": "foundation",
    "texture": "lightweight",
    "finish": "natural",
    "coverage": "light",
    "best_for": ["all skin types"],
    "avoid_for": [],
    "concerns_targeted": ["dullness", "uneven skin tone"],
    "concerns_not_ideal": [],
    "comedogenic_risk": "low",
    "sensitivity_risk": "low",
    "skin_types": ["dry", "normal", "sensitive"],
    "ingredient_intent": "Hyaluronic Acid (draws moisture into skin) + Vitamin C (brightens and evens tone)",
    "pros": ["Lightweight feel", "Natural finish"],
    "cons": ["Low coverage"],
}

# PRODUCTS_BY_BRAND with both matched product and a real alternative
MOCK_PRODUCTS_BY_BRAND = {"Charlotte Tilbury": [MOCK_MATCHED_PRODUCT, MOCK_ALTERNATIVE]}


# ── HTTP branch ────────────────────────────────────────────────────────────────
def test_cors_preflight_returns_200():
    response = handler(OPTIONS_EVENT, None)
    assert response["statusCode"] == 200
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"


def test_missing_image_base64_product_name_query_returns_400():
    response = handler(http_event({}), None)
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body


def test_http_name_search_returns_result_when_matched():
    """Name search finds a product and returns full result shape."""
    with patch("handler.match_product", return_value=MOCK_MATCHED_PRODUCT), patch(
        "handler.PRODUCTS_BY_BRAND", MOCK_PRODUCTS_BY_BRAND
    ), patch("handler.load_products_from_dynamodb", return_value=[]):
        response = handler(
            http_event({"product_name": "Flawless Finish Foundation"}), None
        )
        assert response["statusCode"] == 200
        print(f"response is {response}")
        body = json.loads(response["body"])
        assert body["brand"] == "Charlotte Tilbury"
        assert body["product_name"] == "Flawless Finish Foundation"
        assert "product_summary" in body
        assert "alternatives" in body


def test_http_name_search_returns_not_found_when_no_match():
    """Name search with unknown product returns Not Found — no guessing."""
    with patch("handler.match_product", return_value=None), patch(
        "handler.load_products_from_dynamodb", return_value=[]
    ):
        response = handler(http_event({"product_name": "Unknown Product XYZ"}), None)
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert "Not Found" in body["status"]
        assert "message" in body


def test_http_product_not_found_when_no_match(mock_no_match):
    response = handler(http_event({"image_base64": FAKE_IMAGE}), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "Not Found" in body["status"]


def test_http_response_has_expected_shape(mock_match):
    response = handler(http_event({"image_base64": FAKE_IMAGE}), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    for key in ["status", "brand", "product_name", "product_summary", "alternatives"]:
        assert key in body, f"Missing key: {key}"


def test_http_fit_score_is_none_without_user_profile(mock_match):
    response = handler(http_event({"image_base64": FAKE_IMAGE}), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    summary = body["product_summary"]
    assert summary["personalized"] is False
    assert summary["fit_score"] is None


def test_http_returns_fit_score_when_user_profile_provided(mock_match):
    response = handler(
        http_event(
            {
                "image_base64": FAKE_IMAGE,
                "user_profile": {
                    "skin_type": "oily",
                    "concerns": [],
                    "sensitive": False,
                },
            }
        ),
        None,
    )
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    summary = body["product_summary"]
    assert summary["personalized"] is True
    assert isinstance(summary["fit_score"], int)


def test_alternatives_are_returned(mock_match):
    response = handler(http_event({"image_base64": FAKE_IMAGE}), None)
    body = json.loads(response["body"])
    assert len(body["alternatives"]) > 0


def test_alternatives_have_meaningful_explanations(mock_match):
    response = handler(http_event({"image_base64": FAKE_IMAGE}), None)
    body = json.loads(response["body"])
    for alt in body["alternatives"]:
        assert "name" in alt
        assert "why_different" in alt
        assert (
            len(alt["why_different"]) > 20
        ), f"Explanation too short: '{alt['why_different']}'"
        # Should not be the old generic template
        assert "Different texture () or finish ()" not in alt["why_different"]


# ── S3 branch ──────────────────────────────────────────────────────────────────
def test_s3_event_product_not_found(mock_no_match):
    response = handler(s3_event("scans/unknown.jpg"), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "Not Found" in body["status"]


def test_s3_event_without_user_profile(mock_match):
    response = handler(s3_event("scans/test-image.jpg"), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    summary = body["product_summary"]
    assert summary["personalized"] is False
    assert summary["fit_score"] is None


def test_s3_event_with_user_profile(mock_match):
    user_profile = {"skin_type": "oily", "concerns": [], "sensitive": False}
    response = handler(s3_event("scans/test-image.jpg", user_profile), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    summary = body["product_summary"]
    assert summary["personalized"] is True
    assert isinstance(summary["fit_score"], int)


# ── Fixtures ───────────────────────────────────────────────────────────────────
@pytest.fixture
def mock_match():
    with patch("handler.s3_client") as mock_s3, patch("handler.textract_client"), patch(
        "handler.match_product", return_value=MOCK_MATCHED_PRODUCT
    ), patch("handler.PRODUCTS_BY_BRAND", MOCK_PRODUCTS_BY_BRAND), patch(
        "handler.load_products_from_dynamodb", return_value=[]
    ):  # ← add this
        mock_s3.put_object.return_value = {}
        yield


@pytest.fixture
def mock_no_match():
    with patch("handler.s3_client") as mock_s3, patch("handler.textract_client"), patch(
        "handler.match_product", return_value=None
    ), patch(
        "handler.load_products_from_dynamodb", return_value=[]
    ):  # ← add this
        mock_s3.put_object.return_value = {}
        yield
