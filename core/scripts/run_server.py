import json
import sys
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from core.app.handler import handler as lambda_handler

app = FastAPI()

origins = [
    "http://localhost:5173",  # The default origin domain for the local frontend
    "http://localhost:3000",  # fallback domain in case port 5137 is in use
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
)


@app.post("/scan", response_model=None)
async def scan(req: Request) -> dict:
    body = await req.json()
    user_profile = body.get("user_profile")
    if user_profile:
        print(f"selected user profile is {user_profile}")
    event = {"httpMethod": req.method, "body": json.dumps(body)}
    return lambda_handler(event, context=None)
