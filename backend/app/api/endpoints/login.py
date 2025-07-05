from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.models.users import User, Token
from app.services.user_service import UserService
from app.core.config import settings
from app.core.security import create_access_token
from typing import Annotated
from datetime import timedelta

user_service = UserService()

router = APIRouter()

@router.post("/access-token")
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user: User = await user_service.authenticate(
        username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=create_access_token(
            user.user_id, expires_delta=access_token_expires
        )
    )
