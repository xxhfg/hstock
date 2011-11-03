#!/usr/bin/python
# -*-  coding: UTF8 -*- 

import os

#PROJECT_HOME = '/home/xxhfg/workspace/stock/'
#PROJECT_HOME = '/Users/xxhfg/Documents/workspace/stock/'
PROJECT_HOME = os.path.dirname(__file__) + '/..'

#STOCK_HOME = '/media/BACKUP/NewStock/'
#STOCK_HOME = '/volumes/TOOL/NewStock/'
STOCK_HOME = 'C:/NewStock/'
TDX_HOME = STOCK_HOME + '大金庄/'
DZH_HOME = STOCK_HOME + 'dzh2in1/dzh1/'
THS_HOME = STOCK_HOME + '同花顺/'
EXP_HOME = STOCK_HOME + 'Export/'

VIP_HOME = TDX_HOME + 'Vipdoc/'
SH_LDAY_HOME = VIP_HOME + 'sh/lday/'
SZ_LDAY_HOME = VIP_HOME + 'sz/lday/'
SH_LINE_HOME = VIP_HOME + 'sh/fzline/'
SZ_LINE_HOME = VIP_HOME + 'sz/fzline/'
TDX_GBBQ = TDX_HOME + 'T0002/hq_cache/gbbq'

BLOCK_INI = THS_HOME + 'system/同花顺方案/stockblock.ini'
CODE_BLOCK_INI = THS_HOME + 'xxhfg/CodeToBlock.ini'

DZH_SH_F10_HOME = DZH_HOME + 'DATA/SHase/Base/'
DZH_SZ_F10_HOME = DZH_HOME + 'DATA/SZnse/Base/'
