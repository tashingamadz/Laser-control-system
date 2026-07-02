import tkinter as tk
import json
import threading

last_status = {}
warning_popup = None
labels = {}
HEADER_BG = "#0b8540"
HEADER_FG = "white"
timed_commands = {"ABKG", "ASEC", "ASEQ"}
seconds = 0

root = tk.Tk()
root.title("Laser Control")
#root.overrideredirect(True)
root.geometry("800x600")

with open("data.json") as file:
    info = json.load(file)
    print(info)

command_errors = info["command_errors"]

nchannels = int(info["nchannel"])
channel_number = {}

for i in range(1, nchannels + 1):
    channel_number[info[f"channel_{i}"]] = i

for error in info["errors"]:
    print(error)

data = [
    ["Logo", info["company"], info["serial_number"]]
]

for i in range(1, nchannels + 1):
    name = info[f"channel_{i}"]

    data.append([
        name,
        info["information"],
        info["error_display"]
    ])
    
logo = tk.PhotoImage(file="logo_resize.png")
status_icon = tk.PhotoImage(file="status_resized_80x80.png")

root.grid_columnconfigure(0, weight=1, minsize=50)
root.grid_columnconfigure(1, weight=3, minsize=150)
root.grid_columnconfigure(2, weight=1, minsize=40)
        
root.grid_rowconfigure(0, weight=1, minsize=50)
        
for r in range(1, len(data)):
    root.grid_rowconfigure(r, weight=3, minsize=80)
    
for r in range(len(data)):
    for c in range(len(data[0])):
        if r == 0:
            frame = tk.Frame(
                root,
                borderwidth=1,
                bg=HEADER_BG,
                relief="solid",
                width=120,
                height=80
            )
        else:
            frame = tk.Frame(
                root,
                borderwidth=1,
                relief="solid"        
            )
        if r == 0 and c == 0:
            label = tk.Label(
                frame,
                bg=HEADER_BG,
                image=logo
            )
            label.image = logo
        
        elif r == 0:
            label = tk.Label(
                frame,
                text=data[r][c],
                bg=HEADER_BG,
                fg=HEADER_FG,
                font=("Arial", 14, "bold")
                )
        else:
                label = tk.Label(
                    frame,
                    text=data[r][c]
                )
            
        if not (r == 0  and c == 0):
            labels[(r, c)] = label
        label.pack(expand=True)
        
        frame.grid(row=r, column=c, sticky="nsew")
        frame.grid_propagate(False)

def update_channel(channel, message,show_icon=False):
    
    row = channel_number[channel]
    
    if show_icon:
        labels[(row,1)].config(
            text=message,
            image=status_icon,
            compound="left"
            )
        labels[(row, 1)].image = status_icon
    else:
            labels[(row, 1)].config(
                text=message,
                image="",
                compound="left"
                )
    labels[(row,0)].config(text=channel)
    labels[(row,1)].config(text=message)

def reset_channel(channel):
    row =  channel_number[channel]
    
    labels[(row, 1)].config(text="Channel in operation",
                            image="")
    labels[(row,1)].image = None
    labels[(row, 2)].config(text=info["error_display"])
    
def terminal_input():
    while True:
        value = input("Enter Prompt:").strip().upper()
        
        if value == "EXIT":
            root.after(0, root.destroy)
            break
        
        parts = value.split()
        
        channel_name = parts[0]
        command = parts[1]
        error_key = parts[2]
        duration = parts[3]
        x_char = parts[4]
        average = parts[5]
        
        seconds = int(duration[:-1])
        average = int(average)
        timer = seconds * average
        
        if command in timed_commands:
            duration = next(p for p in parts if p.endswith("S"))
            seconds = int(duration[:-1])
            
        if error_key not in command_errors.get(command, []):
            print(f"{error_key} not valid for {command}")
            continue
        
        root.after(0, update_status, channel_name, command)
        root.after(0, update_error, channel_name, error_key)
        
        if command in timed_commands:
            root.after(
            timer * 1000,
            lambda ch=channel_name: reset_channel(ch))
        
def update_status(channel, value):
    global last_status 

    if value == "exit":
        root.quit()
        return
    
    if value == "PWON":
        update_error(channel, "Laser On")
        update_channel(channel, "Laser On",True)
    elif value == "ABKG":
        update_error(channel, "Acquire Backgorund")
        update_channel(channel, "Acquire Background", False)
    elif value == "CNAC":
        update_error(channel, "Continous Acquisition")
        update_channel(channel, "Contionous Acquistion", False)
    elif value == "ASEQ":
        update_error(channel, "Sequence Acquisition")
        update_channel(channel, "Sequence Acquistion",True)
    elif value == "PWOF":
        update_error(channel, "Laser Off")
        update_channel(channel, "Laser Off", False)
    else:
        update_error(channel, "Acquire Spectrum")
        update_channel(channel, "Acquire Spectrum", True)

def update_error(channel,message):
    row = channel_number[channel]
    error_message = info["errors"].get(message, "Unkwown Error")
    labels[(row, 2)].config(text=error_message)

threading.Thread(
    target=terminal_input
).start()

root.mainloop()