#!/usr/bin/python
# -*-  coding: UTF8 -*- 


from django.db import models
import time
import string

# Create your models here.
"""
价格和金额以分为单位,成交量和股本以股为单位
"""

class GPDM(models.Model):
    """股票代码"""
    SCDM = models.CharField(max_length=1) #市场代码
    GPDM = models.CharField(max_length=10) #股票代码
    SCJC = models.CharField(max_length=2) #市场简称
    GPMC = models.CharField(max_length=10) #股票名称
    CODE = models.CharField(max_length=10, primary_key=True) #识别代码, '市场代码 + 股票代码'

    class Meta:
        ordering = ['CODE']
        
class RXHQ(models.Model):
    """日线行情"""
    CODE = models.CharField(max_length=10, db_index=True) #识别代码, '市场代码 + 股票代码'
    JYRQ = models.DateField(db_index=True) #交易日期
    OPEN = models.IntegerField() #开盘价格
    HIGH = models.IntegerField() #最高价格
    LOW = models.IntegerField() #最低价格
    CLOSE = models.IntegerField() #收盘价格
    PCLOSE = models.IntegerField() #昨日收盘价格
    PHIGH = models.IntegerField() #昨日最高价格
    PLOW = models.IntegerField() #昨日最低价格
    VOL = models.IntegerField() #成交量
    AMT = models.IntegerField() #成交额
    CHG = models.IntegerField() #涨幅

    class Meta:
        unique_together = (('CODE', 'JYRQ'), )
        ordering = ['CODE', 'JYRQ']

class FZHQ(models.Model):
    """5分钟行情"""
    CODE = models.CharField(max_length=10, db_index=True) #识别代码, '市场代码 + 股票代码'
    JYRQ = models.DateField(db_index=True) #交易日期
    TJSD = models.CharField(max_length=4, db_index=True) #统计时段
    OPEN = models.IntegerField() #开盘价格
    HIGH = models.IntegerField() #最高价格
    LOW = models.IntegerField() #最低价格
    CLOSE = models.IntegerField() #收盘价格
    VOL = models.IntegerField() #成交量
    AMT = models.IntegerField() #成交额
        
class ZDRQ(models.Model):
    JYRQ = models.DateField(primary_key=True, default='1900-01-01') #交易日期

    def __unicode__(self):
        return '%s' % (self.JYRQ)

class GPRQ(models.Model):
    CODE = models.CharField(max_length=10) #识别代码, '市场代码 + 股票代码'
    JYRQ = models.DateField() #交易日期

    class Meta:
        unique_together = (('CODE', 'JYRQ'), )
        ordering = ['CODE', 'JYRQ']

class KZHQ(models.Model):
    """扩展行情，经过复权处理"""
    CODE = models.CharField(max_length=10, db_index=True) #识别代码, '市场代码 + 股票代码'
    JYRQ = models.DateField(db_index=True) #交易日期
    OPEN = models.IntegerField() #开盘价格
    HIGH = models.IntegerField() #最高价格
    LOW = models.IntegerField() #最低价格
    CLOSE = models.IntegerField() #收盘价格
    PCLOSE = models.IntegerField() #昨日收盘价格
    PHIGH = models.IntegerField() #昨日最高价格
    PLOW = models.IntegerField() #昨日最低价格
    VOL = models.IntegerField() #成交量
    AMT = models.IntegerField() #成交额
    AVG = models.IntegerField() #均价
    CHG = models.IntegerField() #涨幅
    TOR = models.IntegerField() #换手率TurnOver Ratio
    SPV = models.IntegerField() #股票价格的波动率Stock Price Volatility
    SPT = models.IntegerField() #五日平均换手的波动率Stock Price Volatility
    OWN = models.IntegerField() #价格方差连续下降, 且小于100, 置为1, 且连续增加, 直至大于100
    VWN = models.IntegerField() #换手方差连续下降, 且小于100, 置为1, 且连续增加, 直至大于100
    SEL = models.IntegerField() #价格方差和换手方差同时大于0, 置为1, 且连续增加, 直至价格小于选中均价或大于20
    SEC = models.IntegerField() #SEL大于0时的均价
    TIM = models.IntegerField() #SEL=1时前五日换手与近五日换手的比值
    SIG = models.IntegerField()
    #收盘价格大于SEC且近五日换手相比有20%的增幅置为1, 且连续增加

    class Meta:
        unique_together = (('CODE', 'JYRQ'), )
        ordering = ['CODE', 'JYRQ']

class GBBQ(models.Model):
    """股本变迁"""
    CODE = models.CharField(max_length=10, db_index=True) #识别代码, '市场代码 + 股票代码'
    BGRQ = models.DateField(db_index=True) #变更日期
    TOTAL = models.IntegerField() #总股本
    FLOW = models.IntegerField() #流通A股
    REAL = models.IntegerField() #实际A股

    class Meta:
        unique_together = (('CODE', 'BGRQ'), )
        ordering = ['CODE', '-BGRQ']

class BKDM(models.Model):
    """板块代码"""
    BKDM = models.CharField(max_length=10, primary_key=True) #板块代码
    BKMC = models.CharField(max_length=10) #板块名称

class BKGP(models.Model):
    """板块股票"""
    BKDM = models.CharField(max_length=10) #板块代码
    CODE = models.CharField(max_length=10) #识别代码, '市场代码 + 股票代码'

    class Meta:
        unique_together = (('BKDM', 'CODE'), )
        ordering = ['BKDM', 'CODE']

class GNBK(models.Model):
    """概念板块"""
    GNLX = models.CharField(max_length=10) #概念类型
    BKDM = models.CharField(max_length=10) #板块代码

    class Meta:
        unique_together = (('GNLX', 'BKDM'), )
