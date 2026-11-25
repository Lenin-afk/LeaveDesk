from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models import User, LeaveRequest
from app.schemas import LeaveCreate
from app.security import get_current_user
from sqlalchemy.orm import Session
from datetime import date

router = APIRouter(prefix="/leaves", tags=["Leaves"])


@router.post("")
def create_leave(data: LeaveCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.leave_type not in ["CASUAL", "SICK", "EARNED"]:
        raise HTTPException(status_code=422, detail="Invalid leave type")
    if data.duration_type not in ["FULL_DAY", "HALF_DAY", "HOURS"]:
        raise HTTPException(status_code=422, detail="Invalid duration type")
    if data.duration_type == "FULL_DAY":
        if data.hours is not None or data.half is not None:
            raise HTTPException(
                status_code=422, detail="Cant have hours/Half for full day")
        days_counted = 1.0
    if data.duration_type == "HALF_DAY":
        if data.half not in ["FIRST_HALF", "SECOND_HALF"] or data.hours is not None:
            raise HTTPException(
                status_code=422, detail="Invalid Half / Cant have hours")
        days_counted = 0.5
    if data.duration_type == "HOURS":
        if data.hours is None or data.hours not in [1, 2, 3] or data.half is not None:
            raise HTTPException(
                status_code=422, details="Check hours / Cant have half")
        days_counted = data.hours/8

    existing = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id,
        LeaveRequest.date == data.date,
        LeaveRequest.status.in_(["PENDING", "APPROVED"])
    ).all()

    for item in existing:
        if item.duration_type == "FULL_DAY" and data.duration_type == "FULL_DAY":
            raise HTTPException(status_code=409, detail="Leave already exists")
        if item.duration_type == "HALF_DAY" and data.duration_type == "HALF_DAY":
            if item.half == data.half:
                raise HTTPException(
                    status_code=409, detail="Leave already exists")

    request = LeaveRequest(
        user_id=current_user.id,
        date=data.date,
        leave_type=data.leave_type,
        duration_type=data.duration_type,
        half=data.half,
        hours=data.hours,
        days_counted=days_counted,
        reason=data.reason
    )

    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("/me")
def get_my_leaves(status: str | None = None,
                  from_date: date | None = None,
                  to_date: date | None = None,
                  db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(LeaveRequest).filter(
        LeaveRequest.user_id == current_user.id
    )
    if status:
        query = query.filter(LeaveRequest.status == status)
    if from_date:
        query = query.filter(LeaveRequest.date >= from_date)
    if to_date:
        query = query.filter(LeaveRequest.date <= to_date)

    return query.order_by(LeaveRequest.created_at.desc()).all()


@router.post("/{leave_id}/cancel")
def cancel_leave(leave_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    request = db.query(LeaveRequest).filter(
        LeaveRequest.id == leave_id,
        LeaveRequest.user_id == current_user.id
    ).first()
    if request is None:
        raise HTTPException(
            status_code=404, detail="No record / User not allowed")
    if request.status != "PENDING":
        raise HTTPException(status_code=409, detail="Cannot cancel")
    request.status = "CANCELLED"
    db.commit()
    db.refresh(request)
    return request
