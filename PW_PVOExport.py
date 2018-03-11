#!/usr/bin/env python
import datetime
import PW_Helper

sqlite_file = 'pw.sqlite'
pvo_host= "pvoutput.org"
pvo_key = ""
pvo_systemid = ""
extData = True
log_file="pvo.log"

PW_Helper.setup_logging(log_file)
logger = PW_Helper.logging.getLogger(__name__)
logger.info('Start PVOutput export')

try:
    pvoutz = PW_Helper.Connection(pvo_key, pvo_systemid, pvo_host)
    PVOStatus = pvoutz.get_status()
    pvodate = PVOStatus.split(",")[0]
    pvotime = PVOStatus.split(",")[1]
    sqldate = str(datetime.datetime.strptime(pvodate + " " + pvotime, "%Y%m%d %H:%M"))
    rows = PW_Helper.get_sqlite_data(sqlite_file, sqldate)
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