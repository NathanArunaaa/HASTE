import serial
import time

ser = serial.Serial('/dev/serial0', 9600, timeout=1)
ser.flush()

def send_command(command):
    """Sends a command to Pi 2"""
    command_with_newline = command + "\n"  
    ser.write(command_with_newline.encode('utf-8'))  
    print(f"Sent: {command_with_newline.strip()}")


while True:
    command = "start_sensors"  
    send_command(command)
    time.sleep(5) 
