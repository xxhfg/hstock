#!/usr/bin/python
# -*-  coding: UTF8 -*- 

import ConfigParser, os, string

class INIFILE:
    def __init__(self, filename):
        self.filename = filename
        self.initflag = False
        self.cfg = None
        self.readhandle = None
        self.writehandle = None
    def Init(self):
        self.cfg = ConfigParser.ConfigParser()
        try:
            self.readhandle = open(self.filename, 'r')
            self.cfg.readfp(self.readhandle)
            self.writehandle = open(self.filename, 'w')
            self.initflag = True
        except:
            self.initflag = False
        return self.initflag
    def UnInit(self):
        if self.initflag:
            self.readhandle.close()
            self.writehandle.closse()
    def GetValue(self, Section, Key, Default = ""):
        try:
            value = self.cfg.get(Section, Key)
        except:
            value = Default
        return value
    def SetValue(self, Section, Key, Value):
        try:
            self.cfg.set(Section, Key, Value)
        except:
            self.cfg.add_section(Section)
            self.cfg.set(Section, Key, Value)
            self.cfg.write(self.writehandle)

def LoadConfig(file, config={}): 
    """ 
    returns a dictionary with keys of the form 
    <section>.<option> and the corresponding values 
    """ 
    #返回一个字典,格式如下: key:     <section>.<option> 
    #                   value :  对应的值 

    config = config.copy() 
    cp = ConfigParser.ConfigParser() 
    cp.read(file) 
    for sec in cp.sections(): 
        name = string.lower(sec) 
        for opt in cp.options(sec): 
            config[name + "." + string.lower(opt)] = string.strip( 
                cp.get(sec, opt)) 
    return config 

