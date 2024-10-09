import serial
import time
import random

ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.flush()

from functions import (
    sample_extend,
    sample_retract
)

# Function to filter out non-printable characters
def clean_command(raw_command):
    return ''.join(c for c in raw_command if c.isprintable())

def process_command(command):
    if command == "EXTEND_SAMPLE":
        sample_extend()
        response = "extended sample"
        ser.write(response.encode('utf-8'))  
        print(f"Sent: {response}")
    elif command == "RETRACT_SAMPLE":
        sample_retract()  # Assuming this should be sample_retract, not sample_extend
        response = "retracted sample"
        ser.write(response.encode('utf-8'))  
        print(f"Sent: {response}")
    else:
        ser.write("Unknown command\n".encode('utf-8'))
        print(f"Received unknown command: {command}")

while True:
    if ser.in_waiting > 0:
        raw_data = ser.readline()
        print(f"Raw Data: {raw_data}")

        try:
            # First try decoding with UTF-8 and ignore errors
            command = raw_data.decode('utf-8', errors='ignore').rstrip()

            # Clean command to remove non-printable characters
            cleaned_command = clean_command(command)
            print(f"Received cleaned command: {cleaned_command}")

            if cleaned_command:
                process_command(cleaned_command)
            else:
                print("No valid command found after cleaning")

        except UnicodeDecodeError as e:
            print(f"Error decoding command: {e}")
            print(f"Raw data (hex): {raw_data.hex()}")
        
        # Small delay to prevent CPU hogging
        time.sleep(1)
