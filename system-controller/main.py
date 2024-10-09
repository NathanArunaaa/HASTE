import serial
import time
import random

ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.flush()

from functions import (
    sample_extend,
    sample_retract
)


def process_command(command):
    if command == "EXTEND_SAMPLE":
        sample_extend()
        response = "extended sample"
        ser.write(response.encode('utf-8'))  
        print(f"Sent: {response}")
    if command == "RETRACT_SAMPLE":
        sample_extend()
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
            command = raw_data.decode('utf-8', errors='ignore').rstrip()  
            print(f"Received command: {command}")
            process_command(command)
        except UnicodeDecodeError as e:
            print(f"Error decoding command: {e}")
            print(f"Raw data (hex): {raw_data.hex()}")

    
