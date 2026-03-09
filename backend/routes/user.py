
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from config import settings
from schemas import (
    RegisterUserRequest,
    AddGuardianRequest,
    LoginRequest,
    LoginResponse,
    MeResponse,
    StatusResponse,
)
from utils.security import create_session_token, revoke_session_token, verify_session_token
from utils.storage import init_db, upsert_user, add_guardian

router = APIRouter()
init_db()

@router.post("/register")
def register_user(user: RegisterUserRequest) -> StatusResponse:
    """
    Register a new user.
    """
    upsert_user(user.model_dump())
    return {"status": "registered"}


@router.post("/login")
def login_user(payload: LoginRequest) -> LoginResponse:
    """
    Simple login endpoint for project demo usage.
    """
    if (
        payload.username != settings.DEMO_USERNAME
        or payload.password != settings.DEMO_PASSWORD
    ):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_session_token(payload.username)
    return {
        "status": "authenticated",
        "token": token,
        "username": payload.username,
    }


@router.get("/me")
def me(username: str = Depends(verify_session_token)) -> MeResponse:
    """
    Return logged-in user profile for demo session.
    """
    return {"status": "active", "username": username}


@router.post("/logout")
def logout(_: str = Depends(revoke_session_token)) -> StatusResponse:
    """
    Invalidate current auth token.
    """
    return {"status": "logged out"}

@router.post("/guardian")
def add_guardian_contact(data: AddGuardianRequest) -> StatusResponse:
    """
    Add a guardian contact for a user.
    """
    add_guardian(data.user_id, data.contact)
    return {"status": "guardian added"}
