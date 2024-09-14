
import os
import socket
import customtkinter

def open_input_dialog_event():
    dialog = customtkinter.CTkInputDialog(text="Type in a number:", title="CTkInputDialog")
    print("CTkInputDialog:", dialog.get_input())

def change_appearance_mode_event(new_appearance_mode: str):
    customtkinter.set_appearance_mode(new_appearance_mode)

def change_scaling_event(new_scaling: str):
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(new_scaling_float)

def sidebar_button_event():
    print("sidebar_button click")

def sys_shutdown():
    os.system('sudo shutdown -h now')

def sys_restart():
    os.system('sudo reboot')

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))  
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip
