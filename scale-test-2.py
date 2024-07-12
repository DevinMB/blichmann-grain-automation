import RPi.GPIO as GPIO
from hx711 import HX711
import time
import statistics

# Define GPIO pins
DT_PIN = 6   
SCK_PIN = 5  

# Initialize HX711
hx = HX711(DT_PIN, SCK_PIN)

# Tare to zero
hx.tare()

# Place a known weight (10 lbs = 4535.92 grams) on the load cell and get raw data
reference_unit = 424.7008550023411  # Your previously calculated reference unit
hx.set_reference_unit(reference_unit)

# Reset the HX711
hx.reset()

# Tare to zero again after setting reference unit
hx.tare()

def get_stable_weight(num_readings=10):
    weights = []
    for _ in range(num_readings):
        weight = hx.get_weight(1)
        weights.append(weight)
        time.sleep(0.1)  # Short delay between readings to stabilize
    return statistics.mean(weights), statistics.stdev(weights)

def moving_average(new_value, values, window_size):
    values.append(new_value)
    if len(values) > window_size:
        values.pop(0)
    return sum(values) / len(values)

# Parameters for moving average filter
window_size = 10
weight_values = []

try:
    while True:
        # Read data from the HX711
        average_weight, stdev_weight = get_stable_weight(10)
        stable_weight = moving_average(average_weight, weight_values, window_size)

        if stdev_weight < 5:  # Adjust this threshold as needed
            print(f'Weight: {stable_weight:.2f} g')
        else:
            print("Unstable reading, retrying...")
        
        hx.power_down()
        hx.power_up()
        time.sleep(1)  # Delay between readings
except (KeyboardInterrupt, SystemExit):
    # Cleanup GPIO on exit
    GPIO.cleanup()
    print("Exiting gracefully...")
