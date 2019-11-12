import tkinter as tk
import os
from tkinter import messagebox as tkMessageBox
from tkcalendar import Calendar, DateEntry
import datetime
import getpass
import time

import win32api
import win32gui
import psutil
import win32process
import json

current_year = datetime.datetime.now()
username = getpass.getuser()

class Timer:
    def __init__(self, parent):

        self.active_window = "Chrome.exe"
        self.active_window_time = "0:45:30"

        # On/Off button for tracking + label & settings button
        self.button = tk.Button(root, text="On/Off", command=self.state).place(relx=0.05, rely=0.025, relwidth=0.2)
        self.tracking_state_label = tk.Label(root, text="Tracking is: ").place(relx=0.3, rely=0.03)
        self.tracking_state = tk.Label(root, text="placeholder", bg="red").place(relx=0.5, rely=0.03)
        self.settings = tk.Button(root, text="Settings", command=settings_window).place(relx=0.8, rely=0.025)
        #self.settings = tk.Button(root, text="Settings").place(relx=0.8, rely=0.025)
        
        # active window display
        self.active_window_label = tk.Label(root, text="Active window:").place(relx=0.05, rely=0.1)
        self.active_window = tk.Label(root, text=self.active_window, bg="red").place(relx=0.28, rely=0.1)
        self.active_window_time = tk.Label(root, text=self.active_window_time, bg="red").place(relx=0.8, rely=0.1)

        # export to excel button
        self.export_button = tk.Button(root, text="Export to Excel").place(relx=0.75, rely=0.15)

        # calendar widget
        self.frame = tk.Frame(root).place(relx=0.025, rely=0.15, height=30, width=200)
        self.choose_date_label = tk.Label(self.frame, text="Choose Date").place(x=18, y=125)
        self.cal = DateEntry(self.frame, width=12, background='darkblue', foreground='white', borderwidth=2, year=current_year.year).place(x=110, y=125)

        # variable storing time
        self.seconds = 0
        # label displaying time
        self.label = tk.Label(parent, text="0 s", font="Arial 30", width=10)
        self.label.place(relx=0.2, rely=0.85)
        # start the timer
        self.label.after(1000, self.refresh_label)

    def refresh_label(self):
        #refresh the content of the label every second
        # increment the time
        if self.loop_state == 0:
            self.seconds += 1
            # activate track class/method
            Active_tracker.main_loop_counter(self)            

        # display the new time
        self.label.configure(text="%i s" % self.seconds)
        # request tkinter to call self.refresh after 1s (the delay is given in ms)
        self.label.after(1000, self.refresh_label)



    loop_state = 0 # 1 on/off 0
    def state(self):
        # variable storing the on/off state
        global loop_state
        # switcher
        if self.loop_state == 0:
            self.loop_state = 1
        elif self.loop_state == 1:
            self.loop_state = 0
        print(self.loop_state)



def settings_window():
    top = tk.Toplevel()
    top.resizable(0,0)
    top.geometry("300x300+850+250") #WidthxHeight and x+y
    tk.Label(top, text="Currently tracking user: ").place(relx=0.1)
    tk.Label(top, text=username).place(relx=0.7)
    tk.Checkbutton(top, text="Show activity icon in tray bar.").place(relx=0.1, rely=0.15)  # REMEMBER TO INCLUDE THE VARIABLE WHEN ADDING FUNCTIONALITY
    tk.Button(top, text="About", command=about_app).place(relx=0.4, rely=0.9)

def about_app():
    about_top = tk.Toplevel()
    about_top.resizable(0,0)
    about_top.geometry("200x200+900+300") #WidthxHeight and x+y
    tk.Label(about_top, text="Insert about info in here in the future.").pack()

class Active_tracker:
    def main_loop_counter(self):
            print("tracking")
    

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    root.title("Time Tracker")
    root.geometry("420x800+800+150") #WidthxHeight and x+y of main window
    timer = Timer(root)
    root.mainloop()
