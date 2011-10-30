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

def stats(data):
    """计算均价和方差"""
    if (len(data) <= 1): return (0, 0)

    sum = 0.0
    for value in data:
        sum += value
    mean = sum/len(data)
    sum = 0.0
    for value in data:
        sum += (value - mean)**2
    variance = sum/(len(data) - 1)
    return (mean, variance)

def all_down(data):
    """计算数据连续下降次数"""
    if (len(data) <= 1): return 0

    start = 0
    i = 0
    for value in data:
        if (start > value):
            i += 1
        start = value
    return i

def do_job(args):
    global g_mutex
    global records
    # global rxhqs, gbbqs

    if (len(args)==0):
        return False

    code = args[0]
    print "正在处理 %4s 股票......" % (code.encode('UTF8'))
    rxhqs = models.RXHQ.objects.filter(CODE=code)
    gbbqs = models.GBBQ.objects.filter(CODE=code)

    if (len(gbbqs)==0):
        return False

    latest_gbbq = gbbqs[0]
    recs = []
    pratio = 0
    data = []
    vars = []
    tors = [] #近五日换手率
    p_tors = [] #近十日换手率
    v_tors = []
    pown = 0
    ptor = 0
    avg_close = 0
    sel_close = 0
    chg_c = 0
    kk = 0
    for rxhq in rxhqs:
        rec = {}
        #rec['TOTAL'] = latest_gbbq.TOTAL #最新总股本
        rec['TOTAL'] = latest_gbbq.REAL #最新实际流通股本
        rec['REAL'] = latest_gbbq.REAL #当日实际流通股本
        rec['FLOW'] = latest_gbbq.FLOW #当日流通股
        rec['TOR'] = round(100.0 * rxhq.VOL / latest_gbbq.REAL, 4) if latest_gbbq.REAL > 0 else round(100.0 * rxhq.VOL / latest_gbbq.TOTAL, 4)
        for gbbq in gbbqs:
            if (rxhq.JYRQ >= gbbq.BGRQ):
                #rec['REAL'] = gbbq.TOTAL #当日总股本
                #rec['FLOW'] = gbbq.REAL #当日流通股
                rec['REAL'] = gbbq.REAL #当日实际流通股本
                rec['FLOW'] = gbbq.FLOW #当日流通股
                rec['TOR'] = round(100.0 * rxhq.VOL / gbbq.REAL, 4) if gbbq.REAL > 0 else round(100.0 * rxhq.VOL / gbbq.TOTAL, 4)
                # print gbbq.REAL
                # print rxhq.VOL
                break
                
        ratio = round(1.0 * rec['REAL'] / rec['TOTAL'], 2)
        pratio = ratio if pratio == 0 else pratio
        #print ratio, pratio
        rec['CODE'] = rxhq.CODE
        rec['JYRQ'] = rxhq.JYRQ
        rec['OPEN'] = rxhq.OPEN * ratio
        rec['HIGH'] = rxhq.HIGH * ratio
        rec['LOW'] = rxhq.LOW * ratio
        rec['CLOSE'] = rxhq.CLOSE * ratio
        rec['PCLOSE'] = rxhq.PCLOSE * pratio
        rec['PHIGH'] = rxhq.PHIGH *  pratio
        rec['PLOW'] = rxhq.PLOW *  pratio
        rec['VOL'] = round(1.0 * latest_gbbq.REAL * rec['TOR'] / 100.0, 2) if latest_gbbq.REAL > 0 else round(1.0 * latest_gbbq.TOTAL * rec['TOR'] / 100.0, 2)
        rec['AMT'] = rxhq.AMT
        rec['CHG'] = round((1.0 * rec['CLOSE'] / rec['PCLOSE'] - 1) * 100.0, 2)
        rec['AVG'] = round(rec['AMT'] / rec['VOL'], 2)
        if (len(data) >= 5):
            data.pop(0)
        data.append(rec['AVG'])
        #print data
        (mean, variance) = stats(data)
        rec['SPV'] = variance

        if (len(tors) >= 5):
            tors.pop(0)
        tors.append(round(rec['TOR'] * 100, 0))
        #print tors
        (mtor, vtor)=stats(tors)
        if (len(p_tors) >= 5):
            p_tors.pop(0)
        p_tors.append(mtor)
        (mmtor, vvtor)=stats(p_tors)
        if (len(v_tors) >= 5):
            v_tors.pop(0)
        v_tors.append(vvtor)
        if (ptor > 0):
            if (vvtor < 100) and (vvtor > 0):
                rec['LESS'] = ptor + 1
            else:
                rec['LESS'] = 0
        else:
            if ((all_down(v_tors) == (len(v_tors) - 1)) and (vvtor < 100) and
                (vvtor > 0)):
                rec['LESS'] = 1
            else:
                rec['LESS'] = 0

        if (len(vars) >= 5):
            vars.pop(0)
        vars.append(variance)
        if (pown > 0):
            if (variance < 100) and (variance > 0):
                rec['OWN'] = pown + 1
            else:
                rec['OWN'] = 0
        else:
            if ((all_down(vars) == (len(vars) - 1)) and (variance < 100) and
                (variance > 0)):
                rec['OWN'] = 1
            else:
                rec['OWN'] = 0

        if (rec['OWN'] > 0) and (rec['LESS'] > 0) :
            if (sel_close == 0):
                sel_close = rec['CLOSE']
        if kk > 20:
            sel_close = 0
            kk = 0

        if sel_close > 0:
            chg_c = round((float(rec['CLOSE'])/sel_close - 1) * 100, 2)
            kk += 1

        rec['VWN'] = 0
        rec['SEL'] = 0
        rec['SEC'] = 0
        rec['TIM'] = 0
        rec['SIG'] = 0
        print rec['JYRQ'], rec['OWN'], rec['LESS'], sel_close, rec['CLOSE'], kk, chg_c

        """
        print rec['JYRQ']
        print round(rxhq.AMT / rxhq.VOL, 2)
        print ratio
        print pratio
        print rec['TOR']
        print rec['VOL']
        print rec['AMT']
        print rec['FLOW']
        print rec['REAL']
        print rec['TOTAL']
        print rec['AVG']
        """
        recs.append(rec)
        pratio = ratio
        pown = rec['OWN']
        ptor = rec['LESS']

    g_mutex.acquire()
    i = 0
    for rec in recs:
        records.append(rec)
        i += 1
    print "共处理 %4d 条记录" % (i)
    g_mutex.release()

@transaction.commit_on_success
def save_kzhq():
    global records

    for rec in records:
        print "正在处理 " + rec['CODE'].encode('UTF8') + " 股票 " + str(rec['JYRQ'])[0:10].encode('UTF8') + "日数据......"
        #kzhq = models.KZHQ(CODE=rec['CODE'], JYRQ=rec['JYRQ'],
                           #OPEN=rec['OPEN'], HIGH=rec['HIGH'], LOW=rec['LOW'],
                           #CLOSE=rec['CLOSE'], PCLOSE=rec['PCLOSE'],
                           #PHIGH=rec['PHIGH'], PLOW=rec['PLOW'],
                           #VOL=rec['VOL'], AMT=rec['AMT'], TOR=rec['TOR'],
                           #CHG=rec['CHG'], AVG=rec['AVG'], SPV=rec['SPV'], OWN=rec['OWN'])

        kzhq = models.KZHQ()
        kzhq.__dict__.update(rec)
        kzhq.save()


def main():
    """重新计算股票价格和换手"""
    global g_mutex
    global records

    g_mutex = threading.Lock()
    records = []

    start = time.time()  

    gpdms = models.GPDM.objects.all()

    codes = []
    for gp in gpdms:
        codes.append(gp.CODE)

    #work_manager =  WorkManager(codes, do_job, 10)#或者work_manager =  WorkManager(10000, 20)  
    #work_manager.wait_allcomplete()  
    do_job(['1600000'])

    cursor = connection.cursor()
    cursor.execute('delete from gphq_kzhq')
    transaction.commit_unless_managed()

    save_kzhq()

    end = time.time()  
    print end - start

if __name__ == '__main__':  
    main()
