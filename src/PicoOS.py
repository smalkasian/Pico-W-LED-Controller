#------------------------------------------------------------------------------------
#Copyright (c) 2023, MalkasianGroup, LLC - All rights reserved.
#------------------------------------------------------------------------------------
#This source code is licensed under the BSD-style license found in the
#LICENSE file in the root directory of this source tree. 

#-----------------------------READ BEFORE USING!!!!!!-----------------------------
# This code should run just fine on a pico. I am in the process of adding more colors 
# and eventually a color slider bar. 
# If you see a section that has (!!), it means you need to update that information with 
# your own otherwise the code will not work.
#
# If you run into issues or need help with the code, please feel free to reach out!
# malkasiangroup@gmail.com
#
#--------------------------------------------------------------------------------------
print("STABLE - SOURCE VERSION - 1.5.0")
def deliver_current_version():
    __version__ = (1,5,1)
    return __version__

#------------------------------------CHANGELOG-----------------------------------------
# UPDATES: 1.4.6
# • Patched version display. Displays after the page loads
# • Made minor tweaks to the web page.
# • Fixed page load times from 7 secs to 4 secs.
# UPDATES: 1.4.7
# • Added "yellow, cyan, magenta, teal, pink, amber, lime" colors.
# UPDATES: 1.5.0
# • Added logic for optional motion detector feature.
# • Added version tracking to the webpage
# UPDATES: 1.5.1
# • Quick update for the motion detection. Lowers the sensitivity and adds 2 second "positive" before turning on lights.

# KNOWN ISSUES:
# (IN 1.4.3) Lights hang and get stuck on red while fading. Also needs to be a little faster. (FIXED? Issue was that led only looped once.)
# (ALL VERSIONS) Text align issue when trying to pull in the index.html file causing it to fail page load.
# (ALL VERSIONS) when trying to pull in the index.html "Connection closed due to Exception:  'NoneType' object has no attribute 'replace'"
# (ALL VERSIONS) "An exception occurred - list indices must be integers, not str" (when SSID has numbers or spaces).
# (IN 1.4.4 ON) When switching from strobe to fade, generates a memeory error. Needs to press btn twice.

# IN PROGRESS/NEEDS TESTING:
# - Feature to turn on the lights as a virtual sunrise/sunset. Let the user set the time range they power on.

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

#------------------------------------LOGGING SYSTEM---------------------------------

def log(message, level="INFO"):
    """Enhanced logging with timestamps and levels"""
    try:
        # Get current time (basic format since RTC might not be set)
        timestamp = time.ticks_ms() // 1000
        formatted_msg = f"[{timestamp}s] {level}: {message}"
        print(formatted_msg)

        # Optional: Write to log file (if storage available)
        try:
            with open('system.log', 'a') as f:
                f.write(formatted_msg + '\n')
        except:
            pass  # Fail silently if can't write to file
    except:
        # Fallback to basic print if logging fails
        print(f"{level}: {message}")

def log_info(message):
    log(message, "INFO")

def log_warning(message):
    log(message, "WARN")

def log_error(message):
    log(message, "ERROR")

def log_debug(message):
    log(message, "DEBUG")

def log_system_status():
    """Log current system status for monitoring"""
    try:
        # WiFi status
        station = network.WLAN(network.STA_IF)
        if station.isconnected():
            ip_info = station.ifconfig()
            log_info(f"System Status: WiFi Connected - IP: {ip_info[0]}")
        else:
            log_warning("System Status: WiFi Disconnected")

        # Memory status
        gc.collect()
        log_info(f"System Status: Memory cleaned, thread_flag: {thread_flag}")

        # LED status
        log_info(f"System Status: LED State: {'ON' if isOn else 'OFF'}, Color: {globals().get('current_color', 'unknown')}")

    except Exception as e:
        log_error(f"Error checking system status: {e}")

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
current_color = "off"

# baton = _thread.allocate_lock()

#------------------------------------WIRELESS FUNCTIONS-----------------------------



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
    for i in range(4):
        blue.duty_u16(65025)
        green.duty_u16(65025)
        time.sleep(0.1)
        blue.duty_u16(0)
        green.duty_u16(0)
    time.sleep(1.5)

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

def connect_wifi():
    data = load_wifi_credentials()
    station = network.WLAN(network.STA_IF)
    ssid = data["ssid"]
    password = data["password"]

    # Try connecting with multiple attempts and longer timeouts
    connection_attempts = 3
    log_info(f"Starting WiFi connection to '{ssid}' ({connection_attempts} attempts max)")

    for attempt in range(connection_attempts):
        try:
            log_info(f"WiFi connection attempt {attempt + 1} of {connection_attempts}")

            # Reset WiFi module for clean state
            station.active(False)
            time.sleep(0.5)
            station.active(True)
            time.sleep(1)  # Give WiFi module time to activate

            # Configure power management for better stability
            station.config(pm=0xa11140)  # Disable power saving for stable connection
            log_debug("WiFi power management configured for stability")

            # Scan for networks to verify SSID exists
            log_debug("Scanning for available networks...")
            networks = station.scan()
            log_info(f"Found {len(networks)} networks in scan")

            network_found = False
            for net in networks:
                if net[0].decode('utf-8') == ssid:
                    network_found = True
                    signal_strength = net[3]
                    log_info(f"Target network '{ssid}' found with signal: {signal_strength} dBm")
                    break

            if not network_found:
                log_warning(f"Network '{ssid}' not found in scan")
                if attempt < connection_attempts - 1:
                    log_info("Waiting 3 seconds before retry...")
                    time.sleep(3)
                    continue

            log_info(f"Connecting to '{ssid}'...")
            station.connect(ssid, password)

            # Longer timeout - up to 20 seconds per attempt
            max_retries = 200
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

                # Check for connection status changes
                if max_retries % 50 == 0:
                    status = station.status()
                    log_debug(f"Connection status: {status}, retries left: {max_retries}")

            if station.isconnected():
                lights_off()
                log_info('WiFi connection successful!')
                ip_info = station.ifconfig()
                log_info(f"Network details - IP: {ip_info[0]}, Subnet: {ip_info[1]}, Gateway: {ip_info[2]}")
                led_success_flash()
                return "connected"
            else:
                log_warning(f"Attempt {attempt + 1} failed - will retry...")
                station.disconnect()
                time.sleep(2)

        except Exception as e:
            log_error(f"WiFi error on attempt {attempt + 1}: {e}")
            station.disconnect()
            time.sleep(2)

    # All attempts failed
    log_error("All WiFi connection attempts failed")
    lights_off()
    for i in range(5):
        red.duty_u16(65025)
        time.sleep(0.2)
        red.duty_u16(0)
        time.sleep(0.2)

    # Don't automatically trigger password update - let user decide
    log_error("WiFi connection failed. Check credentials or signal strength.")
    return "failed"

# WiFi health check timing
last_wifi_check = 0
WIFI_CHECK_INTERVAL = 30000  # 30 seconds in milliseconds

def check_wifi_health():
    """Non-blocking WiFi health check - runs on Core 0"""
    global last_wifi_check
    current_time = time.ticks_ms()

    # Only check every 30 seconds
    if time.ticks_diff(current_time, last_wifi_check) < WIFI_CHECK_INTERVAL:
        return

    last_wifi_check = current_time

    try:
        station = network.WLAN(network.STA_IF)
        if not station.isconnected():
            log_warning("WiFi disconnected - attempting reconnection...")

            # Brief red flash to indicate reconnection attempt (only if LEDs not in use)
            if current_color in ["off", "red", "green", "blue", "white", "purple", "orange", "softwhite", "yellow", "cyan", "magenta", "teal", "pink", "amber", "lime"]:
                lights_off()
                red.duty_u16(10000)
                time.sleep(0.2)
                lights_off()

            # Try to reconnect (single attempt)
            result = connect_wifi()
            if result == "connected":
                log_info("WiFi reconnection successful")
            else:
                log_error("WiFi reconnection failed - will retry in 30 seconds")
        else:
            log_debug("WiFi health check: Connected OK")

    except Exception as e:
        log_error(f"WiFi health check error: {e}")

def start_wifi_monitoring():
    """Initialize WiFi health monitoring (no threading needed)"""
    global last_wifi_check
    last_wifi_check = time.ticks_ms()
    log_info("WiFi health monitoring initialized")

#-----------------------------------OTA UPDATE FUNCTIONS----------------------------

def check_remote_version(): #CHECKS FOR SRC VERSION UPDATES ONLY!!! DO NOT PASTE THIS INTO BUILD
    try:
        remote_version_url = 'http://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/src/PicoOS.py'
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

#------------------------------------GENERAL FUNCTIONS------------------------------

# Cache static HTML for ultra-fast serving
cached_static_html = None

def get_cached_html():
    global cached_static_html
    if cached_static_html is None:
        cached_static_html = web_page()
    return cached_static_html

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
    global current_color, thread_flag, brightness
    log_info("Fade mode starting")
    lights_off()

    while current_color == 'fade' and not thread_flag:
        # Red to Blue
        for i in range(0, brightness, 500):
            if current_color != 'fade' or thread_flag:
                lights_off()
                return
            red.duty_u16(brightness - i)
            blue.duty_u16(i)
            time.sleep(0.03)

        # Blue to Green
        for i in range(0, brightness, 500):
            if current_color != 'fade' or thread_flag:
                lights_off()
                return
            blue.duty_u16(brightness - i)
            green.duty_u16(i)
            time.sleep(0.03)

        # Green to Red
        for i in range(0, brightness, 500):
            if current_color != 'fade' or thread_flag:
                lights_off()
                return
            green.duty_u16(brightness - i)
            red.duty_u16(i)
            time.sleep(0.03)

    lights_off()
    log_info("Fade mode stopped")

def strobe_lights():
    global brightness, thread_flag, current_color
    log_info("Strobe mode starting")
    lights_off()
    gc.collect()

    strobe_colors = [
        (brightness, 0, 0),              # Red
        (0, brightness, 0),              # Green
        (0, 0, brightness),              # Blue
        (brightness, brightness, 0),     # Yellow
        (brightness, 0, brightness),     # Magenta
        (0, brightness, brightness),     # Cyan
    ]

    color_index = 0
    while current_color == 'strobe' and not thread_flag:
        r, g, b = strobe_colors[color_index]
        red.duty_u16(r)
        green.duty_u16(g)
        blue.duty_u16(b)

        time.sleep(0.5)

        color_index = (color_index + 1) % len(strobe_colors)

    lights_off()
    log_info("Strobe mode stopped")

def motion_detection():
    global current_color, thread_flag
    MAX_BRIGHTNESS = 65025
    INCREMENT = 2000  # Adjust for faster or slower fade
    DECREMENT = 2000  # Adjust for faster or slower dimming
    SLEEP_INTERVAL = 0.5  # Adjust for speed of fade
    MOTION_DETECTED_DURATION = 30  # Time in seconds lights stay on after motion detected
    DEBOUNCE_TIME = 2  # Time in seconds for debouncing
    
    def set_light_brightness(brightness_value):
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

    def adjust_brightness(target_brightness):
        nonlocal brightness
        while brightness != target_brightness:
            if current_color != 'motion' or thread_flag:
                return
            step = INCREMENT if brightness < target_brightness else -DECREMENT
            brightness = max(min(brightness + step, MAX_BRIGHTNESS), 0)
            set_light_brightness(brightness)
            time.sleep(SLEEP_INTERVAL)

    brightness = 0
    set_light_brightness(brightness)

    if thread_flag:
        return

    motion_counter = 0
    while current_color == 'motion':
        if pir.value() == 1:
            motion_counter += 1
            if motion_counter >= (DEBOUNCE_TIME / SLEEP_INTERVAL):
                print("Motion detected")
                adjust_brightness(MAX_BRIGHTNESS)
                time.sleep(MOTION_DETECTED_DURATION)
                motion_counter = 0
        else:
            motion_counter = 0
            if brightness > 0:
                print("No movement detected - dimming lights")
                adjust_brightness(0)

        time.sleep(SLEEP_INTERVAL)

def LED_colors():
    global thread_flag
    if isOn:
        # Stop any existing threads first
        thread_flag = True
        time.sleep(0.2)  # Give existing threads time to stop
        gc.collect()
        lights_off()
        log_info(f"LED Update - Color: {current_color}, Brightness: {brightness}, State: {'ON' if isOn else 'OFF'}")

        # Reset thread flag for new operations
        thread_flag = False

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
            try:
                log_info("Starting fade mode in new thread")
                _thread.start_new_thread(fade_lights, ())
            except OSError as e:
                log_error(f"Fade thread start error: {e}")
                # Run without threading as fallback
                fade_lights()
        elif current_color == "strobe":
            try:
                log_info("Starting strobe mode in new thread")
                _thread.start_new_thread(strobe_lights, ())
            except OSError as e:
                log_error(f"Strobe thread start error: {e}")
                # Run without threading as fallback
                strobe_lights()
        elif current_color == "sunrise":
            try:
                log_info("Starting sunrise mode in new thread")
                _thread.start_new_thread(sunrise_lights, ())
            except OSError as e:
                log_error(f"Sunrise thread start error: {e}")
        elif current_color == "motion":
            try:
                log_info("Starting motion detection mode in new thread")
                _thread.start_new_thread(motion_detection, ())
            except OSError as e:
                log_error(f"Motion detection thread start error: {e}")
                # Run without threading as fallback
                motion_detection()
        else:
            led_fail_flash()

def handle_change_color_request(color):
    log_info(f"Web request - Change color to: {color}")
    return change_color(color)

def handle_change_brightness_request(brightness_choice):
    log_info(f"Web request - Change brightness to: {brightness_choice}")
    return set_brightness(brightness_choice)

def handle_led_off_request():
    global current_color, thread_flag
    log_info("Web request - Turn LED OFF")
    current_color = "off"
    thread_flag = True
    return change_color(current_color)

def web_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LED Light Control</title>
        <style>
            body{font-family:Arial,sans-serif;text-align:center}.button{padding:10px 20px;margin:20px 0;border:none;border-radius:6px;cursor:pointer;font-size:2em;background-color:#ccc;color:#000}.button:hover{background-color:#999}.button.on{background-color:rgb(48,107,255);color:#fff}.button.off{background-color:rgb(215,215,215)}.button-box{padding:10px;margin:10px;background-color:#fff;border-radius:11px;box-shadow:2px 2px 30px rgba(0,0,0,0.2)}h2,h3{margin:15px 0}
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
                <!-- ADD IN IN VERSION 1.6.0
                <button class="button" data-color='sunrise'>Simulate Sunrise</button>
                -->
                <br>
                <h3>Brightness</h3>
                <button class="button" data-brightness='bright'>Bright</button>
                <button class="button" data-brightness='medium'>Medium</button>
                <button class="button" data-brightness='dim'>Dim</button>
                <!-- ADD IN IN VERSION 1.6.0
                <h3>Auto-Off Timer</h3>
                <button class="button" data-timer='test'>Test</button>
                <button class="button" data-timer='one'>1-Hour</button>
                <button class="button" data-timer='three'>3-Hours</button>
                <button class="button" data-timer='six'>6-Hours</button>
                --> 
            </div>
        </div>
        <div class = "version-update">
            <div class="version-display">
                <p>Web Version: 1.3.1</p>
                <p>Controller Version: <span id="currentVersion">Loading...</span></p>
            </div>
            <p id="updateMessage">{{ Not Checked }}</p>
            <button class="button" onclick="checkUpdates()">Check for Updates</button>
            <button class="button" id="updateButton" style="display: none;" onclick="updateSoftware()">Update Software</button>
		</div>
        <script>
            var isOn = false;
            var current_color = "softwhite";
            
            window.onload = function() {
                fetchCurrentVersion(); // Load immediately for faster performance
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
                var button = document.getElementById("toggleButton");
                button.innerHTML = isOn ? "ON" : "OFF";
                button.className = isOn ? "button on" : "button off";
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
                if (isOn) {
                    makeRequest('/change_color?color=' + color);
                }
            }
            function changeBrightness(brightnessChoice) {
                if (isOn) {
                    makeRequest('/change_brightness?brightness=' + brightnessChoice);
                }
            }
            function auto_off(timer) {
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
                }, 100); // Fast 100ms debounce for better responsiveness
            }
        </script>
    </body>
    </html>
    """
    return html

def parse_request(request):
    request = str(request)

    def extract_parameter(request, prefix):
        start = request.find(prefix)
        if start == -1:
            return None
        start += len(prefix)
        end = request.find(" ", start)
        extracted_value = request[start:end] if end != -1 else request[start:]
        #print(f"extract_parameter: prefix={prefix}, extracted_value={extracted_value}") # Debugging
        return extracted_value

    if "/change_color" in request:
        color = extract_parameter(request, "/change_color?color=")
        if color:
            print("Parsed Color:", color)
            return handle_change_color_request(color)

    if "/change_brightness" in request:
        brightness = extract_parameter(request, "/change_brightness?brightness=")
        if brightness:
            print("Parsed Brightness:", brightness)
            return handle_change_brightness_request(brightness)

    if "/led_off" in request:
        return handle_led_off_request()

    if "/auto_off" in request:
        timer = extract_parameter(request, "/auto_off?timer=")
        if timer:
            print("Auto-Off Timer:", timer)
            return auto_off(timer)

    if "/check_update" in request:
        return check_for_update()

    if "/update_software" in request:
        return software_update_request()

    if "/current_version" in request:
        return str(deliever_local_version_to_web_page())

    return ''

def start_web_server():
    # Cache static HTML once at startup for maximum performance
    static_html = get_cached_html()
    log_info("Web server starting on port 80")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', 80))
    s.listen(5)
    log_info("Web server listening for connections")

    while True:
        conn, addr = None, None
        try:
            conn, addr = s.accept()
            conn.settimeout(1.0)  # Faster 1-second timeout
            log_debug(f'HTTP connection from {addr[0]}:{addr[1]}')

            request = conn.recv(1024)
            request = request.decode('utf-8')
            conn.settimeout(None)

            # Extract request path for logging
            try:
                request_line = request.split('\n')[0]
                path = request_line.split(' ')[1]
                log_info(f'Request: {request_line.strip()}')
            except:
                path = "unknown"
                log_warning("Could not parse request line")

            # Call handle_request with the static_html as an argument
            response, content_type = handle_request(request, static_html)

            # Prepare and send the response
            response_headers = f"HTTP/1.1 200 OK\r\nContent-Type: {content_type}; charset=UTF-8\r\nConnection: close\r\n\r\n"
            full_response = response_headers + response
            conn.sendall(full_response.encode('utf-8'))

            log_debug(f'Response sent - Type: {content_type}, Size: {len(full_response)} bytes')
            gc.collect()  # Clean up memory after request

        except OSError as e:
            if "ECONNRESET" in str(e) or "ENOTCONN" in str(e):
                # Client disconnected - normal operation
                pass
            else:
                print('Connection closed due to OSError: ', str(e))
                # Check if WiFi is still connected
                try:
                    station = network.WLAN(network.STA_IF)
                    if not station.isconnected():
                        print("WiFi disconnected during request - will auto-reconnect")
                except:
                    pass
        finally:
            if conn:
                conn.close()
        time.sleep(0.01) 

def handle_request(request, static_html):
    """
    Handle different request paths efficiently.
    Takes the request and static_html as arguments.
    Returns the response content and content type.
    """
    path = request.split(" ")[1]

    # Handle root path - ALWAYS serve the LED control page
    if path == "/":
        # Serve cached HTML immediately - ultra fast, no blocking operations
        response = static_html.replace('{{ Not Checked }}', 'Ready')
        return response, "text/html"

    # Handle other paths
    else:
        response = parse_request(request)
        return response, "text/plain"

def pico_os_main():
    log_info("=== PicoOS Main Program Starting ===")
    s = ""
    gc.collect()
    log_info("Memory garbage collection completed")

    try:
        log_info("Starting main web server loop")
        while True:
            s = start_web_server()
    except KeyboardInterrupt:
        log_info('KeyboardInterrupt: Gracefully stopping the program...')
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
        log_info("System shutdown complete")
    except Exception as e:
        log_error(f"Unexpected error in main program: {e}")
        log_info("System will attempt to restart...")

#---------------------------------MAIN PROGRAM------------------------------------------
# FOR DEBUG USE. Allows software to run from here rather than main.py
# Comment out before pushing to devices.
# gc.collect()
# connect_wifi()
# pico_os_main()