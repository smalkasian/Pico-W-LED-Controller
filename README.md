# MicroPython Pico-W LED Controller

This Pico operating system allows you to control LED lights in your home from a web app. It's simple to use though requires some technical knowledge about coding and hardware.

## Requirements
1. You need to configure the GPIO pins correctly for this to work properly.
2. You need to connect to your REPL editor the first time you run the code and enter wifi credentials.

## Workflow
1. Drop the [UF2 bootloader](https://micropython.org/download/rp2-pico/) to your device.
2. Clone the "src" repo to your desktop and copy ALL the files onto the device.
3. Open the "PicoOS.py" file through your REPL and change the GPIO pins to whatever you connected your lights to.
* (HINT) Anytime you see (!!) in the code, it means you need to change for your own unique setup.
```python
LED GPIO ASSIGNMENT (!!)
red = PWM(Pin(0)) 👈🏻 # Change the pin numbers!
green = PWM(Pin(1))
blue = PWM(Pin(2))
```
5. The first time you boot up, it should attempt to connect to the wifi.
* 🟡 Yellow pulsing means it's attempting a wifi connection.
* 🟡 Yellow solid means the system froze and needs to be reconnected.
* 🔴 Red flashing means a failure (of any kind).
* 🔴 Red solid means it's waiting for some kind of input through the REPL.
* 🟢 Green (anytime) means a successful connection or action.
* 🔵 Blue flash means the option you selected was successful (when scheduling something to run in advance).
* 🟣 Purple pulsing means the software is updating.
6. Through your console/terminal, it will tell you it cannot connect to the wifi and to enter your wifi credentials after which, should connect successfully.
(Anytime it connects to the wifi, it will show the IP in the terminal. You can enter that in your web browser to access the web GUI).

## What's Coming?
• Color slider for more granular control of the color as well as a slider for brightness.
• Support for a microphone connection so LED lights can respond to music as well as add voice control ("Pico, turn on the kitchen lights - set to white").
• Ability to have multiple devices in your home and to control them all from the web GUI.

## Recent Feature Additions
• OTA Update! You no longer need to connect and copy the updates. It now does it at the press of a button!

## Final Comments
I've designed 3D printed models to house the Pico and I will link the full tutorial at some point in the future (as well as how you can build your own and find supported LED lights).

There is a folder with the Pico 3D model if you want to try building this yourself. The housing is compatable with these lights (not a sponsored link):
https://www.amazon.com/Keepsmile-Bluetooth-Changing-Adapter-Festival/dp/B0B2D52FLK

If you come across any bugs or experience odd behavior, please feel free to reach out and let me know 
malkasian(a)dsm.studio.

As this software IS open source. If you do decide to use/modify it, please let me know! I'd love to learn what features or additions the community has made!
