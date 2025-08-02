from ninja import Router
from ninja.responses import Response
from ninja.errors import HttpError
from django.contrib.auth.models import User
from django.http import HttpRequest

from ..models import GroupInfo, UserGroupMembership
from apps.api.schema import (
    ResponseSchema,
    UnauthorizedSchema,
    ForbiddenSchema,
    NotFoundSchema
)
from ..schema import UserSchema, MemberListResponseSchema
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

    # 멤버 조회
    memberships = UserGroupMembership.objects.filter(group=group).select_related('user')
    users = [membership.user for membership in memberships]

    return Response(
        {
            "message": "Group list fetched",
            "data": {
               "members": [UserSchema.from_orm(user) for user in users]
            }
        },
        status=200
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