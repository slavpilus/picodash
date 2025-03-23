"""
PicoDash - Stub for PicoGraphics library
This is a minimal implementation for development without a physical device
"""

# Constants for display type
DISPLAY_PICO_DISPLAY = 0
PEN_RGB565 = 2  # 16-bit color mode

class PicoGraphics:
    def __init__(self, display=DISPLAY_PICO_DISPLAY, pen_type=PEN_RGB565, rotate=0):
        self.display = display
        self.pen_type = pen_type
        self.rotation = rotate
        self.width = 240
        self.height = 135
        self.current_pen = 0
        print(f"PicoGraphics initialized with display={display}, pen_type={pen_type}")
    
    def get_bounds(self):
        # Return display dimensions
        return (self.width, self.height)
    
    def create_pen(self, r, g, b):
        # Create a pen with the given RGB values
        # In a real implementation, this would create a 16-bit RGB565 value
        # For our stub, just return a simple number
        return (r << 16) | (g << 8) | b
    
    def set_pen(self, pen):
        # Set the current pen
        self.current_pen = pen
        r = (pen >> 16) & 0xFF
        g = (pen >> 8) & 0xFF
        b = pen & 0xFF
        print(f"Set pen to RGB({r}, {g}, {b})")
    
    def clear(self):
        # Clear the display
        print("Display cleared")
    
    def line(self, x1, y1, x2, y2):
        # Draw a line
        print(f"Drawing line from ({x1}, {y1}) to ({x2}, {y2})")
    
    def text(self, text, x, y, width, scale=1):
        # Draw text
        print(f"Drawing text '{text}' at ({x}, {y}) with width={width}, scale={scale}")
    
    def update(self):
        # Update the display
        print("Display updated")
    
    def set_backlight(self, brightness):
        # Set the backlight brightness (0.0-1.0)
        print(f"Setting backlight to {brightness}")