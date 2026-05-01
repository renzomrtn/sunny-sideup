"""
One-time sync: matches identity_db accounts to Authentik users by email,
then updates auth_external_id to the Authentik uid (the JWT 'sub' value).
"""
import httpx
import asyncio
import asyncpg
import os

AUTHENTIK_URL   = "http://localhost:11000"
AUTHENTIK_TOKEN = "U2yxkbPYh6NjTIN8d43so48iH0ndxTHPkIbfVH1fBmgApkxbas3H6b9kloZD"
DB_DSN          = "postgresql://postgres:${POSTGRES_PASSWORD}@localhost:7432/identity_db"

async def fetch_all_authentik_users(client: httpx.AsyncClient) -> dict:
    """Returns {email: uid} for all Authentik users, paginating through all pages."""
    email_to_uid = {}
    page = 1
    while True:
        r = await client.get(
            f"{AUTHENTIK_URL}/api/v3/core/users/",
            params={"page_size": 100, "page": page},
            headers={"Authorization": f"Bearer {AUTHENTIK_TOKEN}"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        for user in data.get("results", []):
            email = user.get("email", "").strip().lower()
            uid   = user.get("uid", "")
            if email and uid:
                email_to_uid[email] = uid
        if not data.get("pagination", {}).get("next"):
            break
        page += 1
    return email_to_uid

async def main():
    async with httpx.AsyncClient() as client:
        print("Fetching Authentik users...")
        email_to_uid = await fetch_all_authentik_users(client)
        print(f"  Found {len(email_to_uid)} Authentik users with emails")

    dsn = DB_DSN.replace("${POSTGRES_PASSWORD}", os.environ.get("POSTGRES_PASSWORD", "postgres"))
    conn = await asyncpg.connect(dsn)

    rows = await conn.fetch("SELECT account_id, contact_email, auth_external_id FROM account")
    print(f"\n  Found {len(rows)} accounts in identity_db\n")

    updated = 0
    skipped = 0
    not_found = 0

    for row in rows:
        email      = (row["contact_email"] or "").strip().lower()
        current_id = row["auth_external_id"]
        account_id = row["account_id"]

        if not email:
            print(f"  [SKIP]    account_id={account_id} — no email")
            skipped += 1
            continue

        authentik_uid = email_to_uid.get(email)
        if not authentik_uid:
            print(f"  [MISSING] account_id={account_id} email={email} — not found in Authentik")
            not_found += 1
            continue

        if current_id == authentik_uid:
            print(f"  [OK]      account_id={account_id} email={email} — already correct")
            skipped += 1
            continue

        await conn.execute(
            "UPDATE account SET auth_external_id = $1 WHERE account_id = $2",
            authentik_uid, account_id
        )
        print(f"  [UPDATED] account_id={account_id} email={email}")
        print(f"            old: {current_id}")
        print(f"            new: {authentik_uid}")
        updated += 1

    await conn.close()
    print(f"\nDone. updated={updated}  skipped={skipped}  not_found={not_found}")

asyncio.run(main())
