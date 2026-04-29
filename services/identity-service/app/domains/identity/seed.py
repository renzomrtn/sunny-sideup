import os
import re
import sys
import time
import psycopg2
from psycopg2.extras import execute_values

# ── Resolve DB URL ────────────────────────────────────────────
_raw_url = os.getenv(
    "IDENTITY_DB_URL",
    "postgresql+asyncpg://postgres:YouthOutH@db:5432/identity_db",
)
DB_URL = re.sub(r"^postgresql\+asyncpg://", "postgresql://", _raw_url)

# ── Bootstrap admin config ────────────────────────────────────
ADMIN_AUTH_ID    = os.getenv("SEED_ADMIN_AUTH_ID",    "18f71d90-5003-4df1-a0b1-ff445e454f30")
ADMIN_FIRST_NAME = os.getenv("SEED_ADMIN_FIRST_NAME", "System")
ADMIN_LAST_NAME  = os.getenv("SEED_ADMIN_LAST_NAME",  "Administrator")
ADMIN_EMAIL      = os.getenv("SEED_ADMIN_EMAIL",      "sknaga.accadmin@gmail.com")


# ── Wait for schema (NEW) ─────────────────────────────────────
def wait_for_schema():
    print("\n⏳ Waiting for database schema to be ready...")

    for attempt in range(30):  # ~60 seconds max
        try:
            conn = psycopg2.connect(DB_URL)
            with conn.cursor() as cur:
                # Check if a required table exists AND is queryable
                cur.execute("SELECT 1 FROM tenant LIMIT 1;")
            conn.close()

            print("✓ Schema is ready.\n")
            return

        except Exception as e:
            print(f"  → Attempt {attempt + 1}: schema not ready yet...")
            time.sleep(2)

    raise RuntimeError("Database schema not ready after waiting.")


# ── Seed data ─────────────────────────────────────────────────
TENANTS: list[tuple[str, bool]] = [
    ("SK Federation", True),
    ("SK Abella", False),
    ("SK Bagumbayan Norte", False),
    ("SK Bagumbayan Sur", False),
    ("SK Balatas", False),
    ("SK Calauag", False),
    ("SK Cararayan", False),
    ("SK Carolina", False),
    ("SK Concepcion Grande", False),
    ("SK Concepcion Pequeña", False),
    ("SK Dayangdang", False),
    ("SK Del Rosario", False),
    ("SK Dinaga", False),
    ("SK Igualdad Interior", False),
    ("SK Lerma", False),
    ("SK Liboton", False),
    ("SK Mabolo", False),
    ("SK Pacol", False),
    ("SK Panicuason", False),
    ("SK Penafrancia", False),
    ("SK Sabang", False),
    ("SK San Felipe", False),
    ("SK San Francisco", False),
    ("SK San Isidro", False),
    ("SK Santa Cruz", False),
    ("SK Tabuco", False),
    ("SK Tinago", False),
    ("SK Triangulo", False),
]

JOB_POSITIONS: list[tuple[str, bool, bool]] = [
    ("SK Chairperson", True, False),
    ("SK Councilor", True, False),
    ("SK Secretary", True, False),
    ("SK Treasurer", True, False),
    ("SKF President", False, True),
    ("SKF Vice President", False, True),
    ("SKF Secretary", False, True),
    ("SKF Treasurer", False, True),
    ("SKF Auditor", False, True),
    ("SKF P.R.O.", False, True),
    ("SKF Sgt. at Arms", False, True),
    ("SKF Property Custodian", False, True),
    ("SKF Member", False, True),
    ("Chief of Staff", False, True),
    ("Administrative Aide", False, True),
    ("Account Management Administrator", False, True),
]


# ── Helpers ───────────────────────────────────────────────────
def log(msg: str) -> None:
    print(f"  → {msg}", flush=True)


def seed_tenants(cur) -> None:
    print("\n[1/4] Seeding tenant …")
    rows = [(name, is_fed, "Active") for name, is_fed in TENANTS]
    execute_values(
        cur,
        """
        INSERT INTO tenant (tenant_name, is_federation, tenant_status)
        VALUES %s
        ON CONFLICT (tenant_name) DO NOTHING
        """,
        rows,
    )
    log(f"{len(rows)} rows processed (duplicates skipped)")


def seed_job_positions(cur) -> None:
    print("\n[2/4] Seeding job_position …")
    execute_values(
        cur,
        """
        INSERT INTO job_position (position_name, is_barangay_sk_role, is_federation_role)
        VALUES %s
        ON CONFLICT (position_name) DO NOTHING
        """,
        JOB_POSITIONS,
    )
    log(f"{len(JOB_POSITIONS)} rows processed (duplicates skipped)")


def seed_admin_account(cur) -> int:
    print("\n[3/4] Upserting bootstrap account …")
    cur.execute(
        """
        INSERT INTO account (
            auth_external_id, identity_provider,
            first_name, last_name, contact_email, account_status
        )
        VALUES (%s, 'authentik', %s, %s, %s, 'Active')
        ON CONFLICT (auth_external_id) DO UPDATE
            SET first_name    = EXCLUDED.first_name,
                last_name     = EXCLUDED.last_name,
                contact_email = EXCLUDED.contact_email,
                synced_at     = NOW()
        RETURNING account_id
        """,
        (ADMIN_AUTH_ID, ADMIN_FIRST_NAME, ADMIN_LAST_NAME, ADMIN_EMAIL),
    )
    account_id = cur.fetchone()[0]
    log(f"account_id={account_id}  auth_external_id={ADMIN_AUTH_ID}")
    return account_id


def seed_admin_role(cur, account_id: int) -> None:
    print("\n[4/4] Assigning Account Management Administrator on SK Federation …")

    cur.execute("SELECT tenant_id FROM tenant WHERE tenant_name = 'SK Federation'")
    row = cur.fetchone()
    if not row:
        raise RuntimeError("'SK Federation' tenant not found — did seed_tenants() run?")
    tenant_id = row[0]

    cur.execute(
        "SELECT position_id FROM job_position WHERE position_name = 'Account Management Administrator'"
    )
    row = cur.fetchone()
    if not row:
        raise RuntimeError("'Account Management Administrator' not found — did seed_job_positions() run?")
    position_id = row[0]

    cur.execute(
        """
        INSERT INTO account_tenant_role (
            account_id, auth_external_id,
            tenant_id, position_id,
            is_primary_tenant, role_status
        )
        VALUES (%s, %s, %s, %s, TRUE, 'Active')
        ON CONFLICT (account_id, tenant_id) DO UPDATE
            SET position_id       = EXCLUDED.position_id,
                is_primary_tenant = EXCLUDED.is_primary_tenant,
                role_status       = EXCLUDED.role_status
        RETURNING role_id
        """,
        (account_id, ADMIN_AUTH_ID, tenant_id, position_id),
    )
    role_id = cur.fetchone()[0]
    log(f"role_id={role_id}  tenant_id={tenant_id}  position_id={position_id}")


# ── Entry point ───────────────────────────────────────────────
def main() -> None:
    print("=" * 60)
    print("identity_seed.py — seeding identity_db")
    print("=" * 60)
    print(f"  DB URL : {re.sub(r':([^:@]+)@', ':***@', DB_URL)}")

    # ✅ WAIT HERE FIRST
    wait_for_schema()

    try:
        conn = psycopg2.connect(DB_URL)
    except psycopg2.OperationalError as exc:
        print(f"\n✗ Cannot connect: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        with conn:
            with conn.cursor() as cur:
                seed_tenants(cur)
                seed_job_positions(cur)
                account_id = seed_admin_account(cur)
                seed_admin_role(cur, account_id)
    except Exception as exc:
        print(f"\n✗ Seed failed and was rolled back: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

    print("\n✓ Seed complete.\n")


if __name__ == "__main__":
    main()