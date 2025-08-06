from ninja import Router
from ninja.responses import Response
from ninja.errors import HttpError
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils import timezone

from ..models import GroupInfo, UserGroupMembership
from apps.users.models import Profile
from apps.summary.models import AIDailySummary
from apps.api.schema import (
    ResponseSchema,
    UnauthorizedSchema,
    ForbiddenSchema,
    NotFoundSchema
)
from ..schema import UserSchema, MemberListResponseSchema, MemberInfoSchema
from apps.api.auth import JWTAuth


router = Router(tags=["Group Member"], auth=JWTAuth())


# 그룹 멤버 리스트 조회
@router.get("/{group_id}/members", response={
    200: ResponseSchema[MemberListResponseSchema],
    401: UnauthorizedSchema,
    403: ForbiddenSchema,
    404: NotFoundSchema
})
def get_group_members(request: HttpRequest, group_id: int):
    """
    그룹의 멤버 목록과 각 멤버의 오늘자 AI 요약을 확인할 수 있습니다.
    """
    today = timezone.now().date()
    
    if not request.user.is_authenticated:
        return Response({"message": "Unauthorized", "data": None}, status=401)

    if not UserGroupMembership.objects.filter(user=request.user, group_id=group_id).exists():
        return Response({"message": "Forbidden", "data": None}, status=403)
    
    try:
        group = GroupInfo.objects.get(id=group_id)
    except GroupInfo.DoesNotExist:
        return Response(
            {"message": "Group not found", "data": None}, 
            status=404
        )

    # 그룹 멤버 전체
    memberships = UserGroupMembership.objects.select_related("user").filter(group_id=group_id)
    user_ids = [m.user.id for m in memberships]
    user_map = {m.user.id: m.user for m in memberships}

    # 요약
    summaries = AIDailySummary.objects.filter(user_id__in=user_ids, date=today)
    summary_map = {s.user_id: s.summary for s in summaries}

    profiles = Profile.objects.filter(user_id__in=user_ids)
    profile_map = {p.user_id: p for p in profiles}

    for p in profiles:
        print(p.user_id, p.profile_image.name, p.profile_image.url if p.profile_image else "No Image")

    results = []
    for uid in user_ids:
        user = user_map[uid]
        if not user:
            continue
        
        summary = summary_map.get(uid, "요약이 없습니다.")
        profile = profile_map.get(uid)
        profile_image_url = profile.profile_image.url if profile and profile.profile_image else None

        results.append(
            MemberInfoSchema(
                user=user,
                summary=summary,
                profile_image_url=profile_image_url
            )
        )
    
    return 200, ResponseSchema(
        message="그룹 멤버 목록",
        data=MemberListResponseSchema(
            members=results
        )
    )


# 그룹에 멤버 추가
@router.post("/{group_id}/members/{user_id}", response={
    201: ResponseSchema[UserSchema],
    401: UnauthorizedSchema,
    403: ForbiddenSchema,
    404: NotFoundSchema
})
def add_member_to_group(request: HttpRequest, group_id: int, user_id: int):
    if not request.user.is_authenticated:
        return Response(
            {"message": "Unauthorized", "data": None},
            status=401
        )

    if not UserGroupMembership.objects.filter(user=request.user, group_id=group_id).exists():
        return Response(
            {"message": "Forbidden: Not a group member", "data": None},
            status=403
        )

    try:
        group = GroupInfo.objects.get(id=group_id)
    except GroupInfo.DoesNotExist:
        return Response(
            {"message": "Group not found", "data": None},
            status=404
        )

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {"message": "User not found", "data": None},
            status=404
        )

    membership, created = UserGroupMembership.objects.get_or_create(user=user, group=group)
    if not created:
        return Response(
            {"message": "User already a member of the group", "data": None},
            status=400
        )

    return Response({
        "message": "User added to group",
        "data": UserSchema.from_orm(user)
    }, status=201)


# 그룹에서 멤버 삭제
@router.delete("/{group_id}/members/{user_id}", response={
    200: ResponseSchema[None],
    401: UnauthorizedSchema,
    403: ForbiddenSchema,
    404: NotFoundSchema
})
def remove_member_from_group(request: HttpRequest, group_id: int, user_id: int):
    if not request.user.is_authenticated:
        return Response(
            {"message": "Unauthorized", "data": None},
            status=401
        )

    if not UserGroupMembership.objects.filter(user=request.user, group_id=group_id).exists():
        return Response(
            {"message": "Forbidden: Not a group member", "data": None},
            status=403
        )

    try:
        membership = UserGroupMembership.objects.get(user_id=user_id, group_id=group_id)
    except UserGroupMembership.DoesNotExist:
        return Response(
            {"message": "Membership not found", "data": None},
            status=404
        )

    membership.delete()
    return Response({
        "message": "Member removed successfully",
        "data": None
    }, status=200)