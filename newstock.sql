CREATE TABLE "gphq_gpdm" (
    "SCDM" varchar(1) NOT NULL,
    "GPDM" varchar(10) NOT NULL,
    "SCJC" varchar(2) NOT NULL,
    "GPMC" varchar(10) NOT NULL,
    "CODE" varchar(10) NOT NULL PRIMARY KEY
);
;
CREATE TABLE "gphq_fzhq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "JYRQ" date NOT NULL,
    "TJSD" varchar(4) NOT NULL,
    "OPEN" real NOT NULL,
    "HIGH" real NOT NULL,
    "LOW" real NOT NULL,
    "CLOSE" real NOT NULL,
    "VOL" real NOT NULL,
    "AMT" real NOT NULL
);
CREATE INDEX "gphq_fzhq_13d0feac" ON "gphq_fzhq" ("CODE");
CREATE INDEX "gphq_fzhq_28cc79d" ON "gphq_fzhq" ("JYRQ");
CREATE INDEX "gphq_fzhq_6d977cc4" ON "gphq_fzhq" ("TJSD");
CREATE TABLE gphq_zdrq (
    "JYRQ" DATE NOT NULL DEFAULT ('1900-01-01')
);
CREATE TABLE "gphq_gprq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "JYRQ" date NOT NULL,
    UNIQUE ("CODE", "JYRQ")
);
;
CREATE TABLE "gphq_gbbq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "BGRQ" date NOT NULL,
    "TOTAL" real NOT NULL,
    "FLOW" real NOT NULL,
    "REAL" real NOT NULL,
    UNIQUE ("CODE", "BGRQ")
);
;
CREATE INDEX "gphq_gbbq_13d0feac" ON "gphq_gbbq" ("CODE");
CREATE INDEX "gphq_gbbq_5ce30a6b" ON "gphq_gbbq" ("BGRQ");
CREATE TABLE "gphq_kzhq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "JYRQ" date NOT NULL,
    "OPEN" real NOT NULL,
    "HIGH" real NOT NULL,
    "LOW" real NOT NULL,
    "CLOSE" real NOT NULL,
    "PCLOSE" real NOT NULL,
    "PHIGH" real NOT NULL,
    "PLOW" real NOT NULL,
    "VOL" real NOT NULL,
    "AMT" real NOT NULL,
    "CHG" real NOT NULL,
    "TOR" real NOT NULL,
    "AVG" real NOT NULL,
    "SPV" real NOT NULL,
    UNIQUE ("CODE", "JYRQ")
);
;
CREATE INDEX "gphq_kzhq_13d0feac" ON "gphq_kzhq" ("CODE");
CREATE INDEX "gphq_kzhq_28cc79d" ON "gphq_kzhq" ("JYRQ");
CREATE TABLE "gphq_bkdm" (
    "BKDM" varchar(10) NOT NULL PRIMARY KEY,
    "BKMC" varchar(10) NOT NULL
);
;
CREATE TABLE "gphq_bkgp" (
    "id" integer NOT NULL PRIMARY KEY,
    "BKDM" varchar(10) NOT NULL,
    "CODE" varchar(10) NOT NULL,
    UNIQUE ("BKDM", "CODE")
);
;
CREATE TABLE "gphq_gnbk" (
    "id" integer NOT NULL PRIMARY KEY,
    "GNLX" varchar(10) NOT NULL,
    "BKDM" varchar(10) NOT NULL,
    UNIQUE ("GNLX", "BKDM")
);
;
CREATE TABLE "gphq_rxhq" (
    "id" INTEGER NOT NULL,
    "CODE" VARCHAR(10) NOT NULL,
    "JYRQ" DATE NOT NULL,
    "OPEN" REAL NOT NULL,
    "HIGH" REAL NOT NULL,
    "LOW" REAL NOT NULL,
    "CLOSE" REAL NOT NULL,
    "PCLOSE" REAL NOT NULL,
    "PHIGH" REAL NOT NULL,
    "PLOW" REAL NOT NULL,
    "VOL" REAL NOT NULL,
    "AMT" REAL NOT NULL
);
CREATE TRIGGER "update_lastday"
   AFTER   INSERT 
   ON gphq_rxhq
   when (select count(*) from gphq_gprq where code=new.code)=1
BEGIN
    update gphq_gprq set jyrq=new.jyrq where code=new.code and jyrq<new.jyrq;
END;
CREATE TRIGGER "insert_lastday"
   BEFORE   INSERT 
   ON gphq_rxhq
   when (select count(*) from gphq_gprq where code=new.code)=0
BEGIN
    insert into gphq_gprq(code, jyrq) values(new.code, new.jyrq);
END;
CREATE TRIGGER "update_maxday"
   AFTER   UPDATE OF JYRQ
   ON gphq_gprq
BEGIN
    update gphq_zdrq set jyrq=new.jyrq where jyrq<new.jyrq;
END;