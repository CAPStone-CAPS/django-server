from typing import Optional
from datetime import date

from ninja import Query
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

router = Router(tags=["사용시간 기록 및 메모 기능 API"], auth=JWTAuth())

COMMON_ERROR_RESPONSES = {
    401: UnauthorizedSchema,
    403: ForbiddenSchema,
    404: NotFoundSchema,
    500: ResponseSchema[None],
}


@router.post("/record",
    summary="사용시간 등록 API",
    description="""
    사용 시간을 등록하는 API입니다.

    - 패키지 이름, 앱 이름, 사용시간, 시작시간, 종료 시간을 예시와 같이 JSON 문자열로 포함해야 합니다.
    """,
    response={
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


@router.get("/list",
    summary="사용시간 리스트 조회 API",
    description="""
    date를 이용한 사용 시간 리스트 조회 API입니다.
    
    - 쿼리파라미터 date에 조회하고자 하는 날짜를 전달합니다.
    - 날짜는 (YYYY-MM-DD)형태로 제공해야 합니다. (ex. 2025-07-30)
    - 날짜를 입력하지 않으면 전체 기록을 조회합니다.
    - 결과값으로 record_id, 등록 시 작성했던 내용, 변환값(시작시간, 종료시간, 사용시간)이 제공됩니다.
    """,
    response={
    200: ResponseSchema[UsageListResponseSchema],
    **COMMON_ERROR_RESPONSES,
})
def list_usage(request, date: Optional[date] = Query(None)):
    user = request.user
    target_date = date or datetime.today().date()  # ✅ 이미 date 타입이므로 바로 사용 가능

    if date:
        # 날짜 범위 (하루의 시작과 끝) → 밀리초 단위
        start_of_day = int(datetime.combine(target_date, datetime.min.time()).timestamp() * 1000)
        end_of_day = int(datetime.combine(target_date, datetime.max.time()).timestamp() * 1000)

        # 해당 날짜와 겹치는 기록 조회 (start_time이나 end_time이 하루에 겹치는 경우)
        records = UsageRecord.objects.select_related("app").filter(
            user=user,
            end_time__gte=start_of_day,
            start_time__lte=end_of_day,
        ).order_by("-start_time")
    else:
        # 날짜가 없을 경우 → 전체 기록 조회
        records = UsageRecord.objects.select_related("app").filter(
            user=user
        ).order_by("-start_time")


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


@router.post("/{record_id}/memo",
    summary="사용시간 별 메모 등록 API",
    description="""
    record_id를 이용한 사용 시간별 메모 등록 API입니다.
    
    - 쿼리파라미터 record_id에 메모를 작성하고자 하는 사용시간의 id(record_id)를 전달합니다.
    - record_id는 사용시간 등록 및 목록 조회 시 결과값으로 제공됩니다.
    - 메모 내용을 JSON 문자열로 포함해야 합니다.
    """,
    response={
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


@router.get("/{record_id}/memo",
    summary="사용시간 별 메모 조회 API",
    description="""
    record_id를 이용한 사용 시간별 메모 조회 API입니다.
    
    - 쿼리파라미터 record_id에 메모를 조회하고자 하는 사용시간의 id(record_id)를 전달합니다.
    - record_id는 사용시간 등록 및 목록 조회 시 결과값으로 제공됩니다.
    - 결과값으로 사용시간 id와 메모 내용을 제공합니다.
    """,
    response={
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


@router.delete("/{record_id}/memo",
    summary="사용시간 별 메모 삭제 API",
    description="""
    record_id를 이용한 사용 시간별 메모 삭제 API입니다.
    
    - 쿼리파라미터 record_id에 메모를 삭제하고자 하는 사용시간의 id(record_id)를 전달합니다.
    - record_id는 사용시간 등록 및 목록 조회 시 결과값으로 제공됩니다.
    """,
    response={
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