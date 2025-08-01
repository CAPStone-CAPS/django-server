from ninja import Router
from ninja.responses import Response
from django.http import HttpRequest
from django.utils import timezone

from ..models import GroupInfo, UserGroupMembership
from apps.api.schema import (
    ResponseSchema,
    UnauthorizedSchema,
    ForbiddenSchema,
    NotFoundSchema
)
from ..schema import (
    GroupSchema,
    GroupCreateRequestSchema,
    GroupListResponseSchema,
    GroupUpdateRequestSchema
)
from apps.api.auth import JWTAuth


router = Router(tags=["Group"], auth=JWTAuth())


@router.get("", response={
    200: ResponseSchema[GroupListResponseSchema],
    401: UnauthorizedSchema,
})
def get_user_groups(request: HttpRequest):
    if not request.user.is_authenticated:
        return Response(
            {"message": "Unauthorized", "data": None},
            status=401
        )

    memberships = UserGroupMembership.objects.filter(user=request.user).select_related('group')
    groups = [membership.group for membership in memberships]

    return Response(
        {
            "message": "Group list fetched",
            "data": {
                "groups": [GroupSchema.from_orm(group) for group in groups]
            }
        },
        status=200
    )


@router.post(path="", response={
    201: ResponseSchema[GroupSchema],
    401: UnauthorizedSchema,
})
def create_group(request: HttpRequest, payload: GroupCreateRequestSchema):
    if not request.user.is_authenticated:
        return Response(
            {"message": "Unauthorized", "data": None},
            status=401
        )

    group = GroupInfo.objects.create(
        group_name=payload.group_name,
        description=payload.description,
        create_date=timezone.now(),
        modify_date=None
    )

    UserGroupMembership.objects.create(user=request.user, group=group)

    return Response(
        {
            "message": "Group created",
            "data": GroupSchema.from_orm(group)
        },
        status=201
    )


@router.patch("/{group_id}", response={
    200: ResponseSchema[GroupSchema],
    401: UnauthorizedSchema,
    403: ForbiddenSchema,
    404: NotFoundSchema
})
def edit_group(request: HttpRequest, group_id: int, payload: GroupUpdateRequestSchema):
    if not request.user.is_authenticated:
        return Response({"message": "Unauthorized", "data": None}, status=401)

    if not UserGroupMembership.objects.filter(user=request.user, group_id=group_id).exists():
        return Response({"message": "Forbidden", "data": None}, status=403)

    try:
        group = GroupInfo.objects.get(id=group_id)
    except GroupInfo.DoesNotExist:
        return Response({"message": "Group not found", "data": None}, status=404)

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

    return Response(
        {
            "message": "Group updated",
            "data": GroupSchema.from_orm(group)
        },
        status=200
    )