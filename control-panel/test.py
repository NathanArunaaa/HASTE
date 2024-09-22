import serial
import time
import random

# Open the serial connection on Pi 2 (Slave)
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.flush()

def read_sensor_data():
    """Simulates sensor data reading (replace with actual sensor code)"""
    sensor_data = random.uniform(20.0, 30.0)  # Simulated sensor reading
    return sensor_data

def process_command(command):
    """Processes received commands and sends back data"""
    if command == "start_sensors":
        sensor_value = read_sensor_data()
        response = f"Sensor data: {sensor_value:.2f} °C"
        ser.write(response.encode('utf-8'))  # Send the response
        print(f"Sent: {response}")
    else:
        ser.write("Unknown command\n".encode('utf-8'))  # Send unknown command response

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
            print(f"Raw data (hex): {raw_data.hex()}")
    
    time.sleep(1)
