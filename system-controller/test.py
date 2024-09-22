import serial
import time
import random  # Simulate sensor data

# Open the serial connection on Pi 2 (Slave)
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.flush()

def read_sensor_data():
    """Simulates sensor data reading (replace this with actual sensor code)"""
    sensor_data = random.uniform(20.0, 30.0)  # Simulated sensor reading (e.g., temperature)
    return sensor_data

def process_command(command):
    """Processes received commands and sends back data"""
    if command == "start_sensors":
        # Simulate a sensor reading or a function triggered by Pi 1
        sensor_value = read_sensor_data()
        print(f"Sensor data: {sensor_value}")
        
        # Send the sensor data back to Pi 1
        response = f"Sensor data: {sensor_value:.2f} °C"
        ser.write(response.encode('utf-8'))
        print(f"Sent: {response}")
    else:
        # Handle unrecognized commands
        ser.write("Unknown command".encode('utf-8'))
        print("Unknown command received")

# Example main loop: Listening for commands
while True:
    if ser.in_waiting > 0:
        # Read the command from Pi 1
        command = ser.readline().decode('utf-8').rstrip()
        print(f"Received command: {command}")
        
        # Process the command (start sensors, etc.)
        process_command(command)
    
    time.sleep(1)  # Adjust this as needed
