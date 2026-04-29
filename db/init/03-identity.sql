\c identity_db;

-- Outbox (Local Copy)
CREATE TABLE IF NOT EXISTS Outbox (
    outbox_id       BIGSERIAL       PRIMARY KEY,
    tenant_id       INT             NOT NULL,
    aggregate_type  VARCHAR(100)    NOT NULL,
    aggregate_id    INT             NOT NULL,
    event_type      VARCHAR(100)    NOT NULL,
    payload         JSONB           NOT NULL,
    created_at      TIMESTAMP       DEFAULT NOW(),
    dispatched      BOOLEAN         DEFAULT FALSE,
    dispatched_at   TIMESTAMP,
    retry_count     INT             DEFAULT 0,
    last_attempted  TIMESTAMP,
    failed          BOOLEAN         DEFAULT FALSE,
    failure_reason  TEXT
);

CREATE INDEX IF NOT EXISTS idx_outbox_undispatched
ON Outbox (dispatched, failed)
WHERE dispatched = FALSE AND failed = FALSE;

-- Enums
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tenant_name_enum') THEN
        CREATE TYPE tenant_name_enum AS ENUM (
            'SK Federation', 'SK Abella', 'SK Bagumbayan Norte', 'SK Bagumbayan Sur',
            'SK Balatas', 'SK Calauag', 'SK Cararayan', 'SK Carolina',
            'SK Concepcion Grande', 'SK Concepcion Pequeña', 'SK Dayangdang', 'SK Del Rosario',
            'SK Dinaga', 'SK Igualdad Interior', 'SK Lerma', 'SK Liboton',
            'SK Mabolo', 'SK Pacol', 'SK Panicuason', 'SK Penafrancia',
            'SK Sabang', 'SK San Felipe', 'SK San Francisco', 'SK San Isidro',
            'SK Santa Cruz', 'SK Tabuco', 'SK Tinago', 'SK Triangulo'
        );
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'job_position_enum') THEN
        CREATE TYPE job_position_enum AS ENUM (
            'SK Chairperson', 'SK Councilor', 'SK Secretary', 'SK Treasurer',
            'SKF President', 'SKF Vice President', 'SKF Secretary', 'SKF Treasurer',
            'SKF Auditor', 'SKF P.R.O.', 'SKF Sgt. at Arms', 'SKF Property Custodian',
            'SKF Member', 'Chief of Staff', 'Administrative Aide', 'Account Management Administrator'
        );
    END IF;
END $$;

-- Tenant
CREATE TABLE IF NOT EXISTS Tenant (
    tenant_id       SERIAL              PRIMARY KEY,
    tenant_name     tenant_name_enum    NOT NULL UNIQUE,
    is_federation   BOOLEAN             DEFAULT FALSE,
    tenant_status   VARCHAR(20)         NOT NULL
        CHECK (tenant_status IN ('Active', 'Inactive'))
);

-- Job_Position
CREATE TABLE IF NOT EXISTS Job_Position (
    position_id           SERIAL              PRIMARY KEY,
    position_name         job_position_enum   NOT NULL UNIQUE,
    is_barangay_sk_role   BOOLEAN             DEFAULT FALSE,
    is_federation_role    BOOLEAN             DEFAULT FALSE,

    CONSTRAINT job_position_check CHECK (
        (position_name::TEXT LIKE 'SK %' AND is_barangay_sk_role = TRUE AND is_federation_role = FALSE) 
        OR
        ((position_name::TEXT LIKE 'SKF %' OR 
          position_name::TEXT IN ('Chief of Staff', 'Administrative Aide', 'Account Management Administrator')) 
          AND is_federation_role = TRUE AND is_barangay_sk_role = FALSE)
    )
);

-- Account
CREATE TABLE IF NOT EXISTS Account (
    account_id        SERIAL          PRIMARY KEY,
    auth_external_id  VARCHAR(255)    NOT NULL UNIQUE,
    identity_provider VARCHAR(50)     NOT NULL DEFAULT 'authentik',
    first_name        VARCHAR(50),
    middle_name       VARCHAR(50),
    last_name         VARCHAR(50),
    contact_number    VARCHAR(20),
    contact_email     VARCHAR(100),
    account_status    VARCHAR(20)     NOT NULL
        CHECK (account_status IN ('Active', 'Inactive')),
    synced_at         TIMESTAMP       DEFAULT NOW()
);

-- Account_Tenant_Role
CREATE TABLE IF NOT EXISTS Account_Tenant_Role (
    role_id             SERIAL          PRIMARY KEY,
    account_id          INT             NOT NULL REFERENCES Account(account_id),
    auth_external_id    VARCHAR(255)    NOT NULL,
    tenant_id           INT             NOT NULL REFERENCES Tenant(tenant_id),
    position_id         INT             NOT NULL REFERENCES Job_Position(position_id),
    is_primary_tenant   BOOLEAN         DEFAULT FALSE,
    role_status         VARCHAR(20)     NOT NULL
        CHECK (role_status IN ('Active', 'Inactive')),
    CONSTRAINT uq_account_tenant UNIQUE (account_id, tenant_id)
);

-- Login_Event
CREATE TABLE IF NOT EXISTS Login_Event (
    event_id            BIGSERIAL       PRIMARY KEY,
    account_id          INT             NOT NULL,
    auth_external_id    VARCHAR(255)    NOT NULL,
    role_id             INT,
    tenant_id           INT,
    event_type          VARCHAR(10)     NOT NULL
        CHECK (event_type IN ('LOGIN', 'LOGOUT')),
    occurred_at         TIMESTAMP       DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_login_event_account ON Login_Event (account_id, occurred_at);

-- Row Level Security
ALTER TABLE Account_Tenant_Role ENABLE ROW LEVEL SECURITY;
ALTER TABLE Login_Event         ENABLE ROW LEVEL SECURITY;

CREATE POLICY rls_atr ON Account_Tenant_Role
    USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::INT);

CREATE POLICY rls_login_event ON Login_Event
    USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::INT);

-- Permissions
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO identity_service;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO identity_service;