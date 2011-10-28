PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE "gphq_gpdm" (
    "SCDM" varchar(1) NOT NULL,
    "GPDM" varchar(10) NOT NULL,
    "SCJC" varchar(2) NOT NULL,
    "GPMC" varchar(10) NOT NULL,
    "CODE" varchar(10) NOT NULL PRIMARY KEY
);
CREATE TABLE "gphq_rxhq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "JYRQ" date NOT NULL,
    "OPEN" integer NOT NULL,
    "HIGH" integer NOT NULL,
    "LOW" integer NOT NULL,
    "CLOSE" integer NOT NULL,
    "PCLOSE" integer NOT NULL,
    "PHIGH" integer NOT NULL,
    "PLOW" integer NOT NULL,
    "VOL" integer NOT NULL,
    "AMT" integer NOT NULL,
    "CHG" real NOT NULL,
    UNIQUE ("CODE", "JYRQ")
);
CREATE TABLE "gphq_fzhq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "JYRQ" date NOT NULL,
    "TJSD" varchar(4) NOT NULL,
    "OPEN" integer NOT NULL,
    "HIGH" integer NOT NULL,
    "LOW" integer NOT NULL,
    "CLOSE" integer NOT NULL,
    "VOL" integer NOT NULL,
    "AMT" integer NOT NULL
);
CREATE TABLE "gphq_zdrq" (
    "JYRQ" date NOT NULL PRIMARY KEY
);
INSERT INTO "gphq_zdrq" VALUES('1900-01-01');
CREATE TABLE "gphq_gprq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "JYRQ" date NOT NULL,
    UNIQUE ("CODE", "JYRQ")
);
CREATE TABLE "gphq_kzhq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "JYRQ" date NOT NULL,
    "OPEN" integer NOT NULL,
    "HIGH" integer NOT NULL,
    "LOW" integer NOT NULL,
    "CLOSE" integer NOT NULL,
    "PCLOSE" integer NOT NULL,
    "PHIGH" integer NOT NULL,
    "PLOW" integer NOT NULL,
    "VOL" integer NOT NULL,
    "AMT" integer NOT NULL,
    "AVG" integer NOT NULL,
    "CHG" real NOT NULL,
    "TOR" real NOT NULL,
    "SPV" integer NOT NULL,
    "OWN" integer NOT NULL,
    "VWN" integer NOT NULL,
    "SEL" integer NOT NULL,
    "SEC" integer NOT NULL,
    "TIM" real NOT NULL,
    "SIG" integer NOT NULL,
    UNIQUE ("CODE", "JYRQ")
);
CREATE TABLE "gphq_gbbq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "BGRQ" date NOT NULL,
    "TOTAL" integer NOT NULL,
    "FLOW" integer NOT NULL,
    "REAL" integer NOT NULL,
    UNIQUE ("CODE", "BGRQ")
);
CREATE TABLE "gphq_bkdm" (
    "BKDM" varchar(10) NOT NULL PRIMARY KEY,
    "BKMC" varchar(10) NOT NULL
);
CREATE TABLE "gphq_bkgp" (
    "id" integer NOT NULL PRIMARY KEY,
    "BKDM" varchar(10) NOT NULL,
    "CODE" varchar(10) NOT NULL,
    UNIQUE ("BKDM", "CODE")
);
CREATE TABLE "gphq_gnbk" (
    "id" integer NOT NULL PRIMARY KEY,
    "GNLX" varchar(10) NOT NULL,
    "BKDM" varchar(10) NOT NULL,
    UNIQUE ("GNLX", "BKDM")
);
CREATE INDEX "gphq_rxhq_ec2f0154" ON "gphq_rxhq" ("CODE");
CREATE INDEX "gphq_rxhq_28cc79d" ON "gphq_rxhq" ("JYRQ");
CREATE INDEX "gphq_fzhq_ec2f0154" ON "gphq_fzhq" ("CODE");
CREATE INDEX "gphq_fzhq_28cc79d" ON "gphq_fzhq" ("JYRQ");
CREATE INDEX "gphq_fzhq_9268833c" ON "gphq_fzhq" ("TJSD");
CREATE INDEX "gphq_kzhq_ec2f0154" ON "gphq_kzhq" ("CODE");
CREATE INDEX "gphq_kzhq_28cc79d" ON "gphq_kzhq" ("JYRQ");
CREATE INDEX "gphq_gbbq_ec2f0154" ON "gphq_gbbq" ("CODE");
CREATE INDEX "gphq_gbbq_a31cf595" ON "gphq_gbbq" ("BGRQ");
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
COMMIT;
