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
    MemoSchema,
    MemoResponseSchema,
)
from apps.usage.models import UsageRecord, AppInfo

router = Router(tags=["Usage"], auth=JWTAuth())

COMMON_ERROR_RESPONSES = {
    401: UnauthorizedSchema,
    403: ForbiddenSchema,
    404: NotFoundSchema,
    500: ResponseSchema[None],
}


@router.post("/record", response={
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

        record = UsageRecord.objects.create(
            user=user,
            app=app,
            usage_time_ms=data.usage_time_ms,
            start_time=data.start_time,
            end_time=data.end_time,
        )

        return Response(
            {"message": "사용시간 기록 성공",
             "data": {
                 "record_id": record.id
                }
             },
            status=200
        )

    except IntegrityError as e:
        return Response(
            {"message": f"앱 정보 저장 실패: {e}", "data": None},
            status=500
        )

    except Exception as e:
        return Response(
            {"message": f"기록 저장 실패: {e}", "data": None},
            status=500
        )


@router.get("/list", response={
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
            id=r.id,
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

    return Response(
        {
            "message": "사용시간 리스트 조회 성공",
            "data": {"records": result}
        },
        status=200
    )


@router.post("/{record_id}/memo", response={
    200: ResponseSchema[MemoResponseSchema],
    **COMMON_ERROR_RESPONSES,
})
def set_usage_memo(request, record_id: int, payload: MemoSchema):
    try:
        record = UsageRecord.objects.get(id=record_id, user=request.user)
    except UsageRecord.DoesNotExist:
        return Response({"message": "사용 기록을 찾을 수 없습니다", "data": None}, status=404)

    record.memo = payload.memo
    record.save()

    return Response({
        "message": "메모 등록/수정 완료",
        "data": {"id": record.id, "memo": record.memo}
    }, status=200)


@router.get("/{record_id}/memo", response={
    200: ResponseSchema[MemoResponseSchema],
    **COMMON_ERROR_RESPONSES,
})
def get_usage_memo(request, record_id: int):
    try:
        record = UsageRecord.objects.get(id=record_id, user=request.user)
    except UsageRecord.DoesNotExist:
        return Response({"message": "사용 기록을 찾을 수 없습니다", "data": None}, status=404)

    return Response({
        "message": "메모 조회 성공",
        "data": {"id": record.id, "memo": record.memo}
    }, status=200)


@router.delete("/{record_id}/memo", response={
    200: ResponseSchema[MemoResponseSchema],
    **COMMON_ERROR_RESPONSES,
})
def delete_usage_memo(request, record_id: int):
    try:
        record = UsageRecord.objects.get(id=record_id, user=request.user)
    except UsageRecord.DoesNotExist:
        return Response({"message": "사용 기록을 찾을 수 없습니다", "data": None}, status=404)

    record.memo = None
    record.save()

    return Response({
        "message": "메모 삭제 완료",
        "data": {"id": record.id, "memo": None}
    }, status=200)