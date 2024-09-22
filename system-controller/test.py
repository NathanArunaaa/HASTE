import serial
import time
import random  # Simulate sensor data

# Open the serial connection on Pi 2 (Slave)
ser = serial.Serial('/dev/serial0', 9600, timeout=1)  # Adjust the port as needed
ser.flush()

def read_sensor_data():
    """Simulates sensor data reading (replace this with actual sensor code)"""
    sensor_data = random.uniform(20.0, 30.0)  # Simulated sensor reading
    return sensor_data

def process_command(command):
    """Processes received commands and sends back data"""
    if command == "start_sensors":
        sensor_value = read_sensor_data()
        response = f"Sensor data: {sensor_value:.2f} °C\n"
        ser.write(response.encode('utf-8'))
        print(f"Sent: {response.strip()}")
    else:
        ser.write("Unknown command\n".encode('utf-8'))
        print("Unknown command received")

while True:
    if ser.in_waiting > 0:
        raw_data = ser.readline()
        print(f"Raw Data: {raw_data}")
        
        try:
            command = raw_data.decode('utf-8').rstrip()
            print(f"Received command: {command}")
            process_command(command)
        except UnicodeDecodeError as e:
            print(f"Error decoding command: {e}")
            print(f"Raw data (hex): {raw_data.hex()}")  # Print hex representation
