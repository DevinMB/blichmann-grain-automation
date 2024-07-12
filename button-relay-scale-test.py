import board
import neopixel
from gpiozero import Button, LED
import time

# Define the GPIO pins
RELAY_PIN = 17  # GPIO pin for the relay
BUTTON_PIN = 23  # GPIO pin for the button
OVERRIDE_PIN = 24
LED_PIN = board.D18  # GPIO pin for the LED data input (using board.D18 for GPIO 18)

# Number of LEDs
NUM_LEDS = 1

# Set up the relay and button using gpiozero
relay = LED(RELAY_PIN)
button = Button(BUTTON_PIN)
override_switch = Button(OVERRIDE_PIN)

# Set up the NeoPixel LED
pixels = neopixel.NeoPixel(LED_PIN, NUM_LEDS)

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
