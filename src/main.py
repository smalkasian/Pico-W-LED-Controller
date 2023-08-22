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
print("Stable - OTA Update Version")
def deliver_current_version():
    __version__ = (1,3,0)
    is_stable = True
    return __version__
#------------------------------------CHANGELOG-----------------------------------------
# • If the wifi files doesn't exist, when the device first boots, it will create the file empty file.
# • Adding feature for multiple wireless networks to be stored. Device will scan through till it finds one and connects.
# • Web pages now pulls from remote file rather within the script.
# • Changed the file name to PicoOS.py rather than main.py as this will no longer be the main.
# • Moved all processes into their own functions (wifi, and main thread)
# • The main program is now main.py. It boots from that and then loads the actual OS from picoOS.py and continues with normal processes.
# • OS now supports OTA updates

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


#----------------------------INITIAL VAR ASSIGNMENT/TASKS---------------------------

# LED GPIO ASSIGNMENT (!!
red = PWM(Pin(0))
green = PWM(Pin(1))
blue = PWM(Pin(2))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

isOn = False
brightness = 0

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

def load_wifi_credentials():
    try:
        with open('wifipasswords.json', 'r') as file:
            networks = json.load(file)
            if isinstance(networks, list) and all(isinstance(network, dict) and 'ssid' in network and 'password' in network for network in networks):
                return networks
            else:
                raise ValueError("Invalid format in 'wifipasswords.json'")
    except (OSError, ValueError):
        with open('wifipasswords.json', 'w') as file:
            json.dump([], file)
        return []

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
            data["ssid"] = new_ssid
            data["password"] = new_password
            with open('wifipasswords.json', "w") as file:
                json.dump(data, file)
            station.active(True)
            station.connect(ssid, password)
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
            update_wireless_password(new_ssid, new_password)
        if update_credentials == "no":
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
    station = network.WLAN(network.STA_IF)
    try:
        with open('wifipasswords.json') as file:
            data = json.load(file)
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
            for i in range(10):
                green.duty_u16(65025)
                time.sleep(0.1)
                green.duty_u16(0)
                time.sleep(0.1)
            green.duty_u16(65025)
            time.sleep(2)
            lights_off()
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
        gc.collect()
        local_version = deliver_current_version()
        remote_version = check_remote_version()
        if remote_version is None:
            return "Failed to fetch remote version. Try again in a little bit."
        elif remote_version == local_version:
            update_message = f"{local_version} is the current version. You are up to date!"
        elif remote_version > local_version:
            update_message = f"Version {remote_version} is available."
        elif remote_version != local_version:
            update_message = "Something went wrong while checking for the update."
        else:
           update_message = "FAILED TO GET UPDATE"
    except Exception as e:
        update_message = "FAILED TO GET UPDATE"
        print("Error:", e)
    return update_message
        
def update_software():
    update_url = 'http://raw.githubusercontent.com/smalkasian/Pico-W-LED-Controller/main/src/PicoOS.py'
    temp_file = "PicoOS_temp.py"
    backup_file = "PicoOS_backup.py"
    gc.collect()
    try:
        response = urequests.get(update_url)
        if response.status_code == 200:
            update_content = response.text()
            with open(temp_file, "w") as f:
                f.write(update_content)
            uos.rename("PicoOS.py", backup_file) # Backup the current OS
            uos.rename(temp_file, "PicoOS.py") # Replace with downloaded file  
            update_message = "Update completed successfully."
            return update_message
            machine.reset
        else:
            update_message = "Update Failed!"
            return update_message
    except Exception as e:
        if uos.path.exists(backup_file):
            uos.rename(backup_file, "PicoOS.py")
            update_message = ("Update Failed. Old OS restored. Error: ", e)
        return update_message 

def software_update_request():
    gc.collect()
    try:
        local_version = deliver_current_version()
        remote_version = check_remote_version()
        if remote_version is None:
            update_message = "Failed to fetch remote version."
        elif remote_version == local_version:
            update_message = (f"{local_version} is the current version. No update needed!")
        elif remote_version > local_version:
            update_message = "Updating software. Please wait."
            _thread.start_new_thread(update_software, ())
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
        brightness = 0
        if brightness == 0:
            brightness = 65025
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
                height: 100vh;
            }
            .button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 2vw;
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
            <p>PicoOS Version: {{ current_version }}</p>
            <p id="updateMessage">{{ update_message }}</p>
            <button class="button" onclick="checkUpdates()">Check for Updates</button>
            <!-- <button class="button" onclick="updateSoftware()">Update Software</button> -->

        <script>
            var isOn = false;
            var current_color = "softwhite";
            
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
    s = None
    try:
        while True:
            s = start_web_server()
    except KeyboardInterrupt:
        print('KeyboardInterrupt: Stopping the program...')
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
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

#---------------------------------MAIN PROGRAM------------------------------------------

gc.collect()
connect_wifi()
pico_os_main()