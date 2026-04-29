from datetime import datetime
from typing import Optional, List
import enum

from sqlalchemy import (
    Boolean, CheckConstraint, DateTime, ForeignKey, Integer,
    String, Text, UniqueConstraint, func, BigInteger
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, JSONB

from app.core.database import Base


# ── Python enums ───────────────────────────────────────────────────────────

class TenantNameEnum(str, enum.Enum):
    SK_FEDERATION          = "SK Federation"
    SK_ABELLA              = "SK Abella"
    SK_BAGUMBAYAN_NORTE    = "SK Bagumbayan Norte"
    SK_BAGUMBAYAN_SUR      = "SK Bagumbayan Sur"
    SK_BALATAS             = "SK Balatas"
    SK_CALAUAG             = "SK Calauag"
    SK_CARARAYAN           = "SK Cararayan"
    SK_CAROLINA            = "SK Carolina"
    SK_CONCEPCION_GRANDE   = "SK Concepcion Grande"
    SK_CONCEPCION_PEQUEÑA  = "SK Concepcion Pequeña"
    SK_DAYANGDANG          = "SK Dayangdang"
    SK_DEL_ROSARIO         = "SK Del Rosario"
    SK_DINAGA              = "SK Dinaga"
    SK_IGUALDAD_INTERIOR   = "SK Igualdad Interior"
    SK_LERMA               = "SK Lerma"
    SK_LIBOTON             = "SK Liboton"
    SK_MABOLO              = "SK Mabolo"
    SK_PACOL               = "SK Pacol"
    SK_PANICUASON          = "SK Panicuason"
    SK_PENAFRANCIA         = "SK Penafrancia"
    SK_SABANG              = "SK Sabang"
    SK_SAN_FELIPE          = "SK San Felipe"
    SK_SAN_FRANCISCO       = "SK San Francisco"
    SK_SAN_ISIDRO          = "SK San Isidro"
    SK_SANTA_CRUZ          = "SK Santa Cruz"
    SK_TABUCO              = "SK Tabuco"
    SK_TINAGO              = "SK Tinago"
    SK_TRIANGULO           = "SK Triangulo"


class JobPositionEnum(str, enum.Enum):
    SK_CHAIRPERSON                   = "SK Chairperson"
    SK_COUNCILOR                     = "SK Councilor"
    SK_SECRETARY                     = "SK Secretary"
    SK_TREASURER                     = "SK Treasurer"
    SKF_PRESIDENT                    = "SKF President"
    SKF_VICE_PRESIDENT               = "SKF Vice President"
    SKF_SECRETARY                    = "SKF Secretary"
    SKF_TREASURER                    = "SKF Treasurer"
    SKF_AUDITOR                      = "SKF Auditor"
    SKF_PRO                          = "SKF P.R.O."
    SKF_SGT_AT_ARMS                  = "SKF Sgt. at Arms"
    SKF_PROPERTY_CUSTODIAN           = "SKF Property Custodian"
    SKF_MEMBER                       = "SKF Member"
    CHIEF_OF_STAFF                   = "Chief of Staff"
    ADMINISTRATIVE_AIDE              = "Administrative Aide"
    ACCOUNT_MANAGEMENT_ADMINISTRATOR = "Account Management Administrator"


# ── Tenant ─────────────────────────────────────────────────────────────────

class Tenant(Base):
    __tablename__ = "tenant"

    tenant_id:     Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True)
    tenant_name:   Mapped[TenantNameEnum] = mapped_column(
        PgEnum(
            TenantNameEnum,
            name="tenant_name_enum",
            create_type=False,
            validate_strings=True,
            values_callable=lambda e: [x.value for x in e],
        ),
        nullable=False, unique=True,
    )
    is_federation: Mapped[bool] = mapped_column(Boolean, default=False)
    tenant_status: Mapped[str]  = mapped_column(String(20), nullable=False)

    __table_args__ = (
        CheckConstraint("tenant_status IN ('Active','Inactive')", name="chk_tenant_status"),
    )

    roles: Mapped[List["AccountTenantRole"]] = relationship("AccountTenantRole", back_populates="tenant")


# ── Job Position ───────────────────────────────────────────────────────────

class JobPosition(Base):
    __tablename__ = "job_position"

    position_id:         Mapped[int]              = mapped_column(Integer, primary_key=True, autoincrement=True)
    position_name:       Mapped[JobPositionEnum]  = mapped_column(
        PgEnum(
            JobPositionEnum,
            name="job_position_enum",
            create_type=False,
            validate_strings=True,
            values_callable=lambda e: [x.value for x in e],
        ),
        nullable=False, unique=True,
    )
    is_barangay_sk_role: Mapped[bool] = mapped_column(Boolean, default=False)
    is_federation_role:  Mapped[bool] = mapped_column(Boolean, default=False)

    roles: Mapped[List["AccountTenantRole"]] = relationship("AccountTenantRole", back_populates="position")


# ── Account ────────────────────────────────────────────────────────────────

class Account(Base):
    __tablename__ = "account"

    account_id:        Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True)
    auth_external_id:  Mapped[str]           = mapped_column(String(255), nullable=False, unique=True)
    identity_provider: Mapped[str]           = mapped_column(String(50), nullable=False, default="authentik")
    first_name:        Mapped[Optional[str]] = mapped_column(String(50))
    middle_name:       Mapped[Optional[str]] = mapped_column(String(50))
    last_name:         Mapped[Optional[str]] = mapped_column(String(50))
    contact_number:    Mapped[Optional[str]] = mapped_column(String(20))
    contact_email:     Mapped[Optional[str]] = mapped_column(String(100))
    account_status:    Mapped[str]           = mapped_column(String(20), nullable=False)
    synced_at:         Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("account_status IN ('Active','Inactive')", name="chk_account_status"),
    )

    tenant_roles: Mapped[List["AccountTenantRole"]] = relationship(
        "AccountTenantRole", back_populates="account", lazy="selectin"
    )
    login_events: Mapped[List["LoginEvent"]] = relationship(
        "LoginEvent",
        back_populates="account",
        primaryjoin="Account.account_id == foreign(LoginEvent.account_id)",
        viewonly=True,
    )

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(p for p in parts if p)


# ── Account Tenant Role ────────────────────────────────────────────────────

class AccountTenantRole(Base):
    __tablename__ = "account_tenant_role"

    role_id:           Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
    account_id:        Mapped[int]  = mapped_column(ForeignKey("account.account_id"), nullable=False)
    auth_external_id:  Mapped[str]  = mapped_column(String(255), nullable=False)
    tenant_id:         Mapped[int]  = mapped_column(ForeignKey("tenant.tenant_id"), nullable=False)
    position_id:       Mapped[int]  = mapped_column(ForeignKey("job_position.position_id"), nullable=False)
    is_primary_tenant: Mapped[bool] = mapped_column(Boolean, default=False)
    role_status:       Mapped[str]  = mapped_column(String(20), nullable=False)

    __table_args__ = (
        UniqueConstraint("account_id", "tenant_id", name="uq_account_tenant"),
        CheckConstraint("role_status IN ('Active','Inactive')", name="chk_role_status"),
    )

    account:  Mapped["Account"]     = relationship("Account",      back_populates="tenant_roles")
    tenant:   Mapped["Tenant"]      = relationship("Tenant",       back_populates="roles")
    position: Mapped["JobPosition"] = relationship("JobPosition",  back_populates="roles")


# ── Login Event ────────────────────────────────────────────────────────────

class LoginEvent(Base):
    __tablename__ = "login_event"

    event_id:         Mapped[int]           = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    account_id:       Mapped[int]           = mapped_column(Integer, nullable=False)
    auth_external_id: Mapped[str]           = mapped_column(String(255), nullable=False)
    role_id:          Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tenant_id:        Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    event_type:       Mapped[str]           = mapped_column(String(10), nullable=False)
    occurred_at:      Mapped[datetime]      = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("event_type IN ('LOGIN','LOGOUT')", name="chk_event_type"),
    )

    account: Mapped["Account"] = relationship(
        "Account",
        back_populates="login_events",
        primaryjoin="foreign(LoginEvent.account_id) == Account.account_id",
        viewonly=True,
    )


# ── Outbox (Transactional Outbox) ──────────────────────────────────────────

class Outbox(Base):
    """
    Written in the same DB transaction as every business change.
    The OutboxRelay worker picks these up and publishes them to RabbitMQ.
    """
    __tablename__ = "outbox"

    outbox_id:      Mapped[int]                = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tenant_id:      Mapped[int]                = mapped_column(Integer, nullable=False)
    aggregate_type: Mapped[str]                = mapped_column(String(100), nullable=False)
    aggregate_id:   Mapped[int]                = mapped_column(Integer, nullable=False)
    event_type:     Mapped[str]                = mapped_column(String(100), nullable=False)
    payload:        Mapped[dict]               = mapped_column(JSONB, nullable=False)
    created_at:     Mapped[datetime]           = mapped_column(DateTime, server_default=func.now())
    dispatched:     Mapped[bool]               = mapped_column(Boolean, default=False)
    dispatched_at:  Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    retry_count:    Mapped[int]                = mapped_column(Integer, default=0)
    last_attempted: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed:         Mapped[bool]               = mapped_column(Boolean, default=False)
    failure_reason: Mapped[Optional[str]]      = mapped_column(Text, nullable=True)
