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
from inifile import * 

@transaction.commit_on_success
def save_bkdm():
    global ini_list

    for key in ini_list:
        if (key.find('block_name_map_table') <> -1):
            dm = key.replace('block_name_map_table.', '')
            mc = string.strip(ini_list[key]).decode('GB2312').encode('UTF8')
            print '正在处理 %4s ---- %-30s ......' % (dm, mc)
            bkdm = models.BKDM(BKDM=str(dm), BKMC=str(mc))
            bkdm.save()

@transaction.commit_on_success
def save_gnbk(gnlx=''):
    global ini_list

    if (gnlx==''):
        return -1

    bkdms = get_gnbk(gnlx)
    for bkdm in bkdms:
        print '正在处理 %4s ---- %-30s ......' % (gnlx, bkdm)
        gnbk = models.GNBK(GNLX=gnlx, BKDM=bkdm)
        gnbk.save()

@transaction.commit_on_success
def save_bkgp(records):
    for rec in records:
        print '正在处理 %4s ---- %-30s ......' % (rec['BKDM'], rec['CODE'])
        bkgp = models.BKGP(BKDM=rec['BKDM'], CODE=rec['CODE'])
        bkgp.save()

def get_gnbk(section=''):
    global ini_list
    result = []

    for key in ini_list:
        if (key.find(section) <> -1):
            dm = key.replace(section + '.', '')
            value = string.strip(ini_list[key])
            result.append(dm)
            if (value.find('@') <> -1):
                result.extend(get_gnbk(value))

    return result

def get_bkgp():
    global lines
    global gpdms
    result = []

    lines.pop(0)
    for line in lines:
        (key, value)=line.split('=')
        (sc, gpdm)=key.split(':')
        if ((sc=='17') or (sc=='33')):
            if (sc=='17'):
                scdm = '1'
                scjc = 'SH'
            else:
                scdm = '0'
                scjc = 'SZ'
            code = scdm + gpdm
            rec = {}
            rec['SCDM'] = scdm
            rec['GPDM'] = gpdm
            rec['SCJC'] = scjc
            rec['GPMC'] = ''
            rec['CODE'] = code
            gpdms.append(rec)

            bkdms = string.lower(string.strip(value)).split(',')
            for bkdm in bkdms:
                rec = {}
                rec['BKDM'] = bkdm
                rec['CODE'] = code
                result.append(rec)

    return result

@transaction.commit_on_success
def save_gpdm():
    global gpdms

    for gp in gpdms:
        print "正在处理 " + gp['SCJC'] + " 市场 " + gp['CODE'] + " 股票......"
        gpdm = models.GPDM(SCDM=gp['SCDM'], GPDM=gp['GPDM'], SCJC=gp['SCJC'], CODE=gp['CODE'], GPMC=gp['GPMC'])
        gpdm.save()

if __name__ == '__main__':  
    global gpdms

    gpdms = []

    if not os.path.isfile(config.BLOCK_INI):
        exit

    start = time.time()  

    cursor = connection.cursor()
    cursor.execute('delete from gphq_bkdm')
    cursor.execute('delete from gphq_gnbk')
    cursor.execute('delete from gphq_bkgp')
    cursor.execute('delete from gphq_gpdm')
    transaction.commit_unless_managed()

    ini_list=LoadConfig(config.BLOCK_INI)

    save_bkdm()
    save_gnbk('@37')
    save_gnbk('@8')
    save_gnbk('@9')

    f = open(config.CODE_BLOCK_INI)
    lines = f.readlines()
    f.close()
    save_bkgp(get_bkgp())
    save_gpdm()

    end = time.time()  
    print end - start
