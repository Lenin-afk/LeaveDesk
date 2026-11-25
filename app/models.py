from sqlalchemy import String, ForeignKey, Date, DateTime, Integer, Float, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from datetime import date as DateType, datetime


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True)

    manager: Mapped["User"] = relationship(
        "User", remote_side=[id], back_populates="employees")
    employees: Mapped[list["User"]] = relationship(
        "User", back_populates="manager")


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[DateType] = mapped_column(Date)
    leave_type: Mapped[str] = mapped_column(String(20))
    duration_type: Mapped[str] = mapped_column(String(20))
    half: Mapped[str | None] = mapped_column(String(20), nullable=True)
    hours: Mapped[int | None] = mapped_column(Integer, nullable=True)
    days_counted: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    decided_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True)
    decided_at: Mapped[DateType | None] = mapped_column(
        DateTime(timezone=True), nullable=True)
    decision_comment: Mapped[str | None] = mapped_column(Text, nullable=True)


class WFHRequest(Base):
    __tablename__ = "wfh_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    start_date: Mapped[DateType] = mapped_column(Date)
    end_date: Mapped[DateType] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    decided_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True)
    decided_at: Mapped[DateType | None] = mapped_column(
        DateTime(timezone=True), nullable=True)
    decision_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
