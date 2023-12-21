# NOT MEANT TO BE ADDED TO PICO FILESYSTEM.
import random
import utime as time
import gc
import _thread
import json
import re
from machine import Pin, PWM
import uos
import machine

#----------------------------INITIAL VAR ASSIGNMENT/TASKS---------------------------

# LED GPIO ASSIGNMENT (!!
red = PWM(Pin(0))
green = PWM(Pin(1))
blue = PWM(Pin(2))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

isOn = False
brightness = 65025
thread_flag = False



# Global variables
cancel_flag = False
scheduled_hour = 0
scheduled_minute = 0
scheduled_second = 0


#------------------------------------GENERAL FUNCTIONS------------------------------

def lights_off():
    red.duty_u16(0)
    green.duty_u16(0)
    blue.duty_u16(0)

def led_success_flash():
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
    lights_off()
    for i in range(5):
        red.duty_u16(65025)
        time.sleep(0.1)
        red.duty_u16(0)
        time.sleep(0.1)

def led_setting_confirm_flash():
    lights_off()
    for i in range(3):
        blue.duty_u16(65025)
        green.duty_u16(65025)
        time.sleep(0.1)
        blue.duty_u16(0)
        green.duty_u16(0)
        time.sleep(0.1)

#------------------------------------MAIN BODY FUNCTIONS------------------------------


scheduled_time = None
current_color = 'sunrise'

def check_and_run_task():
    while True:
        # Check if scheduled_time is set
        if scheduled_time is not None:
            # Get the current time
            current_time = datetime.datetime.now()

            # Check if the current time is equal to or has surpassed the scheduled time
            if current_time >= scheduled_time:
                # Run the task
                sunrise()

                # Reset the scheduled_time to None or set it to the next schedule
                scheduled_time = None

        # Sleep for a short duration to prevent high CPU usage
        time.sleep(1)
        return current_time

def sunrise(current_color):
    global current_time
    thread_flag = False
    lights_off()
    print(f"Starting sunrise simulation" {current_time}) #for debug
    total_duration = 1800 # Currently set to 30 mins
    num_steps = 2048  # More steps for smoother transition - currently set this way arbitrarily.
    step_duration = total_duration / num_steps

    initial_red_steps = int(num_steps * 0.1)  # 10% of the steps for initial fade-in
    red_to_orange_steps = int(num_steps * 0.5)  # Adjusted for 50% of the steps after initial red
    orange_to_white_steps = num_steps - red_to_orange_steps - initial_red_steps
    sunrise_stages = []

    for step in range(initial_red_steps):
        red_value = int((65535 / initial_red_steps) * step)
        green_value = 0
        blue_value = 0
        sunrise_stages.append((red_value, green_value, blue_value))
    for step in range(red_to_orange_steps):
        red_value = 65535
        green_value = int((32767 / red_to_orange_steps) * step)
        blue_value = 0
        sunrise_stages.append((red_value, green_value, blue_value))
    for step in range(orange_to_white_steps):
        red_value = 65535
        green_value = 32767 + int((32768 / orange_to_white_steps) * step)
        blue_value = int((65535 / orange_to_white_steps) * step)  
        sunrise_stages.append((red_value, green_value, blue_value))
    
    while not thread_flag:
        for stage in sunrise_stages:
            if current_color != 'sunrise':
                return
            red.duty_u16(stage[0])
            green.duty_u16(stage[1])
            blue.duty_u16(stage[2])
            time.sleep(step_duration)

# Example usage
check_and_run_task(sunrise(current_color))