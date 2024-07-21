import board
import neopixel 
import RPi.GPIO as GPIO

from gpiozero import Button, LED
import time


# Define the GPIO pins
RELAY_PIN = 17  
BUTTON_PIN = 26 
OVERRIDE_PIN = 24
LED_PIN1 = board.D15 
LED_PIN2 = board.D18  
# Number of LEDs
NUM_LEDS = 1

# Set up the relay and button using gpiozero
relay = LED(RELAY_PIN)
button = Button(BUTTON_PIN)
override_switch = Button(OVERRIDE_PIN)

# Set up the NeoPixel LED
button_1_pixel = neopixel.NeoPixel(
    pin=LED_PIN1, n=NUM_LEDS, brightness=0.2, auto_write=True
)

def turn_off_relay(option=None):
        relay.off()
        pixels[0] = (255, 0, 0)  # Red
        print("Relay is OFF. LED is Red.")

def turn_on_relay(option=None):
    if option == "override":
        relay.on()    
        print("Relay Override On")
    else: 
        relay.on()
        pixels[0] = (0, 255, 0)  # Green
        print("Relay is ON. LED is Green.")
    
try:
    print("Press the button to toggle the relay.")
    while True:
        if button.is_pressed or override_switch.is_pressed:
            if button.is_pressed:
                turn_on_relay()
            if override_switch.is_pressed:
                turn_on_relay("override")
        else:
            turn_off_relay()
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    pixels[0] = (0, 0, 0)  # Turn off LED
    print("GPIO cleanup complete.")
