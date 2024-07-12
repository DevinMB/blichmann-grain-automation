import RPi.GPIO as GPIO
from hx711 import HX711

# Define GPIO pins
DT_PIN = 6   
SCK_PIN = 5  

# Initialize HX711
hx = HX711(DT_PIN, SCK_PIN)

# Tare to zero
hx.tare()

# Place a known weight (10 lbs) on the load cell and get raw data


reference_unit = 424.7008550023411
# Set the reference unit
hx.set_reference_unit(reference_unit)

# Reset the HX711
hx.reset()

# Tare to zero again after setting reference unit
hx.tare()

while True:
    try:
        # Read data from the HX711
        val = hx.get_weight(5)
        print(f'Weight: {val} g')
        hx.power_down()
        hx.power_up()
    except (KeyboardInterrupt, SystemExit):
        # Cleanup GPIO on exit
        GPIO.cleanup()
        break
