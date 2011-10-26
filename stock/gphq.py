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
import Queue  
import threading  
import string
import time
import datetime
from stock.gphq import models
from django.db import connection, transaction

#具体要做的任务  
#@transaction.commit_on_success
# @transaction.commit_manually
def do_job(args):  
    global g_mutex

    if (len(args)==0):
        return False

    filename = args[0]
    filepath = config.EXP_HOME + filename

    scjc = filename[0:2]
    scdm = '0' if scjc == 'SZ' else '1'
    gpdm = filename[2:8]
    code = scdm + gpdm
    print "正在处理 " + scjc + " 市场 " + code + " 股票......"
    gpdm = models.GPDM(SCDM=scdm, GPDM=gpdm, SCJC=scjc, CODE=code, GPMC='')
    gpdm.save()

    day = ''
    opn = 0
    high = 0
    low = 0
    close = 0
    vol = 0
    amt = 0
    lines = file(filepath)
    for line in lines:
        fzjl = line.strip().split(',')
        # jyrq = time.strptime(fzjl[0], "%Y-%m-%d")
        jyrq = fzjl[0]
        # tjsd = fzjl[1]
        if (day <> jyrq):
            if (vol > 0):
                # print "正在处理 " + day + "......"
                rxhq = models.RXHQ(CODE=code, JYRQ=day, OPEN=opn, HIGH=high, LOW=low, CLOSE=close, VOL=vol, AMT=amt)
                rxhq.save()
            day = jyrq
            opn = 0
            high = 0
            low = 0
            close = 0
            vol = 0
            amt = 0

        # if (tjsd == '0935'):
            # opn = string.atof(fzjl[2])
        # high = string.atof(fzjl[3]) if high < string.atof(fzjl[3]) else high
        # low = string.atof(fzjl[4]) if ((low == 0) or (low > string.atof(fzjl[4]))) else low
        # if (tjsd == '1500'):
            # close = string.atof(fzjl[5])
        # vol += string.atof(fzjl[6])
        # amt += string.atof(fzjl[7])
        opn = string.atof(fzjl[1])
        high = string.atof(fzjl[2]) if high < string.atof(fzjl[2]) else high
        low = string.atof(fzjl[3]) if ((low == 0) or (low > string.atof(fzjl[3]))) else low
        close = string.atof(fzjl[4])
        vol += string.atof(fzjl[5])
        amt += string.atof(fzjl[6])

        # fzhq = models.FZHQ(CODE=code, JYRQ=jyrq, TJSD=tjsd, OPEN=opn, HIGH=high, LOW=low, CLOSE=close, VOL=vol, AMT=amt)
        # fzhq.save()

    # transaction.commit()


if __name__ == '__main__':  
    # from singleinstance import * 
    g_mutex = threading.Lock()

    start = time.time()  
    cursor = connection.cursor()
    cursor.execute('delete from gphq_gpdm')
    cursor.execute('delete from gphq_fzhq')
    cursor.execute('delete from gphq_rxhq')
    # transaction.commit_unless_managed()
    transaction.commit()

    # models.GPDM.objects.all().delete()
    # models.FZHQ.objects.all().delete()
    # models.RXHQ.objects.all().delete()

    print config.EXP_HOME
    files = os.listdir(config.EXP_HOME)
    work_manager =  WorkManager(files, 1)#或者work_manager =  WorkManager(10000, 20)  
    work_manager.wait_allcomplete()  

    end = time.time()  
    print end - start
