import RPi.GPIO as GPIO
from hx711 import HX711

# Define GPIO pins
DT_PIN = 6   
SCK_PIN = 5  

# Initialize HX711
hx = HX711(DT_PIN, SCK_PIN)

# Tare to zero
hx.tare()

# Calibration process
# Place a known weight (e.g., 10 lbs = 4535.92 grams) on the load cell
known_weight = 4535.92  # Known weight in grams

# Read raw data from the HX711
raw_data = hx.get_raw_data_mean()

if raw_data:
    print(f'Raw data: {raw_data}')
    # Calculate reference unit
    reference_unit = raw_data / known_weight
    print(f'Reference unit: {reference_unit}')
else:
    print('Failed to read raw data. Please check the sensor.')

# Set the reference unit
hx.set_reference_unit(reference_unit)

# Reset the HX711
hx.reset()

# Tare to zero again after setting reference unit
hx.tare()

print("Calibration complete. Reading weight...")

try:
    while True:
        # Read data from the HX711
        val = hx.get_weight(5)
        print(f'Weight: {val} g')
        hx.power_down()
        hx.power_up()
except (KeyboardInterrupt, SystemExit):
    # Cleanup GPIO on exit
    GPIO.cleanup()
    print("Exiting gracefully...")

