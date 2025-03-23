#!/usr/bin/env python3
"""
Helper script to upload library files to Raspberry Pi Pico W.
This is an alternative to the make upload-lib command.
"""

import os
import sys
import glob
import subprocess
import time

PORT = sys.argv[1] if len(sys.argv) > 1 else "/dev/cu.usbmodem2101"
LIB_DIR = "lib"
LIB_FILES = glob.glob(os.path.join(LIB_DIR, "*.py"))

def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Command failed with return code {result.returncode}")
        print(f"Error: {result.stderr}")
        # Continue anyway
    return result.returncode == 0

# First create the lib directory using mpremote
print("Creating lib directory on Pico...")
run_command(["mpremote", "connect", PORT, "mkdir", "lib"])
time.sleep(1)  # Add a small delay

# Now upload each library file
print(f"Found {len(LIB_FILES)} library files to upload")
for lib_file in LIB_FILES:
    filename = os.path.basename(lib_file)
    print(f"Uploading {lib_file} to lib/{filename}...")
    
    # Try mpremote first
    success = run_command(["mpremote", "connect", PORT, "cp", lib_file, f":lib/{filename}"])
    
    if not success:
        # Fall back to ampy if mpremote fails
        print("Retrying with ampy...")
        run_command(["ampy", "--port", PORT, "put", lib_file, f"lib/{filename}"])
    
    time.sleep(0.5)  # Add a small delay between uploads

print("Library files upload completed!")
