from __future__ import annotations
from typing import TypeVar, Generic, Optional

from http import HTTPStatus

from pydantic import BaseModel



T = TypeVar('T')


class ServiceResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    
    @classmethod
    def ok(cls, data: T, status_code: Optional[int] = HTTPStatus.OK) -> ServiceResponse[T]:
        return cls(success=True, data=data, status_code=status_code)
    
    @classmethod
    def fail(cls, error: str, status_code: Optional[int] = HTTPStatus.INTERNAL_SERVER_ERROR) -> ServiceResponse[T]:
        return cls(success=False, error=error, status_code=status_code)
    

__all__ = (
    'ServiceResponse',
)

