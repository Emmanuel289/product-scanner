import json
import pytest
import base64
from unittest.mock import patch, MagicMock
from handler import handler


FAKE_IMAGE = base64.b64encode(b"fake-image-bytes").decode()
OPTIONS_EVENT = {"httpMethod": "OPTIONS", "body": None}


def generate_s3_event(key, user_profile=None):
    return {
        "Records": [{
            "s3": {
                "bucket": {"name": "product-scanner-maximus"},
                "object": {"key": key},
            },
            **({"user_profile": user_profile} if user_profile else {}),
        }]
    }


def generate_http_event(body):
    return {
        "httpMethod": "POST",
        "body": json.dumps(body),
    }


# A minimal product that satisfies build_result() and recommend()
MOCK_MATCHED_PRODUCT = {
    "product_id":        "charlotte-tilbury-flawless-finish-foundation",
    "brand":             "Charlotte Tilbury",
    "name":              "Flawless Finish Foundation",
    "search_tokens":     ["charlotte", "tilbury", "flawless", "finish", "foundation"],
    "category":          "foundation",
    "texture":           "liquid",
    "finish":            "matte",
    "coverage":          "medium",
    "best_for":          ["oily skin", "combination skin"],
    "avoid_for":         ["dry skin"],
    "concerns_targeted": ["acne", "oil control"],
    "concerns_not_ideal": ["dryness"],
    "comedogenic_risk":  "low",
    "sensitivity_risk":  "low",
    "skin_types":        ["oily", "combination"],
    "ingredient_intent": "Niacinamide (helps reduce pores and control oil) + SPF 15 (protects skin from UV damage)",
    "pros":              ["Long lasting", "Buildable coverage"],
    "cons":              ["Not ideal for dry skin"],
}


# ----- Test HTTP branch ----- #
def test_cors_preflight_returns_200():
    response = handler(OPTIONS_EVENT, None)
    assert response["statusCode"] == 200
    assert response["headers"]["Access-Control-Allow-Origin"] == "*"


def test_missing_image_base64_returns_400():
    response = handler(generate_http_event({}), None)
    assert response["statusCode"] == 400
    body = json.loads(response["body"])
    assert "error" in body


def test_http_product_not_found_when_no_match(mock_textract_no_match):
    response = handler(generate_http_event({"image_base64": FAKE_IMAGE}), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "Not Found" in body["status"]


def test_http_response_has_expected_shape(mock_textract_match):
    response = handler(generate_http_event({"image_base64": FAKE_IMAGE}), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    for key in ["status", "brand", "product_name", "product_summary", "alternatives"]:
        assert key in body, f"Missing key: {key}"


def test_http_fit_score_is_none_without_user_profile(mock_textract_match):
    response = handler(generate_http_event({"image_base64": FAKE_IMAGE}), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    summary = body["product_summary"]
    assert summary["personalized"] is False
    assert summary["fit_score"] is None


def test_http_returns_fit_score_when_user_profile_provided(mock_textract_match):
    response = handler(generate_http_event({
        "image_base64": FAKE_IMAGE,
        "user_profile": {"skin_type": "oily", "concerns": [], "sensitive": False},
    }), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    summary = body["product_summary"]
    assert summary["personalized"] is True
    assert isinstance(summary["fit_score"], int)


# ----- Test S3 branch ----- #

def test_s3_event_product_not_found(mock_textract_no_match):
    response = handler(generate_s3_event("scans/unknown.jpg"), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert "Not Found" in body["status"]


def test_s3_event_without_user_profile(mock_textract_match):
    response = handler(generate_s3_event("scans/test-image.jpg"), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    summary = body["product_summary"]
    assert summary["personalized"] is False
    assert summary["fit_score"] is None


def test_s3_event_with_user_profile(mock_textract_match):
    user_profile = {"skin_type": "oily", "concerns": [], "sensitive": False}
    response = handler(generate_s3_event(
        "scans/test-image.jpg", user_profile), None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    summary = body["product_summary"]
    assert summary["personalized"] is True
    assert isinstance(summary["fit_score"], int)


# ----- Fixtures for mocking calls to the product db, S3 bucket, and Textract ----- #
@pytest.fixture
def mock_textract_match():
    with patch("handler.s3_client") as mock_s3, \
            patch("handler.textract_client"), \
            patch("handler.match_product", return_value=MOCK_MATCHED_PRODUCT):
        mock_s3.put_object.return_value = {}
        yield


@pytest.fixture
def mock_textract_no_match():
    with patch("handler.s3_client") as mock_s3, \
            patch("handler.textract_client"), \
            patch("handler.match_product", return_value=None):
        mock_s3.put_object.return_value = {}
        yield
