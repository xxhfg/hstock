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

def sums(data):
    """计算数组和"""
    #if (len(data) <= 1): return (0, 0)

    sum = 0.0
    for value in data:
        sum += value

    return sum

def stats(data):
    """计算均价和方差"""
    if (len(data) <= 1): return (0, 0)

    sum = 0.0
    for value in data:
        sum += value
    mean = round(sum/len(data), 0)
    sum = 0.0
    for value in data:
        sum += (value - mean)**2
    variance = round(sum/(len(data) - 1), 0)
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
    ttors = [] #近十日换手率
    p_tors = [] 
    v_tors = []
    pown = 0
    ptor = 0
    avg_close = 0
    sel_close = 0
    chg_c = 0
    kk = 0
    tim = 0
    sig = 0
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
                rec['TOR'] = round(100.0 * rxhq.VOL / gbbq.REAL, 4) * 100 \
                        if gbbq.REAL > 0 else round(100.0 * rxhq.VOL / gbbq.TOTAL, 4) * 100
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
        rec['CHG'] = round((1.0 * rec['CLOSE'] / rec['PCLOSE'] - 1) * 100.0, 2) * 100
        rec['AVG'] = round(rec['AMT'] / rec['VOL'], 2) * 100

        #近期5日均价数组
        if (len(data) >= 5):
            data.pop(0)
        data.append(rec['AVG'])
        #求5日均价和方差
        (mean, variance) = stats(data)
        rec['SPV'] = variance

        #近期5日换手数组
        if (len(tors) >= 5):
            tors.pop(0)
        tors.append(round(rec['TOR'], 0))
        if (len(ttors) >= 10):
            ttors.pop(0)
        ttors.append(round(rec['TOR'], 0))
        #求5日平均换手和方差
        (mtor, vtor)=stats(tors)
        #近期5日平均换手数组
        if (len(p_tors) >= 5):
            p_tors.pop(0)
        p_tors.append(mtor)
        #求5日平均换手的5日平均和方差
        (mmtor, vvtor)=stats(p_tors)
        rec['SPT'] = vvtor
        #近5日平均换手方差数组
        if (len(v_tors) >= 5):
            v_tors.pop(0)
        v_tors.append(vvtor)
        #下降标志大于0
        if (ptor > 0):
            #连续下降, 标志加1
            if (vvtor < 100 * 5) and (vvtor > 0):
                rec['VWN'] = ptor + 1
            else:
                #方差大于100, 标志重置为0
                rec['VWN'] = 0
        else:
            #近5日方差数组连续下降, 并且最后一日方差小于100, 标志置为1
            if ((all_down(v_tors) == (len(v_tors) - 1)) and (vvtor < 100 * 5) and
                (vvtor > 0)):
                rec['VWN'] = 1
            else:
                rec['VWN'] = 0

        #近5日均价方差数组
        if (len(vars) >= 5):
            vars.pop(0)
        vars.append(variance)
        #下降标志大于0
        if (pown > 0):
            #连续下降, 标志加1
            if (variance < 100) and (variance > 0):
                rec['OWN'] = pown + 1
            else:
                #方差大于100, 标志重置为0
                rec['OWN'] = 0
        else:
            #近5日方差数组连续下降, 并且最后一日方差小于100, 标志置为1
            if ((all_down(vars) == (len(vars) - 1)) and (variance < 100) and
                (variance > 0)):
                rec['OWN'] = 1
            else:
                rec['OWN'] = 0

        #价格标志和换手标志都大于0, 选中价格为0, 置选中价格为5日均价
        if (rec['OWN'] > 0) and (rec['VWN'] > 0) :
            if (sel_close == 0):
                tim = (sums(ttors) - sums(tors)) / sums(tors) * 100
                sel_close = mean

        tt = ((sums(ttors) - sums(tors)) / sums(tors))
        #选中价格大于0, 选中天数加1
        if sel_close > 0:
            if (rec['AVG'] > sel_close) and (tt > 1.20):
                sig += 1
            chg_c = round((float(rec['CLOSE'])/sel_close - 1) * 100, 2)
            kk += 1

        print kk, sel_close, tt, sig, chg_c
        #选中20日后, 或者均价小于选中价格, 重置为0
        if (kk > 20) or (rec['AVG'] < sel_close) or (chg_c > 20):
            sel_close = 0
            tim = 0
            kk = 0
            sig = 0

        rec['SEL'] = kk
        rec['SEC'] = sel_close
        rec['TIM'] = tim
        rec['SIG'] = sig
        print rec['JYRQ'], rec['OWN'], rec['VWN'], rec['AVG'], sel_close, rec['CLOSE'], kk, chg_c

        recs.append(rec)
        #股本比例记录
        pratio = ratio
        #记录价格标志
        pown = rec['OWN']
        #记录换手标志
        ptor = rec['VWN']

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
    do_job(['1600225'])

    cursor = connection.cursor()
    cursor.execute('delete from gphq_kzhq')
    transaction.commit_unless_managed()

    save_kzhq()

    end = time.time()  
    print end - start

if __name__ == '__main__':  
    main()
