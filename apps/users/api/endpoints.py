from ninja import Router
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from ninja.security import HttpBearer
from django.http import HttpRequest
from apps.users.api.schemas import StandardResponse

from .schemas import SignupSchema, LoginSchema, UpdateUserSchema

router = Router(tags=["Login"])

class JWTAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str):
        try:
            validated_token = JWTAuthentication().get_validated_token(token)
            user = JWTAuthentication().get_user(validated_token)
            request.user = user
            return user
        except Exception:
            return None

@router.post("/signup",
    summary="회원가입 API",
    description="회원가입을 진행합니다. 이미 존재하는 사용자일 경우 오류를 반환합니다.",
    response=StandardResponse
)
def signup(request, data: SignupSchema):
    if User.objects.filter(username=data.username).exists():
        return {"error": "이미 존재하는 사용자입니다."}
    user = User.objects.create_user(username=data.username, password=data.password)
    return {"msg": "회원가입 성공", "username": user.username}

@router.post("/login",
    summary="로그인 API",
    description="회원가입 시 입력한 username과 password를 넣어 로그인하세요. 응답으로 JWT access/refresh 토큰이 발급됩니다. 헤더에 담아서 인가에 사용하세요.",
    response=StandardResponse
)
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user is None:
        return {"error": "아이디 또는 비밀번호가 잘못되었습니다."}
    refresh = RefreshToken.for_user(user)
    return {
            "isSuccess": True,
            "code": "COMMON200",
            "message": "성공입니다.",
            "result": {
                "accessToken": str(refresh.access_token),
                "refresh": str(refresh),
            }
    }

@router.get("/me", auth=JWTAuth(),
    summary="회원 정보 조회 API",
    description="현재 회원 정보를 조회합니다. 응답으로 userId와 username을 반환합니다.",
    response=StandardResponse
)
def me(request):
    return {
            "isSuccess": True,
            "code": "COMMON200",
            "message": "성공입니다.",
            "result": {
                "id": request.user.id,
                "username": request.user.username,
            }
    }


@router.patch("/me", auth=JWTAuth(),
    summary="회원 정보 수정 API",
    description="현재 로그인한 유저의 username 또는 password를 수정합니다. 변경을 원하는 값만 입력해주세요. (변경하지 않을 시, 빈배열 처리"")",
    response=StandardResponse
)
def update_user(request, data: UpdateUserSchema):
    user = request.user

    if data.username:
        if User.objects.exclude(id=user.id).filter(username=data.username).exists():
            return {"error": "이미 존재하는 사용자 이름입니다."}
        user.username = data.username

    if data.password:
        user.set_password(data.password)

    user.save()

    return {
        "isSuccess": True,
        "code": "COMMON200",
        "message": "회원 정보가 성공적으로 수정되었습니다.",
        "result": {
            "id": user.id,
            "username": user.username,
        }
    }