#!/usr/bin/env python
import time
import datetime
import PW_Helper

pvo_host= "pvoutput.org"
pvo_key = ""
pvo_systemid = ""
PowerwallIP = ""
extData = True
log_file="simple.log"

PW_Helper.setup_logging(log_file)
logger = PW_Helper.logging.getLogger(__name__)
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
            pw=PW_Helper.getPowerwallData(PowerwallIP)
            soc=PW_Helper.getPowerwallSOCData(PowerwallIP)
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
            pvPower=PW_Helper.avg(lpvPower)
            pvVoltage=PW_Helper.avg(lpvVoltage)
            pvBatteryFlow=PW_Helper.avg(lpvBatteryFlow)
            pvLoadPower=PW_Helper.avg(lpvLoadPower)
            pvSitePower=PW_Helper.avg(lpvSitePower)
            pvLoadVoltage=PW_Helper.avg(lpvLoadVoltage)
            pvSOC=PW_Helper.avg(lpvSOC)
            if (pvPower<=30):
                pvPower=0
            pvTemp=0
            pvConsumption=0
            pwdate=datetime.datetime.now()
            pvDate=pwdate.strftime("%Y%m%d")
            pvTime=pwdate.strftime("%H:%M")
            pvoutz = PW_Helper.Connection(pvo_key, pvo_systemid, pvo_host)
            if extData==True:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage, battery_flow=pvBatteryFlow, load_power=pvLoadPower, soc=pvSOC, site_power=pvSitePower, load_voltage=pvLoadVoltage, ext_power_exp=pvPower)
            else:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage)
        else:
            logger.info('No data sent')

    except StandardError as e:
        logger.info('Main: Sleeping 5 minutes ' + str(e) )
        time.sleep(60*5)