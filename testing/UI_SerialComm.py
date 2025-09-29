import tkinter as tk
import serial
import serial.tools.list_ports

# Set Up
BAUD = 9600 # MUST BE SAME AS ARDUINO
PORT = "COM5" # WILL CHANGE BASED ON ARDUINO
ser = serial.Serial(PORT, BAUD, timeout=1)

string_f = "F0\n"
string_r = "R0\n"

def press_f(event): 
    string_f = "F1\n"
    ser.write(string_f.encode())
    print("Sent: ", string_f.strip())
def relese_f(event):
    string_f = "F0\n"
    ser.write(string_f.encode())
    print("Sent: ", string_f.strip())    
def press_r(event):
    string_r = "R1\n"
    ser.write(string_r.encode())
    print("Sent: ", string_r.strip()) 
def release_r(event):
    string_r = "R0\n"
    ser.write(string_r.encode())
    print("Sent: ", string_r.strip()) 


# UI

root = tk.Tk()
root.title("UI")

info = tk.Label(root, text="Hold a button to send a command to the arduino")
info.pack(pady=20)

#Foward Button
btnF = tk.Button(root, text="Forward")
btnF.pack(pady=20)
btnF.bind("<ButtonPress-1>", press_f)
btnF.bind("<ButtonRelease-1>", relese_f)

btnR = tk.Button(root, text="Reverse")
btnR.pack(pady=20)
btnR.bind("<ButtonPress-1>", press_r)
btnR.bind("<ButtonRelease-1>", release_r)


def on_close():
    if ser.is_open:
        ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()





