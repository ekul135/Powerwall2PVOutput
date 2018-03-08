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

sqlite_file = "pw.sqlite"
PowerwallIP = ""

def setup_logging():
    log = logging.getLogger('')
    log.setLevel(logging.INFO)
    format = logging.Formatter("%(asctime)s - %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    fh = handlers.RotatingFileHandler("datalogger.log", maxBytes=(1048576*5), backupCount=1)
    fh.setFormatter(format)
    log.addHandler(fh)

def insertdb(values):
    try:
        conn = sqlite3.connect(sqlite_file)
        c = conn.cursor()
        sql = "INSERT INTO pw VALUES(CURRENT_TIMESTAMP,?,?,?,?,?,?,?,?,?)"
        c.execute(sql, (values))
        conn.commit()
        conn.close()
    except StandardError as e:
        logger.info("insertdb: " + str(e))
        return False     

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

setup_logging()
logger = logging.getLogger(__name__)
logger.info('Start PVOutput datalogger')
while True:
    try:
    	pw=getPowerwallData()
        soc=getPowerwallSOCData()
        if (pw!=False and soc!=False):
            lpvPower=float(pw['solar']['instant_power'])
            lpvVoltage=float(pw['solar']['instant_average_voltage'])
            lpvBatteryFlow=float(pw['battery']['instant_power'])
            lpvLoadPower=float(pw['load']['instant_power'])
            lpvSitePower=float(pw['site']['instant_power'])
            lpvLoadVoltage=float(pw['load']['instant_average_voltage'])
            lpvSOC=float(soc['percentage'])
            values=(lpvPower,0,0,lpvVoltage,lpvBatteryFlow,lpvLoadPower,lpvSOC,lpvSitePower,lpvLoadVoltage)
            insertdb(values)
        else:
            logger.info('No data received, retrying')
        time.sleep(5)
        
    except StandardError as e:
        logger.info('Main: Sleeping 5 minutes ' + str(e) )
        time.sleep(60*5)