from fastapi import HTTPException
from app.models.users import User, UserCreate
from app.core.security import get_password_hash, verify_password

class UserService:
    
    async def create_user(self, user_create: UserCreate) -> User:
        if await User.find_one(User.username == user_create.username).exists():
            raise HTTPException(
                status_code=400,
                detail="A user with this username already exists",
            )
        user = User(
            username=user_create.username,
            hashed_password=get_password_hash(user_create.password)
        )
        await User.insert_one(user)
        return user

    async def authenticate(self, username: str, password: str) -> User | None:
        user: User = await User.find_one(User.username == username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
