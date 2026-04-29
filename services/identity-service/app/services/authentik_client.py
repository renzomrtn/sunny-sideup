"""
Authentik Admin API client.

The app stores Authentik's UUID in account.auth_external_id because login
matches that column against the token `sub` claim. Authentik's REST API still
uses the numeric/user API pk for update and delete routes, so this client
resolves identifiers before making write calls.
"""

import logging
import re
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_API_BASE = f"{settings.AUTHENTIK_URL}/api/v3"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.AUTHENTIK_API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _build_username(first_name: str, last_name: str) -> str:
    def clean(s: str) -> str:
        return re.sub(r"[^a-z0-9]", "", s.lower().strip())

    first = clean(first_name)
    last = clean(last_name)
    return f"{first}.{last}" if first and last else (first or last or "user")


def _extract_authentik_uuid(user_data: dict) -> str:
    user_uuid = user_data.get("uuid") or user_data.get("sub") or user_data.get("uid")
    if not user_uuid:
        raise RuntimeError("Authentik user response did not include a uuid")
    return str(user_uuid)


async def _resolve_unique_username(base_username: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        candidate = base_username
        suffix = 2
        while True:
            r = await client.get(
                f"{_API_BASE}/core/users/",
                headers=_headers(),
                params={"username": candidate},
            )
            r.raise_for_status()
            results = r.json().get("results", [])
            if not results:
                return candidate
            candidate = f"{base_username}{suffix}"
            suffix += 1


async def get_authentik_user(auth_identifier: str) -> Optional[dict]:
    """
    Resolve an Authentik user by UUID, uid, API pk, username, or email.
    """
    if not auth_identifier:
        return None

    identifier = str(auth_identifier).strip()
    async with httpx.AsyncClient(timeout=15) as client:
        direct = await client.get(
            f"{_API_BASE}/core/users/{identifier}/",
            headers=_headers(),
        )
        if direct.status_code == 200:
            return direct.json()
        if direct.status_code not in (400, 404):
            direct.raise_for_status()

        for params in (
            {"uuid": identifier},
            {"uid": identifier},
            {"username": identifier},
            {"email": identifier},
            {"search": identifier},
        ):
            r = await client.get(
                f"{_API_BASE}/core/users/",
                headers=_headers(),
                params=params,
            )
            r.raise_for_status()
            for user in r.json().get("results", []):
                if identifier in {
                    str(user.get("pk", "")),
                    str(user.get("uid", "")),
                    str(user.get("uuid", "")),
                    str(user.get("username", "")),
                    str(user.get("email", "")),
                }:
                    return user

    return None


async def resolve_authentik_user_uuid(auth_identifier: str) -> str:
    """
    Convert an imported Authentik identifier to the UUID used by the app.
    This accepts older spreadsheets that contain the Authentik API pk.
    """
    user_data = await get_authentik_user(auth_identifier)
    if not user_data:
        raise RuntimeError(f"Authentik user {auth_identifier} was not found")
    return _extract_authentik_uuid(user_data)


async def create_authentik_user(
    first_name: str,
    last_name: str,
    email: Optional[str] = None,
) -> str:
    """
    Create an Authentik user and return the UUID used by the app.
    """
    base_username = _build_username(first_name, last_name)
    username = await _resolve_unique_username(base_username)

    payload: dict = {
        "username": username,
        "name": f"{first_name} {last_name}".strip(),
        "is_active": True,
        "email": email or "",
        "groups": [],
        "attributes": {},
        "path": "users",
        "type": "internal",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            f"{_API_BASE}/core/users/",
            headers=_headers(),
            json=payload,
        )
        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"Authentik user creation failed ({r.status_code}): {r.text}"
            )
        user_data = r.json()
        user_pk = str(user_data["pk"])
        user_uuid = _extract_authentik_uuid(user_data)

        pw_r = await client.post(
            f"{_API_BASE}/core/users/{user_pk}/set_password/",
            headers=_headers(),
            json={"password": settings.AUTHENTIK_DEFAULT_PASSWORD},
        )
        if pw_r.status_code not in (200, 201, 204):
            logger.warning(
                "Could not set password for Authentik user %s (%d): %s",
                user_pk,
                pw_r.status_code,
                pw_r.text,
            )

    logger.info("Created Authentik user '%s' -> pk=%s uuid=%s", username, user_pk, user_uuid)
    return user_uuid


async def set_authentik_user_active(auth_external_id: str, is_active: bool) -> None:
    user_data = await get_authentik_user(auth_external_id)
    if not user_data:
        logger.warning(
            "Authentik user %s not found; skipping %s sync.",
            auth_external_id,
            "activation" if is_active else "deactivation",
        )
        return

    user_pk = str(user_data["pk"])
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.patch(
            f"{_API_BASE}/core/users/{user_pk}/",
            headers=_headers(),
            json={"is_active": is_active},
        )
        if r.status_code == 404:
            logger.warning("Authentik user %s not found during status sync.", auth_external_id)
            return
        if r.status_code not in (200, 201, 204):
            raise RuntimeError(
                f"Authentik user update failed ({r.status_code}): {r.text}"
            )

    logger.info("Authentik user %s -> is_active=%s", auth_external_id, is_active)


async def delete_authentik_user(auth_external_id: str) -> None:
    """
    Delete the Authentik account tied to a local account deactivation.
    """
    user_data = await get_authentik_user(auth_external_id)
    if not user_data:
        logger.warning("Authentik user %s not found; skipping delete.", auth_external_id)
        return

    user_pk = str(user_data["pk"])
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.delete(
            f"{_API_BASE}/core/users/{user_pk}/",
            headers=_headers(),
        )
        if r.status_code == 404:
            logger.warning("Authentik user %s not found during delete.", auth_external_id)
            return
        if r.status_code not in (200, 202, 204):
            raise RuntimeError(
                f"Authentik user delete failed ({r.status_code}): {r.text}"
            )

    logger.info("Deleted Authentik user %s", auth_external_id)
