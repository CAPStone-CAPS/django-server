from ninja import Schema
from typing import Optional, Generic, TypeVar, Literal
from pydantic.generics import GenericModel


T = TypeVar("T")

# API 응답을 위한 공통 기본 스키마
class ResponseSchema(GenericModel, Generic[T]):
    # status: int
    message: str
    data: Optional[T] = None


class UnauthorizedSchema(Schema):
    message: Literal["Unauthorized"]
    data: Optional[None] = None
 
    
class ForbiddenSchema(Schema):
    message: Literal["Forbidden"]
    data: Optional[None] = None


class NotFoundSchema(Schema):
    message: Literal["Group not found"]
    data: Optional[None] = None