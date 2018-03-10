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
import sqlite3

sqlite_file = 'pw.sqlite'
pvo_host= "pvoutput.org"
pvo_key = ""
pvo_systemid = ""
extData = True

def setup_logging():
    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    fh = handlers.RotatingFileHandler("pvo.log", maxBytes=(1048576*5), backupCount=1)
    fh.setFormatter(format)
    log.addHandler(fh)

def get_sqlite_data(sqldate):
    try:
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()
        sql="SELECT Date, Time, Power,Consumption,Temperature,Voltage,BatteryFlow,LoadPower,SOC,SitePower,LoadVoltage FROM View_pw WHERE LogDate>'%s'" % sqldate
        c.execute(sql)
        rows = c.fetchall()
        conn.commit()
        conn.close()
    except StandardError as e:
        logger.info("get_sqlite_data: " + str(e))
        return False

    return rows

class Connection():
    def __init__(self, api_key, system_id, host):
        self.host = host
        self.api_key = api_key
        self.system_id = system_id

    def get_status(self, date=None, time=None):
        """
        Retrieves status information
        Return example:
          20101107,18:30,12936,202,NaN,NaN,5.280,15.3,240.1
        """
        path = '/service/r2/getstatus.jsp'
        params = {}
        if date:
            params['d'] = date
        if time:
            params['t'] = time
        params = urllib.urlencode(params)

        response = self.make_request("GET", path, params)

        if response.status == 400:
            # Initialise a "No status found"
            return "%s,00:00,,,,,,," % datetime.datetime.now().strftime('%Y%m%d')
        if response.status != 200:
            raise StandardError(response.read())

        return response.read()
        
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

setup_logging()
logger = logging.getLogger(__name__)
logger.info('Start PVOutput export')

try:
    pvoutz = Connection(pvo_key, pvo_systemid, pvo_host)
    PVOStatus = pvoutz.get_status()
    pvodate = PVOStatus.split(",")[0]
    pvotime = PVOStatus.split(",")[1]
    sqldate = str(datetime.datetime.strptime(pvodate + " " + pvotime, "%Y%m%d %H:%M"))
    rows = get_sqlite_data(sqldate)
    if len(rows)>0:

        for row in rows:
            pvPower=row[2]
            pvVoltage=row[5]
            pvBatteryFlow=row[6]
            pvLoadPower=row[7]
            pvSitePower=row[9]
            pvLoadVoltage=row[10]
            pvSOC=row[8]
            if (pvPower<=30):
                pvPower=0
            pvTemp=row[4]
            pvConsumption=row[3]
            pvDate=row[1]
            pvTime=row[0]
            if extData==True:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage, battery_flow=pvBatteryFlow, load_power=pvLoadPower, soc=pvSOC, site_power=pvSitePower, load_voltage=pvLoadVoltage, ext_power_exp=pvPower)
            else:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage)
    else:
        logger.info("No data returned")               

except Exception as err:
    logger.info("[ERROR] %s" % err)

logger.info('End PVOutput export')     