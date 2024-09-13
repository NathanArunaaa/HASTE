import tkinter as tk

def start_machine():
    status_label.config(text="Machine Status: Running", fg="green")

def stop_machine():
    status_label.config(text="Machine Status: Stopped", fg="red")

root = tk.Tk()
root.title("Machine Control Panel")
root.attributes("-fullscreen", True)  
root.configure(bg="black")

title_label = tk.Label(root, text="Machine Control Panel", font=("Arial", 24), bg="black", fg="white")
title_label.pack(pady=20)

start_button = tk.Button(root, text="Start Machine", font=("Arial", 18), command=start_machine, bg="green", fg="white")
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Machine", font=("Arial", 18), command=stop_machine, bg="red", fg="white")
stop_button.pack(pady=10)

status_label = tk.Label(root, text="Machine Status: Stopped", font=("Arial", 18), bg="black", fg="red")
status_label.pack(pady=20)



root.mainloop()
