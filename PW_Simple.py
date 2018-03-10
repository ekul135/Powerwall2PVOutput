#!/usr/bin/env python
import datetime
import time
import urllib
import httplib
import os
import json
import sys
import psycopg2
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers

pvo_host= "pvoutput.org"
pvo_key = ""
pvo_systemid = ""
PowerwallIP = ""
extData = True

def setup_logging():
    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    fh = handlers.RotatingFileHandler("simple.log", maxBytes=(1048576*5), backupCount=1)
    fh.setFormatter(format)
    log.addHandler(fh)

class Connection():
    def __init__(self, api_key, system_id, host):
        self.host = host
        self.api_key = api_key
        self.system_id = system_id

    def add_status(self, date, time, energy_exp=None, power_exp=None, energy_imp=None, power_imp=None, temp=None, vdc=None, battery_flow=None, load_power=None, soc=None, site_power=None, load_voltage=None, ext_power_exp=None, cumulative=False):
        
        path = '/service/r2/addstatus.jsp'
        params = {
                'd': date,
                't': time
                }
        if energy_exp:
            params['v1'] = energy_exp
        if power_exp:
            params['v2'] = power_exp
        if energy_imp:
            params['v3'] = energy_imp
        if power_imp:
            params['v4'] = power_imp
        if temp:
            params['v5'] = temp
        if vdc:
            params['v6'] = vdc
        if battery_flow:
            params['v7'] = battery_flow
        if load_power:
            params['v8'] = load_power
        if soc:
        	params['v9'] = soc    
        if site_power:
            params['v10'] = site_power
        if load_voltage:
            params['v11'] = load_voltage
        if ext_power_exp:
            params['v12'] = ext_power_exp    
        if cumulative:
            params['c1'] = 1
        params = urllib.urlencode(params)

        response = self.make_request('POST', path, params)

        if response.status == 400:
            raise ValueError(response.read())
        if response.status != 200:
            raise StandardError(response.read())
    
    def make_request(self, method, path, params=None):
        conn = httplib.HTTPConnection(self.host)
        headers = {
                'Content-type': 'application/x-www-form-urlencoded',
                'Accept': 'text/plain',
                'X-Pvoutput-Apikey': self.api_key,
                'X-Pvoutput-SystemId': self.system_id
                }
        conn.request(method, path, params, headers)

        return conn.getresponse()

def getPowerwallData():
    try:
        response = urllib.urlopen('http://'+PowerwallIP+'/api/meters/aggregates')
        webz = response.read()
        stuff = json.loads(webz)
        return stuff
    except StandardError as e:
        logger.info("getPowerwallData: " + str(e))
        return False

def getPowerwallSOCData():
    try:   
        response = urllib.urlopen('http://'+PowerwallIP+'/api/system_status/soe')
        webz = response.read()
        soc = json.loads(webz)
        return soc
    except StandardError as e:
        logger.info("getPowerwallSOCData: " + str(e))
        return False

def avg(l):
    return sum(l,0.00)/len(l) 

setup_logging()
logger = logging.getLogger(__name__)
logger.info('Start PVOutput simple')

while True:
    try:
    	lpvPower=[]
        lpvVoltage=[]
        lpvBatteryFlow=[]
        lpvLoadPower=[]
        lpvSitePower=[]
        lpvLoadVoltage=[]
        lpvSOC=[]
        i=0

        while i<60:
            pw=getPowerwallData()
            soc=getPowerwallSOCData()
            if (pw!=False and soc!=False):
                lpvPower.append(float(pw['solar']['instant_power']))
                lpvVoltage.append(float(pw['solar']['instant_average_voltage']))
                lpvBatteryFlow.append(float(pw['battery']['instant_power']))
                lpvLoadPower.append(float(pw['load']['instant_power']))
                lpvSitePower.append(float(pw['site']['instant_power']))
                lpvLoadVoltage.append(float(pw['load']['instant_average_voltage']))
                lpvSOC.append(float(soc['percentage']))
            else:
                logger.info('No data received, retrying')
            i=i+1
            time.sleep(5)

        if (len(lpvPower)!=0):    
            pvPower=avg(lpvPower)
            pvVoltage=avg(lpvVoltage)
            pvBatteryFlow=avg(lpvBatteryFlow)
            pvLoadPower=avg(lpvLoadPower)
            pvSitePower=avg(lpvSitePower)
            pvLoadVoltage=avg(lpvLoadVoltage)
            pvSOC=avg(lpvSOC)
            if (pvPower<=30):
                pvPower=0
            pvTemp=0
            pvConsumption=0
            pwdate=datetime.datetime.now()
            pvDate=pwdate.strftime("%Y%m%d")
            pvTime=pwdate.strftime("%H:%M")
            pvoutz = Connection(pvo_key, pvo_systemid, pvo_host)
            if extData==True:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage, battery_flow=pvBatteryFlow, load_power=pvLoadPower, soc=pvSOC, site_power=pvSitePower, load_voltage=pvLoadVoltage, ext_power_exp=pvPower)
            else:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage)
        else:
            logger.info('No data sent')

    except StandardError as e:
        logger.info('Main: Sleeping 5 minutes ' + str(e) )
        time.sleep(60*5)