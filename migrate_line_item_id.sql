-- Migration: change project.line_item_id from INTEGER to VARCHAR(50)
-- Run this once against the project-service database before restarting services.
-- Safe to run even if already migrated (uses IF EXISTS / type check).

DO $$
BEGIN
  -- Only alter if the column is still an integer type
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'project'
      AND column_name = 'line_item_id'
      AND data_type IN ('integer', 'bigint', 'smallint')
  ) THEN
    ALTER TABLE project
      ALTER COLUMN line_item_id TYPE VARCHAR(50) USING line_item_id::text;
    RAISE NOTICE 'Migrated project.line_item_id to VARCHAR(50)';
  ELSE
    RAISE NOTICE 'project.line_item_id is already a string type — skipping';
  END IF;
END
$$;