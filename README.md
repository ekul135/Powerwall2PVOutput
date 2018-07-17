# Powerwall2PVOutput
Send Tesla Powerwall 2 data to PVOutput

#### Note code has been updated to work with https, firmware versions 1.17+

2 options  
-Datalogger - Collects data on site and then send to PVO, allowing for internet outages or PVO outages  
-Simple - No data collection, simply picks up the data and sends  

#### Datalogger
2 processes  
-PW_Datalogger - Hits your Powerwall 2 every 5 seconds and stores the data in a sqlite db.  
-PW_PVOExport - Designed to be run every N minutes by a scheduler (e.g. Cron) will get your last update from PVOutput and send any outstanding data to it.  
This can be run in 2 modes, either sending extended data or not.  Just set the extData variable to False if you do not want the extended data sent.

#### Simple  
For those people who do not care about losing solar data due to internet outages etc. I have created a simple script called  
PW_Simple, this is designed to run all the time, will collect PW data every 5 seconds and send an average every 5 minutes.  
This can also be run in 2 modes, either sending extended data or not.  Just set the extData variable to False if you do not want the extended data sent.

If sending extended data, you will need a paid account in PVO for this to work properly  

##### PVO Setup for extended data:

![alt text](https://github.com/ekul135/Powerwall2PVOutput/blob/master/ExtendedData7_8.png)
![alt text](https://github.com/ekul135/Powerwall2PVOutput/blob/master/ExtendedData9_12.png)
