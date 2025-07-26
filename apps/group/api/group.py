from ninja import Router
from ninja.errors import HttpError

from django.http import HttpRequest
from django.utils import timezone

from ..models import GroupInfo, UserGroupMembership
from ..schema import (
    GroupSchema, 
    GroupCreateRequestSchema, 
    GroupListResponseSchema, 
    GroupUpdateRequestSchema
)


router = Router(tags=["Group"])


@router.get("", response=GroupListResponseSchema)
def get_user_groups(request: HttpRequest):
    if not request.user.is_authenticated:
        raise HttpError(401, "Unauthorized")

    memberships = UserGroupMembership.objects.filter(user=request.user).select_related('group')
    groups = [membership.group for membership in memberships]

    return 200, {"groups": groups}


@router.post("", response=GroupSchema)
def create_group(request: HttpRequest, payload: GroupCreateRequestSchema):
    if not request.user.is_authenticated:
        raise HttpError(401, "Unauthorized")
    
    group = GroupInfo(
        group_name=payload.group_name,
        description=payload.description,
        create_date=timezone.now(),
        modify_date=None
    )
    group.save()

    # 새 그룹에 만든 유저를 멤버로 자동 등록
    UserGroupMembership.objects.create(user=request.user, group=group)

    return group


@router.patch("/{group_id}", response=GroupSchema)
def edit_group(request: HttpRequest, group_id: int, payload: GroupUpdateRequestSchema):
    if not request.user.is_authenticated:
        raise HttpError(401, "Unauthorized")

    # 요청한 그룹이 로그인한 유저가 가입한 그룹인지 확인
    if not UserGroupMembership.objects.filter(user=request.user, group_id=group_id).exists():
        raise HttpError(403, "Forbidden: You are not a member of this group")

    try:
        group = GroupInfo.objects.get(id=group_id)
    except GroupInfo.DoesNotExist:
        raise HttpError(404, "Group not found")

    # 부분 업데이트: payload에 있는 필드만 업데이트
    updated = False
    if payload.group_name is not None:
        group.group_name = payload.group_name
        updated = True
    if payload.description is not None:
        group.description = payload.description
        updated = True
    
    if updated:
        group.modify_date = timezone.now()
        group.save()

    return group