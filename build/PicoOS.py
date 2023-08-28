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
print("STABLE - OTA Functionality Update")
def deliver_current_version():
    __version__ = (1,4,1)
    return __version__
#------------------------------------CHANGELOG-----------------------------------------
# • Patched web page pulling update every time the page loads. Caused a lag issue with web page loading. 
# • Update button appears when there's an available software update.
# • Bug handling when the update fails. 
# • Global var for thread handling.
# • OTA fully functional after testing.
# • Patched web page button stack issue where text and buttons were too small.
# KNOWN ISSUES:
# Text align issue when trying to pull in the index.html file causing it to fail.
# Connection Failed: An exception occurred - list indices must be integers, not str (when using a SSID with numbers in it).
# 
#------------------------------------IMPORTS-----------------------------------------

try:
    import usocket as socket
except ImportError:
    import socket
import urequests
import time
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

red.freq(1000)
green.freq(1000)
blue.freq(1000)

isOn = False
brightness = 65025
thread_flag = False

# baton = _thread.allocate_lock()

#------------------------------------WIRELESS CONNECTION-----------------------------

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

def led_success_flash():
    for i in range(10):
        green.duty_u16(65025)
        time.sleep(0.1)
        green.duty_u16(0)
        time.sleep(0.1)
    green.duty_u16(65025)
    time.sleep(1)
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
        # If there's an error (file doesn't exist or has invalid format), 
        # create the file with default credentials
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
        station.connect(new_ssid, new_password)  # Use the new credentials here
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
    data = load_wifi_credentials()  # This ensures that data is always initialized
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

#------------------------------------FUNCTIONS---------------------------------------

def check_remote_version():
    try:
        remote_version_url = 'http://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/build/PicoOS.py'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        response = urequests.get(remote_version_url, headers=headers)
        print("Status Code:", response.status_code)
        if response.status_code == 200:
            match = re.search(r'__version__ = \((\d+,\d+,\d+)\)', response.text)
            if match:
                version_string = match.group(1)  # Extract the version string
                version_components = tuple(map(int, version_string.split(',')))
                return version_components
    except Exception as e:
        print("Error:", e)
    return None

def check_for_update():
    try:
        local_version = deliver_current_version()
        remote_version = check_remote_version()
        if remote_version is None:
            return "Failed to fetch remote version. Try again in a little bit."
        elif remote_version == local_version:
            return f"{local_version} is the current version. You are up to date!"
        elif remote_version > local_version:
            return f"Version {str(remote_version)} is available."
        else:
            return "FAILED TO GET UPDATE - TRY AGAIN."
    except Exception as e:
        return "FAILED TO GET UPDATE - TRY AGAIN"

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
            updated_html = "Error: " + str(e)  # Or provide some default/fallback HTML here
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
    update_LED()
    return 'Brightness successfully changed'

def change_color(color):
    global current_color, isOn
    if color in ["red", "green", "blue", "white", "purple", "orange", 'softwhite', 'fade']:
        isOn = True
        current_color = color
    elif color == "off":
        isOn = False
        red.duty_u16(0)
        green.duty_u16(0)
        blue.duty_u16(0)
    else:
        return 'Invalid color'
    update_LED()
    return 'Color successfully changed.'

def fade_lights():
    global current_color
    fade_speed = 1
    color_values = list(range(0, 65026, 100))
    chunk_size = 10
    color_chunks = [color_values[i:i + chunk_size] for i in range(0, len(color_values), chunk_size)]
    for chunk in color_chunks:
        print(f'Current color at start of red-blue fade: {current_color}')  # Added for debugging
        if current_color != 'fade':
            return
        for i in chunk:
            if current_color != 'fade':
                return
            red.duty_u16(65025 - i)
            blue.duty_u16(i)
            time.sleep(fade_speed)
    for chunk in color_chunks:
        print(f'Current color at start of blue-green fade: {current_color}')  # Added for debugging
        if current_color != 'fade':
            return
        for i in chunk:
            if current_color != 'fade':
                return
            blue.duty_u16(65025 - i)
            green.duty_u16(i)
            time.sleep(fade_speed)
    for chunk in color_chunks:
        print(f'Current color at start of green-red fade: {current_color}')  # Added for debugging
        if current_color != 'fade':
            return
        for i in chunk:
            if current_color != 'fade':
                return
            green.duty_u16(65025 - i)
            red.duty_u16(i)
            time.sleep(fade_speed)

def update_LED(): 
    if isOn:
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
        elif current_color == "fade":
            red.duty_u16(0)
            green.duty_u16(0)
            blue.duty_u16(0)
            _thread.start_new_thread(fade_lights, ())
        else:
            red.duty_u16(65026)
            green.duty_u16(0)
            blue.duty_u16(0)

def handle_change_color_request(color):
    print("Changing Color to:", color)
    return change_color(color)

def handle_change_brightness_request(brightness_choice):
    print("Changing Brightness to:", brightness_choice)
    return set_brightness(brightness_choice)

def handle_led_off_request():
    global current_color
    current_color = "off"
    return change_color(current_color)

def web_page_UNUSED(): 
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

def web_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Home LED Light Control</title>
        <style>
            body {
                text-align: center;
                font-family: Arial, sans-serif;
            }
            h1 {
                margin-top: 20px;
                font-size: 4vw;
            }
            h2 {
                font-size: 3vw;
                font-weight: bold;
            }
            h3 {
                font-size: 3vw;
                font-weight: normal;
                
            }
            .button_container{
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .button {
                display: inline-block;
                padding: 10px 20px;
                margin: 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 4vw;
                text-align: center;
                text-decoration: none;
                outline: none;
                color: #000000;
                background-color: #ccc;
            }
            .button:hover {
                background-color: #999;
            }
            .on {
                color: white;
                background-color: rgb(48, 107, 255);
            }
            .off {
                background-color: rgb(215, 215, 215);
                color: #000;
            }
            .centered-text {
                display: flex;
                justify-content: center;
                align-items: center;
                text-align: center;
                padding-bottom: 50px;
            }
            .button-box {
                margin: 10px;
                padding: 10px 50px 20px 50px; /* top right bottom left */
                background-color: white;
                border-radius: 11px;
                text-align: center;
                box-shadow: 2px 2px 30px rgba(0, 0, 0, 0.2);
                max-width: auto;
            }
            .version-update{
                padding-top: 50px;
            }
        </style>
    </head>
    <body>
        <div class="button-container">
            <div class="button-box">
                <h2>Kitchen Lights</h2>
                <button id="toggleButton" class="button off" onclick="toggleLED()">OFF</button>
                <br>
                <h3>Colors</h3>
                <button class="button" onclick="change_color('red')">Red</button>
                <button class="button" onclick="change_color('green')">Green</button>
                <button class="button" onclick="change_color('blue')">Blue</button>
                <button class="button" onclick="change_color('purple')">Purple</button>
                <button class="button" onclick="change_color('orange')">Orange</button>
                <button class="button" onclick="change_color('white')">White</button>
                <button class="button" onclick="change_color('softwhite')">Soft White</button>
                <button class="button" onclick="change_color('fade')">Color Fade</button>
                <br>
                <h3>Brightness</h3>
                <button class="button" onclick="changeBrightness('bright')">Bright</button>
                <button class="button" onclick="changeBrightness('medium')">Medium</button>
                <button class="button" onclick="changeBrightness('dim')">Dim</button>
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
        <script>
            var isOn = false;
            var current_color = "softwhite";
            
            window.onload = fetchCurrentVersion;
            
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
                console.log("Selected color: " + color);
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
            function fetchCurrentVersion() {
                fetch('/current_version')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.text();
                })
                .then(data => {
                    document.getElementById('currentVersion').innerText = data;
                })
                .catch(error => {
                    document.getElementById('currentVersion').innerText = "Error: " + error.message;
                });
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

            function makeRequest(url) {
                var xhr = new XMLHttpRequest();
                xhr.open("GET", url, true);
                xhr.send();
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
    if "/check_update" in request:
        return check_for_update()
    if "/update_software" in request:
        return software_update_request()
    if "/current_version" in request:
        return str(deliver_current_version())
    return ''

def start_web_server():
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

# NULL