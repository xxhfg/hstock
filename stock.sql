DROP TABLE "gphq_gpdm" ;
CREATE TABLE "gphq_gpdm" (
    "SCDM" varchar(1) NOT NULL,
    "GPDM" varchar(10) NOT NULL,
    "SCJC" varchar(2) NOT NULL,
    "GPMC" varchar(10) NOT NULL,
    "CODE" varchar(10) NOT NULL PRIMARY KEY
);

DROP TABLE "gphq_rxhq" ;
CREATE TABLE "gphq_rxhq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "JYRQ" date NOT NULL,
    "OPEN" real NOT NULL,
    "HIGH" real NOT NULL,
    "LOW" real NOT NULL,
    "CLOSE" real NOT NULL,
    "YCLOSE" real NOT NULL,
    "YHIGH" real NOT NULL,
    "YLOW" real NOT NULL,
    "VOL" real NOT NULL,
    "AMT" real NOT NULL,
    UNIQUE ("CODE", "JYRQ")
);

DROP TABLE "gphq_fzhq" ;
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
CREATE INDEX "gphq_rxhq_13d0feac" ON "gphq_rxhq" ("CODE");
CREATE INDEX "gphq_rxhq_28cc79d" ON "gphq_rxhq" ("JYRQ");
CREATE INDEX "gphq_fzhq_13d0feac" ON "gphq_fzhq" ("CODE");
CREATE INDEX "gphq_fzhq_28cc79d" ON "gphq_fzhq" ("JYRQ");
CREATE INDEX "gphq_fzhq_6d977cc4" ON "gphq_fzhq" ("TJSD");

DROP TABLE gphq_zdrq ;
CREATE TABLE gphq_zdrq (
    "JYRQ" DATE NOT NULL DEFAULT ('1900-01-01')
);
INSERT INTO gphq_zdrq values('1900-01-01');

-- Describe GPHQ_GPRQ
DROP TABLE "gphq_gprq" ;
CREATE TABLE "gphq_gprq" (
    "id" integer NOT NULL PRIMARY KEY,
    "CODE" varchar(10) NOT NULL,
    "JYRQ" date NOT NULL,
    UNIQUE ("CODE", "JYRQ")
);

-- Describe TRIGGER
--DROP TRIGGER "update_lastday";
CREATE TRIGGER "update_lastday"
   AFTER   INSERT 
   ON gphq_rxhq
   when (select count(*) from gphq_gprq where code=new.code)=1
BEGIN
    update gphq_gprq set jyrq=new.jyrq where code=new.code and jyrq<new.jyrq;
END;
--DROP TRIGGER "insert_lastday";
CREATE TRIGGER "insert_lastday"
   BEFORE   INSERT 
   ON gphq_rxhq
   when (select count(*) from gphq_gprq where code=new.code)=0
BEGIN
    insert into gphq_gprq(code, jyrq) values(new.code, new.jyrq);
END;
--DROP TRIGGER "update_maxday";
CREATE TRIGGER "update_maxday"
   AFTER   UPDATE OF JYRQ
   ON gphq_gprq
BEGIN
    update gphq_zdrq set jyrq=new.jyrq where jyrq<new.jyrq;
END;



