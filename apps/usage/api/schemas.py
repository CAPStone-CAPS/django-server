from ninja import Schema
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class UsageRecordCreateSchema(BaseModel):
    package_name: str = Field(..., example="com.example.capstone_2")
    app_name: str = Field(..., example="capstone_2")
    usage_time_ms: int = Field(..., example=62163)
    start_time: int = Field(..., example=1753874134830)
    end_time: int = Field(..., example=1753888371658)

class UsageRecordSchema(BaseModel):
    id: Optional[int] = None
    package_name: str
    app_name: str
    usage_time_ms: int
    start_time: int
    end_time: int
    start_time_str: Optional[str] = None
    end_time_str: Optional[str] = None
    usage_time_str: Optional[str] = None

class UsageListResponseSchema(BaseModel):
    records: List[UsageRecordSchema]

class SimpleResponseSchema(BaseModel):
    message: str
    data: Optional[dict] = None

class UsageListQuerySchema(Schema):
    date: Optional[date] = None  # YYYY-MM-DD 형태로 받는 하루 단위 날짜

# 메모 관련 스키마
class MemoSchema(BaseModel):
    memo: Optional[str] = Field(None, description="메모 내용")

class MemoResponseSchema(BaseModel):
    id: int
    memo: Optional[str] = None