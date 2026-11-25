from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, LeaveRequest, WFHRequest
from app.security import require_role
from datetime import date, datetime, timezone
from app.schemas import DecisionRequest

router = APIRouter(prefix="/manager", tags=["Manager"])


@router.get("/requests")
def get_requests(
        status: str = "PENDING",
        employee_id: int | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        db: Session = Depends(get_db), current_manager: User = Depends(require_role("manager"))):
    leave_query = db.query(LeaveRequest).join(
        User, LeaveRequest.user_id == User.id
    ).filter(
        User.manager_id == current_manager.id
    )
    wfh_query = db.query(WFHRequest).join(
        User, WFHRequest.user_id == User.id
    ).filter(
        User.manager_id == current_manager.id
    )

    if status:
        leave_query = leave_query.filter(LeaveRequest.status == status)
        wfh_query = wfh_query.filter(WFHRequest.status == status)
    if employee_id:
        leave_query = leave_query.filter(LeaveRequest.user_id == employee_id)
        wfh_query = wfh_query.filter(WFHRequest.user_id == employee_id)

    if from_date:
        leave_query = leave_query.filter(LeaveRequest.date >= from_date)
        wfh_query = wfh_query.filter(WFHRequest.end_date >= from_date)

    if to_date:
        leave_query = leave_query.filter(LeaveRequest.date <= to_date)
        wfh_query = wfh_query.filter(WFHRequest.start_date <= to_date)

    return {
        "leaves": leave_query.all(),
        "wfh": wfh_query.all()
    }


@router.post("leaves/{leave_id}/approve")
def approve_leave(leave_id: int, db: Session = Depends(get_db), current_manager: User = Depends(require_role("manager"))):
    leave = db.query(LeaveRequest).join(
        User, LeaveRequest.user_id == User.id
    ).filter(
        LeaveRequest.id == leave_id,
        User.manager_id == current_manager.id
    ).first()
    if not leave:
        exists = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_id
        ).first()

        if not exists:
            raise HTTPException(status_code=404, detail="Request not found")

        raise HTTPException(status_code=403, detail="Not your employee")

    if leave.status != "PENDING":
        raise HTTPException(
            status_code=409, detail="Request already processed")

    leave.status = "APPROVED"
    leave.decided_by = current_manager.id
    leave.decided_at = datetime.now(timezone.utc)
    leave.decision_comment = None

    db.commit()
    db.refresh(leave)

    return leave


@router.post("/leaves/{leave_id}/reject")
def reject_leave(leave_id: int,
                 data: DecisionRequest,
                 db: Session = Depends(get_db), current_manager: User = Depends(require_role("manager"))):
    leave = db.query(LeaveRequest).join(
        User, LeaveRequest.user_id == User.id
    ).filter(
        LeaveRequest.id == leave_id,
        User.manager_id == current_manager.id
    ).first()
    if not leave:
        exists = db.query(LeaveRequest).filter(
            LeaveRequest.id == leave_id
        ).first()

        if not exists:
            raise HTTPException(status_code=404, detail="Request not found")

        raise HTTPException(status_code=403, detail="Not your employee")
    if leave.status != "PENDING":
        raise HTTPException(
            status_code=409, detail="Request already processed")
    if len(data.comment.strip()) < 5:
        raise HTTPException(
            status_code=422, detail="Comment must be atleast 5 characters")

    leave.status = "REJECTED"
    leave.decided_by = current_manager.id
    leave.decided_at = datetime.now(timezone.utc)
    leave.decision_comment = data.comment

    db.commit()
    db.refresh(leave)

    return leave


@router.post("wfh/{wfh_id}/approve")
def approve_wfh(wfh_id: int, db: Session = Depends(get_db), current_manager: User = Depends(require_role("manager"))):
    wfh = db.query(WFHRequest).join(
        User, WFHRequest.user_id == User.id
    ).filter(
        WFHRequest.id == wfh_id,
        User.manager_id == current_manager.id
    ).first()
    if not wfh:
        exists = db.query(WFHRequest).filter(
            WFHRequest.id == wfh_id
        ).first()

        if not exists:
            raise HTTPException(status_code=404, detail="Request not found")

        raise HTTPException(status_code=403, detail="Not your employee")

    if wfh.status != "PENDING":
        raise HTTPException(
            status_code=409, detail="Request already processed")

    wfh.status = "APPROVED"
    wfh.decided_by = current_manager.id
    wfh.decided_at = datetime.now(timezone.utc)
    wfh.decision_comment = None

    db.commit()
    db.refresh(wfh)

    return wfh


@router.post("/wfh/{wfh_id}/reject")
def reject_wfh(wfh_id: int,
               data: DecisionRequest,
               db: Session = Depends(get_db), current_manager: User = Depends(require_role("manager"))):
    wfh = db.query(WFHRequest).join(
        User, WFHRequest.user_id == User.id
    ).filter(
        WFHRequest.id == wfh_id,
        User.manager_id == current_manager.id
    ).first()
    if not wfh:
        exists = db.query(WFHRequest).filter(
            WFHRequest.id == wfh_id
        ).first()

        if not exists:
            raise HTTPException(status_code=404, detail="Request not found")

        raise HTTPException(status_code=403, detail="Not your employee")

    if wfh.status != "PENDING":
        raise HTTPException(
            status_code=409, detail="Request already processed")
    if len(data.comment.strip()) < 5:
        raise HTTPException(
            status_code=422, detail="Comment must be atleast 5 characters")

    wfh.status = "REJECTED"
    wfh.decided_by = current_manager.id
    wfh.decided_at = datetime.now(timezone.utc)
    wfh.decision_comment = data.comment

    db.commit()
    db.refresh(wfh)

    return wfh
