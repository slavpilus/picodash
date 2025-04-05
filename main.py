"""
PicoDash - A minimalistic dashboard for Raspberry Pi Pico W with Pimoroni Display Pack
Workspace-driven version with configuration from workspaces.yaml

Features:
- Auto-cycles through workspaces defined in workspaces.yaml
- Simple button controls (A: Next screen, B: System info, Y: Toggle auto-cycle)
- Visual LED indicators (red when WiFi disconnected, off when connected)
- Multiple renderer types (time, date, text, system info)
- Configurable via YAML file

Hardware:
- Raspberry Pi Pico W
- Pimoroni Display Pack (240x135 pixel IPS LCD)

Author: Slav Pilus (original) with Claude optimizations
License: MIT
"""

import time

import network
from picographics import DISPLAY_PICO_DISPLAY, PEN_RGB565, PicoGraphics
from pimoroni import RGBLED, Button

from lib.microdashboard import (
    DateRenderer,
    MicroDashboard,
    SystemRenderer,
    TextRenderer,
    TimeRenderer,
    WelcomeRenderer,
)
from lib.micropyaml import load

# ---- INITIALIZATION ----
print("Starting PicoDash Workspace Edition")

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

# ---- CONFIGURATION ----
# WiFi settings
wifi_connected = False
WIFI_RETRY_INTERVAL = 30000  # 30 seconds between connection attempts

# Dashboard settings
auto_cycle = True


# ---- UTILITY FUNCTIONS ----
def load_wifi_credentials():
    """Load WiFi credentials from config file"""
    try:
        with open("wifi_config.txt", "r") as f:
            config_text = f.read()

        ssid = None
        password = None

        for line in config_text.split("\n"):
            if line.startswith("SSID="):
                ssid = line[5:].strip()
            elif line.startswith("PASSWORD="):
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


def update_led():
    """Update LED status based on WiFi connection"""
    if not wifi_connected:
        led.set_rgb(255, 0, 0)  # Red for WiFi disconnected
    else:
        led.set_rgb(0, 0, 0)  # LED off


def load_workspaces():
    """Load workspaces from YAML file"""
    try:
        config = load("workspaces.yaml")
        if config and "workspaces" in config and config["workspaces"]:
            workspaces = config["workspaces"]
            # Make sure all workspaces have the required fields
            for workspace in workspaces:
                if "renderer" not in workspace:
                    print(f"Warning: Workspace missing renderer: {workspace}")
                if "display_time" not in workspace:
                    workspace["display_time"] = 5  # Default to 5 seconds

            print(f"Loaded {len(workspaces)} workspaces from workspaces.yaml")
            return config
        else:
            print("No valid workspaces found in workspaces.yaml")
            return None
    except Exception as e:
        print(f"Error loading workspaces: {e}")
        print("Using default workspaces")
        return None


# ---- MAIN FUNCTION ----
def main():
    """Main program loop"""
    global auto_cycle, wifi_connected

    try:
        # Attempt initial WiFi connection
        connect_wifi()

        # Initialize dashboard
        dashboard = MicroDashboard(display, width, height, wifi_connected, auto_cycle)
        dashboard.initialize_colors()

        # Register renderers
        dashboard.register_renderer("WelcomeRenderer", WelcomeRenderer)
        dashboard.register_renderer("TimeRenderer", TimeRenderer)
        dashboard.register_renderer("DateRenderer", DateRenderer)
        dashboard.register_renderer("SystemRenderer", SystemRenderer)
        dashboard.register_renderer("TextRenderer", TextRenderer)

        # Load workspaces from config
        config = load_workspaces()
        dashboard.load_workspaces(config)

        # Show initial workspace
        dashboard.render_current_workspace()

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
                dashboard.next_workspace()
                last_button_a = current_time
                last_screen_change = current_time  # Reset auto-cycle timer

            # Check button B with debounce - SYSTEM INFO
            if button_b.read() and (current_time - last_button_b > 300):
                # Find the system info workspace or use current if not found
                for i, workspace in enumerate(dashboard.workspaces):
                    if workspace.get("renderer") == "SystemRenderer":
                        dashboard.current_workspace_index = i
                        dashboard.render_current_workspace()
                        break
                last_button_b = current_time
                last_screen_change = current_time  # Reset auto-cycle timer

            # Check button Y with debounce - TOGGLE AUTO-CYCLE
            if button_y.read() and (current_time - last_button_y > 300):
                auto_cycle = not auto_cycle
                dashboard.auto_cycle = auto_cycle

                # Find the welcome workspace or use current if not found
                for i, workspace in enumerate(dashboard.workspaces):
                    if workspace.get("renderer") == "WelcomeRenderer":
                        dashboard.current_workspace_index = i
                        dashboard.render_current_workspace()
                        break
                last_button_y = current_time
                last_screen_change = current_time  # Reset auto-cycle timer

            # Auto-cycle screens if enabled
            if auto_cycle and (
                current_time - last_screen_change > dashboard.get_current_display_time() * 1000
            ):
                dashboard.next_workspace()
                last_screen_change = current_time

            # Update time display every second if on time screen
            if dashboard.workspaces and (current_time - last_time_update > 1000):
                current_workspace = dashboard.workspaces[dashboard.current_workspace_index]
                if current_workspace.get("renderer") == "TimeRenderer":
                    dashboard.render_current_workspace()
                    last_time_update = current_time

            # Try reconnecting WiFi periodically if disconnected
            if not wifi_connected and (current_time - last_wifi_attempt > WIFI_RETRY_INTERVAL):
                if connect_wifi():
                    # Update WiFi status in dashboard
                    dashboard.wifi_connected = wifi_connected
                    # Refresh current screen to update WiFi status
                    dashboard.render_current_workspace()
                last_wifi_attempt = current_time

            # Update LED based on WiFi status
            update_led()

            # Small delay to prevent CPU overload
            time.sleep(0.05)

    except Exception as e:
        # Show error screen
        display.set_pen(display.create_pen(0, 0, 0))
        display.clear()
        display.set_pen(display.create_pen(255, 0, 0))
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
            with open("error_log.txt", "w") as f:
                f.write(f"{type(e).__name__}: {error_msg}")
        except Exception as write_error:
            # Silently fail if we can't write the error log
            print(f"Could not write error log: {write_error}")


# Start the main program
if __name__ == "__main__":
    main()
