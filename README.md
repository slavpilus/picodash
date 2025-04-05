# PicoDash - Raspberry Pi Pico W Dashboard

A minimalistic dashboard application for the Raspberry Pi Pico W with Pimoroni Display Pack, written in MicroPython.

## Hardware Requirements

- Raspberry Pi Pico W
- Pimoroni Pico Display Pack (240x135 pixel IPS LCD)

## Features

- Auto-cycling screens (Welcome, Time, Date, System Info)
- Simple button controls
- Wi-Fi connectivity status
- Visual LED indicators for different screens
- Memory usage monitoring
- Real-time clock updates

## Setup Instructions (Command Line)

### 1. Flash MicroPython to your Pico W

First, you need to install MicroPython on your Pico W:

1. Download the latest Pimoroni MicroPython firmware for Pico W from: https://github.com/pimoroni/pimoroni-pico/releases (Tested with version [v1.24.0-beta2](https://github.com/pimoroni/pimoroni-pico/releases/tag/v1.24.0-beta2))
2. Hold the BOOTSEL button on your Pico W while connecting it to your computer
3. It will mount as a USB drive
4. Copy the `.uf2` firmware file to the drive
5. The Pico will automatically reboot and unmount

### 2. Install Required Command-Line Tools

```bash
# Create a Python virtual environment (recommended)
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install project requirements
pip install -r requirements.txt
# OR
make install-tools
```

This will install:
- `rshell`: Terminal-based shell for MicroPython
- `ampy`: Tool for transferring files to/from MicroPython boards
- `mpremote`: Official tool for interacting with MicroPython boards

> **Note:** Always activate the virtual environment before working on the project to avoid system package conflicts.

### 3. Configure WiFi

```bash
# Create a wifi_config.txt from the example
cp wifi_config.txt.example wifi_config.txt
# OR
make wifi_config

# Edit the file with your WiFi credentials
nano wifi_config.txt
```

### 4. Upload Files to the Pico W

```bash
# Determine your Pico's serial port
# Linux: typically /dev/ttyACM0
# macOS: typically /dev/cu.usbmodem*
# Windows: typically COM4

# Find serial ports on macOS:
ls /dev/cu.usbmodem*

# Upload the files
mpremote connect /dev/cu.usbmodem* cp picodash.py :/main.py

# OR use make (if available)
make upload PORT=/dev/cu.usbmodem*
```

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Display help information |
| `make install-tools` | Install required Python tools |
| `make upload` | Upload all files to the Pico |
| `make upload-main` | Upload only main files |
| `make upload-lib` | Upload only library files |
| `make list` | List files on the Pico |
| `make connect` | Connect to the Pico's REPL console |
| `make reset` | Reset the Pico |
| `make refresh` | Reset and connect to REPL |
| `make clean` | Remove all files from the Pico |
| `make wifi_config` | Create wifi_config.txt from example |

## Usage

Once setup is complete:

1. The Pico W will automatically run the dashboard on startup
2. It will connect to WiFi if credentials are available
3. The dashboard will cycle through screens:
   - Welcome screen with controls information
   - Time display showing current time
   - Date display showing current date and weekday
   - System info showing memory usage and display size

4. Use the buttons for different functions:
   - Button A: Move to next screen
   - Button B: Jump to system info screen
   - Button Y: Toggle auto-cycle on/off
   - Button X: Not used (known hardware limitation)

5. LED colors indicate current screen:
   - Purple: Welcome screen
   - Blue: Time display
   - Yellow: Date display
   - Green: System info

## Monitoring and Debugging

```bash
# Connect to REPL for live monitoring
mpremote connect /dev/cu.usbmodem* repl

# Reset the Pico
mpremote connect /dev/cu.usbmodem* reset

# List files on the device
mpremote connect /dev/cu.usbmodem* ls
```

## Troubleshooting

### Hardware Issues

- **Can't Connect to Port**: Make sure you're using the correct port and the Pico is connected properly
- **Permission Denied**: On Linux/macOS, you may need to use `sudo` or add your user to the appropriate group
- **Connection Error**: Try unplugging and reconnecting the Pico
- **Memory Errors**: MicroPython has limited RAM - reduce code complexity or use frozen modules
- **Button X Not Working**: This is a known hardware limitation on some display units. The code is designed to work without this button.

## License

MIT