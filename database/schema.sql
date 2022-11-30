BEGIN TRANSACTION;
DROP TABLE IF EXISTS "case";

CREATE TABLE "case" (
    id SERIAL PRIMARY KEY,
    court character varying(100) NOT NULL,
    case_number character varying(100) NOT NULL,
    bcb1_description character varying(200),
    cl_case_title text,
    cl_docket_id integer,
    in_bcb1 boolean DEFAULT FALSE
);

COMMIT;
