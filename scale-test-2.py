import RPi.GPIO as GPIO
from hx711 import HX711
import time

# Define GPIO pins
DT_PIN = 6   
SCK_PIN = 5  

# Initialize HX711
hx = HX711(DT_PIN, SCK_PIN)

time.sleep(1)
print(f"zeroing scale")

# Tare to zero
hx.tare()

# Place a known weight (10 lbs = 4535.92 grams) on the load cell and get raw data
reference_unit = 51678.0942222223  # Your previously calculated reference unit
hx.set_reference_unit(reference_unit)
# For Grams : 21.926201667283962
# For Pounds: 9944.223777777794

# Reset the HX711
hx.reset()

# Tare to zero again after setting reference unit
hx.tare()

def get_stable_weight(num_readings=10):
    weights = []
    for _ in range(num_readings):
        weight = hx.get_weight(1)
        weights.append(weight)
        time.sleep(0.2)  # Short delay between readings to stabilize
    return sum(weights) / len(weights)

# count_loops = 0

hx.power_down()
time.sleep(0.5)  # Ensure the sensor has time to power down
hx.power_up()
time.sleep(1)  # Delay between readings to allow the sensor to stabilize

print(f"starting reads..")

try:
    while True:
        # Read data from the HX711
        time.sleep(.04) # delay between reads to stabalize
        val = hx.get_weight(1)
        print(f'Weight: {val:.2f} LBS')
        # if(count_loops == 10):
        #     hx.power_down()
        #     time.sleep(0.5)  # Ensure the sensor has time to power down
        #     hx.power_up()
        #     time.sleep(1)  # Delay between readings to allow the sensor to stabilize
        #     count_loops = 0
        # else: 
        #     count_loops = count_loops + 1
        
except (KeyboardInterrupt, SystemExit):
    # Cleanup GPIO on exit
    GPIO.cleanup()
    print("Exiting gracefully...")