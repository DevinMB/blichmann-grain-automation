import board
import neopixel 
import RPi.GPIO as GPIO
from gpiozero import Button, LED
import time


# Define the GPIO pins
RELAY_PIN = 17  
OVERRIDE_PIN = 24

BUTTON_PIN_1 = 26 
LED_PIN_1 = board.D21 

BUTTON_PIN_2 = 26 
LED_PIN_2 = board.D18  

SCALE_DT_PIN = 6   
SCALE_SCK_PIN = 5 

# Set led count in neopixel
NUM_LEDS = 1

# Set Up Scale
hx = HX711(SCALE_DT_PIN, SCALE_SCK_PIN)
hx.tare()
reference_unit = 9947.728444444423
hx.set_reference_unit(reference_unit)


# Set up the relay and button using gpiozero
relay = LED(RELAY_PIN)
button_1 = Button(BUTTON_PIN_1)
button_2 = Button(BUTTON_PIN_2)
override_switch = Button(OVERRIDE_PIN)

# Set up the NeoPixel LED
button_1_pixel = neopixel.NeoPixel(
    pin=LED_PIN_1, n=NUM_LEDS, brightness=0.2, auto_write=True
)
button_2_pixel = neopixel.NeoPixel(
    pin=LED_PIN_1, n=NUM_LEDS, brightness=0.2, auto_write=True
)

# def turn_off_relay(option=None):
#         relay.off()
#         button_1_pixel[0] = (255, 0, 0)  # Red
#         print("Relay is OFF. LED is Red.")

# def turn_on_relay(option=None):
#     if option == "override":
#         relay.on()    
#         print("Relay Override On")
#     else: 
#         relay.on()
#         button_1_pixel[0] = (0, 255, 0)  # Green
#         print("Relay is ON. LED is Green.")

is_running = False
button_combo_count  = 0

try: 
    while True: 
        if override_switch.is_pressed:
            relay.on()
        else: 
            if button_2.is_pressed:
                start_job()
            if button_1.is_pressed:
                set_weight()
            if button_1.is_pressed and button_2.is_pressed:

except KeyboardInterrupt:
    print("Goodbyeeeeeeeee")
finally: 
    button_1_pixel[0] = (0, 0, 0)
    button_2_pixel[0] = (0, 0, 0)
    GPIO.cleanup()
    print("GPIO cleanup complete.")


try:
    print("Press the button to toggle the relay.")
    while True:
        if button_1.is_pressed or override_switch.is_pressed:
            if button_1.is_pressed:
                turn_on_relay()
            if override_switch.is_pressed:
                turn_on_relay("override")
        else:
            turn_off_relay()
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    button_1_pixel[0] = (0, 0, 0)  # Turn off LED
    print("GPIO cleanup complete.")
