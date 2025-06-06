from fastapi import APIRouter
from app.models.users import UserCreate, User, UserPublic
from app.services.user_service import UserService
from app.api.deps import CurrentUser
from typing import Any

router = APIRouter()

user_service = UserService()

@router.post('/signup')
async def register_user(user: UserCreate) -> User:
    return await user_service.create_user(user)

@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user
