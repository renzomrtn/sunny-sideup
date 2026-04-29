from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.identity.models import AccountTenantRole, JobPosition


POSITION_CAPACITY = {
    "SKF Member":    19,
    "SK Councilor":   7,
}


def get_position_capacity(position_name: str) -> int:
    return POSITION_CAPACITY.get(position_name, 1)


async def get_capacity_by_tenant(db: AsyncSession, tenant_id: int) -> dict[str, int]:
    result = await db.execute(
        select(JobPosition.position_name, func.count(AccountTenantRole.role_id))
        .join(AccountTenantRole, AccountTenantRole.position_id == JobPosition.position_id)
        .where(
            AccountTenantRole.tenant_id  == tenant_id,
            AccountTenantRole.role_status == "Active",
        )
        .group_by(JobPosition.position_name)
    )
    return {row[0]: row[1] for row in result.all()}


async def ensure_position_capacity(
    db:              AsyncSession,
    tenant_id:       int,
    position_id:     int,
    *,
    exclude_role_id: int | None = None,
) -> None:
    position = await db.get(JobPosition, position_id)
    if not position:
        return

    count_query = select(func.count(AccountTenantRole.role_id)).where(
        AccountTenantRole.tenant_id   == tenant_id,
        AccountTenantRole.position_id == position_id,
        AccountTenantRole.role_status == "Active",
    )
    if exclude_role_id is not None:
        count_query = count_query.where(AccountTenantRole.role_id != exclude_role_id)

    current_count = (await db.execute(count_query)).scalar_one()
    capacity      = get_position_capacity(position.position_name)
    if current_count >= capacity:
        raise ValueError(f"{position.position_name} is already full for the selected tenant")
