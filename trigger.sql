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
