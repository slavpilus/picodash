# Makefile for PicoDash MicroPython project

# Serial port - adjust this based on your OS
# Linux example: /dev/ttyACM0
# macOS example: /dev/cu.usbmodem2101
# Windows example: COM4
PORT ?= /dev/cu.usbmodem2101

# Tools
RSHELL = rshell
AMPY = ampy
MPREMOTE = mpremote

# Target directories
DEVICE_DIR = /pyboard
LIB_DIR = lib
EMULATION_DIR = emulation

# Files to upload
MAIN_FILES = main.py boot.py wifi_config.txt workspaces.yaml
LIB_FILES = $(wildcard $(LIB_DIR)/*.py)

.PHONY: help install-tools setup-venv upload list connect reset refresh clean emulate emulate-build emulate-stop wifi_config workspace_config

help:
	@echo "PicoDash MicroPython Project"
	@echo ""
	@echo "Usage:"
	@echo "  make setup-venv       Create and setup Python virtual environment"
	@echo "  make install-tools    Install required Python tools"
	@echo "  make upload           Upload all project files to the Pico"
	@echo "  make upload-main      Upload only main files (not lib)"
	@echo "  make upload-lib       Upload only library files"
	@echo "  make list             List files on the Pico"
	@echo "  make connect          Connect to the Pico REPL"
	@echo "  make reset            Reset the Pico"
	@echo "  make refresh          Reset and connect to REPL"
	@echo "  make clean            Remove all files from Pico (except firmware)"
	@echo ""
	@echo "Configuration:"
	@echo "  make wifi_config      Create wifi_config.txt from example"
	@echo "  make workspace_config Create workspaces.yaml from example"
	@echo ""
	@echo "Emulation:"
	@echo "  make emulate          Run the project in QEMU emulation"
	@echo "  make emulate-build    Build the emulation Docker image"
	@echo "  make emulate-stop     Stop the emulation container"
	@echo ""
	@echo "Environment:"
	@echo "  PORT                  Set the serial port (default: $(PORT))"
	@echo "  Example: make upload PORT=/dev/ttyACM0"

setup-venv:
	@echo "Creating Python virtual environment..."
	python3 -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "source venv/bin/activate  # On macOS/Linux"
	@echo "venv\\Scripts\\activate     # On Windows"

install-tools:
	@echo "Installing required Python tools..."
	pip install -r requirements.txt

upload: upload-main upload-lib

upload-main:
	@echo "Uploading main files to Pico..."
	for file in $(MAIN_FILES); do \
		$(AMPY) --port $(PORT) put $$file; \
	done
	@echo "Main files uploaded successfully."

upload-lib:
	@echo "Uploading library files to Pico..."
	./upload_lib.py $(PORT)
	@echo "Library files uploaded successfully."

list:
	@echo "Files on Pico:"
	$(AMPY) --port $(PORT) ls

connect:
	@echo "Connecting to Pico REPL..."
	$(MPREMOTE) connect $(PORT) repl

reset:
	@echo "Resetting Pico..."
	$(MPREMOTE) connect $(PORT) reset

refresh: reset connect

clean:
	@echo "Removing all files from Pico..."
	$(RSHELL) -p $(PORT) "rm -rf $(DEVICE_DIR)/*"
	@echo "Files removed successfully."

# Special target - create wifi_config from example if it doesn't exist
wifi_config:
	@if [ ! -f wifi_config.txt ]; then \
		cp wifi_config.txt.example wifi_config.txt; \
		echo "Created wifi_config.txt from example. Please edit with your WiFi credentials."; \
	else \
		echo "wifi_config.txt already exists."; \
	fi

# Create workspace config from example if it doesn't exist
workspace_config:
	@if [ ! -f workspaces.yaml ]; then \
		cp workspaces.yaml.example workspaces.yaml; \
		echo "Created workspaces.yaml from example. Please edit with your workspace configuration."; \
	else \
		echo "workspaces.yaml already exists."; \
	fi

# Emulation targets
emulate-build:
	@echo "Building QEMU emulation environment..."
	cd $(EMULATION_DIR) && docker-compose build

emulate: wifi_config workspace_config
	@echo "Starting PicoDash in QEMU emulation..."
	cd $(EMULATION_DIR) && docker-compose up

emulate-stop:
	@echo "Stopping PicoDash emulation..."
	cd $(EMULATION_DIR) && docker-compose down