import socket
import RPi.GPIO as GPIO
import time

from functions import (
    sample_extend,
    sample_retract
)

# GPIO setup (replace with your actual GPIO pin numbers and setup)
GPIO.setmode(GPIO.BCM)  # or GPIO.BOARD
# Example: GPIO.setup(pin_number, GPIO.OUT)

# Create server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5000))  # Bind to all interfaces on port 5000
server_socket.listen(1)

print("Waiting for a connection...")
connection, address = server_socket.accept()
print(f"Connected to {address}")

try:
    while True:
        data = connection.recv(1024)  # Receive data from the client
        if not data:  # If no data, exit the loop
            break
        command = data.decode('utf-8')  # Decode the received data
        print(f"Received command: {command}")

        # Process the received command
        if command == "load_sample":  # Match the command from the sender
            sample_extend()  # Call the sample extending function
        elif command == "retract_sample":  # Handle sample retraction
            sample_retract()
        else:
            print(f"Unknown command: {command}")

finally:
    connection.close()  # Close the connection
    GPIO.cleanup()  # Clean up GPIO settings
