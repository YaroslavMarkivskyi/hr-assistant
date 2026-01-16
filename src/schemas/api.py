from pydantic import BaseModel

class APIHealthCheckResponse(BaseModel):
    status: str
    

class APISystemInfoResponse(BaseModel):
    service: str
    description: str
    version: str
    
__all__ = (
    "APIHealthCheckResponse",
    "APISystemInfoResponse",
)

