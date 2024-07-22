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

# Set hold duration for combo and weight set
HOLD_DURATION = 10

# Set known weight
KNOWN_WEIGHT_LBS = 10

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

def get_stable_weight(num_readings=10):
    weights = []
    for _ in range(num_readings):
        weight = hx.get_weight(1)
        weights.append(weight)
        time.sleep(0.1)  # Short delay between readings to stabilize
    return sum(weights) / len(weights)

def calabrate_scale():
    hx.tare()
    print("Place 10lbs on scale...")
    time.sleep(60)
    num_readings = 100
    readings = []
    print("Calibrating. Please wait...")
    for _ in range(num_readings):
        raw_data = hx.get_weight(5)  
        if raw_data is not None:
            readings.append(raw_data)
        time.sleep(0.1)  
    if readings:
        average_raw_data = sum(readings) / len(readings)
        print(f'Average raw data: {average_raw_data}')
        reference_unit = average_raw_data / KNOWN_WEIGHT_LBS
        print(f'Reference unit of {reference_unit} has been set.')
    else:
        print('Failed to read raw data. Please check the sensor.')

is_running = False
button_combo_count  = 0
hold_button_1_count = 0
current_weight = 0
target_weight = 0

button_1_pixel[0] = (255, 255, 0)  # Yellow
button_2_pixel[0] = (255, 0, 0)  # Red

try: 
    while True: 
        current_weight = get_stable_weight(2)
        if override_switch.is_pressed:
            relay.on()
            print(f"Override ON: Current Weight: {current_weight} Lbs")
        if button_2.is_pressed and is_running == False:
            relay.on()
            button_2_pixel[0] = (0, 255, 0)  # Green
            print(f"Starting Job")
        if button_2.is_pressed and is_running == True: 
            relay.off()
            button_2_pixel[0] = (0, 0, 255)  # Blue
            print(f"Job Paused")
        if is_running == True and current_weight >= target_weight:
            relay.off()
            button_2_pixel[0] = (0, 0, 255)  # Blue
            print(f"Job Finished! Target weight met.")
        if is_running == True and current_weight < target_weight:
            print(f"Job Running: Current Weight: {current_weight} Lbs Target Weight: {target_weight} Lbs")
        if button_1.is_pressed and is_running == False:
            if hold_button_1_count >= HOLD_DURATION:
                current_weight = target_weight
                hold_button_1_count = 0
                button_1_pixel[0] = (0, 255, 0)  # Green
                print(f'Target weight set: {target_weight} Lbs')
            else: 
                hold_button_1_count = hold_button_1_count + 1
                remaining_count = HOLD_DURATION - hold_button_1_count
                print(f"Requesting weight set in {remaining_count}")
                button_1_pixel[0] = (255, 255, 0)  # Yellow
        if button_1.is_pressed and button_2.is_pressed and is_running == False:
            calabrate_scale()
        else: 
            relay.off()

except KeyboardInterrupt:
    print("Goodbyeeeeeeeee")
finally: 
    button_1_pixel[0] = (0, 0, 0)
    button_2_pixel[0] = (0, 0, 0)
    GPIO.cleanup()
    print("GPIO cleanup complete.")


