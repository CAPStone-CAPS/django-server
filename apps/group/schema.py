from ninja import Schema
from typing import Optional, List
from datetime import datetime


class GroupSchema(Schema):
    id: int
    group_name: str
    description: str
    create_date: datetime
    modify_date: Optional[datetime]

    class Config:
        orm_mode = True


class GroupCreateRequestSchema(Schema):
    group_name: str
    description: str


class GroupUpdateRequestSchema(Schema):
    group_name: Optional[str] = None
    description: Optional[str] = None


class GroupListResponseSchema(Schema):
    groups: List[GroupSchema]


class UserSchema(Schema):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class MemberListResponseSchema(Schema):
    members: List[UserSchema]