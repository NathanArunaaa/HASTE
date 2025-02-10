import os
import socket
import customtkinter
import numpy as np


def change_scaling_event(new_scaling: str):
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(new_scaling_float)


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
        ip = '192.168.1.100:5000'
    finally:
        s.close()
    return ip

