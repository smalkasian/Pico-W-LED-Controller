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
#-----------------------------------CHANGELOG----------------------------------------
print("CURRENT VERSION: 1.3.0 - dev PREVIEW - UNSTABLE")
#
# • If the wifi files doesn't exist, when the device first boots, it will create the file empty file.
# • Adding feature for multiple wireless networks to be stored. Device will scan through till it finds one and connects.
# 
# KNOWN ISSUES:
# "Connection Failed: An exception occurred - list indices must be integers, not str"
# Issue is raised when trying to update the json file.
#
# TO ADD THIS UPDATE
# 1. Finish the wifi stuff
# 2. Make some updates to the web GUI
# 3. Look into creating additional pages fo different features/rooms. Doesn't need to be viewable.
#------------------------------------IMPORTS-----------------------------------------

try:
    import usocket as socket
except ImportError:
    import socket

import time
import network
import errno
import gc
import _thread
import json
from machine import Pin, PWM

gc.collect()

#----------------------------INITIAL VAR ASSIGNMENT/TASKS---------------------------

# LED GPIO ASSIGNMENT (!!)
red = PWM(Pin(0))
green = PWM(Pin(1))
blue = PWM(Pin(2))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

brightness = 0
isOn = False
current_color = "white"
ssid = ''
password = ''
data = {}

red.duty_u16(0)
green.duty_u16(0)
blue.duty_u16(0)

try:
    with open('wifipasswords.json', 'r') as file:
        pass
except OSError:
    with open('wifipasswords.json', 'w') as file:
        json.dump({"ssid": "", "password": ""}, file)


# baton = _thread.allocate_lock()

#------------------------------------WIRELESS CONNECTION-----------------------------

def yes_validator():
        userYesNo = input("Enter yes or no: ")
        while userYesNo not in ['yes', 'no']:
            userYesNo = input("Invalid entry: Please enter yes or no: ")
        else:
            return userYesNo


def yes_decider(userYesNo):
    if userYesNo == 'yes':
        print("")
        return userYesNo
    elif userYesNo == 'no':
        return userYesNo

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
        # File does not exist or has invalid format it eill create a new file with an empty list.
        with open('wifipasswords.json', 'w') as file:
            json.dump([], file)
        return []

def update_wireless_password(ssid, password):
        global station
        lights_off()
        red.duty_u16(50000)
        print("")
        print("")
        print("Current SSID & Password:")
        try:
            with open('wifipasswords.json', "r") as file:
                data = json.load(file)
                for network in data:
                    ssid = network['ssid']
                    password = network['password']
                    print("--------------------------------")
                    print(f"SSID: {ssid}")
                    print(f"Password: {password}")
                    print("--------------------------------")
        except OSError:
            print("No existing network credentials.")
        update_credentials = input("Would you like to add a new network or update a password? [new/update/exit]: ")
        if update_credentials == "new": #THIS NEEDS DATA VALIDATION LIKE YES/NO FUNCTION SO THE USER CAN'T BREAK IT WITH A WRONG ANSWER
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
            max_retries = 100
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
        if update_credentials == "update":
            update_wireless_password(new_ssid, new_password)
        if update_credentials == "exit":
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
    global ssid, password, station, pulse_direction, brightness, max_retries
    try:
        with open('wifipasswords.json') as file:
            networks = load_wifi_credentials()
       
        for network in networks:
            ssid = network["ssid"]
            password = network["password"]
            station.active(True)
            station.connect(ssid, password)

        max_retries = 50
        pulse_direction = 10

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
            print("Connection Failed: Maybe cheeck your connection or password?")
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
        lights_off()
    except Exception as e:
        print("Connection Failed: An exception occurred -", e)
        print("System will now shut down.")
        lights_off()


station = network.WLAN(network.STA_IF)
connect_wifi()
        
#------------------------------------FUNCTIONS---------------------------------------

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
            red.duty_u16()
            green.duty_u16(0)
            blue.duty_u16()
            _thread.start_new_thread(fade_lights, ())
        else:
            red.duty_u16(65026)
            green.duty_u16(0)
            blue.duty_u16(0)

def handle_change_color_request(color):
    return change_color(color)

def handle_change_brightness_request(brightness_choice):
    return set_brightness(brightness_choice)

def handle_led_off_request():
    global current_color
    current_color = "off"
    return change_color(current_color)

def web_page_FUTURE_UPDATE_DO_NOT_CALL(): 
    try:
        with open('index.html', 'r') as file:
            html = file.read()
        html = html.format(str(isOn).lower(), current_color)
        print('HTML content:', html)
        return html
    except Exception as e:
        print('Error reading index.html:', e)
        return ''
    # NOTES: Will pull the web page locally from a file on the device rather than the src code.
    # Implementation will depend on OTA functionality. Goal is to make the web page update independantly from the main code.

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
            }
            .button {
                display: inline-block;
                padding: 10px 20px;
                margin: 10px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
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
            .button-container {
                display: flex;
                justify-content: center;
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
        </style>
    </head>
    <body>
        <div class="button-container">
            <div class="button-box">
                <h1>Kitchen Lights</h1>
                <button id="toggleButton" class="button off" onclick="toggleLED()">OFF</button>
                <br>
                <h2>Colors</h2>
                <button class="button" onclick="change_color('red')">Red</button>
                <button class="button" onclick="change_color('green')">Green</button>
                <button class="button" onclick="change_color('blue')">Blue</button>
                <button class="button" onclick="change_color('purple')">Purple</button>
                <button class="button" onclick="change_color('orange')">Orange</button>
                <button class="button" onclick="change_color('white')">White</button>
                <button class="button" onclick="change_color('softwhite')">Soft White</button>
                <button class="button" onclick="change_color('fade')">Color Fade</button>
                <br>
                <h2>Brightness</h2>
                <button class="button" onclick="changeBrightness('bright')">Bright</button>
                <button class="button" onclick="changeBrightness('medium')">Medium</button>
                <button class="button" onclick="changeBrightness('dim')">Dim</button>
            </div>
        </div>
        <p> VERSION: 1.2 </p>
        <script>
            var isOn = false;
            var current_color = "white";
            
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
        return handle_change_color_request(color)
    if "/change_brightness" in request:
        brightness_start = request.find("/change_brightness?brightness=") + len("/change_brightness?brightness=")
        brightness_end = request.find(" ", brightness_start)
        brightness_choice = request[brightness_start:brightness_end]
        return handle_change_brightness_request(brightness_choice)
    if "/led_off" in request:
        return handle_led_off_request()
    return ''

def main_thread():
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
                response = web_page()
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


#---------------------------------MAIN PROGRAM------------------------------------------

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)

try:
    while True:
        main_thread()
except KeyboardInterrupt:
    print('KeyboardInterrupt: Stopping the program...')
    red.duty_u16(0)
    green.duty_u16(0)
    blue.duty_u16(0)
    for i in range(5): 
        red.duty_u16(65025)
        green.duty_u16(65025)
        time.sleep(0.1)
        red.duty_u16(0)
        green.duty_u16(0)
        time.sleep(0.1)
        red.duty_u16(0)
        green.duty_u16(0)
    station.disconnect()
    station.active(False)
    print("System Disconneted")
finally:
    s.close()
