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
import sys

entry_text = ""

# autosave and save location
autosave_inc = 0
autosave_max = 20 # save automatically every 20(Default) seconds/cycles
currentDirectory = os.getcwd()
path = currentDirectory+"\\dumps\\"
filename = datetime.datetime.now()
autosave = ""

#name and row of the currently selected active task
active_task = {
    "name" : "Resting",
    "row" : 0,
}

# empty or active
grid_cells = {
    "1" : "empty",
    "2" : "empty",
    "3" : "empty",
    "4" : "empty",
    "5" : "empty",
    "6" : "empty",
    "7" : "empty",
    "8" : "empty",
    "9" : "empty",
    "10" : "empty"
}

# list with all tasks and their respective accumulated times
task_accumulated_time = {}

#=========================================================================
def callback():
    if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
        root.destroy()

def load_settings():
    global autosave_max
    file = open(currentDirectory+"\\" + "config.txt", "r")
    contents = file.readlines()
    file.close

    for line in contents:
        if "autosave" in line:
            x = line.split(sep="=")
            autosave_max = int(x[1])

def save_settings():
    autosave_max = int(autosave.get())
    file = open(currentDirectory+"\\" + "config.txt", "w")
    file.write("autosave=" + str(autosave_max))
    file.close

#Convert seconds into hours, minutes and seconds to be displayed
def convert(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds) 

class UI:
    def __init__(self, parent):
        global entry_text, entry, autosave, autosave_max

        #tk.Button(root, text="Settings", command=self.settings_window).place(relx=0.55, rely=0.025, relwidth=0.2)

        entry = tk.StringVar()
        self.entry_space = tk.Entry(root, textvariable=entry)
        self.entry_space.place(relx=0.05, rely=0.1, relheight=0.07, relwidth=0.47)
        entry.set(entry_text)
        
        tk.Label(root, text="On              Off", bg="gray", relief=tk.RIDGE).place(relx=0.55, rely=0.1, relwidth=0.2, relheight=0.064)
        self.on_tb_destroyed = tk.Button(root, text="On", command=self.on_off)
        self.on_tb_destroyed.place(relx=0.55, rely=0.1, relwidth=0.1)

        self.frame = tk.LabelFrame(root, text="Tasks")
        self.frame.place(relx=0.018, rely=0.2, relwidth=0.75, relheight=0.77)

        b0 = tk.Button(self.frame, text="  ", relief=tk.RIDGE).grid(row=0 , column=0)
        self.task = tk.Button(self.frame, text="Resting", width=40, command=lambda row=0: self.task_activate(row)).grid(row=0, column=1)
        self.time_elapsed = tk.Label(self.frame, text="[Time elapsed]", width=15, relief=tk.RIDGE).grid(row=0, column=2)

        tk.Button(self.frame, text="+", command=lambda row=1: self.addnew(row)).grid(row=1 , column=0)
        tk.Button(self.frame, text="+", command=lambda row=2: self.addnew(row)).grid(row=2 , column=0)
        tk.Button(self.frame, text="+", command=lambda row=3: self.addnew(row)).grid(row=3 , column=0)
        tk.Button(self.frame, text="+", command=lambda row=4: self.addnew(row)).grid(row=4 , column=0)
        tk.Button(self.frame, text="+", command=lambda row=5: self.addnew(row)).grid(row=5 , column=0)
        tk.Button(self.frame, text="+", command=lambda row=6: self.addnew(row)).grid(row=6 , column=0)
        tk.Button(self.frame, text="+", command=lambda row=7: self.addnew(row)).grid(row=7 , column=0)
        tk.Button(self.frame, text="+", command=lambda row=8: self.addnew(row)).grid(row=8 , column=0)
        tk.Button(self.frame, text="+", command=lambda row=9: self.addnew(row)).grid(row=9 , column=0)
        tk.Button(self.frame, text="+", command=lambda row=10: self.addnew(row)).grid(row=10 , column=0)

        # settings pane
        self.settings_pane = tk.LabelFrame(root, text="Settings")
        self.settings_pane.place(relx=0.78, rely=0.02, relwidth=0.2, relheight=0.95)
        tk.Label(self.settings_pane, text="Autosave (sec): ").place(x=1, y=1)

        autosave = tk.StringVar()
        tk.Entry(self.settings_pane, width=3, textvariable=autosave).place(x=90, y=1)
        autosave.set(autosave_max)
        tk.Button(self.settings_pane, text="Save Settings", command=save_settings).place(relx=0.15, rely=0.5)
        tk.Button(self.settings_pane, text="About", command=self.about).place(relx=.01, rely=0.92, relwidth=.95)

        # variable storing time
        self.seconds = 0
        # label displaying time
        self.label = tk.Label(parent, text="0 s", font="Arial 20", width=10)
        self.label.place(relx=0.1)
        # start the timer
        self.label.after(1000, self.refresh_label)

    loop_state = 0 # 0 off/on 1
    def refresh_label(self):
        global autosave_max, autosave_inc
        #refresh the content of the label every second
        # increment the time
        if self.loop_state == 1:
            self.seconds += 1
            # increment time label, for specific row
            self.increment_time_label()
            #convert the time into a 00:00:00 format
            self.conv_seconds = convert(self.seconds)
            # display the new time
            self.label.configure(text=self.conv_seconds)
            # increment and activate autosave
            autosave_inc += 1
            if autosave_inc == autosave_max:
                save_data()
                autosave_inc = 0
            else:
                pass
        # request tkinter to call self.refresh after 1s (the delay is given in ms)
        self.label.after(1000, self.refresh_label)

    # add new row of buttons on this specific row
    def addnew(self, row):
        global entry_text
        entry_text = entry.get()
        self.entry_space.delete(0, "end")
        cell_availability = grid_cells[str(row)]
        
        if cell_availability == "empty" and entry_text != "":
            self.task = tk.Button(self.frame, text=entry_text, width=40, command=lambda row=row: self.task_activate(row)).grid(row=row, column=1)
            self.time_elapsed = tk.Label(self.frame, text="[Time elapsed]", width=15, relief=tk.RIDGE).grid(row=row, column=2)
            self.delete_b = tk.Button(self.frame, text="-", command=lambda row=row: self.delete_row(row)).grid(row=row, column=3)
            grid_cells[str(row)] = "active"

    # delete this specific row of buttons, indexes: 2-name, 1-time, 0-delete button
    def delete_row(self, row):
        # set default Resting task when deleting this one if this one is the currently selected:
        self.check_task_if_same = self.frame.grid_slaves(row=row)[2]
        if active_task["name"] == self.check_task_if_same["text"]:
            active_task["name"] = "Resting"
            active_task["row"] = 0

        widget_to_delete = self.frame.grid_slaves(row=row)[2]
        #print(widget_to_delete, widget_to_delete['text'])
        widget_to_delete.destroy()
        widget_to_delete = self.frame.grid_slaves(row=row)[1]
        widget_to_delete.destroy()
        widget_to_delete = self.frame.grid_slaves(row=row)[0]
        widget_to_delete.destroy()
        grid_cells[str(row)] = "empty"



    # get the label index of the currently activated task's row
    def task_activate(self, row):
        if row == 0:
            self.active_timer_row = self.frame.grid_slaves(row=row)[0]
            ttt = self.frame.grid_slaves(row=row)[1]
        else:
            self.active_timer_row = self.frame.grid_slaves(row=row)[1]
            ttt = self.frame.grid_slaves(row=row)[2]

        
        # add task name and row to active task handler
        active_task["name"] = ttt['text']
        active_task["row"] = row
        #turn previous active label back to gray
        self.time_label_to_refresh.configure(bg="#e6e6e6")


    def about(self):
        self.top = tk.Toplevel()
        self.top.resizable(0,0)
        self.top.title("Settings")
        self.top.protocol("WM_DELETE_WINDOW", self.about_callback)
        self.top.wm_attributes("-topmost", 1)
        self.top.geometry("200x100+850+250") #WidthxHeight and x+y
        root.iconify()
        tk.Label(self.top, text="Version: 1.0\n11.12.2019\nCreated by:\nSimeon P. Todorov\nContact me:\nthe_nexus@mail.bg").pack()

    def about_callback(self):
        root.deiconify()
        self.top.destroy()

    def on_off(self):
        try:
            self.on_tb_destroyed.destroy()
        except:
            pass

        global loop_state
        if self.loop_state == 0: #start timer
            self.loop_state += 1
            self.off = tk.Button(root, text="Off", command=self.on_off)
            self.off.place(relx=0.65, rely=0.1, relwidth=0.1)
            try:
                self.on.destroy()
            except:
                pass
        elif self.loop_state == 1: #stop timer
            self.loop_state -= 1
            self.on = tk.Button(root, text="On", command=self.on_off)
            self.on.place(relx=0.55, rely=0.1, relwidth=0.1)
            self.off.destroy()


    def increment_time_label(self):
        # check for the currently selected active task name
        self.currently_selected_task_name = active_task.get("name")
        # if no task is selected, increment Resting by default
        # add this time to dictionary as value to task name as key
        if not self.currently_selected_task_name in task_accumulated_time:
            task_accumulated_time[self.currently_selected_task_name] = 1
        else:
            task_accumulated_time[self.currently_selected_task_name] += 1
        # refresh time label with new accumulated time from the dict
        self.time_row = active_task.get("row")
        self.time_label_to_refresh = self.frame.grid_slaves(row=self.time_row, column=2)[0]
        # convert the time into a 00:00:00 format
        self.conv_time = convert(task_accumulated_time[self.currently_selected_task_name])
        self.time_label_to_refresh.configure(text=self.conv_time, bg="green")
        

def save_data():
    with open(path + "log "+filename.strftime("%d %B %Y")+".txt", "w") as outputfile:
        json.dump(task_accumulated_time, outputfile)

#=========================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    title = root.title("Time Tracker")
    root.wm_attributes("-topmost", 1)
    root.geometry("600x400+800+150") #WidthxHeight and x+y of main window
    root.protocol("WM_DELETE_WINDOW", callback)
    load_settings()
    UI(root)
    root.mainloop()
    
