import board
import neopixel 
import RPi.GPIO as GPIO
from gpiozero import Button, LED
import time
from hx711 import HX711


# Define the GPIO pins
SCALE_DT_PIN = 6   
SCALE_SCK_PIN = 5 

RELAY_PIN = 17  

OVERRIDE_PIN = 24

BUTTON_PIN_1 = 26 
LED_PIN_1 = board.D21 

BUTTON_PIN_2 = 16
LED_PIN_2 = board.D18  

# Set led count in neopixel
NUM_LEDS = 1

# Set hold duration for combo and weight set
HOLD_DURATION = 10

# Set known weight
KNOWN_WEIGHT_LBS = 10

# Set Up Scale
hx = HX711(SCALE_DT_PIN, SCALE_SCK_PIN)
hx.tare()
reference_unit = 9854.586888888884
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
    pin=LED_PIN_2, n=NUM_LEDS, brightness=0.2, auto_write=True
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

current_state = False
is_job_running = False
button_combo_count  = 0
hold_button_1_count = 0
current_weight = 0
target_weight = 0

button_1_pixel[0] = (255, 255, 0)  # Yellow
button_2_pixel[0] = (255, 0, 0)  # Red
try:
    while True:
        current_weight = get_stable_weight(5)

        # Define states based on conditions
        if override_switch.is_pressed:
            state = 'override'
        elif is_job_running:
            if current_weight >= target_weight:
                state = 'job_finished'
            else:
                state = 'job_running'
        else:
            state = 'standing_by'

        # Match the state
        match state:
            case 'override':
                relay.on()
                print(f"Override ON: Current Weight: {current_weight:.2f} LBS")
                # Skip the rest of the loop since override takes priority
                continue
            
            case 'standing_by':
                if relay.is_lit: 
                    relay.off()
                    print("Relay turned off.")
                print(f"Standing By: Current Weight: {current_weight:.2f} LBS")
            
            case 'job_running':
                print(f"Job Running: Current Weight: {current_weight:.2f} LBS Target Weight: {target_weight:.2f} LBS")
            
            case 'job_finished':
                relay.off()
                is_job_running = False
                button_2_pixel[0] = (0, 0, 255)  # Blue
                print("Job Finished! Target weight met.")

        # Handle button press to start/pause the job
        if button_2.is_pressed and not is_job_running:
            is_job_running = True
            relay.on()
            button_2_pixel[0] = (0, 255, 0)  # Green
            print("Starting Job")

        elif button_2.is_pressed and is_job_running:
            is_job_running = False
            relay.off()
            button_2_pixel[0] = (0, 0, 255)  # Blue
            print("Job Paused")

        # Handle weight setting
        if button_1.is_pressed and not is_job_running:
            if hold_button_1_count >= HOLD_DURATION:
                target_weight = current_weight  # Set target weight
                hold_button_1_count = 0
                button_1_pixel[0] = (0, 255, 0)  # Green
                print(f'Target weight set: {target_weight:.2f} LBS')
            else:
                hold_button_1_count += 1
                remaining_count = HOLD_DURATION - hold_button_1_count
                print(f"Requesting weight set in {remaining_count} seconds")
                button_1_pixel[0] = (255, 255, 0)  # Yellow

        # Handle scale calibration
        if button_1.is_pressed and button_2.is_pressed and not is_job_running:
            calabrate_scale()

except KeyboardInterrupt:
    print("Goodbyeeeeeeeee")
finally:
    button_1_pixel[0] = (0, 0, 0)
    button_2_pixel[0] = (0, 0, 0)
    GPIO.cleanup()
    print("GPIO cleanup complete.")