#!/usr/bin/env python
import time
import PW_Helper

sqlite_file = "pw.sqlite"
PowerwallIP = ""
log_file="datalogger.log"

PW_Helper.setup_logging(log_file)
logger = PW_Helper.logging.getLogger(__name__)
logger.info('Start PVOutput datalogger')
while True:
    try:
    	pw=PW_Helper.getPowerwallData(PowerwallIP)
        soc=PW_Helper.getPowerwallSOCData(PowerwallIP)
        if (pw!=False and soc!=False):
            lpvPower=float(pw['solar']['instant_power'])
            lpvVoltage=float(pw['solar']['instant_average_voltage'])
            lpvBatteryFlow=float(pw['battery']['instant_power'])
            lpvLoadPower=float(pw['load']['instant_power'])
            lpvSitePower=float(pw['site']['instant_power'])
            lpvLoadVoltage=float(pw['load']['instant_average_voltage'])
            lpvSOC=float(soc['percentage'])
            values=(lpvPower,0,0,lpvVoltage,lpvBatteryFlow,lpvLoadPower,lpvSOC,lpvSitePower,lpvLoadVoltage)
            PW_Helper.insertdb(sqlite_file, values)
        else:
            logger.info('No data received, retrying')
        time.sleep(5)
        
    except StandardError as e:
        logger.info('Main: Sleeping 5 minutes ' + str(e) )
        time.sleep(60*5)