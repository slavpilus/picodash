"""
PicoDash - Boot file for Raspberry Pi Pico W
This file runs automatically on startup before main.py
"""

import machine
import time
import gc

# Free up as much memory as possible
gc.collect()

# Print startup info
print("PicoDash - Booting up...")
print(f"MicroPython version: {gc.mem_free()} bytes free")

# Set CPU frequency - standard is 125MHz
machine.freq(125_000_000)
print(f"CPU Frequency: {machine.freq() / 1_000_000}MHz")

# Wait a moment
time.sleep(0.5)

# Boot info
print("Ready to run main.py")