from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_account, require_account_management_admin
from app.domains.identity.models import Account, Tenant, JobPosition
from app.domains.identity.schemas import TenantCreate, TenantUpdate, TenantRead, JobPositionRead

router = APIRouter(dependencies=[Depends(require_account_management_admin)])


@router.get("", response_model=list[TenantRead])
async def list_tenants(_: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Tenant).order_by(Tenant.tenant_name))).scalars().all()


@router.get("/{tenant_id}", response_model=TenantRead)
async def get_tenant(tenant_id: int, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    tenant = await db.get(Tenant, tenant_id)
    if not tenant: raise HTTPException(404, "Tenant not found")
    return tenant


@router.post("", response_model=TenantRead, status_code=201)
async def create_tenant(payload: TenantCreate, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    tenant = Tenant(**payload.model_dump())
    db.add(tenant); await db.commit(); await db.refresh(tenant)
    return tenant


@router.patch("/{tenant_id}", response_model=TenantRead)
async def update_tenant(tenant_id: int, payload: TenantUpdate, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    tenant = await db.get(Tenant, tenant_id)
    if not tenant: raise HTTPException(404, "Tenant not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(tenant, k, v)
    await db.commit(); await db.refresh(tenant)
    return tenant


@router.get("/positions/all", response_model=list[JobPositionRead])
async def list_positions(_: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(JobPosition).order_by(JobPosition.position_name))).scalars().all()
