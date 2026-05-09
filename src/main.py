#------------------------------------------------------------------------------------
#Copyright (c) 2023, MalkasianGroup, LLC - All rights reserved.
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
# DO NOT DELETE THIS FILE - SYSTEM WILL NOT BOOT OR RUN.
#------------------------------------------------------------------------------------
import gc
from PicoOS import connect_wifi, pico_os_main, start_wifi_monitoring, log_info, log_error

#----------------------------------MAIN PROGRAM---------------------------------------

log_info("=== PicoLED Controller Boot Sequence ===")
log_info("Performing initial memory cleanup...")
gc.collect()

log_info("Attempting WiFi connection...")
connection_result = connect_wifi()

# Start WiFi monitoring if connection successful
if connection_result == "connected":
    log_info("WiFi connected successfully - starting health monitoring")
    start_wifi_monitoring()
else:
    log_error("WiFi connection failed - continuing without monitoring")

log_info("Starting main application...")
pico_os_main()