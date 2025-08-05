from ninja import Router
from ninja.responses import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.api.schema import ResponseSchema
from apps.api.auth import JWTAuth
from .schemas import SignupSchema, LoginSchema, UpdateUserSchema, UserResponse, SignupResponse, TokenResponse

router = Router(tags=["회원 계정 관련 API"])


@router.post("/signup",
    summary="회원가입 API",
    description="""
    회원가입을 위한 API입니다.
    
    - username과 password를 JSON 문자열로 포함해야 합니다.
    """,
    response=ResponseSchema[SignupResponse])

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


@router.post("/login",
    summary="로그인 API",
    description="""
    로그인을 위한 API입니다.
    
    - username과 password를 JSON 문자열로 포함해야 합니다.
    - 응답으로 JWT 토큰이 발급됩니다. 헤더에 담아서 인가에 사용하세요.
    """,
    response=ResponseSchema[TokenResponse])
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


@router.get("/me", auth=JWTAuth(),
    summary="본인 정보 확인 API",
    description="""
    본인 정보 확인을 위한 API입니다.
    
    - 결과값으로 user_id와 username을 반환합니다.
    """,
    response=ResponseSchema[UserResponse])

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


@router.patch("/me", auth=JWTAuth(),
    summary="정보 수정 API",
    description="""
    정보 수정을 위한 API입니다.
    
    - 변경하고자 하는 username과 password를 JSON 문자열로 포함해야 합니다.
    """,

    response=ResponseSchema[UserResponse])
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