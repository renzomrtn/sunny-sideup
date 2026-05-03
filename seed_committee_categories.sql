-- Seed committee categories for all barangay tenants + federation (tenant_id 1-28)
-- Run against project_db after containers are up.
-- Uses INSERT ... ON CONFLICT DO NOTHING so it's safe to re-run.

\c project_db;

-- Standard SK committee categories (inserted for every tenant)
-- We use a cross-join of tenant IDs with category names.
-- Tenant IDs 1-28 match the seed order: 1=SK Federation, 2=SK Abella, etc.

DO $$
DECLARE
    tid INT;
    categories TEXT[] := ARRAY[
        'Executive',
        'Finance',
        'Logistics',
        'Marketing',
        'Creatives',
        'Technical',
        'Documentation',
        'Program',
        'Volunteer'
    ];
    cat TEXT;
BEGIN
    FOR tid IN 1..28 LOOP
        FOREACH cat IN ARRAY categories LOOP
            INSERT INTO committee_category (tenant_id, category_name)
            VALUES (tid, cat)
            ON CONFLICT (tenant_id, category_name) DO NOTHING;
        END LOOP;
    END LOOP;

    RAISE NOTICE 'Done seeding committee_category (% tenants × % categories)',
        28, array_length(categories, 1);
END
$$;