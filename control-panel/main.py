import tkinter as tk
import numpy as np
import pygame
import io

pygame.mixer.init()

def generate_buzzer_sound(frequency=1000, duration=0.2, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 32767 * 0.5 * (np.sin(2 * np.pi * frequency * t))
    wave = wave.astype(np.int16)
    return wave

def play_buzzer():
    wave = generate_buzzer_sound()
    sound = pygame.mixer.Sound(buffer=wave)
    sound.play()

def start_machine():
    status_label.config(text="Machine Status: Running", fg="green")
    play_buzzer()

def stop_machine():
    status_label.config(text="Machine Status: Stopped", fg="red")
    play_buzzer()

def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)

def enter_fullscreen(event=None):
    root.attributes("-fullscreen", True)


root = tk.Tk()
root.title("Machine Control Panel")
root.attributes("-fullscreen", True)  
root.configure(bg="black")
root.config(cursor="none") 

title_label = tk.Label(root, text="Machine Control Panel", font=("Arial", 24), bg="black", fg="white")
title_label.pack(pady=20)

start_button = tk.Button(root, text="Start Machine", font=("Arial", 18), command=start_machine, bg="green", fg="white")
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Machine", font=("Arial", 18), command=stop_machine, bg="red", fg="white")
stop_button.pack(pady=10)

status_label = tk.Label(root, text="Machine Status: Stopped", font=("Arial", 18), bg="black", fg="red")
status_label.pack(pady=20)

exit_button = tk.Button(root, text="Exit Fullscreen", font=("Arial", 18), command=exit_fullscreen, bg="grey", fg="white")
exit_button.pack(pady=10)

root.bind("<Escape>", exit_fullscreen)
root.bind("<F11>", enter_fullscreen)

root.mainloop()
