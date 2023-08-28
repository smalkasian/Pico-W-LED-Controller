#------------------------------------------------------------------------------------
#Copyright (c) 2023, MalkasianGroup, LLC - All rights reserved.
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
# DO NOT DELETE THIS FILE - SYSTEM WILL NOT BOOT OR RUN.
#------------------------------------------------------------------------------------
import gc
import machine
import urequests
import re
import _thread
import time
from PicoOS import connect_wifi, lights_off, led_fail_flash, led_fail_flash, led_update_status, led_success_flash, pico_os_main
import uos

#-------------------------------------------------------------------------------------


#----------------------------------MAIN PROGRAM---------------------------------------

gc.collect()
connect_wifi()
pico_os_main()
