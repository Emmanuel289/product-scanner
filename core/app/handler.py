import json
from core.app.constants import BRAND_ALIASES, SCANNER_BUCKET, STOPWORDS
from core.app.utils import (
    app_logger,
    cors_headers,
    build_products,
    build_result,
    load_products_from_dynamodb,
    match_product,
    parse_user_profile,
    run_textract_and_match,
    upload_image_to_s3,
)

# ----- Build products at cold-start ----- #
DOWNLOADED_PRODUCTS = load_products_from_dynamodb()
PRODUCTS_BY_BRAND = build_products(DOWNLOADED_PRODUCTS, BRAND_ALIASES, STOPWORDS)
app_logger.info(
    f"Cold start complete. {len(DOWNLOADED_PRODUCTS)} products across {len(PRODUCTS_BY_BRAND)} brands."
)


# ----- Lambda Handler ----- #
def handler(event, context):

    # ------------------------------------------------------------------ #
    # HTTP branch — triggered by API Gateway (POST /scan)                 #
    # ------------------------------------------------------------------ #
    if event.get("httpMethod"):

        # --- CORS preflight --- #
        if event["httpMethod"] == "OPTIONS":
            return {"statusCode": 200, "headers": cors_headers(), "body": ""}

        try:
            body = json.loads(event.get("body", "{}"))
            user_profile_data = body.get("user_profile")

            # ── Name search branch (fallback) ─────────────────────────
            product_name_query = body.get("product_name")
            matched_product_by_name = None
            if product_name_query:
                app_logger.info(f"Name search: {product_name_query}")
                matched_product_by_name = match_product(
                    product_name_query, PRODUCTS_BY_BRAND, STOPWORDS
                )
                if not matched_product_by_name:
                    return {
                        "statusCode": 200,
                        "headers": cors_headers(),
                        "body": json.dumps(
                            {
                                "status": "❌ Product Not Found",
                                "message": "We couldn't confidently identify this product, so we didn't make a guess.",
                            }
                        ),
                    }
                user_profile = parse_user_profile(user_profile_data)
                result = build_result(
                    matched_product_by_name, user_profile, PRODUCTS_BY_BRAND
                )
                return {
                    "statusCode": 200,
                    "headers": cors_headers(),
                    "body": json.dumps(result),
                }

            # --- Upload image to S3 so Textract can read it --- #
            image_b64 = body.get("image_base64")
            if not image_b64 and not product_name_query:
                return {
                    "statusCode": 400,
                    "headers": cors_headers(),
                    "body": json.dumps(
                        {"error": "image_base64 or product name is required"}
                    ),
                }
            key = upload_image_to_s3(image_base64=image_b64, bucket=SCANNER_BUCKET)

            # --- Textract + match --- #
            matched_product_by_image = run_textract_and_match(
                products_by_brand=PRODUCTS_BY_BRAND,
                stop_words=STOPWORDS,
                key=key,
                bucket=SCANNER_BUCKET,
            )
            print(f"matched_product by image", matched_product_by_image)
            if not matched_product_by_image:
                return {
                    "statusCode": 200,
                    "headers": cors_headers(),
                    "body": json.dumps(
                        {
                            "status": "❌ Product Not Found",
                            "message": "We couldn't confidently identify this product, so we didn't make a guess.",
                        }
                    ),
                }

            # --- Decision engine --- #
            user_profile = parse_user_profile(user_profile_data)
            matched_product = matched_product_by_image or matched_product_by_name
            result = build_result(matched_product, user_profile, PRODUCTS_BY_BRAND)
            return {
                "statusCode": 200,
                "headers": cors_headers(),
                "body": json.dumps(result),
            }

        except Exception as e:
            app_logger.error(f"Error in HTTP branch: {str(e)}")
            return {
                "statusCode": 500,
                "headers": cors_headers(),
                "body": json.dumps({"error": str(e)}),
            }

    # ------------------------------------------------------------------ #
    # S3 event branch — triggered directly by S3 event notifications      #
    # ------------------------------------------------------------------ #
    for record in event.get("Records", []):
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        user_profile_data = record.get("user_profile")

        try:
            matched_product = run_textract_and_match(
                products_by_brand=PRODUCTS_BY_BRAND,
                stop_words=STOPWORDS,
                key=key,
                bucket=SCANNER_BUCKET,
            )
            if not matched_product:
                return {
                    "statusCode": 200,
                    "body": json.dumps(
                        {
                            "status": "❌ Product Not Found",
                            "message": "We couldn't confidently identify this product, so we didn't make a guess.",
                        }
                    ),
                }

            user_profile = parse_user_profile(user_profile_data)
            result = build_result(matched_product, user_profile, PRODUCTS_BY_BRAND)

            return {"statusCode": 200, "body": json.dumps(result)}

        except Exception as e:
            print("Error in S3 branch:", str(e))
            return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
