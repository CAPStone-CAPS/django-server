from ninja import Router
from ninja.errors import HttpError
from django.contrib.auth.models import User
from django.http import HttpRequest

from ..models import GroupInfo, UserGroupMembership
from ..schema import UserSchema, MemberListResponseSchema


router = Router(tags=["Group Member"])


# 그룹 멤버 리스트 조회
@router.get("/{group_id}/members", response=MemberListResponseSchema)
def get_group_members(request: HttpRequest, group_id: int):
    try:
        group = GroupInfo.objects.get(id=group_id)
    except GroupInfo.DoesNotExist:
        raise HttpError(404, "Group not found")

    # 멤버 조회
    memberships = UserGroupMembership.objects.filter(group=group).select_related('user')
    users = [membership.user for membership in memberships]

    return {"members": users}

# 그룹에 멤버 추가
@router.post("/{group_id}/members/{user_id}", response=UserSchema)
def add_member_to_group(request: HttpRequest, group_id: int, user_id: int):
    if not request.user.is_authenticated:
        raise HttpError(401, "Unauthorized")

    # 권한 체크 예: 그룹 멤버만 추가 가능 (필요시 관리자 권한 추가 구현)
    if not UserGroupMembership.objects.filter(user=request.user, group_id=group_id).exists():
        raise HttpError(403, "Forbidden: You are not a member of this group")

    try:
        group = GroupInfo.objects.get(id=group_id)
    except GroupInfo.DoesNotExist:
        raise HttpError(404, "Group not found")

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(404, "User not found")

    membership, created = UserGroupMembership.objects.get_or_create(user=user, group=group)
    if not created:
        raise HttpError(400, "User already a member of the group")

    return user

# 그룹에서 멤버 삭제
@router.delete("/{group_id}/members/{user_id}")
def remove_member_from_group(request: HttpRequest, group_id: int, user_id: int):
    if not request.user.is_authenticated:
        raise HttpError(401, "Unauthorized")

    # 권한 체크
    if not UserGroupMembership.objects.filter(user=request.user, group_id=group_id).exists():
        raise HttpError(403, "Forbidden: You are not a member of this group")

    try:
        membership = UserGroupMembership.objects.get(user_id=user_id, group_id=group_id)
    except UserGroupMembership.DoesNotExist:
        raise HttpError(404, "Membership not found")

    membership.delete()
    return {"detail": "Member removed successfully"}
