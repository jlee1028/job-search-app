from pydantic import BaseModel, Field
from beanie import Document, Indexed
import uuid

class UserBase(BaseModel):
    username: Indexed(str, unique=True) # type: ignore[reportInvalidTypeForm]

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)

class User(UserBase, Document):
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    hashed_password: str

# Properties to return via API, id is always required
class UserPublic(UserBase):
    user_id: uuid.UUID

class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int


# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    sub: uuid.UUID | None = None # this is User.user_id
