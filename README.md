# MicroPython Pico-W LED Controller

This Pico operating system allows you to control LED lights in your home from a web app. It's simple to use though requires some technical knowledge about coding and hardware.

## Requirements
1. You need to configure the GPIO pins correctly for this to work properly.
2. You need to connect to your REPL editor the first time you run the code and enter wifi credentials.

## Workflow
1. Drop the [UF2 bootloader](https://micropython.org/download/rp2-pico/) to your device.
2. Clone the "src" repo to your desktop and copy ALL the files onto the device.
3. Open the "main.py" file through your REPL and change the GPIO pins to whatever pins you connected your lights to.
* (HINT) Anytime you see (!!) in the code, it means you need to change for your own unique setup.
```python
LED GPIO ASSIGNMENT (!!)
red = PWM(Pin(0)) 👈🏻 # Change the pin numbers!
green = PWM(Pin(1))
blue = PWM(Pin(2))
```
5. The first tine you boot up, it should attempt to connect to the wifi.
* 🟡 Yellow blinking means it's working on a wifi connection.
* 🟡 Yellow solid means the system froze and needs to be reconnected.
* 🔴 Red blinking means a failure (of any kind).
* 🔴 Red solid means it's waiting for some kind of input through the REPL.
* 🟢 Green (anytime) means a successful connection.
* 🔵 //Unused at this time//
6. Through your console/terminal, it will tell you it cannot connect to the wifi and to enter your wifi credentials after which, should connect successfully.
(Anytime it connects to the wifi, it will show the IP in the terminal. You can enter than in your web browser to access the web GUI).

## What's Coming?
1. I'm actively working on this project and will add features as I have time. One of the features I'm curretnly working on is [OTA updates](https://github.com/rdehuyss/micropython-ota-updater) that YOU control through the web GUI.
2. Color slider for more granular control of the color as well as a slider for brightness.
3. Support for a microphone connection so LED lights can respond to music as well as add voice control ("Pico, turn on the kitchen lights - set to white").
4. I'd like to add a jack and/or bluetooth connectivity so that you can stream music from your device or through a Spotify API connection in the web app directly.
5. Ability to have multiple devices in your home and to control them all from the web GUI.


## Final Comments
I've designed 3D printed models to house the Pico and I will link the full tutorial at some point in the future (as well as how you can build your own and find supported LED lights).

If you come across any bugs or experiecne odd behavior, please feel free to reach out and let me know.
