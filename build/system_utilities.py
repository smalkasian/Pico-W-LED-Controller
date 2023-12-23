#------------------------------------------------------------------------------------
#Copyright (c) 2023, MalkasianGroup, LLC - All rights reserved.
#------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------
# DO NOT DELETE THIS FILE - SYSTEM WILL NOT BE ABLE TO RUN UPDATES.
#------------------------------------------------------------------------------------
# VERSION 1.0.0
#------------------------------------------------------------------------------------

import gc
import machine
import urequests
import re
import _thread
import time
import uos
from machine import Pin, PWM
thread_flag = False

red = PWM(Pin(0))
green = PWM(Pin(1))
blue = PWM(Pin(2))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

def lights_off():
    red.duty_u16(0)
    green.duty_u16(0)
    blue.duty_u16(0)

def led_success_flash():
    lights_off()
    for i in range(10):
        green.duty_u16(65025)
        time.sleep(0.1)
        green.duty_u16(0)
        time.sleep(0.1)
    green.duty_u16(65025)
    time.sleep(1)
    lights_off()

def led_update_status():
    lights_off()
    global thread_flag
    brightness = 50000
    while thread_flag == False:
        for brightness in range(0, 65536, 500):
            blue.duty_u16(brightness)
            red.duty_u16(brightness)
            time.sleep(0.01)
        for brightness in range(65535, -1, -500):
            blue.duty_u16(brightness)
            red.duty_u16(brightness)
            time.sleep(0.01)
        time.sleep(0.1)

def led_fail_flash():
    time.sleep(2)
    lights_off()
    for i in range(5):
        red.duty_u16(65025)
        time.sleep(0.1)
        red.duty_u16(0)
        time.sleep(0.1)
        red.duty_u16(0)
    gc.collect()

#THIS IS THE BUILD VERSION. IT WILL PULL BUILD UPDATES.
def update_software():
    gc.collect()
    global thread_flag
    update_url = 'https://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/build/PicoOS.py'
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
            thread_flag = True
            lights_off()
            led_success_flash()
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
