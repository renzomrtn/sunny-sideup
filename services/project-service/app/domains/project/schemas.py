"""
Project domain Pydantic schemas
"""
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel

from app.domains.project.models import (
    ProjectStatusEnum, CommitteeRoleEnum, TaskStatusEnum, PriorityStatusEnum
)


# ── Committee Category ──────────────────────────────────────────────────────

class CommitteeCategoryCreate(BaseModel):
    category_name: str

class CommitteeCategoryRead(BaseModel):
    committee_cat_id: int
    tenant_id: int
    category_name: str
    model_config = {"from_attributes": True}


# ── Committee Member ────────────────────────────────────────────────────────

class CommitteeMemberCreate(BaseModel):
    role_id: int
    member_snapshot: dict
    committee_role: CommitteeRoleEnum

class CommitteeMemberRead(BaseModel):
    member_id: int
    committee_id: int
    role_id: int
    member_snapshot: dict
    committee_role: CommitteeRoleEnum
    model_config = {"from_attributes": True}


# ── Project Committee ───────────────────────────────────────────────────────

class ProjectCommitteeCreate(BaseModel):
    committee_cat_id: int
    members: List[CommitteeMemberCreate] = []

class ProjectCommitteeRead(BaseModel):
    committee_id: int
    project_id: int
    committee_cat_id: int
    members: List[CommitteeMemberRead] = []
    model_config = {"from_attributes": True}


# ── Task Assignment ─────────────────────────────────────────────────────────

class TaskAssignmentCreate(BaseModel):
    member_id: int

class TaskAssignmentRead(BaseModel):
    assignment_id: int
    task_id: int
    member_id: int
    model_config = {"from_attributes": True}


# ── Project Task ────────────────────────────────────────────────────────────

class ProjectTaskCreate(BaseModel):
    task_name: Optional[str] = None
    due_date: Optional[date] = None
    task_status: TaskStatusEnum = TaskStatusEnum.PENDING
    priority_status: PriorityStatusEnum = PriorityStatusEnum.LOW
    assignee_member_ids: List[int] = []

class ProjectTaskUpdate(BaseModel):
    task_name: Optional[str] = None
    due_date: Optional[date] = None
    task_status: Optional[TaskStatusEnum] = None
    priority_status: Optional[PriorityStatusEnum] = None

class ProjectTaskRead(BaseModel):
    task_id: int
    project_id: int
    task_name: Optional[str] = None
    due_date: Optional[date] = None
    task_status: TaskStatusEnum
    priority_status: PriorityStatusEnum
    assignments: List[TaskAssignmentRead] = []
    model_config = {"from_attributes": True}


# ── Project ─────────────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    line_item_id: str
    line_item_snapshot: dict = {}
    project_title: Optional[str] = None
    date_started: Optional[date] = None
    date_accomplished: Optional[date] = None
    committees: List["ProjectCommitteeCreate"] = []
    # ── New fields ──
    proponent_role_id: Optional[int] = None
    proponent_snapshot: Optional[dict] = None
    
class ProjectUpdate(BaseModel):
    project_title: Optional[str] = None
    date_started: Optional[date] = None
    date_accomplished: Optional[date] = None
    project_status: Optional[ProjectStatusEnum] = None

class ProjectRead(BaseModel):
    project_id: int
    tenant_id: int
    proponent_role_id: int
    proponent_snapshot: dict
    line_item_id: str
    line_item_snapshot: dict
    project_title: Optional[str] = None
    date_started: Optional[date] = None
    date_accomplished: Optional[date] = None
    project_status: ProjectStatusEnum
    committees: List[ProjectCommitteeRead] = []
    tasks: List[ProjectTaskRead] = []
    model_config = {"from_attributes": True}

class ProjectListItem(BaseModel):
    project_id: int
    tenant_id: int
    proponent_role_id: int
    proponent_snapshot: dict
    line_item_id: str
    line_item_snapshot: dict
    project_title: Optional[str] = None
    date_started: Optional[date] = None
    date_accomplished: Optional[date] = None
    project_status: ProjectStatusEnum
    model_config = {"from_attributes": True}

class ProjectStatusUpdate(BaseModel):
    project_status: ProjectStatusEnum