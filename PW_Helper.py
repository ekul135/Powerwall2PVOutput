#!/usr/bin/env python
import datetime
import time
import urllib
import httplib
import os
import json
import sys
import psycopg2
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
from logging import handlers

logger = logging.getLogger(__name__)

def setup_logging(log_file):
    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    fh = handlers.RotatingFileHandler(log_file, maxBytes=(1048576*5), backupCount=1)
    fh.setFormatter(format)
    log.addHandler(fh)

def insertdb(sqlite_file, values):
    try:
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()
        c.execute("PRAGMA journal_mode=wal")
        sql = "INSERT INTO pw VALUES(CURRENT_TIMESTAMP,?,?,?,?,?,?,?,?,?)"
        c.execute(sql, (values))
        conn.commit()
        conn.close()
    except StandardError as e:
        logger.info("insertdb: " + str(e))
        return False     

def get_sqlite_data(sqlite_file, sqldate):
    try:
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()
        c.execute("PRAGMA journal_mode=wal")
        sql="SELECT Date, Time, Power,Consumption,Temperature,Voltage,BatteryFlow,LoadPower,SOC,SitePower,LoadVoltage FROM View_pw WHERE LogDate>'%s'" % sqldate
        c.execute(sql)
        rows = c.fetchall()
        conn.commit()
        conn.close()
    except StandardError as e:
        logger.info("get_sqlite_data: " + str(e))
        return False

    return rows

def delete_sqlite_data(sqlite_file, days):
    try:
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()
        c.execute("PRAGMA journal_mode=wal")
        sql="DELETE FROM pw WHERE LogDate < DATE('now', '%s" % "-"+str(days)+" days')"
        c.execute(sql)
        conn.commit()
        conn.close()
    except StandardError as e:
        logger.info("delete_sqlite_data: " + str(e))
        return False

def avg(l):
    return sum(l,0.00)/len(l) 

def getPowerwallData(PowerwallIP):
    try:
        response = urllib.urlopen('http://'+PowerwallIP+'/api/meters/aggregates')
        webz = response.read()
    	stuff = json.loads(webz)
    	return stuff
    except StandardError as e:
        logger.info("getPowerwallData: " + str(e))
        return False

def getPowerwallSOCData(PowerwallIP):
    try:   
        response = urllib.urlopen('http://'+PowerwallIP+'/api/system_status/soe')
        webz = response.read()
        soc = json.loads(webz)
        return soc
    except StandardError as e:
        logger.info("getPowerwallSOCData: " + str(e))
        return False

class Connection():
    def __init__(self, api_key, system_id, host):
        self.host = host
        self.api_key = api_key
        self.system_id = system_id

    def get_status(self, date=None, time=None):
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