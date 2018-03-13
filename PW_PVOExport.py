#!/usr/bin/env python
import datetime
import PW_Helper as hlp
import PW_Config as cfg

hlp.setup_logging(cfg.log_file)
logger = hlp.logging.getLogger(__name__)
logger.info('Start PVOutput export')

try:
    pvoutz = hlp.Connection(cfg.pvo_key, cfg.pvo_systemid, cfg.pvo_host)
    PVOStatus = pvoutz.get_status()
    pvodate = PVOStatus.split(",")[0]
    pvotime = PVOStatus.split(",")[1]
    sqldate = str(datetime.datetime.strptime(pvodate + " " + pvotime, "%Y%m%d %H:%M"))
    rows = hlp.get_sqlite_data(cfg.sqlite_file, sqldate)
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
            if cfg.extData==True:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage, battery_flow=pvBatteryFlow, load_power=pvLoadPower, soc=pvSOC, site_power=pvSitePower, load_voltage=pvLoadVoltage, ext_power_exp=pvPower)
                std_out="Date: "+str(pvDate)+" Time: " + str(pvTime) + " Watts: " + str(pvPower) + " Load Power: " + str(pvLoadPower) + " SOC: " + str(pvSOC) + " Site Power: " + str(pvSitePower) + " Load Voltage: " + str(pvLoadVoltage) +  " Battery Flow: "+str(pvBatteryFlow)+" Temp: " + str(pvTemp) + " Solar Voltage: " + str(pvVoltage)
                logger.info(std_out)
            else:
                pvoutz.add_status(pvDate, pvTime, power_exp=pvPower, power_imp=pvConsumption, temp=pvTemp, vdc=pvVoltage)
                std_out="Date: "+str(pvDate)+" Time: " + str(pvTime) + " Watts: " + str(pvPower) + " Solar Voltage: " + str(pvVoltage)
                logger.info(std_out)
    else:
        logger.info("No data returned")               

except Exception as err:
    logger.info("[ERROR] %s" % err)

#clean up db
hlp.delete_sqlite_data(cfg.sqlite_file, cfg.retain_days)

logger.info('End PVOutput export')