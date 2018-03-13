#!/usr/bin/env python
import time
import datetime
import PW_Helper as hlp
import PW_Config as cfg

hlp.setup_logging(cfg.log_file)
logger = hlp.logging.getLogger(__name__)
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
            pw=hlp.getPowerwallData(cfg.PowerwallIP)
            soc=hlp.getPowerwallSOCData(cfg.PowerwallIP)
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
            pvPower=hlp.avg(lpvPower)
            pvVoltage=hlp.avg(lpvVoltage)
            pvBatteryFlow=hlp.avg(lpvBatteryFlow)
            pvLoadPower=hlp.avg(lpvLoadPower)
            pvSitePower=hlp.avg(lpvSitePower)
            pvLoadVoltage=hlp.avg(lpvLoadVoltage)
            pvSOC=hlp.avg(lpvSOC)
            if (pvPower<=30):
                pvPower=0
            pvTemp=0
            pvConsumption=0
            pwdate=datetime.datetime.now()
            pvDate=pwdate.strftime("%Y%m%d")
            pvTime=pwdate.strftime("%H:%M")
            pvoutz = hlp.Connection(cfg.pvo_key, cfg.pvo_systemid, cfg.pvo_host)
            if cfg.extData==True:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage, battery_flow=pvBatteryFlow, load_power=pvLoadPower, soc=pvSOC, site_power=pvSitePower, load_voltage=pvLoadVoltage, ext_power_exp=pvPower)
                std_out="Date: "+str(pvDate)+" Time: " + str(pvTime) + " Watts: " + str(pvPower) + " Load Power: " + str(pvLoadPower) + " SOC: " + str(pvSOC) + " Site Power: " + str(pvSitePower) + " Load Voltage: " + str(pvLoadVoltage) +  " Battery Flow: "+str(pvBatteryFlow)+" Temp: " + str(pvTemp) + " Solar Voltage: " + str(pvVoltage)
                logger.info(std_out)
            else:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage)
                std_out="Date: "+str(pvDate)+" Time: " + str(pvTime) + " Watts: " + str(pvPower) + " Solar Voltage: " + str(pvVoltage)
                logger.info(std_out)
        else:
            logger.info('No data sent')

    except StandardError as e:
        logger.info('Main: Sleeping 5 minutes ' + str(e) )
        time.sleep(60*5)