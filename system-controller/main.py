import time
import random
import serial

# Ensure the serial connection is initialized
try:
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    ser.flush()
except serial.SerialException as e:
    print(f"Error initializing serial port: {e}")
    exit(1)

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
        sample_retract()
        response = "retracted sample"
        ser.write(response.encode('utf-8'))  
        print(f"Sent: {response}")
    else:
        response = "Unknown command"
        ser.write(f"{response}\n".encode('utf-8'))
        print(f"Received unknown command: {command}")

while True:
    try:
        if ser.in_waiting > 0:
            raw_data = ser.readline()
            print(f"Raw Data: {raw_data}")

            # First try decoding with UTF-8 and ignore errors
            command = raw_data.decode('utf-8', errors='ignore').rstrip()

            # Clean command to remove non-printable characters
            cleaned_command = clean_command(command)
            print(f"Received cleaned command: {cleaned_command}")

            if cleaned_command:
                process_command(cleaned_command)
            else:
                print("No valid command found after cleaning")

        time.sleep(0.5)  # Adjust this delay to prevent CPU overuse

    except UnicodeDecodeError as e:
        print(f"Error decoding command: {e}")
        print(f"Raw data (hex): {raw_data.hex()}")
    except serial.SerialException as e:
        print(f"Serial communication error: {e}")
        time.sleep(2)  # Wait before retrying
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
