import socket
import RPi.GPIO as GPIO
import time

from functions import (
    sample_extend,
    sample_retract
)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5000))  # Use port 5000
server_socket.listen(1)      

print("Waiting for a connection...")
connection, address = server_socket.accept()
print(f"Connected to {address}")

try:
    while True:
        data = connection.recv(1024)
        if not data:
            break
        command = data.decode('utf-8')
        print(f"Received command: {command}")

        if command == "EXTEND_SAMPLE":
            sample_extend()
        elif command == "RETRACT_SAMPLE":
            sample_retract()

finally:
    connection.close()
    GPIO.cleanup()