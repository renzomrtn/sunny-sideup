import httpx
from functools import lru_cache
from typing import Optional

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.domains.identity.models import Account, AccountTenantRole, JobPosition, JobPositionEnum, Tenant


bearer_scheme = HTTPBearer(auto_error=False)


# ── JWKS / OIDC Discovery ─────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_jwks() -> dict:
    """
    Fetches Authentik's public signing keys via OIDC discovery.
    Result is cached in-process. Restart backend to force a refresh.
    """
    discovery_url = f"{settings.AUTHENTIK_URL}/application/o/{settings.AUTHENTIK_SLUG}/.well-known/openid-configuration"
    r = httpx.get(discovery_url, timeout=10)
    r.raise_for_status()
    jwks_uri = r.json()["jwks_uri"]

    r2 = httpx.get(jwks_uri, timeout=10)
    r2.raise_for_status()
    return r2.json()


def decode_authentik_token(token: str) -> dict:
    """
    Validates an Authentik-issued JWT (RS256) against Authentik's public JWKS.
    Returns the decoded payload on success, raises HTTPException on failure.
    """
    try:
        jwks = _get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=settings.AUTHENTIK_CLIENT_ID,
            options={"verify_at_hash": False},
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {e}",
        )


# ── Current User Dependency ───────────────────────────────────────────────

async def get_current_account(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> Account:
    """
    Validates the Bearer token issued by Authentik, then looks up the
    matching Account row by auth_external_id (Authentik's 'sub' claim).

    Flow:
      1. Validate JWT signature + expiry against Authentik JWKS.
      2. Extract `sub` (Authentik user UUID).
      3. Load the Account whose auth_external_id == sub.
      4. Reject if account is Inactive.
    """
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    payload = decode_authentik_token(credentials.credentials)
    authentik_sub: str = payload.get("sub")

    if not authentik_sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing sub claim")

    result = await db.execute(
        select(Account).where(Account.auth_external_id == authentik_sub)
    )
    account = result.scalar_one_or_none()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No account found for this Authentik user. Contact your administrator.",
        )

    if account.account_status != "Active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Contact your administrator.",
        )

    return account


# ── Tenant Context Dependency ─────────────────────────────────────────────

async def get_current_role(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> AccountTenantRole:
    """
    Returns the primary active role for the authenticated account.
    """
    result = await db.execute(
        select(AccountTenantRole).where(
            AccountTenantRole.account_id == account.account_id,
            AccountTenantRole.role_status == "Active",
            AccountTenantRole.is_primary_tenant == True,
        )
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=403, detail="No active role found for this account")
    return role


async def has_account_management_access(account: Account, db: AsyncSession) -> bool:
    result = await db.execute(
        select(AccountTenantRole)
        .join(JobPosition, AccountTenantRole.position_id == JobPosition.position_id)
        .where(
            AccountTenantRole.account_id == account.account_id,
            AccountTenantRole.role_status == "Active",
            JobPosition.position_name == JobPositionEnum.ACCOUNT_MANAGEMENT_ADMINISTRATOR,
        )
    )
    return result.scalar_one_or_none() is not None


async def require_account_management_admin(
    account: Account = Depends(get_current_account),
    db: AsyncSession = Depends(get_db),
) -> Account:
    if not await has_account_management_access(account, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Role Detected. Unauthorized Access! Keep Out.",
        )
    return account
