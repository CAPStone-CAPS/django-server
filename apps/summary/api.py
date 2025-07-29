from ninja import Router
from ninja.responses import Response
from django.http import HttpRequest
from django.utils import timezone

from .models import AIDailySummary
from apps.api.schema import ResponseSchema


router = Router(
    tags=["AI 요약"],
    description="AI 요약 생성/조회 관련 API들"
)
