from ninja import Schema
from typing import Optional, List
from datetime import date
from pydantic import Field

from .group import UserSchema


class MVPVoteCandidateItem(Schema):
    user: UserSchema
    summary: Optional[str]

class MVPVoteInfoResponse(Schema):
    today_voted: bool
    candidates: List[MVPVoteCandidateItem]
    

class MVPVoteRequest(Schema):
    target_user_id: int = Field(..., description="투표할 대상 유저의 ID")
   
    
class MVPResultItem(Schema):
    candidate: MVPVoteCandidateItem
    vote_count: int


class MVPResultResponse(Schema):
    vote_date: date
    results: List[MVPResultItem]


class MVPVoteHistoryItem(Schema):
    group_name: str
    vote_date: date
    voted_for: UserSchema


class MVPVoteHistoryRequest(Schema):
    vote_date: Optional[date] = Field(None, description="조회할 날짜 (예: 2025-08-01)")


class MVPVoteHistoryResponse(Schema):
    votes: List[MVPVoteHistoryItem]
