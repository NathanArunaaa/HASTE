import serial
import time

# Open the serial connection on Pi 1 (Master)
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.flush()

def send_command(command):
    """Sends a command to Pi 2"""
    command_with_newline = command + "\n"  # Add newline character
    ser.write(command_with_newline.encode('utf-8'))  # Send the command
    print(f"Sent: {command_with_newline.strip()}")

def receive_response():
    """Receives a response from Pi 2"""
    if ser.in_waiting > 0:  # Check if there's data available
        response = ser.readline().decode('utf-8', errors='ignore').rstrip()
        print(f"Received from Pi 2: {response}")
        return response
    return None

# Example main loop: Sending commands periodically
while True:
    command = "start_sensors"  # Example command
    send_command(command)
    
    # Wait for Pi 2 to respond (e.g., sensor data)
    time.sleep(1)  # Small delay to allow Pi 2 to process the command
    
    response = receive_response()
    
    # Repeat every 5 seconds (you can adjust this)
    time.sleep(5)
