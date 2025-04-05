"""
PicoDash - A minimalistic dashboard for Raspberry Pi Pico W with Pimoroni Display Pack
"""

import machine
import time
import json
import network
import gc
import os

# Basic initialization to help with troubleshooting
print("Starting PicoDash - Troubleshooting Mode")

try:
    from pimoroni_i2c import PimoroniI2C
    print("Imported PimoroniI2C successfully")
except ImportError as e:
    print(f"Error importing PimoroniI2C: {e}")

try:
    from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_RGB565
    print("Imported PicoGraphics successfully")
except ImportError as e:
    print(f"Error importing PicoGraphics: {e}")
    
try:
    from pimoroni import RGBLED, Button
    print("Imported RGBLED and Button successfully")
except ImportError as e:
    print(f"Error importing RGBLED/Button: {e}")

# Import workspace and YAML modules
try:
    from lib.microdashboard import WorkspaceManager, Workspace, TimeRenderer, DateRenderer, TextRenderer
    print("Imported workspace modules successfully")
except ImportError as e:
    print(f"Error importing workspace modules: {e}")
    
try:
    from lib.micropyaml import MicroYAML
    print("Imported MicroYAML successfully")
except ImportError as e:
    print(f"Error importing MicroYAML: {e}")

try:
    import urequests
    print("Imported urequests successfully")
except ImportError as e:
    print(f"Error importing urequests: {e}")

print("Import section completed")

# Colors - define some constants for easy reference
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Configuration constants
REFRESH_INTERVAL_MS = 60000  # 1 minute
ERROR_RETRY_INTERVAL_MS = 5000  # 5 seconds
DISPLAY_BRIGHTNESS = 0.5  # 50% brightness (0.0-1.0)
LED_BRIGHTNESS = 0.5  # 50% LED brightness (0.0-1.0)
API_HOST = "api.example.com"
API_PATH = "/notifications/count"
WORKSPACE_CONFIG_FILE = "workspaces.yaml"  # Configuration file for workspaces

# Initialize the Pimoroni Display
# Set rotation=0 for horizontal text orientation
display = PicoGraphics(display=DISPLAY_PICO_DISPLAY, pen_type=PEN_RGB565, rotate=0)
display_width, display_height = display.get_bounds()

# Initialize the workspace manager
workspace_manager = WorkspaceManager(display, display_width, display_height)

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

# Safe wrapper functions for display operations
def safe_set_pen(pen_value):
    """Safely set the pen, handling either color values or pen objects"""
    try:
        # Check if pen_value is an RGB tuple
        if isinstance(pen_value, tuple) and len(pen_value) == 3:
            r, g, b = pen_value
            pen = display.create_pen(r, g, b)
            display.set_pen(pen)
        else:
            # Assume it's a pen object from create_pen
            display.set_pen(pen_value)
    except Exception as e:
        print(f"Error in safe_set_pen: {e}")
        # Last resort fallback - try direct RGB values
        try:
            if pen_value == black_pen:
                display.set_pen(0)  # Black (0 value for all channels)
            elif pen_value == white_pen:
                display.set_pen(0xFFFFFF)  # White (max value for all channels)
            elif pen_value == red_pen:
                display.set_pen(0xFF0000)  # Red
            elif pen_value == green_pen:
                display.set_pen(0x00FF00)  # Green
            elif pen_value == blue_pen:
                display.set_pen(0x0000FF)  # Blue
            else:
                display.set_pen(0xFFFFFF)  # Default to white
        except Exception as e2:
            print(f"Critical error in safe_set_pen fallback: {e2}")

def safe_text(text_str, position):
    """Safely render text, handling different parameter formats"""
    try:
        # Always use the tuple format that's expected by the device
        display.text(text_str, position)
    except Exception as e:
        print(f"Error in safe_text: {e}")
        # Try a different approach as last resort
        try:
            if isinstance(position, tuple):
                x, y = position
                # Try calling with separate arguments
                display.text(text_str, x, y)
            else:
                # If position is not a tuple, try to handle it directly
                display.text(text_str, position)
        except Exception as e2:
            print(f"First fallback in safe_text failed: {e2}")
            try:
                # Try direct integer values for x and y
                if isinstance(position, tuple):
                    x, y = position
                    # Simplest possible approach
                    print(f"Trying text at position {x},{y} with direct method")
                    # Try with fixed values if all else fails
                    display.text(text_str, 10, 10)
                else:
                    display.text(text_str, 10, 10)
            except Exception as e3:
                print(f"Critical error in safe_text all fallbacks failed: {e3}")

class NotificationData:
    """Class to hold notification data"""
    def __init__(self, total_count=0, unread_count=0):
        self.total_count = total_count
        self.unread_count = unread_count

def load_workspace_config():
    """Load workspace configuration from YAML file"""
    try:
        # Check if the file exists, if not create it from example
        try:
            with open(WORKSPACE_CONFIG_FILE, 'r') as f:
                pass  # Just checking if it exists
        except OSError:
            print(f"Workspace config file not found, creating from example")
            try:
                # Try to copy from example
                with open(WORKSPACE_CONFIG_FILE+'.example', 'r') as src:
                    with open(WORKSPACE_CONFIG_FILE, 'w') as dest:
                        dest.write(src.read())
                print(f"Created {WORKSPACE_CONFIG_FILE} from example")
            except OSError as copy_err:
                print(f"Failed to create config from example: {copy_err}")
        
        # Try to load configuration from the YAML file
        config = MicroYAML.load_file(WORKSPACE_CONFIG_FILE)
        
        if not config or 'workspaces' not in config or not config['workspaces']:
            print("Invalid workspace configuration, using defaults")
            # Create a default configuration
            return {
                'workspaces': [
                    {
                        'name': 'Default Workspace',
                        'display_time': 10,
                        'renderer': 'TextRenderer',
                        'text': 'PicoDash - Default Config'
                    }
                ]
            }
        
        return config
    except Exception as e:
        print(f"Error loading workspace config: {e}")
        # Return a minimal default configuration
        return {
            'workspaces': [
                {
                    'name': 'Error Workspace',
                    'display_time': 10,
                    'renderer': 'TextRenderer',
                    'text': f'Config Error: {str(e)}'
                }
            ]
        }

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
    safe_set_pen(black_pen)
    display.clear()
    
    # Draw border
    safe_set_pen(white_pen)
    display.line(0, 0, display_width-1, 0)
    display.line(0, 0, 0, display_height-1)
    display.line(display_width-1, 0, display_width-1, display_height-1)
    display.line(0, display_height-1, display_width-1, display_height-1)
    
    # Draw title
    safe_set_pen(white_pen)
    safe_text("PicoDash", (10, 10))
    
    # Draw notification counts
    safe_text(f"Notifications: {data.total_count}", (10, 50))
    safe_text(f"Unread: {data.unread_count}", (10, 80))
    
    # Show WiFi status
    if wifi_connected:
        safe_set_pen(green_pen)
        safe_text("WiFi: Connected", (10, 110))
    else:
        safe_set_pen(red_pen)
        safe_text("WiFi: Disconnected", (10, 110))
    
    # Update the display
    display.update()

def render_error(error_message):
    """Render error message on display"""
    # Clear the display
    safe_set_pen(black_pen)
    display.clear()
    
    # Draw border in red
    safe_set_pen(red_pen)
    display.line(0, 0, display_width-1, 0)
    display.line(0, 0, 0, display_height-1)
    display.line(display_width-1, 0, display_width-1, display_height-1)
    display.line(0, display_height-1, display_width-1, display_height-1)
    
    # Draw error title
    safe_text("ERROR", (10, 10))
    
    # Draw error message
    safe_text(error_message, (10, 50))
    
    # Update the display
    display.update()

def handle_buttons():
    """Handle button presses"""
    if button_a.read():
        # Button A: Force start transition to next workspace
        print("Button A pressed - next workspace")
        if workspace_manager.workspaces and not workspace_manager.is_transitioning:
            workspace_manager._start_transition()
        return True
    
    if button_b.read():
        # Button B: Toggle WiFi
        print("Button B pressed - toggling WiFi")
        connect_wifi()
        return True
    
    if button_x.read():
        # Button X: Show system info
        print("Button X pressed - showing system info")
        safe_set_pen(black_pen)
        display.clear()
        safe_set_pen(white_pen)
        
        # Get memory info
        gc.collect()
        mem_free = gc.mem_free()
        mem_alloc = gc.mem_alloc()
        total = mem_free + mem_alloc
        
        # Get workspace info
        workspace_count = len(workspace_manager.workspaces)
        current_workspace = workspace_manager.current_index + 1 if workspace_count > 0 else 0
        
        safe_text("System Info", (10, 10))
        safe_text(f"Free Mem: {mem_free} bytes", (10, 40))
        safe_text(f"Used: {mem_alloc} bytes", (10, 60))
        
        # Add workspace info
        safe_set_pen(green_pen)
        safe_text(f"Workspaces: {workspace_count}", (10, 80))
        safe_text(f"Current: {current_workspace}/{workspace_count}", (10, 100))
        
        # Add button controls
        safe_set_pen(white_pen)
        safe_text("A: Next view   B: Toggle WiFi", (10, 120))
        
        display.update()
        time.sleep(3)  # Show for 3 seconds
        return True
    
    if button_y.read():
        # Button Y: Return to first workspace
        print("Button Y pressed - return to first workspace")
        if workspace_manager.workspaces:
            workspace_manager.current_index = 0
        return True
    
    return False

def show_error_led():
    """Flash the LED red to indicate an error"""
    for _ in range(5):  # Flash 5 times
        led.set_rgb(255, 0, 0)  # Red
        time.sleep(0.2)
        led.set_rgb(0, 0, 0)    # Off
        time.sleep(0.2)
    led.set_rgb(255, 0, 0)  # Keep red for continuous error indication

def show_splash_screen():
    """Show a splash screen on startup"""
    # Initialize display
    safe_set_pen(black_pen)
    display.clear()
    safe_set_pen(white_pen)
    safe_text("PicoDash", (10, 10))
    safe_text("Starting...", (10, 50))
    display.update()
    
    # Give the system time to initialize
    time.sleep(1)

def main():
    """Main function"""
    print("PicoDash main function starting...")
    
    try:
        # Set initial LED color
        print("Setting initial LED color")
        led.set_rgb(YELLOW)  # Yellow during startup
        
        # Set display brightness
        print("Setting display brightness")
        display.set_backlight(DISPLAY_BRIGHTNESS)
        
        # Show splash screen
        print("Showing splash screen")
        show_splash_screen()
        
        # Try to connect to WiFi
        print("Connecting to WiFi")
        try:
            connect_wifi()
        except Exception as e:
            print(f"WiFi error: {e}")
        
        # Load workspace configuration
        print("Loading workspace configuration")
        config = load_workspace_config()
        print(f"Config loaded: {config}")
        
        # Configure workspace manager
        print("Configuring workspace manager")
        if not workspace_manager.load_from_config(config):
            # If loading failed, create a default error workspace
            print("Failed to load workspaces from config, creating default")
            error_text = "Failed to load workspaces"
            workspace = Workspace("Error", 10)
            renderer = TextRenderer(error_text)  # Create renderer first
            workspace.set_renderer(renderer)     # Then set it in the workspace
            workspace_manager.add_workspace(workspace)
            print(error_text)
            # Indicate error with LED
            show_error_led()
        
        # Add default notification workspace if configured workspaces exist
        print(f"Workspace count: {len(workspace_manager.workspaces)}")
        if len(workspace_manager.workspaces) > 0:
            # Fetch initial data
            print("Fetching notification data")
            data = fetch_data()
            
            # Create a custom notification renderer
            print("Creating notification workspace")
            notification_text = f"Notifications: {data.total_count}, Unread: {data.unread_count}"
            notification_workspace = Workspace("Notifications", 10)
            renderer = TextRenderer(notification_text)  # Create renderer first
            notification_workspace.set_renderer(renderer)  # Then set it
            workspace_manager.add_workspace(notification_workspace)
        
        # Main loop
        print("Starting main loop")
        last_data_update = time.ticks_ms()
        
        # Force first render before entering loop
        print("Initial workspace render")
        if len(workspace_manager.workspaces) > 0:
            try:
                print("Updating first workspace")
                workspace_manager.workspaces[0].update()
                print("Rendering first workspace")
                workspace_manager.workspaces[0].render()
                print("First workspace rendered successfully")
            except Exception as e:
                print(f"ERROR in initial render: {type(e).__name__}: {e}")
                show_error_led()
        
        while True:
            # Handle button presses
            if handle_buttons():
                # If a button was pressed, reset the last update time
                last_data_update = time.ticks_ms()
                time.sleep(0.2)  # Debounce
                continue
                
            # Check if it's time to update notification data
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, last_data_update) > REFRESH_INTERVAL_MS:
                print("Time to refresh data")
                try:
                    # Get fresh notification data
                    data = fetch_data()
                    
                    # Update the notification workspace if it exists
                    if len(workspace_manager.workspaces) > 0:
                        # For simplicity, we'll assume the last workspace is the notification one
                        notification_text = f"Notifications: {data.total_count}, Unread: {data.unread_count}"
                        last_workspace_index = len(workspace_manager.workspaces) - 1
                        notification_workspace = workspace_manager.workspaces[last_workspace_index]
                        if isinstance(notification_workspace.renderer, TextRenderer):
                            notification_workspace.renderer.text = notification_text
                except Exception as e:
                    print(f"Error refreshing data: {e}")
                    
                last_data_update = time.ticks_ms()
            
            # Update the workspace manager (handles transitions and rendering)
            try:
                print("Updating workspace manager")
                workspace_manager.update()
                print("Workspace manager updated successfully")
            except Exception as e:
                print(f"ERROR updating workspace manager: {type(e).__name__}: {e}")
                # Try a simple direct render as a fallback
                try:
                    print("Attempting simple fallback render")
                    safe_set_pen(black_pen)  # Black
                    display.clear()
                    safe_set_pen(white_pen)  # White
                    safe_text("Error - Check REPL", (10, 10))
                    display.update()
                    show_error_led()
                except Exception as e2:
                    print(f"CRITICAL: Even fallback render failed: {e2}")
            
            # Sleep to reduce power consumption
            time.sleep(0.1)  # Slightly longer sleep for stability
            
    except Exception as e:
        print(f"CRITICAL ERROR in main function: {e}")
        print("Details:", str(type(e)), str(e))
        # Show error LED
        try:
            show_error_led()
        except Exception:
            # Last resort - just set LED to steady red
            try:
                led.set_rgb(255, 0, 0)
            except Exception:
                pass  # Nothing more we can do
                
        # Basic fallback display
        try:
            safe_set_pen(red_pen)  # Red
            display.clear()
            safe_set_pen(white_pen)  # White
            safe_text(f"Error: {type(e).__name__}", (10, 10))
            safe_text(str(e)[:20], (10, 50))
            display.update()
        except Exception as display_err:
            print(f"Cannot even show error: {display_err}")

# Run the main function
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        render_error(f"Fatal error: {str(e)}")
        raise