from core.app.handler import handler

test_event_without_user_profile = {
    "Records": [
        {
            "s3": {
                "bucket": {"name": "product-scanner-uploads-a881c564"},
                "object": {"key": "image3.png"}
            },
        }
    ]
}

user_profile = {
    "skin_type": "oily",
    "concerns": ["acne", "oil control"],
    "sensitive": False,
}


test_event_with_user_profile = {
    "Records": [
        {
            "s3": {
                "bucket": {"name": "product-scanner-uploads-a881c564"},
                "object": {"key": "image3.png"}
            },
            "user_profile": user_profile
        }
    ]
}

print(f"Testing event without user profile ...")
response = handler(test_event_without_user_profile, None)
print(f"Response without user profile:\n{response}")
print(f"Testing event with user profile ...")
response = handler(test_event_with_user_profile, None)
print(f"Response with user profile:\n {response}")
