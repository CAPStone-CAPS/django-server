from ninja import Router
from ninja.responses import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.api.schema import ResponseSchema
from apps.api.auth import JWTAuth
from .schemas import SignupSchema, LoginSchema, UpdateUserSchema, UserResponse, SignupResponse, TokenResponse

router = Router(tags=["Login"])


@router.post("/signup", response=ResponseSchema[SignupResponse])
def signup(request, data: SignupSchema):
    if User.objects.filter(username=data.username).exists():
        return Response(
            {"message": "이미 존재하는 사용자입니다.", "data": None},
            status=400
        )
    user = User.objects.create_user(username=data.username, password=data.password)
    return Response(
        {"message": "회원가입 성공", "data": {"username": user.username}},
        status=201
    )


@router.post("/login", response=ResponseSchema[TokenResponse])
def login(request, data: LoginSchema):
    user = authenticate(username=data.username, password=data.password)
    if user is None:
        return Response(
            {"message": "아이디 또는 비밀번호가 잘못되었습니다.", "data": None},
            status=401
        )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            "message": "로그인 성공",
            "data": {
                "accessToken": str(refresh.access_token),
                "refresh": str(refresh),
            }
        },
        status=200
    )


@router.get("/me", auth=JWTAuth(), response=ResponseSchema[UserResponse])
def me(request):
    return Response(
        {
            "message": "회원 정보 조회 성공",
            "data": {
                "id": request.user.id,
                "username": request.user.username,
            }
        },
        status=200
    )


@router.patch("/me", auth=JWTAuth(), response=ResponseSchema[UserResponse])
def update_user(request, data: UpdateUserSchema):
    user = request.user

    if data.username:
        if User.objects.exclude(id=user.id).filter(username=data.username).exists():
            return Response(
                {"message": "이미 존재하는 사용자 이름입니다.", "data": None},
                status=400
            )
        user.username = data.username

    if data.password:
        user.set_password(data.password)

    user.save()

    return Response(
        {
            "message": "회원 정보가 성공적으로 수정되었습니다.",
            "data": {
                "id": user.id,
                "username": user.username,
            }
        },
        status=200
    )