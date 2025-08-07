from typing import Optional
import datetime
from ninja import Router, Query
from ninja.errors import HttpError
from ninja.responses import Response
from django.http import HttpRequest
from django.utils import timezone

from .models import AIDailySummary
from apps.api.schema import (
    ResponseSchema,
    BadRequestSchema,
    UnauthorizedSchema,
    ForbiddenSchema,
    NotFoundSchema
)
from .schema import AISummary
from .services.gemini_service import generate_summary
from apps.api.auth import JWTAuth


router = Router(tags=["AI 요약"], auth=JWTAuth())


@router.get(
    path="",
    summary="AI 요약 API",
    description="""
선택한 날짜의 요약이 있으면 제공, 없으면 생성 후 제공합니다.
- 날짜를 지정하지 않으면 오늘 날짜의 요약을 제공합니다.
- 날짜 형식은 `YYYY-MM-DD`입니다.
    """,
    response={
        200: ResponseSchema[AISummary],
        401: UnauthorizedSchema,
    },
)
def get_or_generate_ai_summary(
    request: HttpRequest,
    date: Optional[datetime.date] = Query(
        None, 
        description="요약을 확인할 날짜 (YYYY-MM-DD)", 
        example=f"{timezone.now().date()}"
    ),
) -> Response:
    user = request.user
    if not user.is_authenticated:
        raise HttpError(401, message="로그인이 필요합니다.")

    target_date = date or timezone.now().date()

    summary = AIDailySummary.objects.filter(user=user, date=target_date).first()

    if not summary:
        success, generated = generate_summary(user, target_date)
        if not success:
            raise HttpError(404, message=generated)

        summary = AIDailySummary.objects.create(
            user=user,
            date=target_date,
            message=generated
        )
        # summary.save()

    return Response(
        ResponseSchema[str](
            message=f"{target_date} 요약 제공",
            data=summary.message,
        )
    )
