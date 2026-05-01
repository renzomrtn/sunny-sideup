\c project_db;

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
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'project_status_enum') THEN
        CREATE TYPE project_status_enum AS ENUM (
            'Pending', 'In Progress', 'Delayed', 
            'Expense Verification Pending', 'Expense Verification In Progress', 
            'Completed', 'Cancelled'
        );
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'committee_role_enum') THEN
        CREATE TYPE committee_role_enum AS ENUM ('Chairperson', 'Vice Chairperson', 'Member');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'task_status_enum') THEN
        CREATE TYPE task_status_enum AS ENUM ('Pending', 'In Progress', 'Delayed', 'Completed', 'Cancelled');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'priority_status_enum') THEN
        CREATE TYPE priority_status_enum AS ENUM ('Low', 'Medium', 'High');
    END IF;
END $$;

-- Project
CREATE TABLE IF NOT EXISTS Project (
    project_id          SERIAL          PRIMARY KEY,
    tenant_id           INT             NOT NULL,
    proponent_role_id   INT             NOT NULL,
    proponent_snapshot  JSONB           NOT NULL,
    line_item_id        INT             NOT NULL,
    line_item_snapshot  JSONB           NOT NULL,
    project_title       VARCHAR(255),
    date_started        DATE,
    date_accomplished   DATE,
    project_status      project_status_enum NOT NULL DEFAULT 'Pending'
);

-- Committee_Category
CREATE TABLE IF NOT EXISTS Committee_Category (
    committee_cat_id    SERIAL          PRIMARY KEY,
    tenant_id           INT             NOT NULL,
    category_name       VARCHAR(100)    NOT NULL,
    CONSTRAINT uq_committee_cat_per_tenant UNIQUE (tenant_id, category_name)
);

-- Project_Committee
CREATE TABLE IF NOT EXISTS Project_Committee (
    committee_id        SERIAL  PRIMARY KEY,
    project_id          INT     NOT NULL REFERENCES Project(project_id),
    committee_cat_id    INT     NOT NULL REFERENCES Committee_Category(committee_cat_id),
    CONSTRAINT uq_committee_per_project UNIQUE (project_id, committee_cat_id)
);

-- Committee_Member
CREATE TABLE IF NOT EXISTS Committee_Member (
    member_id           SERIAL          PRIMARY KEY,
    committee_id        INT             NOT NULL REFERENCES Project_Committee(committee_id),
    role_id             INT             NOT NULL,
    member_snapshot     JSONB           NOT NULL,
    committee_role      committee_role_enum NOT NULL,
    CONSTRAINT uq_person_per_committee UNIQUE (committee_id, role_id)
);

-- Project_Task
CREATE TABLE IF NOT EXISTS Project_Task (
    task_id          SERIAL          PRIMARY KEY,
    project_id       INT             NOT NULL REFERENCES Project(project_id),
    task_name        VARCHAR(255),
    due_date         DATE,
    task_status      task_status_enum     NOT NULL DEFAULT 'Pending',
    priority_status  priority_status_enum NOT NULL DEFAULT 'Low'
);

-- Project_Task_Assignment
CREATE TABLE IF NOT EXISTS Project_Task_Assignment (
    assignment_id    SERIAL  PRIMARY KEY,
    task_id          INT     NOT NULL REFERENCES Project_Task(task_id),
    member_id        INT     NOT NULL REFERENCES Committee_Member(member_id),
    CONSTRAINT uq_task_assignment UNIQUE (task_id, member_id)
);

-- Row Level Security
ALTER TABLE Project                 ENABLE ROW LEVEL SECURITY;
ALTER TABLE Committee_Category      ENABLE ROW LEVEL SECURITY;
ALTER TABLE Project_Committee       ENABLE ROW LEVEL SECURITY;
ALTER TABLE Committee_Member        ENABLE ROW LEVEL SECURITY;
ALTER TABLE Project_Task            ENABLE ROW LEVEL SECURITY;
ALTER TABLE Project_Task_Assignment ENABLE ROW LEVEL SECURITY;

CREATE POLICY rls_project ON Project
    USING (
        tenant_id = current_setting('app.current_tenant_id', TRUE)::INT
        OR current_setting('app.current_tenant_id', TRUE)::INT = 1
    );

CREATE POLICY rls_committee_category ON Committee_Category
    USING (
        tenant_id = current_setting('app.current_tenant_id', TRUE)::INT
        OR current_setting('app.current_tenant_id', TRUE)::INT = 1
    );

CREATE POLICY rls_project_committee ON Project_Committee
    USING (
        EXISTS (
            SELECT 1 FROM Project p
            WHERE p.project_id = Project_Committee.project_id
              AND (
                  p.tenant_id = current_setting('app.current_tenant_id', TRUE)::INT
                  OR current_setting('app.current_tenant_id', TRUE)::INT = 1
              )
        )
    );

CREATE POLICY rls_committee_member ON Committee_Member
    USING (
        EXISTS (
            SELECT 1 FROM Project_Committee pc
            JOIN Project p ON p.project_id = pc.project_id
            WHERE pc.committee_id = Committee_Member.committee_id
              AND (
                  p.tenant_id = current_setting('app.current_tenant_id', TRUE)::INT
                  OR current_setting('app.current_tenant_id', TRUE)::INT = 1
              )
        )
    );

CREATE POLICY rls_project_task ON Project_Task
    USING (
        EXISTS (
            SELECT 1 FROM Project p
            WHERE p.project_id = Project_Task.project_id
              AND (
                  p.tenant_id = current_setting('app.current_tenant_id', TRUE)::INT
                  OR current_setting('app.current_tenant_id', TRUE)::INT = 1
              )
        )
    );

CREATE POLICY rls_project_task_assignment ON Project_Task_Assignment
    USING (
        EXISTS (
            SELECT 1 FROM Project_Task pt
            JOIN Project p ON p.project_id = pt.project_id
            WHERE pt.task_id = Project_Task_Assignment.task_id
              AND (
                  p.tenant_id = current_setting('app.current_tenant_id', TRUE)::INT
                  OR current_setting('app.current_tenant_id', TRUE)::INT = 1
              )
        )
    );

-- Permissions
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO project_service;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO project_service;
