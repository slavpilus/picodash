"""
PicoDash - A minimalistic dashboard for Raspberry Pi Pico W with Pimoroni Display Pack
Clean, optimized version with auto-cycling and working around broken X button

Features:
- Auto-cycles through different screens (Welcome, Time, Date, System Info)
- Simple button controls (A: Next screen, B: System info, Y: Toggle auto-cycle)
- Visual LED indicators for different screens
- Real-time clock updates
- WiFi connectivity status display
- Memory usage monitoring

Hardware:
- Raspberry Pi Pico W
- Pimoroni Display Pack (240x135 pixel IPS LCD)

Author: Slav Pilus (original) with Claude optimizations
License: MIT
"""

import time
import gc
import network
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_RGB565
from pimoroni import RGBLED, Button

# ---- INITIALIZATION ----
print("Starting PicoDash")

# Initialize display
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_RGB565, rotate=0)
width, height = display.get_bounds()
display.set_backlight(0.8)  # 80% brightness

# Initialize LED and buttons
led = RGBLED(6, 7, 8)
button_a = Button(12)  # Next screen
button_b = Button(13)  # System info
button_y = Button(15)  # Toggle auto-cycle
# Note: X button (14) is not used - known hardware issue

# Create pens
BLACK = display.create_pen(0, 0, 0)
WHITE = display.create_pen(255, 255, 255)
RED = display.create_pen(255, 0, 0)
GREEN = display.create_pen(0, 255, 0)
BLUE = display.create_pen(0, 0, 255)
YELLOW = display.create_pen(255, 255, 0)
PURPLE = display.create_pen(255, 0, 255)
DARK_ORANGE = display.create_pen(255, 140, 0)  # Added dark orange for consistent UI elements

# ---- CONFIGURATION ----
# Auto-cycle settings
auto_cycle = True
current_screen_index = 0
screens = ["welcome", "time", "date", "system"]
display_times = [5, 10, 8, 7]  # Time in seconds for each screen

# WiFi settings
wifi_connected = False
WIFI_RETRY_INTERVAL = 30000  # 30 seconds between connection attempts

# ---- UTILITY FUNCTIONS ----
def draw_border():
    """Draw a border around the screen"""
    display.line(0, 0, width-1, 0)
    display.line(0, 0, 0, height-1) 
    display.line(width-1, 0, width-1, height-1)
    display.line(0, height-1, width-1, height-1)

def load_wifi_credentials():
    """Load WiFi credentials from config file"""
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
            print("WiFi config incomplete")
            return None
    except OSError:
        print("WiFi config file not found")
        return None

def connect_wifi():
    """Attempt to connect to WiFi"""
    global wifi_connected
    
    credentials = load_wifi_credentials()
    if not credentials:
        return False
        
    ssid, password = credentials
    print(f"Connecting to WiFi: {ssid}")
    
    # Set LED to red during connection attempts
    led.set_rgb(255, 0, 0)
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Only attempt connection if not already connected
    if not wlan.isconnected():
        try:
            wlan.connect(ssid, password)
            
            # Wait for connection with timeout
            max_wait = 10  # 5 seconds
            while max_wait > 0:
                if wlan.isconnected():
                    wifi_connected = True
                    print(f"Connected to WiFi. IP: {wlan.ifconfig()[0]}")
                    return True
                max_wait -= 1
                time.sleep(0.5)
            
            # Connection failed
            wifi_connected = False
            print("Failed to connect to WiFi")
            return False
        except Exception as e:
            print(f"WiFi connection error: {e}")
            wifi_connected = False
            return False
    else:
        # Already connected
        wifi_connected = True
        print(f"Already connected to WiFi. IP: {wlan.ifconfig()[0]}")
        return True

# ---- SCREEN RENDERING FUNCTIONS ----
def show_welcome():
    """Show welcome screen with information and controls"""
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    
    # Draw border
    draw_border()
    
    # Draw title and version
    display.text("PicoDash", 10, 10)
    display.text("v1.0", width-40, 10)
    
    # Draw instructions
    display.text("Controls:", 10, 35)
    display.text("A: Next Screen", 20, 55)
    display.text("B: System Info", 20, 75)
    display.text("Y: Toggle Auto-Cycle", 20, 95)
    
    # Use dark orange pen for bottom text
    display.set_pen(DARK_ORANGE)
    
    # Show WiFi status on left side (shortened)
    if wifi_connected:
        wifi_text = "WiFi: ON"
    else:
        wifi_text = "WiFi: OFF"
    display.text(wifi_text, 10, height-25)
    
    # Show auto-cycle status on right side
    auto_text = f"Auto: {('ON' if auto_cycle else 'OFF')}"
    display.text(auto_text, width-100, height-25)
    
    display.update()
    # Only show RED LED when WiFi is disconnected, otherwise off
    if not wifi_connected:
        led.set_rgb(255, 0, 0)  # Red for WiFi disconnected
    else:
        led.set_rgb(0, 0, 0)  # LED off

def show_time():
    """Show current time"""
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    
    # Draw border
    draw_border()
    
    # Get and format current time
    current = time.localtime()
    time_str = "{:02d}:{:02d}:{:02d}".format(current[3], current[4], current[5])  # HH:MM:SS
    
    # Draw text
    display.text("Current Time", 10, 10)
    
    # Draw time in larger text (centered)
    display.set_pen(WHITE)
    display.text(time_str, width//2-30, height//2-10)
    
    # Use dark orange pen for bottom text
    display.set_pen(DARK_ORANGE)
    display.text("A: Next", 10, height-25)
    
    # Show auto-cycle status on right side
    auto_text = f"Auto: {('ON' if auto_cycle else 'OFF')}"
    display.text(auto_text, width-100, height-25)
    
    # Show WiFi status in corner with enough space
    if wifi_connected:
        display.set_pen(GREEN)
    else:
        display.set_pen(RED)
    display.text("WiFi", width-40, 10)
    
    display.update()
    # Only show RED LED when WiFi is disconnected, otherwise off
    if not wifi_connected:
        led.set_rgb(255, 0, 0)  # Red for WiFi disconnected
    else:
        led.set_rgb(0, 0, 0)  # LED off

def show_date():
    """Show current date"""
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    
    # Draw border
    draw_border()
    
    # Get and format current date
    current = time.localtime()
    date_str = "{:04d}-{:02d}-{:02d}".format(current[0], current[1], current[2])  # YYYY-MM-DD
    
    # Draw text
    display.text("Current Date", 10, 10)
    
    # Draw date
    display.set_pen(WHITE)
    display.text(date_str, width//2-50, height//2-20)
    
    # Draw weekday
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday = weekdays[current[6]]  # current[6] is weekday (0-6, Monday is 0)
    display.text(weekday, width//2-30, height//2+10)
    
    # Use dark orange pen for bottom text
    display.set_pen(DARK_ORANGE)
    display.text("A: Next", 10, height-25)
    
    # Show auto-cycle status on right side
    auto_text = f"Auto: {('ON' if auto_cycle else 'OFF')}"
    display.text(auto_text, width-100, height-25)
    
    display.update()
    # Only show RED LED when WiFi is disconnected, otherwise off
    if not wifi_connected:
        led.set_rgb(255, 0, 0)  # Red for WiFi disconnected
    else:
        led.set_rgb(0, 0, 0)  # LED off

def show_system_info():
    """Show system information"""
    display.set_pen(BLACK)
    display.clear()
    display.set_pen(WHITE)
    
    # Draw border
    draw_border()
    
    # Get memory info
    gc.collect()
    mem_free = gc.mem_free()
    mem_alloc = gc.mem_alloc()
    mem_total = mem_free + mem_alloc
    mem_percent = int((mem_alloc / mem_total) * 100)
    
    # Draw title
    display.text("System Info", 10, 10)
    
    # Draw memory stats with KB units for better display
    mem_free_kb = round(mem_free / 1024, 1)
    mem_alloc_kb = round(mem_alloc / 1024, 1)
    
    display.text(f"Free: {mem_free_kb} KB", 10, 35)
    display.text(f"Used: {mem_alloc_kb} KB", 10, 55)
    display.text(f"Usage: {mem_percent}%", 10, 75)
    display.text(f"Display: {width}x{height}", 10, 95)
    
    # Use dark orange pen for bottom text
    display.set_pen(DARK_ORANGE)
    display.text("A: Next", 10, height-25)
    
    # Show auto-cycle status on right side
    auto_text = f"Auto: {('ON' if auto_cycle else 'OFF')}"
    display.text(auto_text, width-100, height-25)
    
    display.update()
    # Only show RED LED when WiFi is disconnected, otherwise off
    if not wifi_connected:
        led.set_rgb(255, 0, 0)  # Red for WiFi disconnected
    else:
        led.set_rgb(0, 0, 0)  # LED off

# ---- SCREEN MANAGEMENT FUNCTIONS ----
def next_screen():
    """Change to the next screen in the cycle"""
    global current_screen_index
    current_screen_index = (current_screen_index + 1) % len(screens)
    show_screen(screens[current_screen_index])
    
def show_screen(screen_name):
    """Show a specific screen by name"""
    if screen_name == "welcome":
        show_welcome()
    elif screen_name == "time":
        show_time()
    elif screen_name == "date":
        show_date()
    elif screen_name == "system":
        show_system_info()

# ---- MAIN FUNCTION ----
def main():
    """Main program loop"""
    global auto_cycle, current_screen_index
    
    try:
        # Attempt initial WiFi connection
        connect_wifi()
        
        # Show initial welcome screen
        show_welcome()
        
        # Initialize timers
        last_button_a = 0
        last_button_b = 0
        last_button_y = 0
        last_screen_change = time.ticks_ms()
        last_time_update = time.ticks_ms()
        last_wifi_attempt = time.ticks_ms()
        
        # Main loop
        while True:
            current_time = time.ticks_ms()
            
            # Check button A with debounce - NEXT SCREEN
            if button_a.read() and (current_time - last_button_a > 300):
                next_screen()
                last_button_a = current_time
                last_screen_change = current_time  # Reset auto-cycle timer
            
            # Check button B with debounce - SYSTEM INFO
            if button_b.read() and (current_time - last_button_b > 300):
                current_screen_index = screens.index("system")
                show_system_info()
                last_button_b = current_time
                last_screen_change = current_time  # Reset auto-cycle timer
            
            # Check button Y with debounce - TOGGLE AUTO-CYCLE
            if button_y.read() and (current_time - last_button_y > 300):
                auto_cycle = not auto_cycle
                current_screen_index = screens.index("welcome")
                show_welcome()  # Show welcome with updated auto-cycle status
                last_button_y = current_time
                last_screen_change = current_time  # Reset auto-cycle timer
            
            # Auto-cycle screens if enabled
            if auto_cycle and (current_time - last_screen_change > display_times[current_screen_index] * 1000):
                next_screen()
                last_screen_change = current_time
            
            # Update time display every second if on time screen
            if screens[current_screen_index] == "time" and (current_time - last_time_update > 1000):
                show_time()
                last_time_update = current_time
            
            # Try reconnecting WiFi periodically if disconnected
            if not wifi_connected and (current_time - last_wifi_attempt > WIFI_RETRY_INTERVAL):
                connect_wifi()
                last_wifi_attempt = current_time
                # Refresh current screen to update WiFi status
                show_screen(screens[current_screen_index])
            
            # Small delay to prevent CPU overload
            time.sleep(0.05)
            
    except Exception as e:
        # Show error screen
        display.set_pen(BLACK)
        display.clear()
        display.set_pen(RED)
        display.text("ERROR:", 10, 10)
        display.text(str(type(e).__name__), 10, 40)
        error_msg = str(e)
        display.text(error_msg[:20], 10, 70)
        if len(error_msg) > 20:
            display.text(error_msg[20:40], 10, 90)
        display.update()
        
        # Red LED for error
        led.set_rgb(255, 0, 0)
        
        # Save error to file for debugging
        try:
            with open('error_log.txt', 'w') as f:
                f.write(f"{type(e).__name__}: {error_msg}")
        except:
            pass

# Start the main program
if __name__ == "__main__":
    main()