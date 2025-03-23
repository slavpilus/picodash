# PicoDash - Raspberry Pi Pico W Dashboard

A minimalistic dashboard application for the Raspberry Pi Pico W with Pimoroni Display Pack, written in MicroPython.

## Hardware Requirements

- Raspberry Pi Pico W
- Pimoroni Pico Display Pack (240x135 pixel IPS LCD)

## Setup Instructions (Command Line)

### 1. Flash MicroPython to your Pico W

First, you need to install MicroPython on your Pico W:

1. Download the latest Pimoroni MicroPython firmware for Pico W from: https://github.com/pimoroni/pimoroni-pico/releases (I tested this with version [v1.24.0-beta2](https://github.com/pimoroni/pimoroni-pico/releases/tag/v1.24.0-beta2))
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

make upload PORT=/dev/cu.usbmodem2101
make upload-main PORT=/dev/cu.usbmodem2101
make upload-lib PORT=/dev/cu.usbmodem2101
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
3. The dashboard will display notification counts
4. Use the buttons for different functions:
   - Button A: Refresh data
   - Button B: Toggle WiFi
   - Button X: Show system info
   - Button Y: Return to dashboard

## Monitoring and Debugging

```bash
# Connect to REPL for live monitoring
make connect PORT=/dev/cu.usbmodem2101

# Reset the Pico
make reset PORT=/dev/cu.usbmodem2101

# List files on the device
make list PORT=/dev/cu.usbmodem2101
```

## Project Structure

- `main.py` - Main application code
- `boot.py` - Startup configuration
- `lib/` - Libraries for the project:
  - `picographics.py` - Display graphics library
  - `pimoroni_i2c.py` - I2C communication
  - `pimoroni.py` - RGB LED and button handling
- `Makefile` - Build and deployment tools
- `requirements.txt` - Required Python packages for development
- `wifi_config.txt.example` - Template for WiFi configuration

## Development

The project is organized into phases:

- **Phase 1**: Basic display rendering ✅
- **Phase 2**: WiFi connectivity ✅
- **Phase 3**: Data integration from real API ⏳
- **Phase 4**: Power management and optimization ⏳
- **Phase 5**: User interface refinement ⏳

## Advanced Development

### Running Scripts Directly

You can run Python scripts directly on the Pico without permanently uploading them:

```bash
mpremote connect /dev/cu.usbmodem2101 run your_script.py
```

### Executing Commands

Execute single commands on the Pico:

```bash
mpremote connect /dev/cu.usbmodem2101 exec "import machine; machine.reset()"
```

### File System Operations

Work with the Pico's filesystem directly:

```bash
# Copy a file to the Pico
ampy --port /dev/cu.usbmodem2101 put local_file.py remote_file.py

# Read a file from the Pico
ampy --port /dev/cu.usbmodem2101 get remote_file.py

# Delete a file
ampy --port /dev/cu.usbmodem2101 rm remote_file.py
```

## Troubleshooting

### Hardware Issues

- **Can't Connect to Port**: Make sure you're using the correct port and the Pico is connected properly
- **Permission Denied**: On Linux/macOS, you may need to use `sudo` or add your user to the appropriate group
- **Connection Error**: Try unplugging and reconnecting the Pico
- **Memory Errors**: MicroPython has limited RAM - reduce code complexity or use frozen modules
- **Build Tools Not Found**: Make sure the tools are in your PATH after installation

## License

MIT