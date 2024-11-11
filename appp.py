import threading
import sys
import cv2
import imutils
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# Initialize global variables
cap = None
alarm = False
alarm_mode = False
alarm_counter = 0
running = False
start_frame = None

# Function to initialize the camera
def init_camera():
    global cap, start_frame
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    _, start_frame = cap.read()
    start_frame = imutils.resize(start_frame, width=500)
    start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)
    start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

# Beep alarm when motion is detected (cross-platform support)
def beep_alarm():
    global alarm
    for _ in range(5):
        if not alarm_mode:
            break
        if sys.platform == "win32":
            import winsound
            winsound.Beep(2500, 1000)
        else:
            print("Beep! (motion detected)")  # Alternative action
    alarm = False

# Start detection
def start_detection():
    global running, alarm_mode, status_label
    if not running:
        running = True
        alarm_mode = True
        status_label.config(text="Detection Running...", fg="green")
        start_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        init_camera()
        update_frame()

# Stop detection
def stop_detection():
    global running, alarm_mode, status_label
    running = False
    alarm_mode = False
    if cap:
        cap.release()
    canvas.delete("all")
    status_label.config(text="Camera Stopped", fg="red")
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# Update the camera frame in the Tkinter canvas
def update_frame():
    global start_frame, alarm, alarm_counter, running
    if running and cap.isOpened():
        _, frame = cap.read()
        frame = imutils.resize(frame, width=500)

        if alarm_mode:
            frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_bw = cv2.GaussianBlur(frame_bw, (5, 5), 0)
            difference = cv2.absdiff(frame_bw, start_frame)
            threshold = cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
            start_frame = frame_bw

            if threshold.sum() > 300:
                alarm_counter += 1
            else:
                if alarm_counter > 0:
                    alarm_counter -= 1

            display_image = Image.fromarray(threshold)
        else:
            display_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        if alarm_counter > 20 and not alarm:
            alarm = True
            threading.Thread(target=beep_alarm).start()

        img_tk = ImageTk.PhotoImage(display_image)
        canvas.create_image(0, 0, anchor="nw", image=img_tk)
        canvas.image = img_tk

        root.after(30, update_frame)
    else:
        canvas.delete("all")

# Exit the application
def exit_application():
    global running
    if running:
        stop_detection()  # Stop detection if running
    root.quit()  # Close the window

# Set up the GUI
root = tk.Tk()
root.title("Motion Detection Application")
root.geometry("600x500")

# Create canvas to display video feed
canvas = tk.Canvas(root, width=500, height=400)
canvas.pack()

# Start and Stop buttons
start_button = tk.Button(root, text="Start", command=start_detection)
start_button.pack(side=tk.LEFT, padx=10, pady=10)

stop_button = tk.Button(root, text="Stop", command=stop_detection, state=tk.DISABLED)
stop_button.pack(side=tk.RIGHT, padx=10, pady=10)

# Exit button
exit_button = tk.Button(root, text="Exit", command=exit_application)
exit_button.pack(side=tk.BOTTOM, padx=10, pady=10)

# Status label for feedback
status_label = tk.Label(root, text="Camera Stopped", fg="red")
status_label.pack(pady=10)

# Close window gracefully
root.protocol("WM_DELETE_WINDOW", exit_application)

# Run the Tkinter main loop
root.mainloop()
