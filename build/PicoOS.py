#------------------------------------------------------------------------------------
#Copyright (c) 2023, MalkasianGroup, LLC - All rights reserved.
#------------------------------------------------------------------------------------
#This source code is licensed under the BSD-style license found in the
#LICENSE file in the root directory of this source tree. 

#-----------------------------READ ME BEFORE USING!!!!!!-----------------------------
# This code should run just fine on a pico. I am in the process of adding more colors 
# and eventually a color slider bar. 
# If you see a section that has (!!), it means you need to update that information with 
# your own otherwise the code will not work.
#
# If you run into issues or need help with the code, please feel free to reach out!
# malkasiangroup@gmail.com
#
#--------------------------------------------------------------------------------------
print("UNSTABLE - BUILT VERSION - BETA 1.5.0b")
def deliver_current_version():
    __version__ = (1,5,0)
    return __version__

#------------------------------------CHANGELOG-----------------------------------------
# UPDATES: 1.4.6
# • Patched version display. Displays after the page loads
# • Made minor tweaks to the web page.
# • Fixed page load times from 7 secs to 4 secs.
# UPDATES: 1.4.7
# • Added "yellow, cyan, magenta, teal, pink, amber, lime" colors.
# UPDATES: 1.5.0 (MAJOR UPDATES COMING)
# • Virtual sunrise that lets you select the custom time for sunrise and wakeup.
# • Added logic for optional motion detector feature.

# KNOWN ISSUES:
# (IN 1.4.3) Lights hang and get stuck on red while fading. Also needs to be a little faster. (FIXED? Issue was that led only looped once.)
# (ALL VERSIONS) Text align issue when trying to pull in the index.html file causing it to fail page load.
# (ALL VERSIONS) when trying to pull in the index.html "Connection closed due to Exception:  'NoneType' object has no attribute 'replace'"
# (ALL VERSIONS) "An exception occurred - list indices must be integers, not str" (when SSID has numbers or spaces).
# (IN 1.4.4 ON) When switching from strobe to fade, generates a memeory error. Needs to press btn twice.

# IN PROGRESS/NEEDS TESTING:
# - Adding timer button that turns the lights off. Not sure how to handle. Threadding?
# - Flashing lights between colors.
# - Feature to turn on the lights as a virtual sunrise/sunset. Let the user set the time range they power on.
# - Lights dim on to white when a motion sensor is connected and stay on for 60 seconds and then fade out.
# - Added new light "white" in case the strip has stand-alone white lights (called anytime white is).
#------------------------------------IMPORTS-----------------------------------------

try:
    import usocket as socket
except ImportError:
    import socket
import urequests
import random
import time
import utime as time
import network
import errno
import gc
import _thread
import json
import re
from machine import Pin, PWM
import uos
import machine
from system_utilities import update_software


#----------------------------INITIAL VAR ASSIGNMENT/TASKS---------------------------

# LED GPIO ASSIGNMENT (!!
red = PWM(Pin(0))
green = PWM(Pin(1))
blue = PWM(Pin(2))
white = PWM(Pin(3))
pir = Pin(5, Pin.IN, Pin.PULL_UP)

red.freq(1000)
green.freq(1000)
blue.freq(1000)
white.freq(1000)

isOn = False
brightness = 65025
thread_flag = False

# baton = _thread.allocate_lock()

#------------------------------------WIRELESS FUNCTIONS-----------------------------

def yes_validator():
    userYesNo = input("[yes/no]: ")
    while userYesNo.lower() not in ['yes', 'no']:
        userYesNo = input("Invalid entry: Please enter yes or no: ")
    else:
        if userYesNo == 'yes':
            print("")
            return userYesNo
        elif userYesNo == 'no':
            return userYesNo
        
def number_option_validator():
    user_choice = input("Choose a network -- [1] [2] [3] [4] [5]: ")
    while user_choice not in ["1", "2", "3", "4", "5"]:
        user_choice = input("Invalid entry: Please enter a valid number: ")
    else:
        if user_choice == '1':
            print("")
            return 0
        elif user_choice == '2':
            print("")
            return 1
        elif user_choice == '3':
            print("")
            return 2
        elif user_choice == '4':
            print("")
            return 3
        if user_choice == '5':
            print("")
            return 4

def lights_off():
    red.duty_u16(0)
    green.duty_u16(0)
    blue.duty_u16(0)
    white.duty_u16(0)

def led_success_flash():
    for i in range(10):
        green.duty_u16(65025)
        time.sleep(0.1)
        green.duty_u16(0)
        time.sleep(0.1)
    green.duty_u16(65025)
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
        time.sleep(1.5)
    lights_off()

def load_wifi_credentials():
    DEFAULT_CREDENTIALS = {
    "ssid": "DEFAULT_SSID",
    "password": "DEFAULT_PASSWORD"
    }
    try:
        with open('wifipasswords.json', 'r') as file:
            data = json.load(file)
            if isinstance(data, dict) and 'ssid' in data and 'password' in data:
                return data
            else:
                raise ValueError("Invalid format in 'wifipasswords.json'")
    except (OSError, ValueError):
        with open('wifipasswords.json', 'w') as file:
            json.dump(DEFAULT_CREDENTIALS, file)
        return DEFAULT_CREDENTIALS

def update_wireless_password(ssid, password):
    station = network.WLAN(network.STA_IF)
    lights_off()
    red.duty_u16(50000)
    print("")
    print("")
    print("Current SSID & Password:")
    print("--------------------------------")
    print(f"SSID: {ssid}")
    print(f"Password: {password}")
    print("--------------------------------")
    print("")
    print("Would you like to update the password?")
    update_credentials = yes_validator()
    if update_credentials == "yes":
        new_ssid = input("Enter your WiFi SSID: ")
        new_password = input("Enter your WiFi password: ")
        new_credentials = {"ssid": new_ssid, "password": new_password}
        with open('wifipasswords.json', "w") as file:
            json.dump(new_credentials, file)
        station.active(True)
        station.connect(new_ssid, new_password)
        lights_off()
        pulse_direction = 10
        max_retries = 50
        brightness = 0
        while not station.isconnected() and max_retries > 0:
            brightness += pulse_direction * 1000
            if brightness >= 50000:
                brightness = 50000
                pulse_direction = -5
            elif brightness <= 0:
                brightness = 0
                pulse_direction = 5
            red.duty_u16(brightness)
            green.duty_u16(int(brightness*0.5))
            blue.duty_u16(0)
            max_retries -= 1
            time.sleep(0.1)
        if not station.isconnected():
            print("Failed to connect with the new credentials. Trying again in 5 seconds.")
            time.sleep(5)
            connect_wifi()
    elif update_credentials == "no":
        print("Device will not work without WiFi.")
        print("Powering Down.")
        lights_off()
        for i in range(2): 
            red.duty_u16(65025)
            time.sleep(0.1)
            red.duty_u16(0)
            time.sleep(0.1)
            red.duty_u16(0)
        station.disconnect()
        station.active(False)
        lights_off()

def connect_wifi():
    data = load_wifi_credentials()
    station = network.WLAN(network.STA_IF)
    try:
        ssid = data["ssid"]
        password = data["password"]
        station.active(True)
        station.connect(ssid, password)
        max_retries = 50
        pulse_direction = 10
        brightness = 0
        while not station.isconnected() and max_retries > 0:
            brightness += pulse_direction * 1000
            if brightness >= 50000:
                brightness = 50000
                pulse_direction = -5
            elif brightness <= 0:
                brightness = 0
                pulse_direction = 5
            red.duty_u16(brightness)
            green.duty_u16(int(brightness * 0.5))
            blue.duty_u16(0)
            max_retries -= 1
            time.sleep(0.1)
        if station.isconnected():
            lights_off()
            print('Connection successful!')
            print(station.ifconfig())
            led_success_flash()
        else:
            print("Connection Failed: No specific reason identified")
            red.duty_u16(0)
            green.duty_u16(0)
            blue.duty_u16(0)
            for i in range(5):
                red.duty_u16(65025)
                time.sleep(0.1)
                red.duty_u16(0)
                time.sleep(0.1)
                red.duty_u16(0)
            update_wireless_password(ssid, password)
    except KeyError:
        print("Connection Failed: No Valid Password Record")
        update_wireless_password(ssid, password)
    except Exception as e:
        print("Connection Failed: An exception occurred -", e)

#------------------------------------GENERAL FUNCTIONS------------------------------

def check_remote_version(): #CHECKS FOR BUILD VERSION UPDATES ONLY!!! DO NOT PASTE THIS INTO SRC
    try:
        remote_version_url = 'http://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/build/PicoOS.py'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = urequests.get(remote_version_url, headers=headers)
        print("Status Code:", response.status_code)
        
        if response.status_code == 200:
            match = re.search(r'__version__ = \((\d+,\d+,\d+)\)', response.text)
            if match:
                version_string = match.group(1)
                version_components = tuple(map(int, version_string.split(',')))
                return version_components
    except Exception as e:
        print("Error:", e)
    return None

def deliever_local_version_to_web_page():
    __version__ = deliver_current_version()
    dot_seperated_local_verson = '.'.join(map(str, __version__))
    return dot_seperated_local_verson

def deliever_remote_version_to_web_page():
    __remote_version__ = check_remote_version()
    dot_separated_remote_version = '.'.join(map(str, __remote_version__))
    return dot_separated_remote_version

def check_for_update():
    try:
        local_version = deliver_current_version()
        remote_version = check_remote_version()
        display_remote_version = deliever_remote_version_to_web_page()
        display_local_version = deliever_local_version_to_web_page()
        if remote_version is None:
            return "Failed to fetch remote version. Try again in a little bit."
        elif remote_version == local_version:
            return f"{display_local_version} is the current version. You are up to date!"
        elif remote_version > local_version:
            return f"Version {str(display_remote_version)} is available."
        else:
            return "Version Check Failed. Try again in a little bit."
    except Exception as e:
        return f"Version Check Failed: {e}. Try again in a little bit."

def software_update_request():
    try:
        local_version = deliver_current_version()
        remote_version = check_remote_version()
        if remote_version is None:
            update_message = "Failed to fetch remote version."
        elif remote_version == local_version:
            update_message = (f"{local_version} is the current version. No update needed!")
        elif remote_version > local_version:
            update_message = "Updating software. Please wait."
            update_software()
    except Exception as e:
        update_message = "FAILED TO GET UPDATE"
        print("Error:", e)
    return update_message

def generate_updated_web_page():
    html_template = web_page()
    try:
        current_version = deliver_current_version()
        update_message = check_for_update()

        updated_html = html_template.replace("{{ current_version }}", str(current_version) if current_version else "Unknown")
        updated_html = updated_html.replace("{{ update_message }}", str(update_message))

    except OSError as e:
        if e.errno == errno.ENOMEM:
            print("System out of memory")
            updated_html = "Error: System out of memory"  # Or provide some default/fallback HTML here
        else:
            print("Error:", e)
            updated_html = "Error: " + str(e)  # Or provide some default/fallback HTML here (Maybe add in the future?)
    return updated_html

def set_brightness(brightnessChoice):
    global brightness
    if brightnessChoice == "bright":
        brightness = 65025
    elif brightnessChoice == "medium":
        brightness = 40000
    elif brightnessChoice == "dim":
        brightness = 20000
    else:
        return 'Invalid brightness'
    LED_colors()
    return 'Brightness successfully changed'

def change_color(color):
    global current_color, isOn, thread_flag
    if color in ["fade", "strobe", "sunrise", "motion", "red", "green", "blue", "white", "purple", "orange", "softwhite", "yellow", "cyan", "magenta", "teal", "pink", "amber", "lime"]:
        isOn = True
        current_color = color
    elif color == "off":
        isOn = False
        thread_flag = True
        lights_off()
    else:
        return 'Invalid color'
    LED_colors()
    return 'Color successfully changed.'

def fade_lights():
    global current_color
    thread_flag = False
    lights_off()
    print("Starting color fade")
    fade_speed = .05 # Higher number = slower fade | Lower (into decimal) = faster fade
    color_values = list(range(0, 65026, 100))
    chunk_size = 10
    color_chunks = [color_values[i:i + chunk_size] for i in range(0, len(color_values), chunk_size)]
    while thread_flag == False:
        for chunk in color_chunks:
            if current_color != 'fade':
                return
            for i in chunk:
                if current_color != 'fade':
                    return
                red.duty_u16(65025 - i)
                blue.duty_u16(i)
                time.sleep(fade_speed)
        for chunk in color_chunks:
            if current_color != 'fade':
                return
            for i in chunk:
                if current_color != 'fade':
                    return
                blue.duty_u16(65025 - i)
                green.duty_u16(i)
                time.sleep(fade_speed)
        for chunk in color_chunks:
            if current_color != 'fade':
                return
            for i in chunk:
                if current_color != 'fade':
                    return
                green.duty_u16(65025 - i)
                red.duty_u16(i)
                time.sleep(fade_speed)

def strobe_lights():
    gc.collect()
    global brightness, thread_flag, isOn
    thread_flag = False
    print(thread_flag)
    if isOn:
        while thread_flag == False:
            red.duty_u16(brightness)
            green.duty_u16(0)
            blue.duty_u16(0)
            time.sleep(1)
            if thread_flag == True:
                break
            red.duty_u16(0)
            green.duty_u16(brightness)
            blue.duty_u16(0)
            time.sleep(1)
            if thread_flag == True:
                break
            red.duty_u16(0)
            green.duty_u16(0)
            blue.duty_u16(brightness)
            time.sleep(1)
            if thread_flag == True:
                break
            red.duty_u16(int(brightness * 0.6))
            green.duty_u16(0)
            blue.duty_u16(brightness)
            time.sleep(1)
            if thread_flag == True:
                break
            red.duty_u16(brightness)
            green.duty_u16(int(brightness * 0.3))
            blue.duty_u16(0)
            time.sleep(1)
            if thread_flag == True:
                break
            red.duty_u16(brightness)
            green.duty_u16(brightness)
            blue.duty_u16(0)
            time.sleep(1)
            if thread_flag == True:
                break
            red.duty_u16(0)
            green.duty_u16(brightness)
            blue.duty_u16(brightness)

# UPDATES: 1.5.0 (START) ----------------------------------------------------------------

def sunrise_lights(): # STILL NEEDS TIMER OPTION!!!
    led_setting_confirm_flash()
    #ADD - FUNCTION FOR TIME SELECTION about selecting the time you want it to start up at.
    global thread_flag
    thread_flag = False
    sunrise_duration = 30 * 60  # 30 minutes in seconds
    start_time = time.time()
    end_time = start_time + sunrise_duration
    while time.time() < end_time and not thread_flag:
        elapsed_time = time.time() - start_time
        progress = elapsed_time / sunrise_duration

        # Calculate brightness based on progress
        sunrise_brightness = int(progress * 65025)

        # Sunrise color transition: red to orange to yellow to white
        red_value = 65025
        green_value = int(sunrise_brightness * progress if progress < 0.5 else sunrise_brightness)
        blue_value = int(sunrise_brightness * (progress - 0.5) if progress > 0.5 else 0)

        red.duty_u16(red_value)
        green.duty_u16(green_value)
        blue.duty_u16(blue_value)

def auto_off(timer): # trying to avoi sleeping in the current version. It can cause the system to hang.
    # The function is not fully completed. Still need to fix the error generated when selecting the time.
    global thread_flag
    if thread_flag == False:
        if timer == "test":
            time.sleep(10)
            led_setting_confirm_flash()
        elif timer == "one":
            duration = 3600
        elif timer == "three":
            duration = 10800
        elif timer == "six":
            duration = 21600
    else:
        pass

def motion_detection(): # NOTES: Still needs to be tested if it's actilly working on the motion detection
    # Last left off adding the debugging to see where its getting to and if the flag is changing accordingly.
    global current_color, thread_flag
    MAX_BRIGHTNESS = 65025
    INCREMENT = 500  # Adjust this for a faster or slower fade
    DECREMENT = 500  # Adjust this for a faster or slower dimming
    SLEEP_INTERVAL = 0.1  # Adjust this for a faster or slower fade
    lights_off()
    print("Successfully started motion detection mode")
    brightness = 0
    if thread_flag == False:
        while current_color == 'motion':
            if pir.value() == 0:
                print("Motion detected")
                print(f"Thread Flag: {thread_flag}. PIR Sensor Value:", pir.value()) #Added for debugging
                while brightness < MAX_BRIGHTNESS:
                    if current_color != 'motion' or thread_flag:
                        return
                    brightness += INCREMENT
                    brightness = min(brightness, MAX_BRIGHTNESS)
                    red.duty_u16(brightness)
                    green.duty_u16(brightness)
                    blue.duty_u16(brightness)
                    white.duty_u16(brightness)
                    time.sleep(SLEEP_INTERVAL)
                print('simulate lights on for 60 seconds')
                time.sleep(5)
            else:
                print("Waiting for movement")
                print('simulating them dimming')
                while brightness > 0:
                    if current_color != 'motion' or thread_flag:
                        return
                    brightness -= DECREMENT
                    brightness = max(brightness, 0)
                    red.duty_u16(brightness)
                    green.duty_u16(brightness)
                    blue.duty_u16(brightness)
                    white.duty_u16(brightness)
                    time.sleep(SLEEP_INTERVAL)
                print('waiting briefly before checking again for movement')
                time.sleep(1)
    else:
        return

# UPDATES (END) ----------------------------------------------------------------

def LED_colors(): 
    global thread_flag
    if isOn:
        thread_flag = True
        gc.collect()
        lights_off()
        print(f"Updating LED. Color: {current_color}, Brightness: {brightness}, isOn: {isOn}")
        if current_color == "red":
            red.duty_u16(brightness)
            green.duty_u16(0)
            blue.duty_u16(0)
        elif current_color == "green":
            red.duty_u16(0)
            green.duty_u16(brightness)
            blue.duty_u16(0)
        elif current_color == "blue":
            red.duty_u16(0)
            green.duty_u16(0)
            blue.duty_u16(brightness)
        elif current_color == "white":
            red.duty_u16(brightness)
            green.duty_u16(brightness)
            blue.duty_u16(brightness)
            white.duty_u16(brightness)
        elif current_color == "purple":
            red.duty_u16(int(brightness*0.6))
            green.duty_u16(0)
            blue.duty_u16(brightness)
        elif current_color == "orange":
            red.duty_u16(brightness)
            green.duty_u16(int(brightness*0.3))
            blue.duty_u16(0)
        elif current_color == "softwhite":
            red.duty_u16(int(brightness / 65025 * 65535))
            green.duty_u16(int(brightness*0.7 / 65025 * 65535))
            blue.duty_u16(int(brightness*0.6 / 65025 * 65535))
            white.duty_u16(brightness)
        elif current_color == "yellow":
            red.duty_u16(brightness)
            green.duty_u16(brightness)
            blue.duty_u16(0)
        elif current_color == "cyan":
            red.duty_u16(0)
            green.duty_u16(brightness)
            blue.duty_u16(brightness)
        elif current_color == "magenta":
            red.duty_u16(brightness)
            green.duty_u16(0)
            blue.duty_u16(brightness)
        elif current_color == "teal":
            red.duty_u16(0)
            green.duty_u16(brightness)
            blue.duty_u16(int(brightness*0.5))
        elif current_color == "pink":
            red.duty_u16(brightness)
            green.duty_u16(int(brightness*0.4))
            blue.duty_u16(int(brightness*0.6))
        elif current_color == "amber":
            red.duty_u16(brightness)
            green.duty_u16(int(brightness*0.75))
            blue.duty_u16(0)
        elif current_color == "lime":
            red.duty_u16(int(brightness*0.75))
            green.duty_u16(brightness)
            blue.duty_u16(0)
        elif current_color == "fade":
            print(thread_flag)
            _thread.start_new_thread(fade_lights, ())
        elif current_color == "strobe":
            print(thread_flag)
            _thread.start_new_thread(strobe_lights, ())
        elif current_color == "sunrise":
            _thread.start_new_thread(sunrise_lights, ())
        elif current_color == "motion":
            _thread.start_new_thread(motion_detection, ())
        else:
            led_fail_flash()

def handle_change_color_request(color):
    print("Changing Color to:", color)
    return change_color(color)

def handle_change_brightness_request(brightness_choice):
    print("Changing Brightness to:", brightness_choice)
    return set_brightness(brightness_choice)

def handle_led_off_request():
    global current_color, thread_flag
    current_color = "off"
    thread_flag = True
    return change_color(current_color)

def web_page_UNUSED(): # CAN'T GET THIS TO WORK.
    try:
        with open('index.html', 'r') as file:
            html = file.read()
        html = html.format(str(isOn).lower(), current_color)
        return html
    except OSError as e:
        print('OSError:', str(e)) 
    except KeyError as ke:
        print('KeyError:', str(ke))
    except Exception as e:
        print('Exception:', str(e))

def web_page(): #NOTES: Test without the javascript and see of that helps the page load faster.
    # Also add the motion and sunrise button to a new page or button section.
    # Add javascript code for the auto off setting. Not sure how to handle the threading aspect of it...
    # Maybe try adding a new thread for each of those? I might need to add in a parse() feature for it.
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LED Light Control</title>
        <style>
            body{text-align:center;font-family:Arial,sans-serif;}h1{margin-top:20px;font-size:4vw;}h2,h3{font-size:3vw;}h2{font-weight:bold;}h3{font-weight:normal;}.button_container{display:flex;justify-content:center;align-items:center;}.button{display:inline-block;padding:10px 20px;margin:20px;border:none;border-radius:6px;cursor:pointer;font-size:4vw;text-align:center;outline:none;background-color:#ccc;color:#000;}.button:hover{background-color:#999;}.on{background-color:rgb(48,107,255);color:#fff;}.off{background-color:rgb(215,215,215);}.centered-text{display:flex;justify-content:center;align-items:center;text-align:center;padding-bottom:50px;}.button-box{margin:10px;padding:10px 50px 20px;background-color:#fff;border-radius:11px;text-align:center;box-shadow:2px 2px 30px rgba(0,0,0,0.2);max-width:auto;}.version-update{padding-top:50px;}
        </style>
    </head>
    <body>
        <div class="button-container">
            <div class="button-box">
                <h2>Power</h2>
                <button id="toggleButton" class="button off" onclick="toggleLED()">OFF</button>
                <br>
                <h3>Colors</h3>
                <button class="button" data-color='red'>Red</button>
                <button class="button" data-color='green'>Green</button>
                <button class="button" data-color='blue'>Blue</button>
                <button class="button" data-color='purple'>Purple</button>
                <button class="button" data-color='orange'>Orange</button>
                <button class="button" data-color='white'>White</button>
                <button class="button" data-color='softwhite'>Soft White</button>
                <button class="button" data-color='yellow'>Yellow</button>
                <button class="button" data-color='cyan'>Cyan</button>
                <button class="button" data-color='magenta'>Magenta</button>
                <button class="button" data-color='teal'>Teal</button>
                <button class="button" data-color='pink'>Pink</button>
                <button class="button" data-color='amber'>Amber</button>
                <button class="button" data-color='lime'>Lime</button>
                <br>
                <h3>Automatic Functions</h3>
                <button class="button" data-color='fade'>Color Fade</button>
                <button class="button" data-color='strobe'>Color Strobe</button>
                <button class="button" data-color='motion'>Motion Detection</button>
                <button class="button" data-color='sunrise'>Simulate Sunrise</button>
                <br>
                <h3>Brightness</h3>
                <button class="button" data-brightness='bright'>Bright</button>
                <button class="button" data-brightness='medium'>Medium</button>
                <button class="button" data-brightness='dim'>Dim</button>
                <h3>Auto-Off Timer</h3>
                <button class="button" data-timer='test'>Test</button>
                <button class="button" data-timer='one'>1-Hour</button>
                <button class="button" data-timer='three'>3-Hours</button>
                <button class="button" data-timer='six'>6-Hours</button>
            </div>
        </div>
        <div class = "version-update">
            <div class="version-display">
                <p>Controller Version: <span id="currentVersion">Loading...</span></p>
            </div>
            <p id="updateMessage">{{ Not Checked }}</p>
            <button class="button" onclick="checkUpdates()">Check for Updates</button>
            <button class="button" id="updateButton" style="display: none;" onclick="updateSoftware()">Update Software</button>
		</div>
        <p>Note from the developer: When you select an option where the lights have a delay </p>
        <p>(i.e., sunrise or auto off timer) the lights will flash teal to confirm the action was successful. </p>
        <script>
            var isOn = false;
            var current_color = "softwhite";
            
            window.onload = function() {
                setTimeout(fetchCurrentVersion, 5000); // Waits 5 seconds before calling
                document.querySelector('.button-container').addEventListener('click', function(event) {
                    if(event.target.classList.contains('button')) {
                        if(event.target.hasAttribute('data-color')) {
                            change_color(event.target.getAttribute('data-color'));
                        } else if(event.target.hasAttribute('data-brightness')) {
                            changeBrightness(event.target.getAttribute('data-brightness'));
                        } else if(event.target.hasAttribute('data-timer')) {
                            auto_off(event.target.getAttribute('data-timer'));
                        }
                    }
                });
            };

            function updateUI() {
                // Update the UI elements based on the current state
                var button = document.getElementById("toggleButton");
                button.innerHTML = isOn ? "ON" : "OFF";
                button.className = isOn ? "button on" : "button off";

                // Update color buttons or other elements as needed
            }
            
            function toggleLED() {
                var button = document.getElementById("toggleButton");
                if (isOn) {
                    button.innerHTML = "OFF";
                    button.className = "button off";
                    isOn = false;
                    change_color('off');
                    makeRequest('/led_off');
                } else {
                    button.innerHTML = "ON";
                    button.className = "button on";
                    isOn = true;
                    change_color(current_color);
                }
            }

            function change_color(color) {
                console.log("Trying to change color to: " + color); // Debugging line
                if (isOn) {
                    makeRequest('/change_color?color=' + color);
                }
            }
            
            function changeBrightness(brightnessChoice) {
                console.log("Selected brightness: " + brightnessChoice);
                if (isOn) {
                    makeRequest('/change_brightness?brightness=' + brightnessChoice);
                }
            }
            
            function auto_off(timer) {
                console.log("Selected Timer: " + timer);
                if (isOn) {
                    makeRequest('/auto_off?timer=' + timer);
                }
            }
            
            async function fetchCurrentVersion() {
                try {
                    let response = await fetch('/current_version');
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    let data = await response.text();
                    document.getElementById('currentVersion').innerText = data;
                } catch (error) {
                    document.getElementById('currentVersion').innerText = "Error: " + error.message;
                }
            }
            
            function checkUpdates() {
                fetch('/check_update')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    document.getElementById('updateMessage').innerText = data;
                    // If "Version" is found in the response, show the update button
                    if (data.includes("Version")) {
                        document.getElementById('updateButton').style.display = 'inline-block';
                    } else {
                        document.getElementById('updateButton').style.display = 'none';
                    }
                })
                .catch(error => {
                    document.getElementById('updateMessage').innerText = "Error: " + error.message;
                });
            }

            function updateSoftware() {
                fetch('/update_software')
                .then(response => response.text())
                .then(data => {
                    document.getElementById('updateMessage').innerText = data;
                });
            }

            let debounceTimer;
            function makeRequest(url) {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    var xhr = new XMLHttpRequest();
                    xhr.open("GET", url, true);
                    xhr.send();
                }, 300); // Debounce for 300ms
            }
        </script>
    </body>
    </html>
    """
    return html

def parse_request(request):
    request = str(request)
    if "/change_color" in request:
        color_start = request.find("/change_color?color=") + len("/change_color?color=")
        color_end = request.find(" ", color_start)
        color = request[color_start:color_end]
        print("Parsed Color:", color)
        return handle_change_color_request(color)
    if "/change_brightness" in request:
        brightness_start = request.find("/change_brightness?brightness=") + len("/change_brightness?brightness=")
        brightness_end = request.find(" ", brightness_start)
        brightness_choice = request[brightness_start:brightness_end]
        print("Parsed Brightness:", brightness_choice)
        return handle_change_brightness_request(brightness_choice)
    if "/led_off" in request:
        return handle_led_off_request()
    if "/auto_off" in request:
        auto_off_start = request.find("/auto_off?timer=") + len("/auto_off?timer=")
        auto_off_end = request.find(" ", auto_off_start)
        auto_off_choice = request[auto_off_start:auto_off_end]
        print("Auto-Off Timer:", auto_off_choice)
        return auto_off(auto_off_choice)
    
    if "/check_update" in request:
        return check_for_update()
    if "/update_software" in request:
        return software_update_request()
    if "/current_version" in request:
        return str(deliever_local_version_to_web_page())
    return ''

def start_web_server_OLD(): # TESTING OPTOMIZED SERVER LOGIC
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    while True:
        try:
            conn, addr = s.accept()
            conn.settimeout(3.0)
            print('Received HTTP GET connection request from %s' % str(addr))
            request = conn.recv(1024)
            request = request.decode('utf-8')
            conn.settimeout(None)
            response = ''  
            if "GET / " in request:
                response = generate_updated_web_page()
                response_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nConnection: close\r\n\r\n"
            else:
                response = parse_request(request)
                response_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n"
            full_response = response_headers + response
            conn.sendall(full_response.encode('utf-8'))
            conn.close()
        except OSError as e:
            conn.close()
            print('Connection closed due to OSError: ', str(e)) 
        except Exception as e:
            conn.close()
            print('Connection closed due to Exception: ', str(e))
    return s

def start_web_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)

    # Pre-load static content into memory
    static_html = web_page()

    while True:
        try:
            conn, addr = s.accept()
            conn.settimeout(3.0)
            print('Received HTTP GET connection request from %s' % str(addr))
            request = conn.recv(1024)
            request = request.decode('utf-8')
            conn.settimeout(None)
            
            # Splitting request to get the path
            path = request.split(" ")[1]

            if path == "/":
                # Only replace dynamic content here
                dynamic_content = {
                    '{{ current_version }}': str(deliever_local_version_to_web_page()),
                    '{{ update_message }}': check_for_update()
                }
                for key, value in dynamic_content.items():
                    static_html = static_html.replace(key, value)
                response_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=UTF-8\r\nConnection: close\r\n\r\n"
                full_response = response_headers + static_html
            else:
                response = parse_request(request)
                response_headers = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nConnection: close\r\n\r\n"
                full_response = response_headers + response
                
            conn.sendall(full_response.encode('utf-8'))
            conn.close()

        except OSError as e:
            conn.close()
            print('Connection closed due to OSError: ', str(e)) 
        except Exception as e:
            conn.close()
            print('Connection closed due to Exception: ', str(e))
    return s

def pico_os_main():
    s = ""
    gc.collect()
    try:
        while True:
            s = start_web_server()
    except KeyboardInterrupt:
        print('KeyboardInterrupt: Stopping the program...')
        lights_off()
        for i in range(5): 
            red.duty_u16(65025)
            green.duty_u16(65025)
            time.sleep(0.1)
            red.duty_u16(0)
            green.duty_u16(0)
            time.sleep(0.1)
            red.duty_u16(0)
            green.duty_u16(0)
        station = network.WLAN(network.STA_IF)
        station.disconnect()
        station.active(False)
        if s:
            s.close()
        print("System Disconnected")
    except Exception as e:
        print(f"Unexpected error: {e}")

#---------------------------------MAIN PROGRAM------------------------------------------
# FOR DEBUG USE. Allows software to run from here rather than main.py
# Comment out before pushing to devices.
gc.collect()
connect_wifi()
pico_os_main()