from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar
from ninja import Schema

T = TypeVar("T")

class StandardResponse(BaseModel, Generic[T]):
    isSuccess: bool = True
    code: str = "COMMON200"
    message: str = "성공입니다."
    result: Optional[T] = None

class UserResponse(BaseModel):
    id: int
    username: str
    profile_image_url: Optional[str] = None

class SignupSchema(BaseModel):
    username: str
    password: str

class LoginSchema(BaseModel):
    username: str
    password: str

class UpdateUserSchema(BaseModel):
    username: Optional[str] = Field(None, example="newusername")
    password: Optional[str] = Field(None, example="newpassword")

class SignupResponse(Schema):
    username: str

class TokenResponse(Schema):
    accessToken: str
    refresh: str
 
    
class UploadProfileResponse(Schema):
    profile_image_url: str