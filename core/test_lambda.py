from app import handler

test_event = {
    "Records": [
        {
            "s3": {
                "bucket": {"name": "product-scanner-uploads-ada0307c"},
                "object": {"key": "image1.png"}
            }
        }
    ]
}

response = handler(test_event, None)
print(response)