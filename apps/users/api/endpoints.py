import os
import magic

from ninja import Router, File
from ninja.files import UploadedFile
from ninja.responses import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.api.schema import (
    ResponseSchema,
    BadRequestSchema,
    UnauthorizedSchema,
    ForbiddenSchema,
    NotFoundSchema
)
from apps.api.auth import JWTAuth
from .schemas import (
    SignupSchema,
    LoginSchema,
    UpdateUserSchema,
    UserResponse,
    SignupResponse,
    TokenResponse,
    UploadProfileResponse
)
from ..models import Profile

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
    
    
@router.post(
    "/upload-profile-image", 
    response={
        200: ResponseSchema[UploadProfileResponse],
        400: BadRequestSchema,
        401: UnauthorizedSchema,
    },
    description="""
프로필 이미지 업로드 엔드포인트입니다.
- 인증된 사용자만 접근할 수 있습니다.
- 업로드된 이미지는 사용자 프로필에 저장됩니다.
- 요청 본문에 `file` 필드로 이미지를 포함해야 합니다.
- 성공 시 이미지 URL을 반환합니다.
- 프로필 수정을 원하면 다시 여기로 요청하면 됩니다.
"""
)
def upload_profile_image(request, file: File[UploadedFile]):
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
    MAX_SIZE_MB = 5
    
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return 400, {"message": "지원하지 않는 이미지 형식입니다."}
    
    
    if file.size > MAX_SIZE_MB * 1024 * 1024:
        return 400, {"message": f"{MAX_SIZE_MB}MB 이하의 이미지만 업로드할 수 있습니다."}
    
    # MIME 타입 검사
    mime = magic.from_buffer(file.file.read(1024), mime=True)
    file.file.seek(0)  # 읽은 뒤 포인터 초기화
    if not mime.startswith("image/"):
        return 400, {"message": "이미지 파일만 업로드할 수 있습니다."}
    
    user = request.user
    if not user.is_authenticated:
        return 401, {"message": "인증되지 않은 사용자입니다."}
    
    profile, _ = Profile.objects.get_or_create(user=user)
    if profile.profile_image:
        profile.profile_image.delete(save=False)
        
    profile.profile_image.save(file.name, file, save=True)
    profile.save()

    return ResponseSchema(
        message="프로필 이미지 업로드 성공",
        data=UploadProfileResponse(
            image_url=profile.profile_image.url
        )
    )