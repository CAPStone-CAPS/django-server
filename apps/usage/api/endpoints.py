from datetime import datetime, timedelta

from ninja import Router
from ninja.responses import Response
from django.db import IntegrityError

from apps.api.auth import JWTAuth
from apps.api.schema import (
    ResponseSchema,
    UnauthorizedSchema,
    ForbiddenSchema,
    NotFoundSchema,
)
from apps.usage.api.schemas import (
    UsageRecordCreateSchema,
    UsageRecordSchema,
    UsageListResponseSchema,
)
from apps.usage.models import UsageRecord, AppInfo

router = Router(tags=["Usage"], auth=JWTAuth())

COMMON_ERROR_RESPONSES = {
    401: UnauthorizedSchema,
    403: ForbiddenSchema,
    404: NotFoundSchema,
    500: ResponseSchema[None],
}


@router.post("/usage/record", response={
    200: ResponseSchema[None],
    **COMMON_ERROR_RESPONSES,
})
def record_usage(request, data: UsageRecordCreateSchema):
    user = request.user

    try:
        app, _ = AppInfo.objects.get_or_create(
            package_name=data.package_name,
            defaults={"app_name": data.app_name}
        )

        UsageRecord.objects.create(
            user=user,
            app=app,
            usage_time_ms=data.usage_time_ms,
            start_time=data.start_time,
            end_time=data.end_time,
        )

        return 200, ResponseSchema(
            message="사용시간 기록 성공",
            data=None
        )

    except IntegrityError as e:
        return 500, ResponseSchema(
            message=f"앱 정보 저장 실패: {e}",
            data=None
        )

    except Exception as e:
        return 500, ResponseSchema(
            message=f"기록 저장 실패: {e}",
            data=None
        )


@router.get("/usage/list", response={
    200: ResponseSchema[UsageListResponseSchema],
    **COMMON_ERROR_RESPONSES,
})
def list_usage(request):
    user = request.user
    records = UsageRecord.objects.select_related("app").filter(user=user).order_by("-start_time")

    result = []
    for r in records:
        start_str = datetime.fromtimestamp(r.start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
        end_str = datetime.fromtimestamp(r.end_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
        usage_time_str = str(timedelta(milliseconds=r.usage_time_ms))

        record = UsageRecordSchema(
            package_name=r.app.package_name,
            app_name=r.app.app_name,
            usage_time_ms=r.usage_time_ms,
            start_time=r.start_time,
            end_time=r.end_time,
            start_time_str=start_str,
            end_time_str=end_str,
            usage_time_str=usage_time_str,
        )
        result.append(record)

    return 200, ResponseSchema(
        message="사용시간 리스트 조회 성공",
        data={"records": result}
    )