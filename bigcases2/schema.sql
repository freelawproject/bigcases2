BEGIN TRANSACTION;
DROP TABLE IF EXISTS "cases";
CREATE TABLE IF NOT EXISTS "cases" (
	"case_id"	INTEGER NOT NULL,
	"court"	TEXT NOT NULL,
	"case_number"	TEXT NOT NULL,
	"bcb1_description"	TEXT,
	"cl_case_title"	TEXT,
	"cl_docket_id"	INTEGER,
	"in_bcb1"	INTEGER NOT NULL DEFAULT 0,
	PRIMARY KEY("case_id" AUTOINCREMENT)
);
COMMIT;
