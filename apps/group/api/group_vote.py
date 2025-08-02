from ninja import Router
from ninja.responses import Response
from django.http import HttpRequest
from django.utils import timezone
from typing import Optional
from datetime import datetime

from ..models import UserGroupMembership, MVPVote
from apps.summary.models import AIDailySummary
from apps.api.schema import (
    ResponseSchema,
    UnauthorizedSchema,
    ForbiddenSchema,
    NotFoundSchema
)
from ..schema import (
    UserSchema,
    MVPVoteCandidateItem,
    MVPVoteInfoResponse,
    MVPVoteRequest,
    MVPResultItem,
    MVPResultResponse,
    MVPVoteHistoryResponse
)
from apps.api.auth import JWTAuth

router = Router(tags=["Group Vote"], auth=JWTAuth())


@router.get("/{group_id}/vote", response={
    200: ResponseSchema[MVPVoteInfoResponse],
    401: UnauthorizedSchema,
    403: ForbiddenSchema,
})
def get_vote_info(request: HttpRequest, group_id: int):
    """
    해당 그룹의 투표 정보를 조회합니다.

    - 오늘 투표 여부 반환
    - 투표 후보 리스트(멤버 및 요약 포함) 반환
    """
    user = request.user
    today = timezone.now().date()

    # 그룹 소속 여부 확인
    if not UserGroupMembership.objects.filter(group_id=group_id, user=user).exists():
        return 403, ForbiddenSchema(message="해당 그룹의 멤버가 아닙니다.", data=None)

    # 오늘 투표 여부 확인
    today_voted = MVPVote.objects.filter(group_id=group_id, voter=user, vote_date=today).exists()

    # 후보군 조회 (자기 자신 제외 가능 여부에 따라 결정)
    member_qs = UserGroupMembership.objects.select_related("user").filter(group_id=group_id)

    # 오늘자 요약 미리 조회
    user_ids = [m.user.id for m in member_qs]
    summary_map = {
        s.user_id: s.summary
        for s in AIDailySummary.objects.filter(user_id__in=user_ids, date=today)
    }

    candidates = [
        MVPVoteCandidateItem(
            user=m.user,
            summary=summary_map.get(m.user.id) or "요약이 없습니다."
        )
        for m in member_qs
    ]

    return ResponseSchema(
        message="투표 정보입니다.",
        data=MVPVoteInfoResponse(
            today_voted=today_voted,
            candidates=candidates
        )
    )



@router.post("/{group_id}/vote", response={
    200: ResponseSchema[None],
    401: UnauthorizedSchema,
    403: ForbiddenSchema,
    404: NotFoundSchema
})
def vote_mvp(request: HttpRequest, group_id: int, data: MVPVoteRequest):
    user = request.user
    target_id = data.target_user_id
    today = timezone.now().date()

    if not UserGroupMembership.objects.filter(group_id=group_id, user=user).exists():
        return 403, ForbiddenSchema(message="해당 그룹의 멤버가 아닙니다.", data=None)

    if target_id == user.id:
        return 403, ForbiddenSchema(message="자기 자신에게는 투표할 수 없습니다.", data=None)

    if MVPVote.objects.filter(group_id=group_id, voter=user, vote_date=today).exists():
        return 403, ForbiddenSchema(message="오늘은 이미 투표를 완료했습니다.", data=None)

    if not UserGroupMembership.objects.filter(group_id=group_id, user_id=target_id).exists():
        return 404, NotFoundSchema(message="해당 그룹에 속한 사용자를 찾을 수 없습니다.", data=None)

    MVPVote.objects.create(
        group_id=group_id,
        voter=user,
        target_id=target_id,
        vote_date=today
    )
    return ResponseSchema(message="투표가 완료되었습니다.", data=None)


@router.get("/{group_id}/vote/result", response={
    200: ResponseSchema[MVPResultResponse],
    401: UnauthorizedSchema,
    403: ForbiddenSchema
})
def get_vote_result(request: HttpRequest, group_id: int):
    user = request.user
    today = timezone.now().date()

    if not UserGroupMembership.objects.filter(group_id=group_id, user=user).exists():
        return 403, ForbiddenSchema(message="해당 그룹의 멤버가 아닙니다.", data=None)

    # 투표 집계
    votes = MVPVote.objects.filter(group_id=group_id, vote_date=today)
    vote_count_map = {}
    for vote in votes:
        vote_count_map[vote.target_id] = vote_count_map.get(vote.target_id, 0) + 1

    # 그룹 멤버 전체
    memberships = UserGroupMembership.objects.select_related("user").filter(group_id=group_id)
    user_ids = [m.user.id for m in memberships]
    user_map = {m.user.id: m.user for m in memberships}

    # 요약
    summaries = AIDailySummary.objects.filter(user_id__in=user_ids, date=today)
    summary_map = {s.user_id: s.summary for s in summaries}

    # 결과 조립
    results = [
        MVPResultItem(
            candidate=MVPVoteCandidateItem(
                user=user_map[uid],
                summary=summary_map.get(uid, "요약이 없습니다.")
            ),
            vote_count=vote_count_map.get(uid, 0)
        )
        for uid in user_ids
    ]

    # 투표 수 기준 정렬
    results.sort(key=lambda x: x.vote_count, reverse=True)

    return ResponseSchema(
        message="투표 결과입니다.",
        data=MVPResultResponse(
            group_id=group_id,
            vote_date=today,
            results=results
        )
    )


@router.get("/{group_id}/vote/history", response={
    200: ResponseSchema[MVPVoteHistoryResponse],
    401: UnauthorizedSchema,
    403: ForbiddenSchema
})
def get_vote_history(request: HttpRequest, group_id: int, vote_date: Optional[str] = None):
    user = request.user

    if not UserGroupMembership.objects.filter(group_id=group_id, user=user).exists():
        return 403, ForbiddenSchema(message="해당 그룹의 멤버가 아닙니다.", data=None)

    qs = MVPVote.objects.filter(group_id=group_id, voter=user)
    if vote_date:
        try:
            parsed_date = datetime.strptime(vote_date, "%Y-%m-%d").date()
            qs = qs.filter(vote_date=parsed_date)
        except ValueError:
            return 403, ForbiddenSchema(message="날짜 형식이 올바르지 않습니다. YYYY-MM-DD", data=None)

    history = [
        {
            "group_id": vote.group_id,
            "group_name": vote.group.group_name,
            "vote_date": vote.vote_date,
            "voted_for": vote.target,
        }
        for vote in qs.select_related("group", "target")
    ]

    return ResponseSchema(
        message="투표 히스토리입니다.",
        data=MVPVoteHistoryResponse(votes=history)
    )
