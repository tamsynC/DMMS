import tkinter as tk

root = tk.Tk()
root.title("UI")

# Track whether each button is being held
forward_holding = False
backward_holding = False

def start_forward(event=None):
    global forward_holding
    forward_holding = True
    repeat_forward()

def stop_forward(event=None):
    global forward_holding
    forward_holding = False

def repeat_forward():
    if forward_holding:
        print("Forward")
        root.after(100, repeat_forward)  # repeat every 100 ms

def start_backward(event=None):
    global backward_holding
    backward_holding = True
    repeat_backward()

def stop_backward(event=None):
    global backward_holding
    backward_holding = False

def repeat_backward():
    if backward_holding:
        print("Backward")
        root.after(100, repeat_backward)

# Forward button
forward_btn = tk.Button(root, text="Forward")
forward_btn.pack(pady=20)
forward_btn.bind("<ButtonPress-1>", start_forward)
forward_btn.bind("<ButtonRelease-1>", stop_forward)

# Backward button
backward_btn = tk.Button(root, text="Backward")
backward_btn.pack(pady=20)
backward_btn.bind("<ButtonPress-1>", start_backward)
backward_btn.bind("<ButtonRelease-1>", stop_backward)

# Run the Tkinter event loop
root.mainloop()

