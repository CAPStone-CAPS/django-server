from ninja import Schema
from typing import Optional, Generic, TypeVar, Literal
from pydantic.generics import GenericModel


T = TypeVar("T")

# API 응답을 위한 공통 기본 스키마
class ResponseSchema(GenericModel, Generic[T]):
    # status: int
    message: str
    data: Optional[T] = None


class BadRequestSchema(Schema):
    message: str = "Bad Request"
    data: Optional[None] = None


class UnauthorizedSchema(Schema):
    message: str = "Unauthorized"
    data: Optional[None] = None
    
    
class ForbiddenSchema(Schema):
    message: str = "Forbidden"
    data: Optional[None] = None


class NotFoundSchema(Schema):
    message: str = "Not found"
    data: Optional[None] = None