from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import User
from django.http import HttpRequest
from ninja.security import HttpBearer
from ninja.errors import HttpError

class JWTAuthHandler:
    def __init__(self):
        self.jwt_auth = JWTAuthentication()

    def authenticate(self, request: HttpRequest, token: str) -> User | None:
        try:
            validated_token = self.jwt_auth.get_validated_token(token.encode())
            user = self.jwt_auth.get_user(validated_token)
            request.user = user
            return user
        except Exception:
            raise HttpError(
                status_code=401, 
                message="유효하지 않은 토큰입니다. 다시 로그인 해주세요."
            )

    def get_user_info(self, token: str) -> dict | None:
        try:
            validated_token = self.jwt_auth.get_validated_token(token.encode())
            payload = validated_token.payload
            return {
                "user_id": payload.get("user_id"),
                "username": payload.get("username"),
            }
        except Exception:
            raise HttpError(
                status_code=401, 
                message="유효하지 않은 토큰입니다. 다시 로그인 해주세요."
            )

class JWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        return JWTAuthHandler().authenticate(request, token)