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
from PicoOS import connect_wifi, pico_os_main
import uos

#-------------------------------------------------------------------------------------

def update_software():
    update_url = 'http://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/src/PicoOS.py'
    temp_file = "PicoOS_temp.py"
    backup_file = "PicoOS_backup.py"
    try:
        response = urequests.get(update_url)
        if response.status_code == 200:
            update_content = response.text()
            with open(temp_file, "w") as f:
                f.write(update_content)
            uos.rename("PicoOS.py", backup_file) # Backup the current OS
            uos.rename(temp_file, "PicoOS.py") # Replace with downloaded file  
            print("Update completed successfully.")
            machine.reset
        else:
            print("Failed to fetch the update.")
    except Exception as e:
        # In case of any error, restore the original file from backup (if needed)
        if uos.path.exists(backup_file):
            uos.rename(backup_file, "PicoOS.py")
        print("Update failed:", e)

#----------------------------------MAIN PROGRAM---------------------------------------


gc.collect()
connect_wifi()
time.sleep(5)
pico_os_main()