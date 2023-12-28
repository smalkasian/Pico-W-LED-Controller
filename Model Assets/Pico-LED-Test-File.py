from machine import Pin


onboard = Pin(25, Pin.OUT)
red = Pin(0, Pin.OUT)
green = Pin(1, Pin.OUT)
blue = Pin(2, Pin.OUT)
white = Pin(3, Pin.OUT)

green.toggle()