#!/usr/bin/env python
import time
import PW_Helper as hlp
import PW_Config as cfg

hlp.setup_logging(cfg.log_file)
logger = hlp.logging.getLogger(__name__)
logger.info('Start PVOutput datalogger')

while True:
    try:
    	pw=hlp.getPowerwallData(cfg.PowerwallIP)
        soc=hlp.getPowerwallSOCData(cfg.PowerwallIP)
        if (pw!=False and soc!=False):
            lpvPower=float(pw['solar']['instant_power'])
            lpvVoltage=float(pw['solar']['instant_average_voltage'])
            lpvBatteryFlow=float(pw['battery']['instant_power'])
            lpvLoadPower=float(pw['load']['instant_power'])
            lpvSitePower=float(pw['site']['instant_power'])
            lpvLoadVoltage=float(pw['load']['instant_average_voltage'])
            lpvSOC=float(soc['percentage'])
            values=(lpvPower,lpvLoadPower,0,lpvVoltage,lpvBatteryFlow,lpvLoadPower,lpvSOC,lpvSitePower,lpvLoadVoltage)
            hlp.insertdb(cfg.sqlite_file, values)
        else:
            logger.info('No data received, retrying')
        time.sleep(5)
        
    except StandardError as e:
        logger.info('Main: Sleeping 5 minutes ' + str(e) )
        time.sleep(60*5)