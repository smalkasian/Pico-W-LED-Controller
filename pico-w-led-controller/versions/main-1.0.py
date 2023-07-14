#------------------------------------------------------------------------------------
#Copyright (c) 2023, MalkasianGroup, LLC
#All rights reserved.
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
# VERSION 1.0

#------------------------------------IMPORTS-----------------------------------------
try:
    import usocket as socket
except ImportError:
    import socket

import time
import network
import gc
from machine import Pin, PWM


gc.collect()

#------------------------------------VAR ASSIGNMENT----------------------------------

# ADD YOUR WIFI INFORMATION  (!!)
ssid = 'YOUR WIFI NAME'
password = 'YOUR WIFI PASSWORD'

# CHANGE GPIO NIMBERS  (!!)
red = PWM(Pin(0))
green = PWM(Pin(1))
blue = PWM(Pin(2))

red.freq(1000)
green.freq(1000)
blue.freq(1000)

brightness = 0
isOn = False
currentColor = "white"

#------------------------------------WIRELESS CONNECTION-----------------------------

station = network.WLAN(network.STA_IF)
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
    green.duty_u16(int(brightness*0.5))
    blue.duty_u16(0)

    max_retries -= 1
    time.sleep(0.1)

#Turns off the lights after the wifi connects
red.duty_u16(0)
green.duty_u16(0)
blue.duty_u16(0)

if station.isconnected():
    print('Connection successful')
    print(station.ifconfig())
    for i in range(10):
        green.duty_u16(65025)
        time.sleep(0.1)
        green.duty_u16(0)
        time.sleep(0.1)
    green.duty_u16(65025)
    time.sleep(2)
    red.duty_u16(0)
    green.duty_u16(0)
    blue.duty_u16(0)
else:
    print('Connection failed after 50 attempts')
    for i in range(16): 
        red.duty_u16(65025)
        time.sleep(0.1)
        red.duty_u16(0)
        time.sleep(0.1)
    red.duty_u16(0)

#---------------------------------FUNCTIONS / MAIN-----------------------------------

def setBrightness(brightnessChoice):
    global brightness
    if brightnessChoice == "bright":
        brightness = 65025
    elif brightnessChoice == "medium":
        brightness = 40000
    elif brightnessChoice == "dim":
        brightness = 20000
    else:
        return 'Invalid brightness'
    updateLEDs()

def changeColor(color):
    global currentColor, isOn
    if color in ["red", "green", "blue", "white", "purple", "orange"]:
        isOn = True
        currentColor = color
    elif color == "off":
        isOn = False
        red.duty_u16(0)
        green.duty_u16(0)
        blue.duty_u16(0)
    else:
        return 'Invalid color'
    updateLEDs()

def updateLEDs():
    if isOn:
        if currentColor == "red":
            red.duty_u16(brightness)
            green.duty_u16(0)
            blue.duty_u16(0)
        elif currentColor == "green":
            red.duty_u16(0)
            green.duty_u16(brightness)
            blue.duty_u16(0)
        elif currentColor == "blue":
            red.duty_u16(0)
            green.duty_u16(0)
            blue.duty_u16(brightness)
        elif currentColor == "white":
            red.duty_u16(brightness)
            green.duty_u16(brightness)
            blue.duty_u16(brightness)
        elif currentColor == "purple":
            red.duty_u16(int(brightness*0.6))
            green.duty_u16(0)
            blue.duty_u16(brightness)
        elif currentColor == "orange":
            red.duty_u16(brightness)
            green.duty_u16(int(brightness*0.3))
            blue.duty_u16(0)
        else:
            red.duty_u16(0)
            green.duty_u16(0)
            blue.duty_u16(0)

def handle_change_color_request(color):
    return changeColor(color)

def handle_change_brightness_request(brightness_choice):
    return setBrightness(brightness_choice)

def handle_led_off_request():
    global currentColor
    currentColor = "off"
    return changeColor(currentColor)

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
                padding: 10px 25px 20px 25px; /* top right bottom left */
                background-color: white;
                border-radius: 11px;
                text-align: center;
                box-shadow: 2px 2px 30px rgba(0, 0, 0, 0.2);
                max-width: 400px;
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
                <button class="button" onclick="changeColor('red')">Red</button>
                <button class="button" onclick="changeColor('green')">Green</button>
                <button class="button" onclick="changeColor('blue')">Blue</button>
                <button class="button" onclick="changeColor('purple')">Purple</button>
                <button class="button" onclick="changeColor('orange')">Orange</button>
                <button class="button" onclick="changeColor('white')">White</button>
                <br>
                <h2>Brightness</h2>
                <button class="button" onclick="changeBrightness('bright')">Bright</button>
                <button class="button" onclick="changeBrightness('medium')">Medium</button>
                <button class="button" onclick="changeBrightness('dim')">Dim</button>
            </div>
        </div>
        <script>
            var isOn = false;
            var currentColor = "white";
            
            function toggleLED() {
                var button = document.getElementById("toggleButton");
                
                if (isOn) {
                    button.innerHTML = "OFF";
                    button.className = "button off";
                    isOn = false;
                    changeColor('off');
                    makeRequest('/led_off');
                } else {
                    button.innerHTML = "ON";
                    button.className = "button on";
                    isOn = true;
                    changeColor(currentColor);
                }
            }
            
            function changeColor(color) {
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
s.close()