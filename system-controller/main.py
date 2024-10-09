import time
import threading
import serial
from functions import (
    sample_extend,
    sample_retract
)

def initialize_serial_connection():
    try:
        ser = serial.Serial('/dev/serial0', 9600, timeout=1)
        ser.flush()
        print("Serial port opened successfully.")
        return ser
    except serial.SerialException as e:
        print(f"Error initializing serial port: {e}")
        exit(1)

def clean_command(raw_command):
    return ''.join(c for c in raw_command if c.isprintable())

def process_command(ser, command):
    # Define the commands
    command_map = {
        "lrp": sample_extend,  # Assuming lrp means "extend sample"
        "sllp": sample_retract  # Assuming sllp means "retract sample"
    }

    # Execute command if it exists in the command map
    if command in command_map:
        command_map[command]()  # Call the associated function
        response = f"Executed: {command}"
    else:
        response = "Unknown command"
    
    # Send response back over serial
    ser.write(f"{response}\n".encode('utf-8'))
    print(f"Sent: {response}")

def listen_for_commands(ser):
    while True:
        try:
            if ser.in_waiting > 0:
                raw_data = ser.readline()
                print(f"Raw Data: {raw_data}")

                command = raw_data.decode('utf-8', errors='ignore').rstrip()
                cleaned_command = clean_command(command)
                print(f"Received cleaned command: {cleaned_command}")

                if cleaned_command:
                    process_command(ser, cleaned_command)
                else:
                    print("No valid command found after cleaning")

            time.sleep(0.5)

        except UnicodeDecodeError as e:
            print(f"Error decoding command: {e}")
            print(f"Raw data (hex): {raw_data.hex()}")
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            time.sleep(2)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main():
    ser = initialize_serial_connection()

    listener_thread = threading.Thread(target=listen_for_commands, args=(ser,), daemon=True)
    listener_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program.")
        ser.close()
        exit(0)

if __name__ == "__main__":
    main()
