import socket
import RPi.GPIO as GPIO
from functions import sample_extend, sample_retract

# GPIO setup
GPIO.setmode(GPIO.BCM)
# Example: GPIO.setup(pin_number, GPIO.OUT)

# Create server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5000))  # Listen on all interfaces
server_socket.listen(1)

print("Waiting for a connection...")

try:
    connection, address = server_socket.accept()
    print(f"Connected to {address}")

    while True:
        data = connection.recv(1024)  # Receive data from the client
        if not data:  # If no data, exit the loop
            print("No data received, closing connection.")
            break
        
        command = data.decode('utf-8').strip()  # Decode and strip whitespace from the received data
        print(f"Received command: {command}")

        # Process the received command
        if command == "EXTEND_SAMPLE":
            sample_extend()  # Call the sample extending function
        elif command == "RETRACT_SAMPLE":
            sample_retract()
        else:
            print(f"Unknown command: {command}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    connection.close()  # Close the connection
    GPIO.cleanup()  # Clean up GPIO settings
