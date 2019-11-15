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

classname = str()
dictionary = {"Idle": 0}
idle_time_max = 300.0 # 5 minutes max idle time
idle_state = "below 0" # 0 - below idle_time_max, 1 - above idle_time_max once, 2 - increment by seconds
export_iterator = 0
export_iterator_max = 20 # save automatically every 20(Default) seconds/cycles
filename = datetime.datetime.now()
autosave = ""

def load_settings():
    global export_iterator_max
    file = open("config.txt", "r")
    contents = file.readlines()
    file.close

    for line in contents:
        if "autosave" in line:
            x = line.split(sep="=")
            export_iterator_max = int(x[1])

def save_settings():
    global export_iterator_max
    file = open("config.txt", "w")
    file.write("autosave=" + str(export_iterator_max))
    file.close



class Timer:
    def __init__(self, parent):
        # On/Off button for tracking + label & settings button
        self.button = tk.Button(root, text="On/Off", command=self.state).place(relx=0.05, rely=0.025, relwidth=0.2)
        self.tracking_state_label = tk.Label(root, text="Tracking is: ").place(relx=0.3, rely=0.03)
        self.settings = tk.Button(root, text="Settings", command=settings_window).place(relx=0.8, rely=0.025)
        
        # active window display
        self.active_window_label = tk.Label(root, text="Active window:").place(relx=0.05, rely=0.1)
        
        # export to excel button
        self.export_button = tk.Button(root, text="Export to Excel").place(relx=0.75, rely=0.15)

        # calendar widget
        self.frame = tk.Frame(root).place(relx=0.025, rely=0.15, height=30, width=200)
        self.choose_date_label = tk.Label(self.frame, text="Choose Date").place(x=18, y=125)
        self.cal = DateEntry(self.frame, width=12, background='darkblue', foreground='white', borderwidth=2, year=current_year.year).place(x=110, y=125)


        # stats text display
        #self.text_frame_main = tk.Frame(root, bg="red").place(relx=0.025,rely=0.28,relheight=0.55,relwidth=0.95)
        self.header = tk.Label(root, text="Window").place(relx=0.025, rely=0.25, height=30, relwidth=0.5)
        self.header = tk.Label(root, text="Time").place(relx=0.525, rely=0.25, height=30, relwidth=0.45)
        
        
        

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



    loop_state = 1 # 0 on/off 1
    def state(self):
        # variable storing the on/off state
        global loop_state
        try:
            self.tracking_state.after(1, self.tracking_state.destroy)
        except:
            pass
        # switcher
        if self.loop_state == 0:
            self.loop_state = 1
            self.tracking_state = tk.Label(root, text="Off") 

        elif self.loop_state == 1:
            self.loop_state = 0
            self.tracking_state = tk.Label(root, text="Active")

        self.tracking_state.place(relx=0.5, rely=0.03)
        
        #print(self.loop_state)



def settings_window():
    global export_iterator_max
    global autosave
    top = tk.Toplevel()
    top.resizable(0,0)
    top.title("Settings")
    top.geometry("300x300+850+250") #WidthxHeight and x+y
    tk.Label(top, text="Currently tracking user: ").place(relx=0.1)
    tk.Label(top, text=username).place(relx=0.7)
    tk.Checkbutton(top, text="Show activity icon in tray bar.").place(relx=0.1, rely=0.15)  # REMEMBER TO INCLUDE THE VARIABLE WHEN ADDING FUNCTIONALITY
    tk.Label(top, text="Autosave (sec): ").place(relx=0.1, rely=0.25)

    autosave = tk.StringVar()
    autos = tk.Entry(top, width=3, textvariable=autosave).place(relx=0.5, rely=0.25)
    autosave.set(export_iterator_max)
    tk.Button(top, text="Set", command=autosave_set).place(relx=0.75, rely=0.25)

    tk.Button(top, text="About", command=about_app).place(relx=0.4, rely=0.9)


def autosave_set():
    global export_iterator_max
    export_iterator_max = int(autosave.get())
    save_settings()

def about_app():
    about_top = tk.Toplevel()
    about_top.resizable(0,0)
    about_top.geometry("200x200+900+300") #WidthxHeight and x+y
    tk.Label(about_top, text="Insert about info in here in the future.").pack()


class Active_tracker:
    def main_loop_counter(self):
        global classname
        global export_iterator

        self.w=win32gui                                # detect window every second
        self.w.GetWindowText (self.w.GetForegroundWindow()) # get active window code
        self.pid = win32process.GetWindowThreadProcessId(self.w.GetForegroundWindow()) # get process name.exe
        self.classname = self.w.GetClassName (self.w.GetForegroundWindow()) # get process class name
        print(username, self.classname, psutil.Process(self.pid[-1]).name())

        # add window class name to dictionary if missing and iterate its value by 1 second
        if not self.classname in dictionary:
            dictionary[self.classname] = 1
        else:
            dictionary[self.classname] += 1

        self.active_window_time = dictionary.get(self.classname)
        
        # add and refresh label for active window
        self.active_window = tk.Label(root, text=self.classname).place(relx=0.28, rely=0.1)
        self.active_window_time = tk.Label(root, text=self.active_window_time).place(relx=0.8, rely=0.1)

        print(dictionary)
        Active_tracker.getIdleTime(self)
        export_iterator += 1 # auto-save timer/counter
        if export_iterator == export_iterator_max:
            Active_tracker.export()
            export_iterator = 0

        text1 = tk.Text(root)#.place(relx=0.025,rely=0.28,relheight=0.55,relwidth=0.95)
        for x in dictionary:
            text1.insert(tk.END, x)
            text1.insert(tk.END, "\t")
            text1.insert(tk.END, dictionary[x])
            text1.insert(tk.END, "\n")

        text1.place(relx=0.025,rely=0.28,relheight=0.55,relwidth=0.95)

    def getIdleTime(self):
        global idle_state
        global idle_time_max
        self.idle_time = (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0
        print(self.idle_time)
        if self.idle_time >= idle_time_max:
            print("5 minutes passed")
            Active_tracker.add_idle_max(self)
        else:
            idle_state = "below 0"

    def add_idle_max(self):
        global idle_state
        global idle_time_max
        if idle_state == "below 0":
            idle_state = "add max time"
            dictionary["Idle"] += idle_time_max
            dictionary[self.classname] -= 1
            idle_state = "add seconds"
        elif idle_state == "add seconds":
            dictionary["Idle"] += 1
            dictionary[self.classname] -= 1


    def export():
        with open("export "+filename.strftime("%d %B %Y")+".txt", "w") as outputfile:
            json.dump(dictionary, outputfile)
            print("Exported data to file!")


    

    
    
        


# INITIALIZE =========================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    root.title("Time Tracker")
    root.geometry("420x800+800+150") #WidthxHeight and x+y of main window
    load_settings()
    timer = Timer(root)
    root.mainloop()
