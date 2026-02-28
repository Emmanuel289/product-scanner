from handler import handler

test_event = {
    "Records": [
        {
            "s3": {
                "bucket": {"name": "product-scanner-uploads-fb45fe8f"},
                "object": {"key": "image2.png"}
            }
        }
    ]
}

response = handler(test_event, None)
print(response)
