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

print("Place 10lbs on scale...")
time.sleep(60)

# Calibration process
# Place a known weight (e.g., 10 lbs) on the load cell
known_weight_lbs = 10.0  # Known weight in pounds

# Read raw data from the HX711 multiple times
num_readings = 100
readings = []

print("Starting calibration. Please wait...")

for _ in range(num_readings):
    raw_data = hx.get_weight(5)  # Take one reading at a time
    if raw_data is not None:
        readings.append(raw_data)
    time.sleep(0.1)  # Short delay between readings to stabilize

# Calculate the average raw data value
if readings:
    average_raw_data = sum(readings) / len(readings)
    print(f'Average raw data: {average_raw_data}')
    # Calculate reference unit
    reference_unit = average_raw_data / known_weight_lbs
    print(f'Reference unit: {reference_unit}')
else:
    print('Failed to read raw data. Please check the sensor.')

GPIO.cleanup()
