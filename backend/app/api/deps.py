from fastapi.security import OAuth2PasswordBearer

from fastapi import Depends, HTTPException, status
from app.models.users import User, TokenPayload
from app.core.config import settings
from app.core import security
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

TokenDep = Annotated[str, Depends(reusable_oauth2)]

async def get_current_user(token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    print(token_data.sub)
    print(type(token_data.sub))
    user = await User.find_one(User.user_id == token_data.sub)
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
