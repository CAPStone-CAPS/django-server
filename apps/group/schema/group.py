from ninja import Schema
from typing import Optional, List
from datetime import datetime


class GroupSchema(Schema):
    id: int
    group_name: str
    description: str
    create_date: datetime
    modify_date: Optional[datetime]

    model_config = {
        "from_attributes": True
    }


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

    model_config = {
        "from_attributes": True
    }

class MemberInfoSchema(Schema):
    user: UserSchema
    summary: str
    profile_image_url: Optional[str] = None


class MemberListResponseSchema(Schema):
    members: List[MemberInfoSchema]
    
    
class AddMemberSchema(Schema):
    username: str
    
    
class RemoveMemberSchema(Schema):
    username: str