
import os
import socket
import customtkinter
import pygame
import numpy as np

def play_buzzer_sound(frequency=440, duration=0.1, sample_rate=44100):
    """Generate a buzzer sound wave."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 32767 * 0.5 * (np.sin(2 * np.pi * frequency * t))
    wave = wave.astype(np.int16)
    return wave

def play_buzzer():
    """Play a buzzer sound."""
    wave = play_buzzer_sound()
    
    sound = pygame.mixer.Sound(buffer=wave)
    sound.play()
    
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


def testing():
    play_buzzer_sound()
    print('test')


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
