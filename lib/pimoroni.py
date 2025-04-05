"""
PicoDash - Stub for Pimoroni library
This is a minimal implementation for development without a physical device
"""


class RGBLED:
    def __init__(self, r_pin, g_pin, b_pin):
        self.r_pin = r_pin
        self.g_pin = g_pin
        self.b_pin = b_pin
        self.r = 0
        self.g = 0
        self.b = 0
        print(f"RGBLED initialized with R={r_pin}, G={g_pin}, B={b_pin}")

    def set_rgb(self, r, g, b):
        # Set the LED color
        self.r = r
        self.g = g
        self.b = b
        print(f"LED set to RGB({r}, {g}, {b})")


class Button:
    def __init__(self, pin):
        self.pin = pin
        self.state = False
        print(f"Button initialized on pin {pin}")

    def read(self):
        # In a simulator, we'll always return False
        # On real hardware, this would read the pin state
        return False

    # For simulation, add a method to simulate a button press
    def press(self):
        self.state = True
        print(f"Button on pin {self.pin} pressed")
        return True
