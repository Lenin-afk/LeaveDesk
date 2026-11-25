from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, WFHRequest, WFHRequest
from app.schemas import WFHCreate
from app.security import get_current_user
from datetime import date, timedelta

router = APIRouter(prefix="/wfh", tags=["WFH"])


@router.post("")
def create_wfh(data: WFHCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    working_days = 0
    current_date = data.start_date

    while current_date <= data.end_date:
        if current_date.weekday() < 5:
            working_days += 1
        current_date += (timedelta(days=1))

    if working_days > 2:
        raise HTTPException(
            status_code=422, detail="WFH exceeds two working days")

    existing_requests = db.query(WFHRequest).filter(
        WFHRequest.user_id == current_user.id,
        WFHRequest.status.in_(["PENDING", "APPROVED"])
    ).all()

    for existing in existing_requests:
        if existing.start_date <= data.end_date and existing.end_date >= data.start_date:
            raise HTTPException(status_code=409, detail="WFH dates overlaps")

    existing_leaves = db.query(WFHRequest).filter(
        WFHRequest.user_id == current_user.id,
        WFHRequest.status.in_(["PENDING", "APPROVED"]),
        WFHRequest.duration_type == "FULL_DAY",
        WFHRequest.date >= data.start_date,
        WFHRequest.date <= data.end_date
    ).all()

    if existing_leaves:
        raise HTTPException(
            status_code=409, details="WFH overlaps with full day leave")

    request = WFHRequest(
        user_id=current_user.id,
        start_date=data.start_date,
        end_date=data.end_date,
        reason=data.reason
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return request


@router.get("/me")
def get_my_wfh(status: str | None = None,
               from_date: date | None = None,
               to_date: date | None = None,
               db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(WFHRequest).filter(
        WFHRequest.user_id == current_user.id
    )
    if status:
        query = query.filter(WFHRequest.status == status)
    if from_date:
        query = query.filter(WFHRequest.start_date >= from_date)
    if to_date:
        query = query.filter(WFHRequest.end_date <= to_date)

    return query.order_by(WFHRequest.created_at.desc()).all()


@router.post("/{wfh_id}/cancel")
def cancel_wfh(wfh_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    request = db.query(WFHRequest).filter(
        WFHRequest.id == wfh_id,
        WFHRequest.user_id == current_user.id
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
