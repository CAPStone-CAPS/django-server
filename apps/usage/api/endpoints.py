from datetime import datetime, timedelta

from ninja import Router
from ninja.responses import Response

from apps.api.auth import JWTAuth
from apps.usage.api.schemas import (
    UsageRecordCreateSchema,
    UsageRecordSchema,
    UsageListResponseSchema,
    SimpleResponseSchema,
)
from apps.usage.models import UsageRecord, AppInfo

router = Router(tags=["Usage"])

@router.post("/usage/record", auth=JWTAuth(), response=SimpleResponseSchema)
def record_usage(request, data: UsageRecordCreateSchema):
    user = request.user
    try:
        app, _ = AppInfo.objects.get_or_create(
            package_name=data.package_name,
            defaults={"app_name: data.app_name"}
        )

        UsageRecord.objects.create(
            user=user,
            app = app,
            usage_time_ms=data.usage_time_ms,
            start_time=data.start_time,
            end_time=data.end_time,
        )
        return {"message": "사용시간 기록 성공", "data": None}
    except Exception as e:
        return Response({"message": f"기록 저장 실패: {e}", "data": None}, status=500)


@router.get("/usage/list", auth=JWTAuth(), response=UsageListResponseSchema)
def list_usage(request):
    user = request.user
    records = UsageRecord.objects.filter(user=user).order_by("-start_time")

    result = []
    for r in records:
        start_str = datetime.fromtimestamp(r.start_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
        end_str = datetime.fromtimestamp(r.end_time / 1000).strftime("%Y-%m-%d %H:%M:%S")
        duration = timedelta(milliseconds=r.usage_time_ms)
        usage_time_str = str(duration)

        record = UsageRecordSchema(
            package_name=r.package_name,
            app_name=r.app_name,
            usage_time_ms=r.usage_time_ms,
            start_time=r.start_time,
            end_time=r.end_time,
            start_time_str=start_str,
            end_time_str=end_str,
            usage_time_str=usage_time_str,
        )
        result.append(record)

    return {"records": result}