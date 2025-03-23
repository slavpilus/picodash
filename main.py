"""
PicoDash - A minimalistic dashboard for Raspberry Pi Pico W with Pimoroni Display Pack
"""

import machine
import time
import json
import network
import urequests
import gc
import os

from pimoroni_i2c import PimoroniI2C
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_RGB565
from pimoroni import RGBLED, Button

# Colors - define some constants for easy reference
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Configuration constants
REFRESH_INTERVAL_MS = 60000  # 1 minute
ERROR_RETRY_INTERVAL_MS = 5000  # 5 seconds
DISPLAY_BRIGHTNESS = 0.5  # 50% brightness (0.0-1.0)
API_HOST = "api.example.com"
API_PATH = "/notifications/count"

# Initialize the Pimoroni Display
# Set rotation=0 for horizontal text orientation
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_RGB565, rotate=0)
display_width, display_height = display.get_bounds()

# Initialize the RGB LED
led = RGBLED(6, 7, 8)  # RGB pins for Pico Display Pack

# Initialize buttons
button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

# Create pens for drawing
black_pen = display.create_pen(0, 0, 0)
white_pen = display.create_pen(255, 255, 255)
red_pen = display.create_pen(255, 0, 0)
green_pen = display.create_pen(0, 255, 0)
blue_pen = display.create_pen(0, 0, 255)

# WiFi status
wifi_connected = False

class NotificationData:
    """Class to hold notification data"""
    def __init__(self, total_count=0, unread_count=0):
        self.total_count = total_count
        self.unread_count = unread_count

def load_wifi_credentials():
    """Load WiFi credentials from config file or return defaults"""
    try:
        with open('wifi_config.txt', 'r') as f:
            config_text = f.read()
            
        ssid = None
        password = None
        
        for line in config_text.split('\n'):
            if line.startswith('SSID='):
                ssid = line[5:].strip()
            elif line.startswith('PASSWORD='):
                password = line[9:].strip()
                
        if ssid and password:
            return (ssid, password)
        else:
            print("WiFi config incomplete, using defaults")
            return ("YourSSID", "YourPassword")
    except OSError:
        print("WiFi config file not found, using defaults")
        return ("YourSSID", "YourPassword")

def connect_wifi():
    """Connect to WiFi using credentials from config file"""
    global wifi_connected
    
    ssid, password = load_wifi_credentials()
    print(f"Connecting to WiFi: {ssid}")
    
    # Set LED to blue during connection
    led.set_rgb(0, 0, 255)
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Connect to WiFi
    if not wlan.isconnected():
        # Clear any previous connection
        wlan.disconnect()
        wlan.connect(ssid, password)
        
        # Wait for connection with timeout
        max_wait = 20  # 10 seconds
        while max_wait > 0:
            if wlan.isconnected():
                wifi_connected = True
                led.set_rgb(0, 255, 0)  # Green when connected
                print(f"Connected to WiFi. IP: {wlan.ifconfig()[0]}")
                return True
            max_wait -= 1
            led.set_rgb(0, 0, int(255 * (max_wait % 2)))  # Flash blue during connection
            time.sleep(0.5)
        
        # Connection failed
        wifi_connected = False
        led.set_rgb(255, 0, 0)  # Red for failure
        print("Failed to connect to WiFi")
        return False
    else:
        # Already connected
        wifi_connected = True
        led.set_rgb(0, 255, 0)  # Green when connected
        print(f"Already connected to WiFi. IP: {wlan.ifconfig()[0]}")
        return True

def fetch_data():
    """Fetch notification data from API"""
    if not wifi_connected:
        if not connect_wifi():
            return NotificationData(0, 0)
    
    try:
        # In Phase 2, we'll implement actual API fetching
        # For Phase 1, return dummy data
        dummy_data = {
            "notifications": {
                "total": 5,
                "unread": 2
            }
        }
        
        # Parse the data
        data = NotificationData(
            total_count=dummy_data["notifications"]["total"],
            unread_count=dummy_data["notifications"]["unread"]
        )
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return NotificationData(0, 0)

def render_dashboard(data):
    """Render dashboard with notification data"""
    # Clear the display
    display.set_pen(black_pen)
    display.clear()
    
    # Draw border
    display.set_pen(white_pen)
    display.line(0, 0, display_width-1, 0)
    display.line(0, 0, 0, display_height-1)
    display.line(display_width-1, 0, display_width-1, display_height-1)
    display.line(0, display_height-1, display_width-1, display_height-1)
    
    # Draw title
    display.set_pen(white_pen)
    display.text("PicoDash", 10, 10, 240, 3)
    
    # Draw notification counts
    display.text(f"Notifications: {data.total_count}", 10, 50, 220, 2)
    display.text(f"Unread: {data.unread_count}", 10, 80, 220, 2)
    
    # Show WiFi status
    if wifi_connected:
        display.set_pen(green_pen)
        display.text("WiFi: Connected", 10, 110, 220, 2)
    else:
        display.set_pen(red_pen)
        display.text("WiFi: Disconnected", 10, 110, 220, 2)
    
    # Update the display
    display.update()

def render_error(error_message):
    """Render error message on display"""
    # Clear the display
    display.set_pen(black_pen)
    display.clear()
    
    # Draw border in red
    display.set_pen(red_pen)
    display.line(0, 0, display_width-1, 0)
    display.line(0, 0, 0, display_height-1)
    display.line(display_width-1, 0, display_width-1, display_height-1)
    display.line(0, display_height-1, display_width-1, display_height-1)
    
    # Draw error title
    display.text("ERROR", 10, 10, 240, 3)
    
    # Draw error message
    display.text(error_message, 10, 50, 220, 2)
    
    # Update the display
    display.update()

def handle_buttons():
    """Handle button presses"""
    if button_a.read():
        # Button A: Refresh data
        print("Button A pressed - refreshing data")
        data = fetch_data()
        render_dashboard(data)
        return True
    
    if button_b.read():
        # Button B: Toggle WiFi
        print("Button B pressed - toggling WiFi")
        connect_wifi()
        return True
    
    if button_x.read():
        # Button X: Show system info
        print("Button X pressed - showing system info")
        display.set_pen(black_pen)
        display.clear()
        display.set_pen(white_pen)
        
        # Get memory info
        gc.collect()
        mem_free = gc.mem_free()
        mem_alloc = gc.mem_alloc()
        total = mem_free + mem_alloc
        
        display.text("System Info", 10, 10, 220, 3)
        display.text(f"Free Mem: {mem_free} bytes", 10, 50, 220, 2)
        display.text(f"Used: {mem_alloc} bytes", 10, 80, 220, 2)
        display.text(f"Total: {total} bytes", 10, 110, 220, 2)
        
        display.update()
        return True
    
    if button_y.read():
        # Button Y: Go back to dashboard
        print("Button Y pressed - back to dashboard")
        data = fetch_data()
        render_dashboard(data)
        return True
    
    return False

def main():
    """Main function"""
    print("PicoDash starting...")
    
    # Set initial LED color
    led.set_rgb(255, 255, 0)  # Yellow during startup
    
    # Set display brightness
    display.set_backlight(DISPLAY_BRIGHTNESS)
    
    # Initialize display
    display.set_pen(black_pen)
    display.clear()
    display.set_pen(white_pen)
    display.text("PicoDash", 10, 10, 240, 3)
    display.text("Starting...", 10, 50, 220, 2)
    display.update()
    
    # Give the system time to initialize
    time.sleep(1)
    
    # Try to connect to WiFi (not required for Phase 1)
    try:
        connect_wifi()
    except Exception as e:
        print(f"WiFi error: {e}")
    
    # Fetch initial data
    data = fetch_data()
    
    # Render dashboard
    render_dashboard(data)
    
    # Main loop
    last_update = time.ticks_ms()
    
    while True:
        # Handle button presses
        if handle_buttons():
            # If a button was pressed, reset the last update time
            last_update = time.ticks_ms()
            time.sleep(0.2)  # Debounce
            continue
            
        # Check if it's time to update
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_update) > REFRESH_INTERVAL_MS:
            print("Time to refresh data")
            try:
                data = fetch_data()
                render_dashboard(data)
            except Exception as e:
                render_error(str(e))
                time.sleep(ERROR_RETRY_INTERVAL_MS / 1000)
                
            last_update = time.ticks_ms()
        
        # Sleep to reduce power consumption
        time.sleep(0.1)

# Run the main function
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        render_error(f"Fatal error: {str(e)}")
        raise