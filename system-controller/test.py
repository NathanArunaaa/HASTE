import serial
import time

# Open the serial connection on Pi 1 (Master)
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.flush()

def send_command(command):
    """Sends a command to Pi 2"""
    command_with_newline = command + "\n"  # Ensure there's a newline character
    ser.write(command_with_newline.encode('utf-8'))  # Properly encode to UTF-8
    print(f"Sent: {command_with_newline.strip()}")

# Main loop to send a command
while True:
    command = "start_sensors"  # Command to send
    send_command(command)
    time.sleep(5)  # Wait before sending the next command
