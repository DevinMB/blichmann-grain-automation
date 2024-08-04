import RPi.GPIO as GPIO
from hx711 import HX711
import time
# Define GPIO pins
DT_PIN = 6   
SCK_PIN = 5  
# Initialize HX711
hx = HX711(DT_PIN, SCK_PIN)
# Tare to zero
hx.tare()

# Place a known weight (10 lbs = 4535.92 grams) on the load cell and get raw data
reference_unit = 11613.582222222207  # Your previously calculated reference unit
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
        time.sleep(0.1)  # Short delay between readings to stabilize
    return sum(weights) / len(weights)
try:
    while True:
        # Read data from the HX711
        val = get_stable_weight(2)  # Get the average of 10 readings
        print(f'Weight: {val:.2f} LBS')
        
        hx.power_down()
        time.sleep(0.1)  # Ensure the sensor has time to power down
        hx.power_up()
        time.sleep(.7)  # Delay between readings to allow the sensor to stabilize
except (KeyboardInterrupt, SystemExit):
    # Cleanup GPIO on exit
    GPIO.cleanup()
    print("Exiting gracefully...")