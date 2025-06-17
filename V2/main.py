# main.py  (runs on the Pi with real hardware)
import board, neopixel
from gpiozero import Button, LED
from hx711 import HX711
from controller import ScaleController

# ------------------------------------------------------------------ #
# Instantiate actual hardware objects
hx = HX711(dout_pin=6, pd_sck_pin=5)
relay = LED(17)
button_1 = Button(26)
button_2 = Button(16)
override_switch = Button(24)
pixel_1 = neopixel.NeoPixel(pin=board.D21, n=1, brightness=0.2, auto_write=True)
pixel_2 = neopixel.NeoPixel(pin=board.D18, n=1, brightness=0.2, auto_write=True)

ctrl = ScaleController(
    hx=hx,
    relay=relay,
    button_1=button_1,
    button_2=button_2,
    override_switch=override_switch,
    pixel_1=pixel_1,
    pixel_2=pixel_2,
)

try:
    while True:
        ctrl.tick()
finally:
    pixel_1[0] = (0, 0, 0)
    pixel_2[0] = (0, 0, 0)
    relay.off()
    print("Clean shutdown")
