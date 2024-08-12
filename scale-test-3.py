import RPi.GPIO as GPIO
from hx711 import HX711
import time
import statistics

# Define GPIO pins
DT_PIN = 6
SCK_PIN = 5

# Initialize HX711
hx = HX711(DT_PIN, SCK_PIN)

# Set reference unit (calibrated previously)
reference_unit = -752.5262222222248
hx.set_reference_unit(reference_unit)

# Tare to zero
hx.reset()
hx.tare()

# Function to get stable weight with a statistical filter
def get_stable_weight(num_readings=10, tolerance=2):
    weights = []
    for _ in range(num_readings):
        weight = hx.get_weight(1)
        weights.append(weight)
        time.sleep(0.05)  # Short delay between readings to stabilize

    # Use median filtering to remove outliers
    median_weight = statistics.median(weights)
    filtered_weights = [w for w in weights if abs(w - median_weight) <= tolerance]

    # Return the average of filtered weights
    return sum(filtered_weights) / len(filtered_weights) if filtered_weights else median_weight

try:
    while True:
        # Read data from the HX711
        val = get_stable_weight(10, tolerance=2)
        print(f'Weight: {val:.2f} LBS')
        
        hx.power_down()
        time.sleep(0.1)  # Ensure the sensor has time to power down
        hx.power_up()
        time.sleep(0.5)  # Shorter delay to increase the frequency of readings
except (KeyboardInterrupt, SystemExit):
    # Cleanup GPIO on exit
    GPIO.cleanup()
    print("Exiting gracefully...")
