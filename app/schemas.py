from pydantic import BaseModel
from datetime import date


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class LeaveCreate(BaseModel):
    date: date
    leave_type: str
    duration_type: str
    half: str | None
    hours: str | None
    reason: str | None


class WFHCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str | None


class DecisionRequest(BaseModel):
    comment: str
