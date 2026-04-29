import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_account, has_account_management_access
from app.domains.identity.models import (
    Account, AccountTenantRole, Tenant, JobPosition, LoginEvent, Outbox
)
from app.domains.identity.schemas import TokenResponse, CurrentUserRead, RoleInAccount

PHT = ZoneInfo("Asia/Manila")


def pht_now():
    """Return current Philippine Standard Time (UTC+8) as a naive datetime.
    Naive because all DB columns are TIMESTAMP WITHOUT TIME ZONE."""
    return datetime.now(PHT).replace(tzinfo=None)




router = APIRouter()

AUTHENTIK_TOKEN_URL = f"{settings.AUTHENTIK_URL}/application/o/token/"


async def _exchange_code_for_tokens(code: str, redirect_uri: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            AUTHENTIK_TOKEN_URL,
            data={
                "grant_type":    "authorization_code",
                "code":          code,
                "redirect_uri":  redirect_uri,
                "client_id":     settings.AUTHENTIK_CLIENT_ID,
                "client_secret": settings.AUTHENTIK_CLIENT_SECRET,
            },
            timeout=15,
        )
        if r.status_code != 200:
            raise HTTPException(502, f"Authentik token exchange failed: {r.text}")
        return r.json()


# ── Helpers ────────────────────────────────────────────────────────────────

async def _record_login_event(
    db:         AsyncSession,
    account:    Account,
    event_type: str,            # "LOGIN" or "LOGOUT"
) -> None:
    """
    Writes a Login_Event row to identity_db AND enqueues an outbox entry
    so audit-service and eventing-service both receive it via RabbitMQ.
    """
    # Resolve primary active role for context
    role_result = await db.execute(
        select(AccountTenantRole).where(
            AccountTenantRole.account_id        == account.account_id,
            AccountTenantRole.is_primary_tenant == True,
            AccountTenantRole.role_status       == "Active",
        )
    )
    primary_role = role_result.scalar_one_or_none()

    role_id   = primary_role.role_id   if primary_role else None
    tenant_id = primary_role.tenant_id if primary_role else None

    # 1. Write Login_Event row directly to identity_db
    login_event = LoginEvent(
        account_id       = account.account_id,
        auth_external_id = account.auth_external_id,
        role_id          = role_id,
        tenant_id        = tenant_id,
        event_type       = event_type,
        occurred_at      = pht_now(),
    )
    db.add(login_event)

    # 2. Enqueue to Outbox so audit-service records it too
    actor_snapshot = {
        "account_id":       account.account_id,
        "auth_external_id": account.auth_external_id,
        "full_name":        account.full_name,
        "role_id":          role_id,
        "tenant_id":        tenant_id,
    }
    outbox_row = Outbox(
        tenant_id      = tenant_id or 0,
        aggregate_type = "login",
        aggregate_id   = account.account_id,
        event_type     = event_type.lower(),    # "login" or "logout"
        payload        = {
            "actor":      actor_snapshot,
            "event_type": event_type,
            "role_id":    role_id,
            "tenant_id":  tenant_id,
        },
    )
    db.add(outbox_row)

    await db.commit()


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get("/callback")
async def oidc_callback(request: Request):
    """
    Authentik redirects here with ?code=... after the user authenticates.
    We exchange the code for tokens, then redirect the frontend to /auth/finish.
    Login_Event is recorded in /api/auth/me (first authenticated call after login).
    """
    code  = request.query_params.get("code")
    error = request.query_params.get("error")
    if error:
        raise HTTPException(400, f"Authentik login error: {error}")
    if not code:
        raise HTTPException(400, "Missing authorization code")

    tokens       = await _exchange_code_for_tokens(code, settings.AUTHENTIK_REDIRECT_URI)
    access_token = tokens.get("access_token")
    id_token     = tokens.get("id_token", "")
    return RedirectResponse(url=f"/auth/finish?token={access_token}&id_token={id_token}")


@router.post("/logout")
async def logout(
    account: Account      = Depends(get_current_account),
    db:      AsyncSession = Depends(get_db),
):
    """
    Records a LOGOUT event in Login_Event and publishes to RabbitMQ via Outbox.
    Frontend calls this before clearing its local token.
    """
    await _record_login_event(db, account, "LOGOUT")
    return {"message": "Logged out"}


@router.post("/login-event")
async def record_login(
    account: Account      = Depends(get_current_account),
    db:      AsyncSession = Depends(get_db),
):
    """
    Called by the frontend immediately after a successful OIDC callback
    (i.e. after /auth/finish stores the token and the app boots).
    Records a LOGIN event in Login_Event and publishes to RabbitMQ via Outbox.

    Why a separate endpoint instead of recording in /callback:
      /callback runs before we have a DB session with the authenticated user —
      we only have a code at that point. Once the frontend has exchanged it for
      a token and calls this endpoint with Bearer auth, we have the full Account.
    """
    await _record_login_event(db, account, "LOGIN")
    return {"message": "Login recorded"}


@router.get("/me", response_model=CurrentUserRead)
async def me(
    account: Account      = Depends(get_current_account),
    db:      AsyncSession = Depends(get_db),
):
    """Return the currently authenticated user's profile and primary role."""
    role_result = await db.execute(
        select(AccountTenantRole).where(
            AccountTenantRole.account_id        == account.account_id,
            AccountTenantRole.is_primary_tenant == True,
            AccountTenantRole.role_status       == "Active",
        )
    )
    pri = role_result.scalar_one_or_none()
    primary_role = None
    if pri:
        t = await db.get(Tenant,      pri.tenant_id)
        p = await db.get(JobPosition, pri.position_id)
        primary_role = RoleInAccount(
            role_id           = pri.role_id,
            tenant_id         = pri.tenant_id,
            tenant_name       = t.tenant_name   if t else "Unknown",
            position_id       = pri.position_id,
            position_name     = p.position_name if p else "Unknown",
            is_primary_tenant = pri.is_primary_tenant,
            role_status       = pri.role_status,
        )
    return CurrentUserRead(
        account_id     = account.account_id,
        full_name      = account.full_name,
        contact_email  = account.contact_email,
        account_status = account.account_status,
        primary_role   = primary_role,
        can_access_account_management = await has_account_management_access(account, db),
    )

@router.get("/exchange")
async def exchange_code(code: str, redirect_uri: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            AUTHENTIK_TOKEN_URL,
            data={
                "grant_type":    "authorization_code",
                "code":          code,
                "redirect_uri":  redirect_uri,
                "client_id":     settings.MAINSYS_CLIENT_ID,
                "client_secret": settings.MAINSYS_CLIENT_SECRET,
            },
            timeout=15,
        )
        if r.status_code != 200:
            raise HTTPException(502, f"Authentik token exchange failed: {r.text}")
        tokens = r.json()
        return {"access_token": tokens.get("access_token")}