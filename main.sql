/*
Navicat SQLite Data Transfer

Source Server         : stock
Source Server Version : 30706
Source Host           : :0

Target Server Type    : SQLite
Target Server Version : 30706
File Encoding         : 65001

Date: 2011-11-04 01:55:31
*/

PRAGMA foreign_keys = OFF;

-- ----------------------------
-- Records of gphq_zdrq
-- ----------------------------
DELETE FROM "main"."gphq_zdrq";
INSERT INTO "main"."gphq_zdrq" VALUES ('1900-01-01');

-- ----------------------------
-- Triggers structure for table "main"."gphq_gprq"
-- ----------------------------
DROP TRIGGER IF EXISTS "main"."update_maxday";
DELIMITER ;;
CREATE TRIGGER "update_maxday"
   AFTER   UPDATE OF JYRQ
   ON gphq_gprq
BEGIN
    update gphq_zdrq set jyrq=new.jyrq where jyrq<new.jyrq;
END
;;
DELIMITER ;

-- ----------------------------
-- Triggers structure for table "main"."gphq_rxhq"
-- ----------------------------
DROP TRIGGER IF EXISTS "main"."insert_lastday";
DELIMITER ;;
CREATE TRIGGER "insert_lastday" AFTER INSERT ON "gphq_rxhq"
   when (select count(*) from gphq_gprq where code=new.code)=0
BEGIN
    insert into gphq_gprq(code, jyrq) values(new.code, new.jyrq);
END
;;
DELIMITER ;
DROP TRIGGER IF EXISTS "main"."update_lastday";
DELIMITER ;;
CREATE TRIGGER "update_lastday" AFTER INSERT ON "gphq_rxhq"
   when (select count(*) from gphq_gprq where code=new.code)>0
BEGIN
    update gphq_gprq set jyrq=new.jyrq where code=new.code and jyrq<new.jyrq;
END
;;
DELIMITER ;
