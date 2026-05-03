"""
Project domain router — fully implemented
"""
import httpx
from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func as sqlfunc, text
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.rabbitmq import rabbitmq
from app.core.config import settings

from app.domains.project.models import (
    Project, CommitteeCategory, ProjectCommittee, CommitteeMember,
    ProjectTask, ProjectTaskAssignment, Outbox,
    ProjectStatusEnum, TaskStatusEnum,
)
from app.domains.project.schemas import (
    ProjectCreate, ProjectRead, ProjectListItem, ProjectUpdate, ProjectStatusUpdate,
    CommitteeCategoryCreate, CommitteeCategoryRead,
    ProjectCommitteeCreate, ProjectCommitteeRead,
    CommitteeMemberCreate, CommitteeMemberRead,
    ProjectTaskCreate, ProjectTaskRead, ProjectTaskUpdate,
    TaskAssignmentCreate, TaskAssignmentRead,
)

router = APIRouter()


# ── Auth helper ─────────────────────────────────────────────────────────────

async def get_current_role(
    authorization: str = Header(...),
    x_tenant_id: str   = Header(..., alias="X-Tenant-ID"),
):
    """Calls identity-service /api/auth/account to validate the bearer token
    and returns the role dict with tenant context."""
    token = authorization.removeprefix("Bearer ").strip()
    try:
        tenant_id = int(x_tenant_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="X-Tenant-ID must be an integer")

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(
            f"{settings.IDENTITY_SERVICE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
    if r.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    account = r.json()
    roles = account.get("tenant_roles") or []
    if account.get("primary_role"):
        roles.append(account["primary_role"])

    eligible = [
        role for role in roles
        if role["role_status"] == "Active"
        and role["tenant_id"] == tenant_id
    ]
    if not eligible:
        raise HTTPException(status_code=403, detail="No active role in this tenant")

    role = eligible[0]
    role["_token"] = token
    role["full_name"] = account.get("full_name", "")
    return role


async def _set_tenant(db: AsyncSession, tenant_id: int):
    await db.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": str(tenant_id)},
    )


def _can_view_all_tenants(role: dict) -> bool:
    return role.get("tenant_id") == 1


async def _publish_event(
    db: AsyncSession, tenant_id: int, aggregate_type: str,
    aggregate_id: int, event_type: str, payload: dict,
):
    outbox = Outbox(
        tenant_id=tenant_id,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        payload=payload,
    )
    db.add(outbox)
    await rabbitmq.publish(f"project.{event_type}", {
        "tenant_id":      tenant_id,
        "aggregate_type": aggregate_type,
        "aggregate_id":   aggregate_id,
        "event_type":     event_type,
        "payload":        payload,
    })


def _make_role_snapshot(role: dict) -> dict:
    return {
        "role_id":       role["role_id"],
        "position_name": role["position_name"],
        "full_name":     role.get("full_name", ""),
        "tenant_id":     role["tenant_id"],
        "tenant_name":   role["tenant_name"],
    }


# ── Helper: load a project with all relations ───────────────────────────────

async def _get_project_full(
    project_id: int,
    tenant_id: Optional[int],
    db: AsyncSession,
) -> Project:
    conditions = [Project.project_id == project_id]
    if tenant_id is not None:
        conditions.append(Project.tenant_id == tenant_id)

    result = await db.execute(
        select(Project)
        .options(
            selectinload(Project.committees).selectinload(ProjectCommittee.members),
            selectinload(Project.committees).selectinload(ProjectCommittee.category),
            selectinload(Project.tasks).selectinload(ProjectTask.assignments),
        )
        .where(*conditions)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ── Committee Categories ────────────────────────────────────────────────────

@router.get("/committee-categories", response_model=List[CommitteeCategoryRead])
async def list_committee_categories(
    include_all_tenants: bool = Query(False),
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    q = select(CommitteeCategory)
    if not (include_all_tenants and _can_view_all_tenants(role)):
        q = q.where(CommitteeCategory.tenant_id == role["tenant_id"])
    q = q.order_by(CommitteeCategory.category_name)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/committee-categories", response_model=CommitteeCategoryRead, status_code=201)
async def create_committee_category(
    body: CommitteeCategoryCreate,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])

    # Check for duplicate within this tenant
    existing = await db.execute(
        select(CommitteeCategory).where(
            CommitteeCategory.tenant_id == role["tenant_id"],
            CommitteeCategory.category_name == body.category_name,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Committee category already exists")

    cat = CommitteeCategory(tenant_id=role["tenant_id"], **body.model_dump())
    db.add(cat)
    await db.flush()
    await db.refresh(cat)
    return cat


@router.delete("/committee-categories/{committee_cat_id}", status_code=204)
async def delete_committee_category(
    committee_cat_id: int,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    result = await db.execute(
        select(CommitteeCategory).where(
            CommitteeCategory.committee_cat_id == committee_cat_id,
            CommitteeCategory.tenant_id == role["tenant_id"],
        )
    )
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Committee category not found")
    await db.delete(cat)


# ── Projects ────────────────────────────────────────────────────────────────

@router.get("", response_model=List[ProjectListItem])
async def list_projects(
    project_status: Optional[ProjectStatusEnum] = Query(None),
    include_all_tenants: bool = Query(False),
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    can_view_all = include_all_tenants and _can_view_all_tenants(role)
    q = select(Project)
    if not can_view_all:
        q = q.where(Project.tenant_id == role["tenant_id"])
    if project_status:
        q = q.where(Project.project_status == project_status)
    q = q.order_by(Project.project_id.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=ProjectRead, status_code=201)
async def create_project(
    body: ProjectCreate,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    snapshot = _make_role_snapshot(role)

    # Exclude committees — handled separately below
    project_fields = body.model_dump(exclude={"committees"})

    project = Project(
        tenant_id=role["tenant_id"],
        proponent_role_id=role["role_id"],
        proponent_snapshot=snapshot,
        project_status=ProjectStatusEnum.PENDING,
        **project_fields,
    )
    db.add(project)
    await db.flush()

    # Create committees atomically with the project
    for committee_data in body.committees:
        cat_result = await db.execute(
            select(CommitteeCategory).where(
                CommitteeCategory.committee_cat_id == committee_data.committee_cat_id,
                CommitteeCategory.tenant_id == role["tenant_id"],
            )
        )
        if not cat_result.scalar_one_or_none():
            raise HTTPException(
                status_code=404,
                detail=f"Committee category {committee_data.committee_cat_id} not found",
            )

        committee = ProjectCommittee(
            project_id=project.project_id,
            committee_cat_id=committee_data.committee_cat_id,
        )
        db.add(committee)
        await db.flush()

        for m in committee_data.members:
            member = CommitteeMember(committee_id=committee.committee_id, **m.model_dump())
            db.add(member)

    await db.flush()

    await _publish_event(
        db, role["tenant_id"], "Project", project.project_id,
        "created",
        {"actor": snapshot, "line_item_id": body.line_item_id, "title": body.project_title},
    )

    return await _get_project_full(project.project_id, role["tenant_id"], db)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    tenant_id = None if _can_view_all_tenants(role) else role["tenant_id"]
    return await _get_project_full(project_id, tenant_id, db)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    body: ProjectUpdate,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    project = await _get_project_full(project_id, role["tenant_id"], db)

    changed = body.model_dump(exclude_none=True)
    for field, value in changed.items():
        setattr(project, field, value)
    await db.flush()

    snapshot = _make_role_snapshot(role)
    await _publish_event(
        db, role["tenant_id"], "Project", project_id,
        "updated",
        {"actor": snapshot, "changes": changed},
    )

    return await _get_project_full(project_id, role["tenant_id"], db)


@router.patch("/{project_id}/status", response_model=ProjectRead)
async def update_project_status(
    project_id: int,
    body: ProjectStatusUpdate,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    project = await _get_project_full(project_id, role["tenant_id"], db)

    old_status = project.project_status
    project.project_status = body.project_status
    await db.flush()

    snapshot = _make_role_snapshot(role)
    await _publish_event(
        db, role["tenant_id"], "Project", project_id,
        "status_changed",
        {"actor": snapshot, "old_status": old_status, "new_status": body.project_status},
    )

    return await _get_project_full(project_id, role["tenant_id"], db)


@router.delete("/{project_id}", status_code=204)
async def cancel_project(
    project_id: int,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    """Soft-cancel: sets status to Cancelled instead of deleting."""
    await _set_tenant(db, role["tenant_id"])
    project = await _get_project_full(project_id, role["tenant_id"], db)

    if project.project_status == ProjectStatusEnum.CANCELLED:
        raise HTTPException(status_code=409, detail="Project is already cancelled")

    project.project_status = ProjectStatusEnum.CANCELLED
    await db.flush()

    snapshot = _make_role_snapshot(role)
    await _publish_event(
        db, role["tenant_id"], "Project", project_id,
        "cancelled",
        {"actor": snapshot},
    )


# ── Committees ──────────────────────────────────────────────────────────────

@router.get("/{project_id}/committees", response_model=List[ProjectCommitteeRead])
async def list_committees(
    project_id: int,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    # Confirm project belongs to tenant
    await _get_project_full(project_id, role["tenant_id"], db)

    result = await db.execute(
        select(ProjectCommittee)
        .options(selectinload(ProjectCommittee.members))
        .where(ProjectCommittee.project_id == project_id)
    )
    return result.scalars().all()


@router.post("/{project_id}/committees", response_model=ProjectCommitteeRead, status_code=201)
async def add_committee(
    project_id: int,
    body: ProjectCommitteeCreate,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    # Verify the category belongs to this tenant
    cat_result = await db.execute(
        select(CommitteeCategory).where(
            CommitteeCategory.committee_cat_id == body.committee_cat_id,
            CommitteeCategory.tenant_id == role["tenant_id"],
        )
    )
    if not cat_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Committee category not found")

    # Check for duplicate committee in this project
    dup = await db.execute(
        select(ProjectCommittee).where(
            ProjectCommittee.project_id == project_id,
            ProjectCommittee.committee_cat_id == body.committee_cat_id,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Committee already exists for this project")

    committee = ProjectCommittee(project_id=project_id, committee_cat_id=body.committee_cat_id)
    db.add(committee)
    await db.flush()

    for m in body.members:
        member = CommitteeMember(committee_id=committee.committee_id, **m.model_dump())
        db.add(member)

    await db.flush()

    snapshot = _make_role_snapshot(role)
    await _publish_event(
        db, role["tenant_id"], "Project", project_id,
        "committee_added",
        {"actor": snapshot, "committee_cat_id": body.committee_cat_id},
    )

    result = await db.execute(
        select(ProjectCommittee)
        .options(selectinload(ProjectCommittee.members))
        .where(ProjectCommittee.committee_id == committee.committee_id)
    )
    return result.scalar_one()


@router.delete("/{project_id}/committees/{committee_id}", status_code=204)
async def remove_committee(
    project_id: int,
    committee_id: int,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    result = await db.execute(
        select(ProjectCommittee).where(
            ProjectCommittee.committee_id == committee_id,
            ProjectCommittee.project_id == project_id,
        )
    )
    committee = result.scalar_one_or_none()
    if not committee:
        raise HTTPException(status_code=404, detail="Committee not found")
    await db.delete(committee)


# ── Committee Members ───────────────────────────────────────────────────────

@router.post(
    "/{project_id}/committees/{committee_id}/members",
    response_model=CommitteeMemberRead,
    status_code=201,
)
async def add_committee_member(
    project_id: int,
    committee_id: int,
    body: CommitteeMemberCreate,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    # Confirm committee belongs to this project
    committee_result = await db.execute(
        select(ProjectCommittee).where(
            ProjectCommittee.committee_id == committee_id,
            ProjectCommittee.project_id == project_id,
        )
    )
    if not committee_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Committee not found")

    # Check for duplicate member in this committee
    dup = await db.execute(
        select(CommitteeMember).where(
            CommitteeMember.committee_id == committee_id,
            CommitteeMember.role_id == body.role_id,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="This role is already a member of this committee")

    member = CommitteeMember(committee_id=committee_id, **body.model_dump())
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member


@router.delete(
    "/{project_id}/committees/{committee_id}/members/{member_id}",
    status_code=204,
)
async def remove_committee_member(
    project_id: int,
    committee_id: int,
    member_id: int,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    result = await db.execute(
        select(CommitteeMember).where(
            CommitteeMember.member_id == member_id,
            CommitteeMember.committee_id == committee_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Committee member not found")
    await db.delete(member)


# ── Tasks ───────────────────────────────────────────────────────────────────

@router.get("/{project_id}/tasks", response_model=List[ProjectTaskRead])
async def list_tasks(
    project_id: int,
    task_status: Optional[TaskStatusEnum] = Query(None),
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    q = (
        select(ProjectTask)
        .options(selectinload(ProjectTask.assignments))
        .where(ProjectTask.project_id == project_id)
    )
    if task_status:
        q = q.where(ProjectTask.task_status == task_status)
    q = q.order_by(ProjectTask.task_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/{project_id}/tasks", response_model=ProjectTaskRead, status_code=201)
async def create_task(
    project_id: int,
    body: ProjectTaskCreate,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    task_data = body.model_dump(exclude={"assignee_member_ids"})
    task = ProjectTask(project_id=project_id, **task_data)
    db.add(task)
    await db.flush()

    for member_id in body.assignee_member_ids:
        # Validate member exists and belongs to this project's committees
        member_result = await db.execute(
            select(CommitteeMember)
            .join(ProjectCommittee, CommitteeMember.committee_id == ProjectCommittee.committee_id)
            .where(
                CommitteeMember.member_id == member_id,
                ProjectCommittee.project_id == project_id,
            )
        )
        if not member_result.scalar_one_or_none():
            raise HTTPException(
                status_code=404,
                detail=f"Committee member {member_id} not found in this project",
            )
        assignment = ProjectTaskAssignment(task_id=task.task_id, member_id=member_id)
        db.add(assignment)

    await db.flush()

    snapshot = _make_role_snapshot(role)
    await _publish_event(
        db, role["tenant_id"], "Project", project_id,
        "task_created",
        {"actor": snapshot, "task_id": task.task_id, "task_name": body.task_name},
    )

    result = await db.execute(
        select(ProjectTask)
        .options(selectinload(ProjectTask.assignments))
        .where(ProjectTask.task_id == task.task_id)
    )
    return result.scalar_one()


@router.patch("/{project_id}/tasks/{task_id}", response_model=ProjectTaskRead)
async def update_task(
    project_id: int,
    task_id: int,
    body: ProjectTaskUpdate,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    result = await db.execute(
        select(ProjectTask)
        .options(selectinload(ProjectTask.assignments))
        .where(ProjectTask.task_id == task_id, ProjectTask.project_id == project_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    changed = body.model_dump(exclude_none=True)
    for field, value in changed.items():
        setattr(task, field, value)
    await db.flush()

    snapshot = _make_role_snapshot(role)
    await _publish_event(
        db, role["tenant_id"], "Project", project_id,
        "task_updated",
        {"actor": snapshot, "task_id": task_id, "changes": changed},
    )

    result = await db.execute(
        select(ProjectTask)
        .options(selectinload(ProjectTask.assignments))
        .where(ProjectTask.task_id == task_id)
    )
    return result.scalar_one()


@router.delete("/{project_id}/tasks/{task_id}", status_code=204)
async def delete_task(
    project_id: int,
    task_id: int,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    result = await db.execute(
        select(ProjectTask).where(
            ProjectTask.task_id == task_id,
            ProjectTask.project_id == project_id,
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    await db.delete(task)


# ── Task Assignments ────────────────────────────────────────────────────────

@router.post(
    "/{project_id}/tasks/{task_id}/assignments",
    response_model=TaskAssignmentRead,
    status_code=201,
)
async def assign_member_to_task(
    project_id: int,
    task_id: int,
    body: TaskAssignmentCreate,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    # Confirm task belongs to this project
    task_result = await db.execute(
        select(ProjectTask).where(
            ProjectTask.task_id == task_id,
            ProjectTask.project_id == project_id,
        )
    )
    if not task_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Task not found")

    # Confirm member belongs to one of this project's committees
    member_result = await db.execute(
        select(CommitteeMember)
        .join(ProjectCommittee, CommitteeMember.committee_id == ProjectCommittee.committee_id)
        .where(
            CommitteeMember.member_id == body.member_id,
            ProjectCommittee.project_id == project_id,
        )
    )
    if not member_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Committee member not found in this project")

    # Check for duplicate
    dup = await db.execute(
        select(ProjectTaskAssignment).where(
            ProjectTaskAssignment.task_id == task_id,
            ProjectTaskAssignment.member_id == body.member_id,
        )
    )
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Member is already assigned to this task")

    assignment = ProjectTaskAssignment(task_id=task_id, member_id=body.member_id)
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return assignment


@router.delete(
    "/{project_id}/tasks/{task_id}/assignments/{assignment_id}",
    status_code=204,
)
async def unassign_member_from_task(
    project_id: int,
    task_id: int,
    assignment_id: int,
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    await _get_project_full(project_id, role["tenant_id"], db)

    result = await db.execute(
        select(ProjectTaskAssignment).where(
            ProjectTaskAssignment.assignment_id == assignment_id,
            ProjectTaskAssignment.task_id == task_id,
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await db.delete(assignment)


# ── Stats ───────────────────────────────────────────────────────────────────

@router.get("/stats/summary")
async def project_stats(
    role: dict = Depends(get_current_role),
    db: AsyncSession = Depends(get_db),
):
    await _set_tenant(db, role["tenant_id"])
    tid = role["tenant_id"]

    counts = {}
    for s in ProjectStatusEnum:
        r = await db.execute(
            select(sqlfunc.count()).where(
                Project.tenant_id == tid,
                Project.project_status == s,
            )
        )
        counts[s.value] = r.scalar() or 0

    total_r = await db.execute(
        select(sqlfunc.count()).where(Project.tenant_id == tid)
    )

    return {
        "total":          total_r.scalar() or 0,
        "by_status":      counts,
    }