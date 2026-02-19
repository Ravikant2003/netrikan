from fastapi import APIRouter

router = APIRouter()

users = {}
guardians = {}


@router.post("/register")
def register_user(user: dict):
    users[user["id"]] = user
    return {"status": "registered"}


@router.post("/guardian")
def add_guardian(data: dict):
    guardians.setdefault(data["user_id"], []).append(data["contact"])
    return {"status": "guardian added"}
