from ninja import Router
from ninja.errors import HttpError
from ninja.responses import Response
from django.http import HttpRequest
from django.utils import timezone

from .models import AIDailySummary
from apps.api.schema import ResponseSchema
from .schema import AISummary
from .services.gemini_service import generate_summary


router = Router(tags=["AI 요약"])


@router.get(
    path="", 
    description="오늘자 요약이 있으면 제공, 없으면 생성 후 제공합니다.",
    response=ResponseSchema[AISummary]
)
def get_ai_summary(request: HttpRequest) -> Response:
    user = request.user
    if not user.is_authenticated:
        return HttpError(
            status=401,
            data={"message": "로그인이 필요합니다."}
        )

    today = timezone.now().date()
    summary = AIDailySummary.objects.filter(user=user, date=today).first()

    if not summary:
        # 여기에 시간 데이터 DB에서 가져오는 로직 넣어보기
        generated = generate_summary()
        summary = AIDailySummary.objects.create(
            user=user,
            date=today,
            message=generated
        )
        summary.save()

    return Response(
        ResponseSchema[str](
            message="성공",
            data=summary.message,
        )
    )
