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
print("UNSTABLE - Developer Preview")
def deliver_current_version():
    __version__ = (1,3,0)
    is_stable = False
    local_version = '.'.join(str(i) for i in __version__)
    print(f"CURRENT VERSION: {local_version}")
    return __version__
#------------------------------------CHANGELOG-----------------------------------------
# • If the wifi files doesn't exist, when the device first boots, it will create the file empty file.
# • Adding feature for multiple wireless networks to be stored. Device will scan through till it finds one and connects.
# • Web pages now pulls from remote file rather within the script.
# • Changed the file name to PicoOS.py rather than main.py as this will no longer be the main.
# • Moved all processes into their own functions (wifi, and main thread)
# KNOWN ISSUES:
# "Connection Failed: An exception occurred - list indices must be integers, not str"
# Issue is raised when trying to update the json file. 
# Haven't finished updating the or adding version tracking to the web page file so it cna be remotly updated.
# OTA still doesn't work. As of now, the system will break.
# Connection Failed: An exception occurred - list indices must be integers, not str (when using a SSID with numbers in it).
# Also fails when trying to "update" the password.
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
        global station
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
    red = PWM(Pin(0))
    green = PWM(Pin(1))
    blue = PWM(Pin(2))
    red.freq(1000)
    green.freq(1000)
    blue.freq(1000)
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

def web_page(): 
    try:
        with open('index.html', 'r') as file:
            html = file.read()
        html = html.format(str(isOn).lower(), current_color)
        print('HTML content:', html)
        return html
    except Exception as e:
        print('Error reading index.html:', e)
        return ''

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
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('', 80))
            s.listen(5)
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

def pico_os_main():
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
