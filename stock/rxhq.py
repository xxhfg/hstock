#!/usr/bin/python
# -*-  coding: UTF8 -*- 

import config
import sys
sys.path.append(config.PROJECT_HOME) #先要把自己的项目目录加入path
from django.core.management import setup_environ #这是重头戏，全靠它了
from stock import settings #介绍自已人
setup_environ(settings) #安排自己人
#干活去吧
import os
import string
import time
import datetime
import numpy
from stock.gphq import models
from django.db import connection, transaction
from workmanager import * 

def do_job2(args):
    """处理通达信五分钟数据"""
    global g_mutex
    global max_day
    global lastdays
    global records
    global gpdms
    recs = []

    if (len(args)==0):
        return False

    filepath = args[0]
    filename = os.path.basename(filepath).upper()

    if not os.path.isfile(filepath):
        return False

    scjc = filename[0:2]
    scdm = '0' if scjc == 'SZ' else '1'
    gpdm = filename[2:8]
    code = scdm + gpdm
    if not (code in gpdms):
        return False

    last_day = lastdays[code] if code in lastdays else datetime.date(1900, 1, 1)

    dayline = numpy.fromfile(open(filepath, 'rb'), 'i')
    dm = numpy.fromfile(open(filepath, 'rb'), 'f')

    j = len(dayline)
    i = 0
    opn = 0
    high = 0
    low = 0
    close = 0
    prec = 0
    preh = 0
    prel = 0
    vol = 0
    amt = 0
    yvol = 0
    yamt = 0
    i = 0
    for k in range( -j, -7, 8):
        mins = (dayline[k] >> 16) & 0xffff
        mds  = dayline[k] & 0xffff
        year = mds / 100 / 12 + 2000 - 1
        month = mds / 100 % 12 + 1
        day   = mds % 100 - 36
        hour = int(mins / 60)
        minute = mins % 60

        cday = datetime.date(year, month, day)
        #print cday, hour, minute
        #print dayline[k], dm[k], dm[k+1], dm[k+2], dm[k+3], dm[k+4], dm[k+5], dm[k+6], dayline[k+6]
        if (cday > last_day):
            if k == -j:
                sday = cday
                preh = dm[k + 2] * 100
                prel = dm[k + 3] * 100
                prec = dm[k + 4] * 100

            if  ((cday <> sday) and (opn > 0)):
                record = {}
                record['CODE'] = code
                record['JYRQ'] = sday
                record['OPEN'] = opn * 100  #以分为单位
                record['HIGH'] = high * 100 #以分为单位
                record['LOW'] = low * 100 #以分为单位
                record['CLOSE'] = close * 100 #以分为单位
                record['PCLOSE'] = prec * 100 #以分为单位
                record['PHIGH'] = preh * 100 #以分为单位
                record['PLOW'] = prel * 100 #以分为单位
                record['VOL'] = vol #以股为单位
                record['AMT'] = amt * 100 #以分为单位
                record['CHG'] = round(((close * 1.0) / (prec * 1.0) - 1) * 100,
                                      2) * 100
                #print record
                #print vol, yvol, amt, yamt, 1.0*yvol/vol, yamt/amt
                recs.append(record)

                sday = cday
                prec = close
                preh = high
                prel = low
                opn = 0
                high = 0
                low = 0
                close = 0
                vol = 0
                amt = 0
                yvol = 0
                yamt = 0
                i = 0
            
            #股票价格改为以分为单位,便于计算
            if ((hour==9) and (minute==35)):
                opn = dm[k + 1]
                high = dm[k + 2]
                low = dm[k + 3]

            chg = round((dm[k + 2] / dm[k + 3] - 1) * 100, 2)
            if (abs(chg) >= 1):
                i += 1
                yamt += dm[k + 5]
                yvol += dayline[k + 6]

            if ((hour==15) and (minute==0)):
                close = dm[k + 4]

            if (high < dm[k + 2]):
                high = dm[k + 2]

            if (low > dm[k + 3]):
                low = dm[k + 3]


            amt += dm[k + 5]
            vol += dayline[k + 6]


    g_mutex.acquire()
    print u"正在处理 %s 市场 %s 股票......" % (scjc, code)
    for rec in recs:
        records.append(rec)
    print "共处理 %4d 条记录" % (len(recs))
    g_mutex.release()
    
#具体要做的任务  
# @transaction.commit_on_success
# @transaction.commit_manually
def do_job(args):  
    global g_mutex
    global max_day
    global lastdays
    global records
    global gpdms
    recs = []

    if (len(args)==0):
        return False

    filepath = args[0]
    filename = os.path.basename(filepath).upper()

    if not os.path.isfile(filepath):
        return False

    scjc = filename[0:2]
    scdm = '0' if scjc == 'SZ' else '1'
    gpdm = filename[2:8]
    code = scdm + gpdm
    if not (code in gpdms):
        return False

    last_day = lastdays[code] if code in lastdays else datetime.date(1900, 1, 1)

    dayline = numpy.fromfile(open(filepath, 'rb'), 'i')
    dm = numpy.fromfile(open(filepath, 'rb'), 'f')
    j = len(dayline)
    i = 0
    for k in range( -j, -7, 8):
        sday = str(dayline[k])
        day = datetime.date(string.atoi(sday[0:4]), string.atoi(sday[4:6]), string.atoi(sday[6:8]))
        if (day > last_day):
            if k == -j: #第一条数据
            #股票价格改为以分为单位,便于计算
                prec = dayline[k + 1] #以开盘价做为前日收盘价
                preh = dayline[k + 2] #以最高价做为前日最高价
                prel = dayline[k + 3] #以最低价做为前日最低价
            	"""
                prec = dayline[k + 1] / 100.0 #以开盘价做为前日收盘价
                preh = dayline[k + 2] / 100.0 #以最高价做为前日最高价
                prel = dayline[k + 3] / 100.0 #以最低价做为前日最低价
            	"""
            else:
                prec = dayline[k - 4]  #前日收盘价
                preh = dayline[k - 6]  #前日最高价
                prel = dayline[k - 5]  #前日最低价
            	"""
                prec = dayline[k - 4] / 100.0 #前日收盘价
                preh = dayline[k - 6] / 100.0 #前日最高价
                prel = dayline[k - 5] / 100.0 #前日最低价
            	"""

            #股票价格改为以分为单位,便于计算
            opn = dayline[k + 1] 
            high = dayline[k + 2] 
            low = dayline[k + 3] 
            close = dayline[k + 4] 
            amt = dm[k + 5] * 100   #以分为单位
            vol = dayline[k + 6] #以股为单位
            """
            opn = dayline[k + 1] / 100.0 #换算成元
            high = dayline[k + 2] / 100.0 #换算成元
            low = dayline[k + 3] / 100.0 #换算成元
            close = dayline[k + 4] / 100.0 #换算成元
            amt = dm[k + 5]    #换算成元
            vol = dayline[k + 6] #换算成股
            """

            record = {}
            record['CODE'] = code
            record['JYRQ'] = day
            record['OPEN'] = opn
            record['HIGH'] = high
            record['LOW'] = low
            record['CLOSE'] = close
            record['PCLOSE'] = prec
            record['PHIGH'] = preh
            record['PLOW'] = prel
            record['VOL'] = vol
            record['AMT'] = amt
            record['CHG'] = round(((close * 1.0) / (prec * 1.0) - 1) * 100, 2)
            recs.append(record)
            i += 1

    g_mutex.acquire()
    print u"正在处理 %s 市场 %s 股票......" % (scjc, code)
    # gpdms.append(gp)
    for rec in recs:
        records.append(rec)
    print "共处理 %4d 条记录" % (i)
    g_mutex.release()


@transaction.commit_on_success
def save_rxhq():
    global records

    for rec in records:
        print u"正在处理 %s 股票 %s 日数据......" % (rec['CODE'], str(rec['JYRQ'])[0:10])
        rxhq = models.RXHQ(CODE=rec['CODE'], JYRQ=rec['JYRQ'],
                           OPEN=rec['OPEN'], HIGH=rec['HIGH'], LOW=rec['LOW'],
                           CLOSE=rec['CLOSE'], PCLOSE=rec['PCLOSE'],
                           PHIGH=rec['PHIGH'], PLOW=rec['PLOW'],
                           VOL=rec['VOL'], AMT=rec['AMT'], CHG = rec['CHG'])
        rxhq.save()

@transaction.commit_on_success
def save_gpdm():
    global gpdms

    for gp in gpdms:
        print u"正在处理 %s 市场 %s 股票......" % (gp['SCJC'], gp['CODE'])
        gpdm = models.GPDM(SCDM=gp['SCDM'], GPDM=gp['GPDM'], SCJC=gp['SCJC'], CODE=gp['CODE'], GPMC=gp['GPMC'])
        gpdm.save()

def main1():
    """处理通达信日线数据"""
    global g_mutex
    global max_day
    global lastdays
    global records
    global gpdms

    # from singleinstance import * 
    g_mutex = threading.Lock()
    records = []
    gpdms = []

    start = time.time()  
    """
    cursor = connection.cursor()
    cursor.execute('delete from gphq_fzhq')
    cursor.execute('delete from gphq_rxhq')
    cursor.execute('delete from gphq_zdrq')
    cursor.execute('delete from gphq_gprq')
    cursor.execute('insert into gphq_zdrq values("1900-01-01")')
    transaction.commit_unless_managed()
    """

    # models.GPDM.objects.all().delete()
    # models.FZHQ.objects.all().delete()
    # models.RXHQ.objects.all().delete()
    gps = models.GPDM.objects.all()
    for gp in gps:
        gpdms.append(gp.CODE)

    days = models.ZDRQ.objects.all()
    if (len(days) > 1):
        exit
    max_day = days[0].JYRQ

    days = models.GPRQ.objects.all()
    lastdays = {}
    for day in days:
        lastdays[day.CODE] = day.JYRQ

    print config.SH_LDAY_HOME
    files = os.listdir(config.SH_LDAY_HOME)
    sh_files = []
    for f in files:
        sh_files.append(config.SH_LDAY_HOME + f)

    work_manager =  WorkManager(sh_files, do_job, 10)#或者work_manager =  WorkManager(10000, 20)  
    work_manager.wait_allcomplete()  
    save_rxhq()
    records = []

    print config.SZ_LDAY_HOME
    files = os.listdir(config.SZ_LDAY_HOME)
    sz_files = []
    for f in files:
        sz_files.append(config.SZ_LDAY_HOME + f)

    work_manager =  WorkManager(sz_files, do_job, 10)#或者work_manager =  WorkManager(10000, 20)  
    work_manager.wait_allcomplete()  

    save_rxhq()
    records = []

    end = time.time()  
    print end - start
    

def main2():
    """处理通达信五分钟数据"""
    global g_mutex
    global max_day
    global lastdays
    global records
    global gpdms

    # from singleinstance import * 
    g_mutex = threading.Lock()
    records = []
    gpdms = []

    start = time.time()  
    cursor = connection.cursor()
    cursor.execute('delete from gphq_fzhq')
    cursor.execute('delete from gphq_rxhq')
    cursor.execute('delete from gphq_zdrq')
    cursor.execute('delete from gphq_gprq')
    cursor.execute('insert into gphq_zdrq values("1900-01-01")')
    transaction.commit_unless_managed()

    # models.GPDM.objects.all().delete()
    # models.FZHQ.objects.all().delete()
    # models.RXHQ.objects.all().delete()
    gps = models.GPDM.objects.all()
    for gp in gps:
        gpdms.append(gp.CODE)

    days = models.ZDRQ.objects.all()
    if (len(days) > 1):
        exit
    max_day = days[0].JYRQ

    days = models.GPRQ.objects.all()
    lastdays = {}
    for day in days:
        lastdays[day.CODE] = day.JYRQ

    print config.SH_LINE_HOME
    files = os.listdir(config.SH_LINE_HOME)
    sh_files = []
    for f in files:
        sh_files.append(config.SH_LINE_HOME + f)

    work_manager =  WorkManager(sh_files, do_job2, 10)#或者work_manager =  WorkManager(10000, 20)  
    work_manager.wait_allcomplete()  
    save_rxhq()
    records = []

    print config.SZ_LINE_HOME
    files = os.listdir(config.SZ_LINE_HOME)
    sz_files = []
    for f in files:
        sz_files.append(config.SZ_LINE_HOME + f)

    work_manager =  WorkManager(sz_files, do_job2, 10)#或者work_manager =  WorkManager(10000, 20)  
    work_manager.wait_allcomplete()  

    save_rxhq()
    records = []

    end = time.time()  
    print end - start

if __name__ == '__main__':  
    #do_job2([config.SZ_LINE_HOME + '/sz000001.lc5', ])
    main1()
