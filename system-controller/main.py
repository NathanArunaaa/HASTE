import serial
import time
import random

ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.flush()

def read_sensor_data():
    # Simulate reading sensor data
    sensor_data = random.uniform(20.0, 30.0)
    return sensor_data

def calculate_checksum(command):
    # Calculate a simple checksum (sum of ASCII values)
    return sum(ord(c) for c in command)

def is_valid_command(command):
    # Check if the command format is valid and checksum matches
    if command.startswith("<") and command.endswith(">"):
        main_command = command[1:-1]  # Remove < and >
        *split_command, checksum = main_command.split('*')
        expected_command = split_command[0]  # The command part
        expected_checksum = calculate_checksum(expected_command)
        
        try:
            return expected_command == "start_sensors" and expected_checksum == int(checksum)
        except ValueError:
            return False  # If conversion fails, return False
    return False

def clean_command(command):
    # Filter out unwanted characters
    return ''.join(c for c in command if c.isprintable() or c in {'<', '>', '_', ' '} )

def process_command(command):
    if command == "<start_sensors>":
        sensor_value = read_sensor_data()
        response = f"Sensor data: {sensor_value:.2f} °C"
        ser.write(response.encode('utf-8'))
        print(f"Sent: {response}")
    else:
        ser.write("Unknown command\n".encode('utf-8'))
        print(f"Received unknown command: {command}")

invalid_command_count = 0
max_invalid_count = 5

while True:
    if ser.in_waiting > 0:
        raw_data = ser.readline()
        print(f"Raw Data: {raw_data}")

        try:
            # Decode the raw data, ignoring decoding errors
            command = raw_data.decode('utf-8', errors='ignore').rstrip()
            # Clean the command from unwanted characters
            cleaned_command = clean_command(command)

            if is_valid_command(cleaned_command):
                print(f"Received valid command: {cleaned_command}")
                process_command(cleaned_command)
                invalid_command_count = 0  # Reset on valid command
            else:
                invalid_command_count += 1
                print(f"Ignoring invalid command: {cleaned_command}")

                if invalid_command_count > max_invalid_count:
                    print("Too many invalid commands, taking action (e.g., resetting).")
                    invalid_command_count = 0  # Reset or take action here

        except UnicodeDecodeError as e:
            print(f"Error decoding command: {e}")
            print(f"Raw data (hex): {raw_data.hex()}")

    time.sleep(1)
