BEGIN TRANSACTION;

DROP TABLE IF EXISTS "case" CASCADE;
DROP TABLE IF EXISTS "docket_entry" CASCADE;
DROP TABLE IF EXISTS "webhook_event" CASCADE;
DROP TABLE IF EXISTS "post" CASCADE;

CREATE TABLE "case" (
    id SERIAL PRIMARY KEY,
    court character varying(100) NOT NULL,
    case_number character varying(100) NOT NULL,
    bcb1_description character varying(200),
    cl_case_title text,
    cl_docket_id integer,
    in_bcb1 boolean DEFAULT FALSE
);

CREATE TABLE "docket_entry" (
    id SERIAL PRIMARY KEY,
    cl_docket_entry_id INTEGER,
    case_id INTEGER REFERENCES "case" ON DELETE CASCADE,
    entry_number INTEGER,
    pacer_sequence_number INTEGER
);

CREATE TABLE "webhook_event" (
    idempotency_key VARCHAR(100) PRIMARY KEY,
    received_at TIMESTAMP WITHOUT TIME ZONE
    -- TODO: Clear out idempotency keys after 55 hours (more than max. elapsed retries)
);

CREATE TABLE "post" (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES "case" ON DELETE RESTRICT,
    docket_entry_id INTEGER REFERENCES "docket_entry" ON DELETE RESTRICT,
    channel VARCHAR(100) NOT NULL,
    channel_post_id TEXT,
    "text" TEXT,
    posted_at TIMESTAMP WITHOUT TIME ZONE
);

COMMIT;
