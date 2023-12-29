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
white = PWM(Pin(3)) #
pir = Pin(5, Pin.IN, Pin.PULL_UP)

red.freq(1000)
green.freq(1000)
blue.freq(1000)
white.freq(1000)

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


def motion_detection():
    global current_color, thread_flag
    MAX_BRIGHTNESS = 65025
    INCREMENT = 500  # Adjust for faster or slower fade
    DECREMENT = 500  # Adjust for faster or slower dimming
    SLEEP_INTERVAL = 0.1  # Adjust for speed of fade
    MOTION_DETECTED_DURATION = 3  # Time in seconds lights stay on after motion detected

    def set_light_brightness(brightness_value):
        # Replace with your actual LED control logic
        red.duty_u16(brightness_value)
        green.duty_u16(brightness_value)
        blue.duty_u16(brightness_value)
        white.duty_u16(brightness_value)

    def adjust_brightness(target_brightness):
        nonlocal brightness
        while brightness != target_brightness:
            if current_color != 'motion' or thread_flag:
                return
            step = INCREMENT if brightness < target_brightness else -DECREMENT
            brightness = max(min(brightness + step, MAX_BRIGHTNESS), 0)
            set_light_brightness(brightness)
            time.sleep(SLEEP_INTERVAL)

    # Initialize the brightness to 0 (lights off)
    brightness = 0
    set_light_brightness(brightness)

    if thread_flag:
        return

    while current_color == 'motion':
        # Check PIR sensor value (assuming 1 is motion detected)
        if pir.value() == 1:
            print("Motion detected")
            adjust_brightness(MAX_BRIGHTNESS)
            time.sleep(MOTION_DETECTED_DURATION)  # Keep lights on for a set duration
        else:
            if brightness > 0:  # Only dim if the lights are on
                print("No movement detected - dimming lights")
                adjust_brightness(0)

        time.sleep(.5)  # Wait a bit before checking for motion again

# Example usage
current_color = 'motion'
thread_flag = False
motion_detection()