from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator

from app.domains.identity.models import TenantNameEnum, JobPositionEnum


# ── Token ──────────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    expires_in:   int


class AuthCallbackRequest(BaseModel):
    code:  str
    state: Optional[str] = None


# ── Tenant ─────────────────────────────────────────────────────────────────

class TenantBase(BaseModel):
    tenant_name:   TenantNameEnum
    is_federation: bool = False
    tenant_status: str  = "Active"

    @field_validator("tenant_status")
    @classmethod
    def validate_status(cls, v):
        if v not in ("Active", "Inactive"):
            raise ValueError("tenant_status must be Active or Inactive")
        return v


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    tenant_status: Optional[str] = None

    @field_validator("tenant_status")
    @classmethod
    def validate_status(cls, v):
        if v and v not in ("Active", "Inactive"):
            raise ValueError("tenant_status must be Active or Inactive")
        return v


class TenantRead(TenantBase):
    tenant_id: int
    model_config = {"from_attributes": True}


# ── Job Position ───────────────────────────────────────────────────────────

class JobPositionRead(BaseModel):
    position_id:         int
    position_name:       JobPositionEnum
    is_barangay_sk_role: bool
    is_federation_role:  bool
    model_config = {"from_attributes": True}


# ── Account ────────────────────────────────────────────────────────────────

class AccountBase(BaseModel):
    first_name:     Optional[str] = None
    middle_name:    Optional[str] = None
    last_name:      Optional[str] = None
    contact_number: Optional[str] = None
    contact_email:  Optional[str] = None


class AccountCreate(AccountBase):
    auth_external_id: str
    account_status:   str = "Active"

    @field_validator("account_status")
    @classmethod
    def validate_status(cls, v):
        if v not in ("Active", "Inactive"):
            raise ValueError("account_status must be Active or Inactive")
        return v


class AccountUpdate(AccountBase):
    account_status: Optional[str] = None

    @field_validator("account_status")
    @classmethod
    def validate_status(cls, v):
        if v and v not in ("Active", "Inactive"):
            raise ValueError("account_status must be Active or Inactive")
        return v


class RoleInAccount(BaseModel):
    role_id:           int
    tenant_id:         int
    tenant_name:       TenantNameEnum
    position_id:       int
    position_name:     JobPositionEnum
    is_primary_tenant: bool
    role_status:       str
    model_config = {"from_attributes": True}


class AccountRead(AccountBase):
    account_id:        int
    auth_external_id:  str
    identity_provider: str
    account_status:    str
    synced_at:         datetime
    full_name:         str
    tenant_roles:      List[RoleInAccount] = []
    model_config = {"from_attributes": True}


class AccountListItem(BaseModel):
    account_id:       int
    full_name:        str
    contact_email:    Optional[str] = None
    account_status:   str
    synced_at:        datetime
    primary_tenant:   Optional[str] = None
    primary_position: Optional[str] = None
    # Populated by the /tenants/{id}/officials endpoint so callers
    # (e.g. project-service committee creation) get role_id + snapshot
    # without a second round-trip.
    role_id:          Optional[int] = None
    position_name:    Optional[str] = None
    tenant_name:      Optional[str] = None
    model_config = {"from_attributes": True}


# ── Role Assignment ────────────────────────────────────────────────────────

class RoleAssignRequest(BaseModel):
    account_id:        int
    tenant_id:         int
    position_id:       int
    is_primary_tenant: bool = False
    role_status:       str  = "Active"

    @field_validator("role_status")
    @classmethod
    def validate_status(cls, v):
        if v not in ("Active", "Inactive"):
            raise ValueError("role_status must be Active or Inactive")
        return v


class RoleUpdateRequest(BaseModel):
    position_id:       Optional[int]  = None
    is_primary_tenant: Optional[bool] = None
    role_status:       Optional[str]  = None

    @field_validator("role_status")
    @classmethod
    def validate_status(cls, v):
        if v and v not in ("Active", "Inactive"):
            raise ValueError("role_status must be Active or Inactive")
        return v


class RoleRead(BaseModel):
    role_id:           int
    account_id:        int
    tenant_id:         int
    position_id:       int
    is_primary_tenant: bool
    role_status:       str
    account:           Optional[AccountBase]    = None
    tenant:            Optional[TenantRead]     = None
    position:          Optional[JobPositionRead] = None
    model_config = {"from_attributes": True}


# ── Login Event ────────────────────────────────────────────────────────────

class LoginEventRead(BaseModel):
    event_id:         int
    account_id:       int
    auth_external_id: str
    role_id:          Optional[int] = None
    tenant_id:        Optional[int] = None
    event_type:       str
    occurred_at:      datetime
    model_config = {"from_attributes": True}


# ── Pagination ─────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items:       list
    total:       int
    page:        int
    page_size:   int
    total_pages: int


class AccountImportIssue(BaseModel):
    row:     int
    message: str


class AccountImportWarning(BaseModel):
    row:     int
    message: str


class AccountImportResponse(BaseModel):
    created:       int
    updated:       int
    roles_created: int
    roles_updated: int
    skipped:       int
    errors:        List[AccountImportIssue]
    warnings:      List[AccountImportWarning]


class AccountImportJobAccepted(BaseModel):
    job_id:         str
    status:         str
    total_rows:     int
    processed_rows: int
    message:        Optional[str] = None


class AccountImportJobStatus(AccountImportJobAccepted):
    result:      Optional[AccountImportResponse] = None
    error:       Optional[str] = None
    created_at:  datetime
    started_at:  Optional[datetime] = None
    finished_at: Optional[datetime] = None


# ── Current User ───────────────────────────────────────────────────────────

class CurrentUserRead(BaseModel):
    account_id:     int
    full_name:      str
    contact_email:  Optional[str]      = None
    account_status: str
    primary_role:   Optional[RoleInAccount] = None
    can_access_account_management: bool = False
    model_config = {"from_attributes": True}