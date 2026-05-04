from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_account, require_account_management_admin
from app.domains.identity.models import Account, AccountTenantRole, Tenant, JobPosition
from app.domains.identity.schemas import RoleAssignRequest, RoleUpdateRequest, RoleRead, AccountBase
from app.domains.identity.services.role_capacity import ensure_position_capacity, get_capacity_by_tenant

router = APIRouter(dependencies=[Depends(require_account_management_admin)])


def _validate_role_assignment(tenant: Tenant, position: JobPosition) -> str | None:
    if tenant.is_federation and not position.is_federation_role:
        return "Federation tenants only allow federation positions"
    if not tenant.is_federation and not position.is_barangay_sk_role:
        return "Barangay tenants only allow barangay SK positions"
    return None


async def _build_role_read(role: AccountTenantRole, db: AsyncSession) -> RoleRead:
    account  = await db.get(Account,      role.account_id)
    tenant   = await db.get(Tenant,       role.tenant_id)
    position = await db.get(JobPosition,  role.position_id)
    return RoleRead(
        role_id=role.role_id, account_id=role.account_id,
        tenant_id=role.tenant_id, position_id=role.position_id,
        is_primary_tenant=role.is_primary_tenant, role_status=role.role_status,
        account=AccountBase(first_name=account.first_name if account else None,
                            last_name=account.last_name   if account else None) if account else None,
        tenant=tenant, position=position,
    )


@router.post("", response_model=RoleRead, status_code=201)
async def assign_role(payload: RoleAssignRequest, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    account  = await db.get(Account,      payload.account_id)
    if not account:  raise HTTPException(404, "Account not found")
    tenant   = await db.get(Tenant,       payload.tenant_id)
    if not tenant:   raise HTTPException(404, "Tenant not found")
    position = await db.get(JobPosition,  payload.position_id)
    if not position: raise HTTPException(404, "Position not found")
    err = _validate_role_assignment(tenant, position)
    if err: raise HTTPException(409, err)
    if (await db.execute(select(AccountTenantRole).where(
        AccountTenantRole.account_id == payload.account_id,
        AccountTenantRole.tenant_id  == payload.tenant_id,
    ))).scalar_one_or_none():
        raise HTTPException(409, "This account already has a role in this tenant")
    if payload.role_status == "Active":
        try: await ensure_position_capacity(db, payload.tenant_id, payload.position_id)
        except ValueError as e: raise HTTPException(409, str(e))
    # Auto-promote to primary if the account has no primary role yet,
    # regardless of what the caller sent. This prevents users getting locked
    # out with primary_role=null after their first role assignment.
    has_primary = (await db.execute(
        select(AccountTenantRole).where(
            AccountTenantRole.account_id      == payload.account_id,
            AccountTenantRole.is_primary_tenant == True,
        )
    )).scalar_one_or_none() is not None

    make_primary = payload.is_primary_tenant or (not has_primary and payload.tenant_id != 1)

    if make_primary:
        for op in (await db.execute(select(AccountTenantRole).where(
            AccountTenantRole.account_id == payload.account_id,
            AccountTenantRole.is_primary_tenant == True,
        ))).scalars().all():
            op.is_primary_tenant = False
    role = AccountTenantRole(
        account_id=payload.account_id, auth_external_id=account.auth_external_id,
        tenant_id=payload.tenant_id, position_id=payload.position_id,
        is_primary_tenant=make_primary, role_status=payload.role_status,
    )
    db.add(role); await db.commit(); await db.refresh(role)
    return await _build_role_read(role, db)


@router.get("/capacity")
async def get_role_capacity(tenant_id: int = Query(...), _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    if not await db.get(Tenant, tenant_id): raise HTTPException(404, "Tenant not found")
    return await get_capacity_by_tenant(db, tenant_id)


@router.get("/{role_id}", response_model=RoleRead)
async def get_role(role_id: int, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    role = await db.get(AccountTenantRole, role_id)
    if not role: raise HTTPException(404, "Role not found")
    return await _build_role_read(role, db)


@router.patch("/{role_id}", response_model=RoleRead)
async def update_role(role_id: int, payload: RoleUpdateRequest, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    role     = await db.get(AccountTenantRole, role_id)
    if not role: raise HTTPException(404, "Role not found")
    position = await db.get(JobPosition, payload.position_id or role.position_id)
    tenant   = await db.get(Tenant, role.tenant_id)
    err = _validate_role_assignment(tenant, position)
    if err: raise HTTPException(409, err)
    if payload.is_primary_tenant:
        for op in (await db.execute(select(AccountTenantRole).where(
            AccountTenantRole.account_id == role.account_id,
            AccountTenantRole.is_primary_tenant == True,
            AccountTenantRole.role_id != role_id,
        ))).scalars().all():
            op.is_primary_tenant = False
    next_status = payload.role_status or role.role_status
    if next_status == "Active":
        try: await ensure_position_capacity(db, role.tenant_id, payload.position_id or role.position_id, exclude_role_id=role.role_id)
        except ValueError as e: raise HTTPException(409, str(e))
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(role, k, v)
    await db.commit(); await db.refresh(role)
    return await _build_role_read(role, db)


@router.delete("/{role_id}", status_code=204)
async def remove_role(role_id: int, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    role = await db.get(AccountTenantRole, role_id)
    if not role: raise HTTPException(404, "Role not found")
    await db.delete(role); await db.commit()