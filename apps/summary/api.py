from ninja import Router
from ninja.responses import Response
from django.http import HttpRequest
from django.utils import timezone

from .models import AIDailySummary
from apps.api.schema import ResponseSchema
from .schema import AISummary


# Gemini 호출 (추후 구현)
def generate_summary_for_user(user):
    pass

router = Router(tags=["AI 요약"])


@router.get(
    path="", 
    description="오늘자 요약이 있으면 제공, 없으면 생성 후 제공합니다.",
    response=ResponseSchema[AISummary]
)
def get_ai_summary(request: HttpRequest):
    user = request.user
    if not user.is_authenticated:
        return Response(status=401, data={"message": "로그인이 필요합니다."})

    today = timezone.now().date()
    summary, created = AIDailySummary.objects.get_or_create(
        user=user,
        date=today,
        defaults={
            "message": generate_summary_for_user(user)  # Gemini 호출 (추후 구현)
        }
    )

    return ResponseSchema[AISummary](
        message="성공",
        data=AISummary(
            message=summary.message,
            date=str(summary.date)
        )
    )
