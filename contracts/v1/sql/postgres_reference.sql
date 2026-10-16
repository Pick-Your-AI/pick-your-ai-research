-- AI Builder v1.0 reference persistence; PostgreSQL 15+.
-- IMPORTANT: The JSON Schemas under ../schemas/ plus application semantic validation
-- must run before write. JSONB is transport-agnostic source of truth; these tables
-- do NOT replace strict JSON Schema, reference checks, compatibility or security gates.
-- Snapshot IDs and derived document IDs are globally stable and immutable.

CREATE SCHEMA IF NOT EXISTS ai_builder;

CREATE TABLE IF NOT EXISTS ai_builder.catalog_snapshots (
    id text PRIMARY KEY,
    revision bigint NOT NULL CHECK (revision > 0),
    captured_at timestamptz NOT NULL,
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ai_builder.dependency_graphs (
    id text PRIMARY KEY,
    revision bigint NOT NULL CHECK (revision > 0),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS ai_builder.rulesets (
    id text NOT NULL,
    version text NOT NULL,
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id, version)
);

CREATE TABLE IF NOT EXISTS ai_builder.pricebooks (
    id text PRIMARY KEY,
    revision bigint NOT NULL CHECK (revision > 0),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Every build revision is an immutable canonical BuildSnapshot JSON document.
-- Never store "live selections" in a separate mutable table; that would create
-- two conflicting configuration sources of truth. Materialized views are allowed.
CREATE TABLE IF NOT EXISTS ai_builder.build_revisions (
    build_id text NOT NULL,
    revision bigint NOT NULL CHECK (revision > 0),
    catalog_snapshot_id text NOT NULL REFERENCES ai_builder.catalog_snapshots(id),
    ruleset_id text NOT NULL,
    ruleset_version text NOT NULL,
    dependency_graph_id text NOT NULL REFERENCES ai_builder.dependency_graphs(id),
    dependency_graph_revision bigint NOT NULL CHECK (dependency_graph_revision > 0),
    pricebook_id text REFERENCES ai_builder.pricebooks(id),
    status text NOT NULL CHECK (status IN ('draft', 'validated', 'ready', 'deployed', 'archived')),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (build_id, revision),
    FOREIGN KEY (ruleset_id, ruleset_version) REFERENCES ai_builder.rulesets(id, version)
);

-- Current head is a pointer into immutable history. Lock head row to enforce CAS.
CREATE TABLE IF NOT EXISTS ai_builder.build_heads (
    build_id text PRIMARY KEY,
    current_revision bigint NOT NULL,
    updated_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (build_id, current_revision)
        REFERENCES ai_builder.build_revisions(build_id, revision)
);

-- Each result references the exact revision of the build that produced it.
CREATE TABLE IF NOT EXISTS ai_builder.compatibility_reports (
    id text PRIMARY KEY,
    build_id text NOT NULL,
    build_revision bigint NOT NULL,
    evaluated_at timestamptz NOT NULL,
    dependency_graph_id text NOT NULL REFERENCES ai_builder.dependency_graphs(id),
    dependency_graph_revision bigint NOT NULL,
    result text NOT NULL CHECK (result IN ('valid','invalid','indeterminate')),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    FOREIGN KEY (build_id, build_revision)
        REFERENCES ai_builder.build_revisions(build_id, revision)
);

CREATE TABLE IF NOT EXISTS ai_builder.resource_estimates (
    id text PRIMARY KEY,
    build_id text NOT NULL,
    build_revision bigint NOT NULL,
    generated_at timestamptz NOT NULL,
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    FOREIGN KEY (build_id, build_revision)
        REFERENCES ai_builder.build_revisions(build_id, revision)
);

CREATE TABLE IF NOT EXISTS ai_builder.cost_estimates (
    id text PRIMARY KEY,
    build_id text NOT NULL,
    build_revision bigint NOT NULL,
    pricebook_id text NOT NULL REFERENCES ai_builder.pricebooks(id),
    estimated_at timestamptz NOT NULL,
    coverage text NOT NULL CHECK (coverage IN ('complete','partial','unknown')),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    FOREIGN KEY (build_id, build_revision)
        REFERENCES ai_builder.build_revisions(build_id, revision)
);

CREATE TABLE IF NOT EXISTS ai_builder.quality_evaluation_runs (
    id text PRIMARY KEY,
    build_id text NOT NULL,
    build_revision bigint NOT NULL,
    completed_at timestamptz NOT NULL,
    status text NOT NULL CHECK (status IN ('passed','failed','incomplete')),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    FOREIGN KEY (build_id, build_revision)
        REFERENCES ai_builder.build_revisions(build_id, revision)
);

CREATE TABLE IF NOT EXISTS ai_builder.deployment_manifests (
    id text PRIMARY KEY,
    build_id text NOT NULL,
    build_revision bigint NOT NULL,
    compatibility_report_id text NOT NULL REFERENCES ai_builder.compatibility_reports(id),
    quality_run_id text NOT NULL REFERENCES ai_builder.quality_evaluation_runs(id),
    cost_estimate_id text NOT NULL REFERENCES ai_builder.cost_estimates(id),
    resource_estimate_id text NOT NULL REFERENCES ai_builder.resource_estimates(id),
    status text NOT NULL CHECK (status IN ('proposed','approved','rejected','deployed','rolled_back')),
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    created_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (build_id, build_revision)
        REFERENCES ai_builder.build_revisions(build_id, revision)
    -- Service must also check that each evidence document points to the SAME
    -- build_id/revision, all approvals are valid, and the rollout is authorized.
);

-- Transactional outbox: writes are atomic with head revision changes and
-- delivered at least once. Consumers dedupe by event ID/idempotency key.
CREATE TABLE IF NOT EXISTS ai_builder.event_outbox (
    id text PRIMARY KEY,
    event_type text NOT NULL,
    subject_type text NOT NULL,
    subject_id text NOT NULL,
    subject_revision bigint NOT NULL CHECK (subject_revision > 0),
    correlation_id text NOT NULL,
    idempotency_key text NOT NULL,
    body jsonb NOT NULL CHECK (jsonb_typeof(body) = 'object'),
    occurred_at timestamptz NOT NULL,
    processed_at timestamptz,
    UNIQUE (subject_type, subject_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS build_revisions_snapshot_gin
    ON ai_builder.build_revisions USING gin (body jsonb_path_ops);
CREATE INDEX IF NOT EXISTS catalog_snapshots_gin
    ON ai_builder.catalog_snapshots USING gin (body jsonb_path_ops);
CREATE INDEX IF NOT EXISTS compatibility_report_build_idx
    ON ai_builder.compatibility_reports (build_id, build_revision, evaluated_at DESC);
CREATE INDEX IF NOT EXISTS cost_estimate_build_idx
    ON ai_builder.cost_estimates (build_id, build_revision, estimated_at DESC);
CREATE INDEX IF NOT EXISTS event_outbox_unprocessed_idx
    ON ai_builder.event_outbox (occurred_at) WHERE processed_at IS NULL;

-- CAS example (execute in one transaction; app checks row count == 1):
-- BEGIN;
-- SELECT current_revision FROM ai_builder.build_heads WHERE build_id = :id FOR UPDATE;
-- ASSERT returned revision == :expected_revision (otherwise rollback / HTTP 409);
-- INSERT INTO ai_builder.build_revisions (... revision = :expected_revision+1, ...);
-- UPDATE ai_builder.build_heads SET current_revision = :expected_revision+1,
--        updated_at = now()
--   WHERE build_id = :id AND current_revision = :expected_revision;
-- INSERT INTO ai_builder.event_outbox (...);
-- COMMIT;

-- To enforce immutability, grant application roles INSERT and SELECT (not UPDATE
-- or DELETE) on revision/quote/ruleset tables. The exception is mutable head
-- pointers, mutable outbox delivery state, and approval workflows with audited
-- state transitions. Application-specific RLS and tenancy are required.
