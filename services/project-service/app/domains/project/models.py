"""
Project domain SQLAlchemy ORM models
"""
import enum
from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import (
    Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, JSONB

from app.core.database import Base


# ── Enums ───────────────────────────────────────────────────────────────────

class ProjectStatusEnum(str, enum.Enum):
    PENDING                         = "Pending"
    IN_PROGRESS                     = "In Progress"
    DELAYED                         = "Delayed"
    EXPENSE_VERIFICATION_PENDING    = "Expense Verification Pending"
    EXPENSE_VERIFICATION_IN_PROGRESS = "Expense Verification In Progress"
    COMPLETED                       = "Completed"
    CANCELLED                       = "Cancelled"


class CommitteeRoleEnum(str, enum.Enum):
    CHAIRPERSON      = "Chairperson"
    VICE_CHAIRPERSON = "Vice Chairperson"
    MEMBER           = "Member"


class TaskStatusEnum(str, enum.Enum):
    PENDING     = "Pending"
    IN_PROGRESS = "In Progress"
    DELAYED     = "Delayed"
    COMPLETED   = "Completed"
    CANCELLED   = "Cancelled"


class PriorityStatusEnum(str, enum.Enum):
    LOW    = "Low"
    MEDIUM = "Medium"
    HIGH   = "High"


# ── Models ──────────────────────────────────────────────────────────────────

class Project(Base):
    __tablename__ = "project"

    project_id:         Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id:          Mapped[int]  = mapped_column(Integer, nullable=False)
    proponent_role_id:  Mapped[int]  = mapped_column(Integer, nullable=False)
    proponent_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    line_item_id:       Mapped[int]  = mapped_column(Integer, nullable=False)
    line_item_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    project_title:      Mapped[Optional[str]] = mapped_column(String(255))
    date_started:       Mapped[Optional[date]] = mapped_column(Date)
    date_accomplished:  Mapped[Optional[date]] = mapped_column(Date)
    project_status: Mapped[ProjectStatusEnum] = mapped_column(
        PgEnum(ProjectStatusEnum, name="project_status_enum", create_type=False,
               values_callable=lambda e: [x.value for x in e]),
        nullable=False, server_default="Pending",
    )

    committees: Mapped[List["ProjectCommittee"]] = relationship(
        "ProjectCommittee", back_populates="project", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["ProjectTask"]] = relationship(
        "ProjectTask", back_populates="project", cascade="all, delete-orphan"
    )


class CommitteeCategory(Base):
    __tablename__ = "committee_category"

    committee_cat_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id:        Mapped[int] = mapped_column(Integer, nullable=False)
    category_name:    Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("tenant_id", "category_name", name="uq_committee_cat_per_tenant"),
    )

    committees: Mapped[List["ProjectCommittee"]] = relationship(
        "ProjectCommittee", back_populates="category"
    )


class ProjectCommittee(Base):
    __tablename__ = "project_committee"

    committee_id:     Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id:       Mapped[int] = mapped_column(Integer, ForeignKey("project.project_id"), nullable=False)
    committee_cat_id: Mapped[int] = mapped_column(Integer, ForeignKey("committee_category.committee_cat_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("project_id", "committee_cat_id", name="uq_committee_per_project"),
    )

    project:  Mapped["Project"]           = relationship("Project", back_populates="committees")
    category: Mapped["CommitteeCategory"] = relationship("CommitteeCategory", back_populates="committees")
    members:  Mapped[List["CommitteeMember"]] = relationship(
        "CommitteeMember", back_populates="committee", cascade="all, delete-orphan"
    )


class CommitteeMember(Base):
    __tablename__ = "committee_member"

    member_id:       Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    committee_id:    Mapped[int]  = mapped_column(Integer, ForeignKey("project_committee.committee_id"), nullable=False)
    role_id:         Mapped[int]  = mapped_column(Integer, nullable=False)
    member_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    committee_role: Mapped[CommitteeRoleEnum] = mapped_column(
        PgEnum(CommitteeRoleEnum, name="committee_role_enum", create_type=False,
               values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("committee_id", "role_id", name="uq_person_per_committee"),
    )

    committee:   Mapped["ProjectCommittee"]          = relationship("ProjectCommittee", back_populates="members")
    assignments: Mapped[List["ProjectTaskAssignment"]] = relationship(
        "ProjectTaskAssignment", back_populates="member"
    )


class ProjectTask(Base):
    __tablename__ = "project_task"

    task_id:   Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("project.project_id"), nullable=False)
    task_name: Mapped[Optional[str]] = mapped_column(String(255))
    due_date:  Mapped[Optional[date]] = mapped_column(Date)
    task_status: Mapped[TaskStatusEnum] = mapped_column(
        PgEnum(TaskStatusEnum, name="task_status_enum", create_type=False,
               values_callable=lambda e: [x.value for x in e]),
        nullable=False, server_default="Pending",
    )
    priority_status: Mapped[PriorityStatusEnum] = mapped_column(
        PgEnum(PriorityStatusEnum, name="priority_status_enum", create_type=False,
               values_callable=lambda e: [x.value for x in e]),
        nullable=False, server_default="Low",
    )

    project:     Mapped["Project"]                    = relationship("Project", back_populates="tasks")
    assignments: Mapped[List["ProjectTaskAssignment"]] = relationship(
        "ProjectTaskAssignment", back_populates="task", cascade="all, delete-orphan"
    )


class ProjectTaskAssignment(Base):
    __tablename__ = "project_task_assignment"

    assignment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id:       Mapped[int] = mapped_column(Integer, ForeignKey("project_task.task_id"), nullable=False)
    member_id:     Mapped[int] = mapped_column(Integer, ForeignKey("committee_member.member_id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("task_id", "member_id", name="uq_task_assignment"),
    )

    task:   Mapped["ProjectTask"]     = relationship("ProjectTask", back_populates="assignments")
    member: Mapped["CommitteeMember"] = relationship("CommitteeMember", back_populates="assignments")


class Outbox(Base):
    __tablename__ = "outbox"

    outbox_id:      Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_id:      Mapped[int]  = mapped_column(Integer, nullable=False)
    aggregate_type: Mapped[str]  = mapped_column(String(100), nullable=False)
    aggregate_id:   Mapped[int]  = mapped_column(Integer, nullable=False)
    event_type:     Mapped[str]  = mapped_column(String(100), nullable=False)
    payload:        Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at:     Mapped[datetime]       = mapped_column(DateTime, server_default=func.now())
    dispatched:     Mapped[bool]           = mapped_column(Boolean, server_default="false")
    dispatched_at:  Mapped[Optional[datetime]] = mapped_column(DateTime)
    retry_count:    Mapped[int]            = mapped_column(Integer, server_default="0")
    last_attempted: Mapped[Optional[datetime]] = mapped_column(DateTime)
    failed:         Mapped[bool]           = mapped_column(Boolean, server_default="false")
    failure_reason: Mapped[Optional[str]]  = mapped_column(Text)
