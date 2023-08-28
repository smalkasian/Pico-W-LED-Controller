#------------------------------------------------------------------------------------
#Copyright (c) 2023, MalkasianGroup, LLC - All rights reserved.
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
# DO NOT DELETE THIS FILE - SYSTEM WILL NOT BE ABLE TO RUN UPDATES
#------------------------------------------------------------------------------------

import gc
import machine
import urequests
import re
import _thread
import time
from PicoOS import lights_off, led_fail_flash, led_fail_flash, led_update_status, led_success_flash
import uos

thread_flag = False


def update_software():
    global thread_flag
    update_url = 'http://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/build/PicoOS.py'
    temp_file = "PicoOS_temp.py"
    current_file = "PicoOS.py"
    backup_file = "PicoOS_backup.py"

    def download_update():
        gc.collect()
        print("Fetching update from:", update_url)
        response = urequests.get(update_url)
        if response.status_code == 200:
            print("Received update data. Writing to temp file...")  # Progress message
            with open(temp_file, "w") as f:
                f.write(response.text)
            return True
        else:
            print(f"Error: Received status code {response.status_code}")  # Progress message
            led_fail_flash()
            return False

    def backup_current():
        print("Backing up current OS...")  # Progress message
        uos.rename(current_file, backup_file)
        return True

    def apply_update():
        print("Applying update...")  # Progress message
        uos.rename(temp_file, current_file)
        thread_flag = True
        lights_off()
        led_success_flash()
        return True

    def restore_backup():
        print("Restoring old OS...")  # Progress message
        uos.rename(backup_file, current_file)

    gc.collect()
    print("Starting software update...")
    try:
        _thread.start_new_thread(led_update_status, ())
    finally:
        pass
    
    try:
        if download_update() and backup_current() and apply_update():
            print("Update completed successfully.")  # Progress message
            machine.reset()
        else:
            raise Exception("Failed to complete one of the steps.")
    except Exception as e:
        thread_flag = True
        print(f"Update Failed. Error: {e}")  # Progress message
        led_fail_flash()
        try:
            restore_backup()
            print("Restored old OS due to error.")  # Progress message
        except:
            print("Could not restore old OS. Device may be in an unstable state.")  # Progress message
    finally:
        machine.reset()