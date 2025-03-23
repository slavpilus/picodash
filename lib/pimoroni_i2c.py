"""
PicoDash - Stub for Pimoroni I2C library
This is a minimal implementation for development without a physical device
"""

class PimoroniI2C:
    def __init__(self, sda_pin, scl_pin):
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        print(f"PimoroniI2C initialized with SDA={sda_pin}, SCL={scl_pin}")
    
    def scan(self):
        # Return a list of device addresses (would be populated on actual hardware)
        return []