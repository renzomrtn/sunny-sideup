\c cms_db;

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

-- CMS_Publication
CREATE TABLE IF NOT EXISTS CMS_Publication (
    publication_id          SERIAL          PRIMARY KEY,
    tenant_id               INT             NOT NULL,

    -- Cross-db references
    ref_archive_id          INT,
    ref_line_item_id        INT,
    ref_expenditure_id      INT,

    content_snapshot        JSONB           NOT NULL,

    -- Computed content type
    content_type            VARCHAR(50) GENERATED ALWAYS AS (
        CASE
            WHEN ref_archive_id     IS NOT NULL THEN 'archive'
            WHEN ref_line_item_id   IS NOT NULL THEN 'line_item'
            WHEN ref_expenditure_id IS NOT NULL THEN 'expenditure'
        END
    ) STORED,

    scheduled_at            TIMESTAMP,
    status                  VARCHAR(20)     NOT NULL 
        CHECK (status IN ('to_publish', 'scheduled', 'published', 'unpublished'))
        DEFAULT 'to_publish',
    published_at            TIMESTAMP,
    published_by_role_id    INT,
    published_by_snapshot   JSONB,
    unpublished_at          TIMESTAMP,
    unpublished_by_role_id  INT,
    unpublished_by_snapshot JSONB,

    CONSTRAINT chk_exactly_one_ref CHECK (
        (ref_archive_id     IS NOT NULL)::INT +
        (ref_line_item_id   IS NOT NULL)::INT +
        (ref_expenditure_id IS NOT NULL)::INT = 1
    )
);

CREATE INDEX IF NOT EXISTS idx_cms_tenant_status  ON CMS_Publication (tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_cms_archive        ON CMS_Publication (ref_archive_id) WHERE ref_archive_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cms_line_item      ON CMS_Publication (ref_line_item_id) WHERE ref_line_item_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cms_expenditure    ON CMS_Publication (ref_expenditure_id) WHERE ref_expenditure_id IS NOT NULL;

-- Site_Settings
CREATE TABLE IF NOT EXISTS Site_Settings (
    setting_id              SERIAL          PRIMARY KEY,
    setting_key             VARCHAR(50)     NOT NULL 
        CHECK (setting_key IN (
            'city_logo', 'admin_brand', 'sk_logo',
            'sk_email', 'sk_contact', 'facebook_url'
        )),
    setting_value           TEXT,
    file_ref_id             INT,            -- reference to file_db
    last_updated            TIMESTAMP       DEFAULT NOW(),
    updated_by_role_id      INT,
    updated_by_snapshot     JSONB,
    CONSTRAINT uq_setting_key UNIQUE (setting_key)
);

-- Row Level Security
ALTER TABLE CMS_Publication ENABLE ROW LEVEL SECURITY;
ALTER TABLE Site_Settings   ENABLE ROW LEVEL SECURITY;

CREATE POLICY rls_cms_publication ON CMS_Publication
    USING (tenant_id = current_setting('app.current_tenant_id', TRUE)::INT);

-- Permissions
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO cms_service;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO cms_service;