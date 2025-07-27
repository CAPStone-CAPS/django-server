from ninja import Schema
from typing import Optional, Generic, TypeVar
from pydantic.generics import GenericModel


T = TypeVar("T")

# API 응답을 위한 공통 기본 스키마
class ResponseSchema(GenericModel, Generic[T]):
    # status: int
    message: str
    data: Optional[T] = None
