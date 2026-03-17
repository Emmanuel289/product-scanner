import sys
import os
import json
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.app.handler import handler as lambda_handler  # noqa
from core.app.auth import AuthManager  # noqa
from core.app.client import ScannerClient  # noqa
from core.app.exceptions import AuthError, ClientError, ClientNotFound  # noqa

app = FastAPI(redirect_slashes=False)

origins = [
    "http://localhost:5173",  # The default origin domain for the local frontend
    "http://localhost:3000",  # fallback domain in case port 5137 is in use
]


auth_mgr = AuthManager()


def get_auth_manager():
    return auth_mgr


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.post("/scan", response_model=None)
async def scan(req: Request) -> dict:
    body = await req.json()
    user_profile = body.get("user_profile")
    if user_profile:
        print(f"selected user profile is {user_profile}")
    event = {"httpMethod": req.method, "body": json.dumps(body)}
    return lambda_handler(event, context=None)


@app.post("/signup", response_model=None)
async def signup(
    client: ScannerClient, auth_mgr: AuthManager = Depends(get_auth_manager)
):
    try:
        auth_mgr.store_client(client=client)
        return {"registered": True, "client": auth_mgr.generate_client_dict(client)}
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ClientError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/login", response_model=None)
async def login(
    client: ScannerClient, auth_mgr: AuthManager = Depends(get_auth_manager)
):
    try:
        login_client = auth_mgr.login(client=client)
        return login_client
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ClientNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/logout", response_model=None)
async def logout(client_dict: dict, auth_mgr: AuthManager = Depends(get_auth_manager)):
    try:
        logout_client = auth_mgr.logout(client_dict=client_dict)
        return logout_client
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ClientNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ClientError as e:
        raise HTTPException(status_code=422, detail=str(e))
