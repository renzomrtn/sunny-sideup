\c eventing_db;

-- Service_Integration
CREATE TABLE IF NOT EXISTS Service_Integration (
    integration_id  SERIAL PRIMARY KEY,
    local_table     VARCHAR(100) NOT NULL,
    local_id        INT NOT NULL,
    service_name    VARCHAR(100) NOT NULL,
    external_id     VARCHAR(255) NOT NULL,
    synced_at       TIMESTAMP DEFAULT NOW(),
    CONSTRAINT uq_service_record UNIQUE (local_table, local_id, service_name)
);

-- Inbound_Event
CREATE TABLE IF NOT EXISTS Inbound_Event (
    inb_event_id BIGSERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    external_id VARCHAR(255),
    payload JSONB,
    received_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    retry_count INT DEFAULT 0,
    last_attempted TIMESTAMP,
    failed BOOLEAN DEFAULT FALSE,
    failure_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_inbound_unprocessed
ON Inbound_Event (processed, failed)
WHERE processed = FALSE AND failed = FALSE;

-- Outbox
CREATE TABLE IF NOT EXISTS Outbox (
    outbox_id BIGSERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id INT NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    dispatched BOOLEAN DEFAULT FALSE,
    dispatched_at TIMESTAMP,
    retry_count INT DEFAULT 0,
    last_attempted TIMESTAMP,
    failed BOOLEAN DEFAULT FALSE,
    failure_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_outbox_undispatched
ON Outbox (dispatched, failed)
WHERE dispatched = FALSE AND failed = FALSE;

-- Domain_Event
CREATE TABLE IF NOT EXISTS Domain_Event (
    dom_event_id BIGSERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id INT NOT NULL,
    triggered_by_role_id INT,
    triggered_by_snapshot JSONB,
    payload JSONB,
    occurred_at TIMESTAMP DEFAULT NOW(),
    processed BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP,
    failed BOOLEAN DEFAULT FALSE,
    failure_reason TEXT
);

CREATE INDEX IF NOT EXISTS idx_domain_event_type
ON Domain_Event (event_type);

CREATE INDEX IF NOT EXISTS idx_domain_event_agg
ON Domain_Event (aggregate_type, aggregate_id);

CREATE INDEX IF NOT EXISTS idx_domain_event_tenant
ON Domain_Event (tenant_id);

CREATE INDEX IF NOT EXISTS idx_domain_event_unproc
ON Domain_Event (processed)
WHERE processed = FALSE;

GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO eventing_service;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO eventing_service;