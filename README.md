# Powerwall2PVOutput
Send Tesla Powerwall data to PVOutput

Currently in Beta, my first Git project.

2 processes  
-PW_Datalogger - Hits your powerwall every 5 seconds and stores the data in a sqlite db.  
-PW_PVOExport - Designed to be run every N minutes by a scheduler (e.g. Cron) will get your last update from PVOutput and send any outstanding data to it.

You will need a paid account in PVO for this to work properly, due to sending extended data.

I will post the PVO setup shortly.
