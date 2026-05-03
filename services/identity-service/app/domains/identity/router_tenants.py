from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_account, require_account_management_admin
from app.domains.identity.models import Account, Tenant, JobPosition, AccountTenantRole
from app.domains.identity.schemas import TenantCreate, TenantUpdate, TenantRead, JobPositionRead, AccountListItem

# Guard moved from router-level to per-route so /barangays can use a lighter
# dependency without needing a separate router registration.
router = APIRouter()


# ── Barangay list (any authenticated user) ────────────────────────────────
# MUST be declared before /{tenant_id} so FastAPI does not try to cast
# the literal string "barangays" to int.

@router.get("/barangays", response_model=list[TenantRead])
async def list_barangay_tenants(
    _: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns all active, non-federation tenants ordered by name.
    Accessible to any authenticated user — federation officials and SK
    chairmen alike — so the Monitoring page can populate its barangay
    dropdown / overview grid without needing admin rights.
    """
    result = await db.execute(
        select(Tenant)
        .where(Tenant.is_federation == False, Tenant.tenant_status == "Active")  # noqa: E712
        .order_by(Tenant.tenant_name)
    )
    return result.scalars().all()


@router.get("/{tenant_id}/officials", response_model=list[AccountListItem])
async def list_tenant_officials(
    tenant_id: int,
    _: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Account)
        .options(selectinload(Account.tenant_roles).selectinload(AccountTenantRole.tenant),
                 selectinload(Account.tenant_roles).selectinload(AccountTenantRole.position))
        .join(AccountTenantRole)
        .where(
            AccountTenantRole.tenant_id == tenant_id,
            AccountTenantRole.role_status == "Active",
            Account.account_status == "Active"
        )
        .distinct()
    )
    accounts = result.scalars().all()

    items = []
    for acc in accounts:
        role = next(
            (r for r in acc.tenant_roles if r.tenant_id == tenant_id and r.role_status == "Active"),
            None,
        )
        items.append(AccountListItem(
            account_id=acc.account_id,
            full_name=acc.full_name,
            contact_email=acc.contact_email,
            account_status=acc.account_status,
            synced_at=acc.synced_at,
            role_id=role.role_id if role else None,
            position_name=role.position.position_name if role and role.position else None,
            tenant_name=role.tenant.tenant_name if role and role.tenant else None,
        ))
    return items


# ── Admin-only routes ─────────────────────────────────────────────────────

@router.get("", response_model=list[TenantRead], dependencies=[Depends(require_account_management_admin)])
async def list_tenants(_: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(Tenant).order_by(Tenant.tenant_name))).scalars().all()


@router.get("/{tenant_id}", response_model=TenantRead, dependencies=[Depends(require_account_management_admin)])
async def get_tenant(tenant_id: int, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    tenant = await db.get(Tenant, tenant_id)
    if not tenant: raise HTTPException(404, "Tenant not found")
    return tenant


@router.post("", response_model=TenantRead, status_code=201, dependencies=[Depends(require_account_management_admin)])
async def create_tenant(payload: TenantCreate, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    tenant = Tenant(**payload.model_dump())
    db.add(tenant); await db.commit(); await db.refresh(tenant)
    return tenant


@router.patch("/{tenant_id}", response_model=TenantRead, dependencies=[Depends(require_account_management_admin)])
async def update_tenant(tenant_id: int, payload: TenantUpdate, _: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    tenant = await db.get(Tenant, tenant_id)
    if not tenant: raise HTTPException(404, "Tenant not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(tenant, k, v)
    await db.commit(); await db.refresh(tenant)
    return tenant


@router.get("/positions/all", response_model=list[JobPositionRead], dependencies=[Depends(require_account_management_admin)])
async def list_positions(_: Account = Depends(get_current_account), db: AsyncSession = Depends(get_db)):
    return (await db.execute(select(JobPosition).order_by(JobPosition.position_name))).scalars().all()