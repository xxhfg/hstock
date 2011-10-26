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
import re
import urllib
import httplib2
import random
import socket
from stock.gphq import models
from django.db import connection, transaction
from workmanager import * 

def get_html(url):
    """下载网页"""
    opener = urllib.FancyURLopener({})      #不使用代理
    #www.my-proxy.com 需要下面这个Cookie才能正常抓取
    opener.addheaders = [
        ('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)'),
        ('Cookie','permission=1'), 
        ]
    t=time.time()
    if (url.find("?")==-1):
        url=url+'?rnd='+str(random.random())
    else:
        url=url+'&rnd='+str(random.random())

    #time.sleep(5)
    try:
        # h = httplib2.Http('cache')
        h = httplib2.Http()
        response, html = h.request(url)
        if response.status <> 200:
            html = ''

        #html = mdcode(html)
    except:
        html = ''

    return html.lower()
    
#具体要做的任务  
# @transaction.commit_on_success
# @transaction.commit_manually
def do_job2(args):
    """从和讯网上下载股本变动数据, 分解之后写入数据库中"""
    global gb_records
    global rx_records
    global g_mutex
    global pat_in, pat_out, pat_date, pat_total, pat_rxhq
    global file_base
    recs = []

    if (len(args)==0):
        return False

    code = args[0]
    scdm = code[0]
    scjc = 'SH' if scdm == '1' else 'SZ'
    gpdm = code[1:]
    list_url= file_base % (gpdm, )

    #f = open(list_url)
    #html = f.read()
    #f.close()

    html = get_html(list_url)

    if html == '':
        exit

    lbegin = html.find(pat_in)
    lend = html.find(pat_out)
    line = html[lbegin:lend]

    rdates = pat_date.findall(line)
    rtotals = pat_total.findall(line)

    if (len(rdates) == 0): 
        print '页面发生变化, 请查看!'
        exit

    for i in range(len(rdates)):
        bgrq = rdates[i]
        total = string.atof(rtotals[i * 3][0].replace(',', '')) if (rtotals[i * 3][0] <> '') else 0
        flow = string.atof(rtotals[i * 3 + 1][0].replace(',', '')) if (rtotals[i * 3 + 1][0] <> '') else 0
        real = string.atof(rtotals[i * 3 + 2][0].replace(',', '')) if (rtotals[i * 3 + 2][0] <> '') else 0

        rec = {}
        rec['CODE'] = code
        rec['BGRQ'] = bgrq
        rec['TOTAL'] = total * 10000
        rec['FLOW'] = flow * 10000
        rec['REAL'] = real * 10000

        for r in recs:
            if (r['BGRQ']==rec['BGRQ']):
                if  (r['FLOW'] < rec['FLOW']):
                    recs.delete(r)
                else:
                    rec = None
                break

        if (rec):
            recs.append(rec)

    g_mutex.acquire()
    print u"正在处理 %s 市场 %s 股票......" % (scjc, code)
    for rec in recs:
        gb_records.append(rec)
    g_mutex.release()

    
def do_job1(args):  
    global gb_records
    global rx_records
    global g_mutex
    global pat_in, pat_out
    # global pattern
    recs = []

    if (len(args)==0):
        return False

    filepath = args[0]
    filename = os.path.basename(filepath).upper()
    filedir = os.path.dirname(filepath) + '/'

    if not os.path.isfile(filepath):
        return False


    scjc = 'SZ' if filedir == config.DZH_SZ_F10_HOME else 'SH'
    scdm = '0' if scjc == 'SZ' else '1'
    gpdm = filename[0:6]
    code = scdm + gpdm

    f = open(filepath)
    lines = f.readlines()
    f.close()
    bz = False
    for line in lines:
        if (line.find(pat_in) <> -1):
            bz = True
            continue

        if (line.find(pat_out) <> -1):
            break

        if (bz):
            # result = pattern.findall(line)
            result = line.split()
            if ((len(result) > 1) and (result[0][0:4].isdigit())):
                # print result
                rec = {}
                rec['CODE'] = code
                rec['BGRQ'] = result[0]
                rec['TOTAL'] = string.atof(result[1]) * 10000 if result[1].find('-') == -1 else 0
                rec['FLOW'] = string.atof(result[2]) * 10000 if result[2].find('-') == -1 else 0
                rec['REAL'] = string.atof(result[2]) * 10000 if result[2].find('-') == -1 else 0
                for r in recs:
                    if (r['BGRQ']==rec['BGRQ']):
                        if  (r['FLOW'] < rec['FLOW']):
                            recs.delete(r)
                        else:
                            rec = None
                        break

                if (rec):
                    recs.append(rec)

    g_mutex.acquire()
    print u"正在处理 %s 市场 %s 股票......" % (scjc, code)
    for rec in recs:
        gb_records.append(rec)
    g_mutex.release()

@transaction.commit_on_success
def save_gbbq():
    global gb_records
    global rx_records

    for rec in gb_records:
        print u"正在处理 %s 股票 %s 日数据......" % (rec['CODE'], rec['BGRQ'])
        try:
            gbbq = models.GBBQ(CODE=rec['CODE'], BGRQ=rec['BGRQ'], TOTAL=rec['TOTAL'], FLOW=rec['FLOW'], REAL=rec['REAL'])
            gbbq.save()
        except Exception, e:
            #raise e
            pass

def main2(Num):
    """
    处理和讯数据
    """
    global gb_records
    global rx_records
    global g_mutex
    global pat_in, pat_out, pat_date, pat_total, pat_rxhq
    global pattern
    global file_base

    #file_base = 'http://stockdata.stock.hexun.com/2009_gbjg_%s.shtml'
    #file_base = '/Users/xxhfg/Documents/%s.html'
    #file_base = 'http://stockpage.10jqka.com.cn/%s/company.html'
    #pat_in = '变更原因'.decode('UTF8').encode('GB2312')
    #pat_out = '<!--行业概念-->'.decode('UTF8').encode('GB2312')
    file_base = 'http://stock.quote.stockstar.com/share/structure_%s.shtml'
    pat_in = '<!-- 股本变化 begin -->'.decode('UTF8').encode('GB2312')
    pat_out = '<!-- 股本变化 end -->'.decode('UTF8').encode('GB2312')
    pat_date = re.compile(r'<td.*?>(\d{4}-\d{2}-\d{2})</td>')
    pat_total = re.compile(r'<td.*?>([\d\,]*(\.\d+)?)</td>')
    pat_rxhq = re.compile(r'stock_quoteinfo_(\D*?)[\"|\'].*?>(.*?)</')
    # from singleinstance import * 
    g_mutex = threading.Lock()
    socket.setdefaulttimeout(60)
    gb_records = []
    rx_records = []

    start = time.time()  

    gpdms = models.GPDM.objects.all()
    codes = []
    for gp in gpdms:
        codes.append(gp.CODE)

    #do_job2(['0002118', ])
    work_manager =  WorkManager(codes, do_job2, Num)#或者work_manager =  WorkManager(10000, 20)  
    work_manager.wait_allcomplete()  

    #cursor = connection.cursor()
    #cursor.execute('delete from gphq_gbbq')
    #transaction.commit_unless_managed()

    save_gbbq()

    end = time.time()  
    print end - start
   
def main1(Num):
    """
    处理大智慧数据
    """
    global gb_records
    global rx_records
    global g_mutex
    global pat_in, pat_out, pat_date, pat_total
    global pattern

    pat_in = '二、股本变动'.decode('UTF8').encode('GB2312')
    pat_out = '三、分红扩股'.decode('UTF8').encode('GB2312')
    pattern = re.compile(r'(\d{4}-\d{2}-\d{2})\s+(\d+(\.\d+)?)\s+(\d+(\.\d+)?)\s+(.*)')
    # from singleinstance import * 
    g_mutex = threading.Lock()
    socket.setdefaulttimeout(10)
    gb_records = []
    rx_records = []

    start = time.time()  
    cursor = connection.cursor()
    cursor.execute('delete from gphq_gbbq')
    transaction.commit_unless_managed()

    print config.DZH_SH_F10_HOME
    files = os.listdir(config.DZH_SH_F10_HOME)
    sh_files = []
    for f in files:
        if (f[7:11] == '011'):
            sh_files.append(config.DZH_SH_F10_HOME + f)
            # do_job1([config.DZH_SH_F10_HOME + f, ])

    work_manager =  WorkManager(sh_files, do_job1, Num)#或者work_manager =  WorkManager(10000, 20)  
    work_manager.wait_allcomplete()  

    print config.DZH_SZ_F10_HOME
    files = os.listdir(config.DZH_SZ_F10_HOME)
    sz_files = []
    for f in files:
        if (f[7:11] == '011'):
            sz_files.append(config.DZH_SZ_F10_HOME + f)

    work_manager =  WorkManager(sz_files, do_job1, Num)#或者work_manager =  WorkManager(10000, 20)  
    work_manager.wait_allcomplete()  

    save_gbbq()

    end = time.time()  
    print end - start
     
if __name__ == '__main__':  
    global iNum

    if (len(sys.argv)==1):
        iNum = 30
    else:
        iNum = int(sys.argv[1])

    main2(iNum)
