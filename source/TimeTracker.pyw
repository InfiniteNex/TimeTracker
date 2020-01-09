import tkinter as tk
import os
from os import path
from tkinter import messagebox as tkMessageBox
from tkinter import simpledialog
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
import winshell

entry_text = ""
current_year = datetime.datetime.now()
# autosave and save location
autosave_inc = 0
autosave_max = 20 # save automatically every 20(Default) seconds/cycles
currentDirectory = os.getcwd()
path_to_logs = currentDirectory+"\\logs\\"
autosave = ""

#name and row of the currently selected active task
active_task = {
    "name" : "Resting",
    "row" : 0,
}

# empty or active
grid_cells = {
    "0" : "Resting",
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

current_day = None


#=========================================================================

def startup_today():
    global filename, current_day

    filename = datetime.datetime.now() #set the filename to the current day
      
def today():
    global filename, current_day, grid_cells
    #check the current day and compare it to the old day registry
    current_day = datetime.datetime.now()
    if current_day != filename:
        # empty the task times from the previous day
        task_accumulated_time = {}
    else:
        pass

def callback():
    if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
        save_settings()
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
    save_data()

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
        self.entry_space.place(relx=0.02, rely=0.01, relheight=0.07, relwidth=0.22)
        entry.set(entry_text)
        
        tk.Label(root, text="On              Off", bg="gray", relief=tk.RIDGE).place(relx=0.245, rely=0.01, relwidth=0.2, relheight=0.064)
        self.on_tb_destroyed = tk.Button(root, text="On", command=self.on_off)
        self.on_tb_destroyed.place(relx=0.245, rely=0.01, relwidth=0.1, relheight=0.064)

        self.frame = tk.LabelFrame(root, text="Tasks")
        self.frame.place(relx=0.018, rely=0.1, relwidth=0.75, relheight=0.87)

        b0 = tk.Button(self.frame, text="  ", relief=tk.RIDGE).grid(row=0 , column=0)
        self.task = tk.Button(self.frame, text="Resting", width=30, command=lambda row=0: self.task_activate(row)).grid(row=0, column=1)
        self.time_elapsed = tk.Label(self.frame, text="[Time elapsed]", width=15, relief=tk.RIDGE)
        self.time_elapsed.grid(row=0, column=2)
        self.add_time = tk.Button(self.frame, text="Add Time", command=lambda row=0: self.add_time_postmortem(row)).grid(row=0, column=3)
        b5 = tk.Label(self.frame).grid(row=0, column=4)


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


        # calendar widget
        self.cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, year=current_year.year)
        self.cal.place(relx=0.55, rely=0.015)
        tk.Button(root, text="Load", command=self.load_date_log).place(relx=0.71, rely=0.01)


        #load saved times from last file of the current day
        try:
            with open(path_to_logs + "log "+filename.strftime("%d %B %Y")+".txt", "r") as load_times:
                accu_times = eval(load_times.read())
                for key in accu_times:
                    # add this time to dictionary as value to task name as key
                    try:
                        task_accumulated_time[key] = accu_times.get(key)
                    except:
                        pass
        except:
            print("No log for this day to load.")


        #load grid layout data
        with open(currentDirectory+"\\grid.txt", "r") as inf:
            grid_cells_load = eval(inf.read())
        #parse loaded grid data
        for key in grid_cells_load:
            cell_name = grid_cells_load.get(key)
            #print(key, cell_name)
            if cell_name != "empty" and cell_name != "Resting":
                self.task = tk.Button(self.frame, text=cell_name, width=30, command=lambda row=key: self.task_activate(row)).grid(row=key, column=1)
                try:
                    self.conv_time = convert(task_accumulated_time.get(cell_name))  #load times in 00:00:00 format rather than seconds
                except:
                    self.conv_time = 0
                self.time_elapsed = tk.Label(self.frame, text=self.conv_time, width=15, relief=tk.RIDGE).grid(row=key, column=2)
                self.add_time = tk.Button(self.frame, text="Add Time", command=lambda row=key: self.add_time_postmortem(row)).grid(row=key, column=3)
                self.delete_b = tk.Button(self.frame, text="-", command=lambda row=key: self.delete_row(row)).grid(row=key, column=4)
                grid_cells[str(key)] = cell_name
            elif cell_name == "Resting":
                try:
                    self.conv_time = convert(task_accumulated_time.get(cell_name))
                except:
                    self.conv_time = 0
                self.time_elapsed.configure(text=self.conv_time)


        # settings pane
        self.settings_pane = tk.LabelFrame(root, text="Settings")
        self.settings_pane.place(relx=0.78, rely=0.02, relwidth=0.22, relheight=0.95)
        tk.Label(self.settings_pane, text="Autosave (sec): ").place(x=1, y=1)

        autosave = tk.StringVar()
        tk.Entry(self.settings_pane, width=3, textvariable=autosave).place(x=90, y=1)
        autosave.set(autosave_max)
        
        
        self.desktop_shortcut_state = tk.IntVar(self.settings_pane)
        self.startup_shortcut_state = tk.IntVar(self.settings_pane)

        tk.Checkbutton(self.settings_pane, text="Start with Windows", variable=self.startup_shortcut_state, command=startup_shortcut, onvalue = 1, offvalue = 0).place(x=1, y=30)
        tk.Checkbutton(self.settings_pane, text="Desktop Shortcut", variable=self.desktop_shortcut_state ,command=desktop_shortcut, onvalue = 1, offvalue = 0).place(x=1, y=60)
        
        #check if a desktop shortcut exists and set the control state
        desktop = winshell.desktop()
        if path.exists(os.path.join(desktop, "TimeTracker.lnk")):
            self.desktop_shortcut_state.set(1)
        else:
            self.desktop_shortcut_state.set(0)

        #check if a startup shortcut exists and set the control state
        startup = winshell.startup()
        if path.exists(os.path.join(startup, "TimeTracker.lnk")):
            self.startup_shortcut_state.set(1)
        else:
            self.startup_shortcut_state.set(0)


        tk.Button(self.settings_pane, text="Save Settings", command=save_settings).place(relx=0.15, rely=0.5)
        tk.Button(self.settings_pane, text="About", command=self.about).place(relx=.01, rely=0.90, relwidth=.95)

        # variable storing time
        self.seconds = 0
        # label displaying time
        self.label = tk.Label(parent, text="00:00:00", font="Arial 10", width=7)
        self.label.place(relx=0.446, rely = 0.015)
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
            self.task = tk.Button(self.frame, text=entry_text, width=30, command=lambda row=row: self.task_activate(row)).grid(row=row, column=1)
            self.time_elapsed = tk.Label(self.frame, text="[Time elapsed]", width=15, relief=tk.RIDGE).grid(row=row, column=2)
            self.add_time = tk.Button(self.frame, text="Add Time", command=lambda row=row: self.add_time_postmortem(row)).grid(row=row, column=3)
            self.delete_b = tk.Button(self.frame, text="-", command=lambda row=row: self.delete_row(row)).grid(row=row, column=4)
            grid_cells[str(row)] = entry_text
        elif entry_text == "":
            tkMessageBox.showerror("Error", "Please add a name before creating new task!")

    # delete this specific row of buttons
    def delete_row(self, row):
        # set default Resting task when deleting this one if this one is the currently selected:
        self.check_task_if_same = self.frame.grid_slaves(row=row)[2]
        if active_task["name"] == self.check_task_if_same["text"]:
            active_task["name"] = "Resting"
            active_task["row"] = 0

        widget_to_delete = self.frame.grid_slaves(row=row)[3]
        widget_to_delete.destroy()  #task_name
        widget_to_delete = self.frame.grid_slaves(row=row)[2]
        #print(widget_to_delete, widget_to_delete['text'])
        widget_to_delete.destroy()  #time_label
        widget_to_delete = self.frame.grid_slaves(row=row)[1]
        widget_to_delete.destroy()  #add_time
        widget_to_delete = self.frame.grid_slaves(row=row)[0]
        widget_to_delete.destroy()  #delete_button
        grid_cells[str(row)] = "empty"

    # get the label index of the currently activated task's row
    def task_activate(self, row):
        self.active_timer_row = self.frame.grid_slaves(row=row)[1]
        task_name = self.frame.grid_slaves(row=row)[3]

        # add task name and row to active task handler
        active_task["name"] = task_name['text']
        active_task["row"] = row
        #turn previous active label back to gray
        self.time_label_to_refresh.configure(bg="#e6e6e6")

    def about(self):
        self.top = tk.Toplevel()
        self.top.resizable(0,0)
        self.top.title("About")
        self.top.iconbitmap("icon_OKt_icon.ico")
        self.top.protocol("WM_DELETE_WINDOW", self.about_callback)
        self.top.wm_attributes("-topmost", 1)
        self.top.geometry("200x90+850+250") #WidthxHeight and x+y
        root.iconify()
        tk.Label(self.top, text="Version: 1.1\n2019\nCreated by:\nSimeon P. Todorov\nthe_nexus@mail.bg").pack()

    def about_callback(self):
        root.deiconify()
        self.top.destroy()

    def on_off(self):
        today() # check the current day
        try:
            self.on_tb_destroyed.destroy()
        except:
            pass

        global loop_state
        if self.loop_state == 0: #start timer
            self.loop_state += 1
            self.off = tk.Button(root, text="Off", command=self.on_off)
            self.off.place(relx=0.345, rely=0.01, relwidth=0.1, relheight=0.064)
            try:
                self.on.destroy()
            except:
                pass
        elif self.loop_state == 1: #stop timer
            self.loop_state -= 1
            self.on = tk.Button(root, text="On", command=self.on_off)
            self.on.place(relx=0.245, rely=0.01, relwidth=0.1, relheight=0.064)
            self.off.destroy()
            save_data()

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
        
    def load_date_log(self):
        #open a top window
        self.top = tk.Toplevel()
        self.top.resizable(0,0)
        self.top.title("Logs")
        self.top.iconbitmap("icon_OKt_icon.ico")
        self.top.protocol("WM_DELETE_WINDOW", self.about_callback)
        self.top.wm_attributes("-topmost", 1)
        self.top.geometry("600x400+800+150") #WidthxHeight and x+y
        root.iconify()
        tk.Label(self.top, text="Showing logs for:").pack()
        self.get_cal_date = self.cal.get_date()
        tk.Label(self.top, text=self.get_cal_date).pack()
        self.display_logs = tk.LabelFrame(self.top)
        self.display_logs.place(relx=0.1, rely=0.2, relwidth=0.8, relheight=0.7)

        
        #load file for chosen date from the logs folder (\\logs)
        self.load_log_file = {}
        self.index_rows = 0
        try:
            with open(path_to_logs + "log " + self.get_cal_date.strftime("%d %B %Y") + ".txt", "r") as log_file:
                self.load_log_file = eval(log_file.read())
                log_file.close()
                #display the data in a readable format
                for key in self.load_log_file:
                    task_time = self.load_log_file.get(key)
                    task_time_conv = convert(task_time)
                    tk.Label(self.display_logs, text=key).grid(row=self.index_rows, column=0)
                    tk.Label(self.display_logs, text=task_time_conv).grid(row=self.index_rows, column=1)
                    self.index_rows += 1

        except:
            tk.Label(self.top, text="No log data for chosen date.").pack()

    def add_time_postmortem(self, row):
        #prompt for time input
        self.time_to_add = tk.simpledialog.askstring(title="asktime", prompt="How much time do you want to add?\n(ex.: 00:30:00)")
        #get row/task name of pressed button
        self.taskID_to_add_to = self.frame.grid_slaves(row=row)[3]
        self.taskname_to_add_to = self.taskID_to_add_to['text']
        #Convert postmortem time back into seconds
        self.convertedhrs = sum(x * int(t) for x, t in zip([1, 60, 3600], reversed(self.time_to_add.split(":"))))
        #add them to the currently accumulated time in the dictionary
        if not self.taskname_to_add_to in task_accumulated_time:
            task_accumulated_time[self.taskname_to_add_to] = self.convertedhrs
        else:
            task_accumulated_time[self.taskname_to_add_to] += self.convertedhrs
        #refresh the time label
        save_data()
        self.time_label = self.frame.grid_slaves(row=row)[2]
        self.converttosec = convert(task_accumulated_time[self.taskname_to_add_to])
        self.time_label['text'] = self.converttosec

        

def save_data():
    #save names and accumulated times
    with open(path_to_logs + "log "+filename.strftime("%d %B %Y")+".txt", "w") as outputfile:
        json.dump(task_accumulated_time, outputfile)

    #save grid layout
    with open(currentDirectory+"\\grid.txt", "w") as outputfile:
        json.dump(grid_cells, outputfile)

def startup_shortcut():
    startup = winshell.startup()
    if path.exists(os.path.join(startup, "TimeTracker.lnk")):
        os.remove(os.path.join(startup, "TimeTracker.lnk"))
    else:
        with winshell.shortcut(os.path.join(startup, "TimeTracker.lnk")) as shortcut: # name of the shortcut and where to place it
            shortcut.path = currentDirectory + "\\TimeTracker.exe"               # target .exe for the shortcut to execute
            shortcut.icon = sys.executable, 0
            shortcut.description = "TimeTracker - Shortcut"
            shortcut.working_directory = currentDirectory

def desktop_shortcut():
    desktop = winshell.desktop()
    if path.exists(os.path.join(desktop, "TimeTracker.lnk")):
        os.remove(os.path.join(desktop, "TimeTracker.lnk"))
    else:
        with winshell.shortcut(os.path.join(desktop, "TimeTracker.lnk")) as shortcut: # name of the shortcut and where to place it
            shortcut.path = currentDirectory + "\\TimeTracker.exe"               # target .exe for the shortcut to execute
            shortcut.icon = sys.executable, 0
            shortcut.description = "TimeTracker - Shortcut"
            shortcut.working_directory = currentDirectory

#=========================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    title = root.title("Time Tracker")
    root.wm_attributes("-topmost", 1)
    root.iconbitmap("icon_OKt_icon.ico")
    root.geometry("600x360+800+150") #WidthxHeight and x+y of main window
    root.protocol("WM_DELETE_WINDOW", callback)
    startup_today() # check the current day on startup
    load_settings()
    UI(root)
    root.mainloop()
    
