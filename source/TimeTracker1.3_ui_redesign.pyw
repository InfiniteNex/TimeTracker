import tkinter as tk
import win32api
import win32gui
import win32process
import os
import sys
from os import path
from tkinter import messagebox as tkMessageBox
from tkinter import simpledialog
from tkcalendar import Calendar, DateEntry
import datetime
import getpass
import time
import psutil
import json
import winshell
import urllib
from urllib import request
import webbrowser

master_x = -269
scr_height = win32api.GetSystemMetrics(1)
wmx = None
website = "https://infinitenex.github.io/TimeTracker/"
current_version = "1.3"
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
    "name" : "blank",
    "row" : 0
}

# empty or full
grid_cells = {
    "0" : "empty",
    "1" : "empty",
    "2" : "empty",
    "3" : "empty",
    "4" : "empty",
    "5" : "empty",
    "6" : "empty",
    "7" : "empty",
    "8" : "empty",
    "9" : "empty",
    "10" : "empty",
    "11" : "empty",
    "12" : "empty",
    "13" : "empty",
    "14" : "empty"
}

# list with all tasks and their respective accumulated times
task_accumulated_time = {}

#set the filename to the current day
filename = datetime.datetime.now() 
#=========================================================================
def webcallback():
    webbrowser.open_new(website)

def version_check():
    link = urllib.request.urlopen(website).read()
    lnk = link.split()
    aa = str(lnk[115]).split("v")
    aaa = str(aa[1]).split("<")
    #print(aaa[0])
    if aaa[0] != current_version:
        if tkMessageBox.askokcancel(title="New version available!", message="A new version of TimeTracker is available!\nCurrent version: "+current_version+"\nNew version: "+aaa[0]+"\nDo you wish to update now?"):
            webcallback()
    else:
        pass # Running latest version.

# on startup, create \logs\, autosave and grid files
def required_dir_check():
    # logs dir
    logs_path = ".\\logs"
    if os.path.isdir(".\\logs") == True:
        print("Step skipped: logs folder already exists")
    else:
        os.mkdir(logs_path)
    
    # grid.txt
    if os.path.isfile(".\\grid.txt") == True:
        print("Step skipped: grid.txt already exists")
    else:
        file = open("grid.txt", "w")
        file.write(str(grid_cells))
        file.close()

    # config.txt
    if os.path.isfile(".\\config.txt") == True:
        print("Step skipped: config.txt already exists")
    else:
        file = open("config.txt", "w")
        file.write("autosave=" + str(autosave_max))
        file.close()  

#Convert seconds into hours, minutes and seconds to be displayed
def convert(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%02d:%02d:%02d" % (hour, minutes, seconds) 

def callback_quit(event):
    if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?\nAll data will be saved."):
        save_settings()
        raise SystemExit

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
    file = open(currentDirectory+"\\" + "config.txt", "w")
    file.write("autosave=" + str(autosave_max))
    file.close()

def save_data():
    #save names and accumulated times
    with open(path_to_logs + "log "+filename.strftime("%d %B %Y")+".txt", "w") as outputfile:
        json.dump(task_accumulated_time, outputfile)

    #save grid layout
    with open(currentDirectory+"\\grid.txt", "w") as outputfile:
        json.dump(grid_cells, outputfile)

def callback_show_hide_ui(event):
    global master_x, root, wmx
    get_mouse_pos()
    
    if wmx >= 260:
        master_x = -269
        root.geometry("270x%i+%i+0" % (scr_height, master_x))
    else:
        master_x = 0
        root.geometry("270x%i+%i+0" % (scr_height, master_x))

def get_mouse_pos():
    global wmx
    # mouse pos on screen
    try:
        mpos = win32gui.GetCursorInfo()
        mposxy = mpos[2]
        wmx = mposxy[0]
    except:
        pass

class GradientFrame(tk.Canvas):
    '''A gradient frame which uses a canvas to draw the background'''
    def __init__(self, parent, color1="black", color2="white", **kwargs):
        tk.Canvas.__init__(self, parent, bd=0, highlightthickness=0, **kwargs)
        self._color1 = color1
        self._color2 = color2
        self.bind("<Configure>", self._draw_gradient)

    def _draw_gradient(self, event=None):
        '''Draw the gradient'''
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        limit = width
        (r1,g1,b1) = self.winfo_rgb(self._color1)
        (r2,g2,b2) = self.winfo_rgb(self._color2)
        r_ratio = float(r2-r1) / limit
        g_ratio = float(g2-g1) / limit
        b_ratio = float(b2-b1) / limit

        for i in range(limit):
            nr = int(r1 + (r_ratio * i))
            ng = int(g1 + (g_ratio * i))
            nb = int(b1 + (b_ratio * i))
            color = "#%4.4x%4.4x%4.4x" % (nr,ng,nb)
            self.create_line(i,0,i,height, tags=("gradient",), fill=color)
        self.lower("gradient")

class UI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        backgr = GradientFrame(self, "#00134d", "#001a69", borderwidth=1, relief="sunken")
        backgr.pack(side="bottom", fill="both", expand=True)
        backgr.bind("<Motion>", callback_show_hide_ui)

        self.quit = tk.Label(backgr, bg="#5100ba", text="☼", foreground="white", relief="ridge")
        self.quit.place(relx=0.85, rely=0.005, relwidth=0.1, relheight=0.02)
        self.quit.bind("<Button-1>", callback_quit)

        self.new = tk.Label(backgr, bg="#5100ba", text="New", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.new.place(relx=0.15, rely=0.03, relwidth=0.7, relheight=0.02)
        self.new.bind("<Button-1>", self.add_new)

        self.logs = tk.Label(backgr, bg="#5100ba", text="Logs", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.logs.place(relx=0.15, rely=0.90, relwidth=0.7, relheight=0.02)
        self.logs.bind("<Button-1>", self.logs_win)

        self.settings = tk.Label(backgr, bg="#5100ba", text="Settings", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.settings.place(relx=0.15, rely=0.95, relwidth=0.7, relheight=0.02)
        self.settings.bind("<Button-1>", self.settings_win)


        self.ui_grid = tk.Frame(root, bg="#162554")
        self.ui_grid.place(relx=0.05, rely=0.075, relwidth=0.9, relheight=0.8)
        for row in range(15):
            tk.Label(self.ui_grid, bg="#162554", height=2).grid(row=row, column=0, pady=10)
            tk.Label(self.ui_grid, bg="#162554").grid(row=row, column=6) #"#162554"

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
            self.cell_name = grid_cells_load.get(key)
            if self.cell_name != "empty":
                self.task = tk.Label(self.ui_grid, text=str(self.cell_name), width=12, bg="#162554", relief="ridge", foreground="white", font=("Helvetica", 12))
                self.task.grid(row=int(key), column=1)
                self.task.bind("<Button-1>", lambda event, row=int(key): self.on_off(event, row))
                try:
                    self.conv_time = convert(task_accumulated_time.get(self.cell_name))  #load times in 00:00:00 format rather than seconds
                except:
                    self.conv_time = "00:00:00"
                tk.Label(self.ui_grid, text=self.conv_time, bg="#162554", foreground="white", font=("Helvetica", 12)).grid(row=int(key), column=2)
                self.add = tk.Label(self.ui_grid, text="+", bg="#3c4757", foreground="white", font=("Helvetica", 12)).grid(row=int(key), column=3)
                # self.add.bind("<Button-1>", add_time_postmortem)
                tk.Label(self.ui_grid, text="", bg="#162554").grid(row=int(key), column=4)
                self.delete = tk.Label(self.ui_grid, text="Del", bg="#3c4757", foreground="white", font=("Helvetica", 12))
                self.delete.grid(row=int(key), column=5)
                self.delete.bind("<Button-1>", lambda event, row=int(key): self.delete_row(event, row))
                grid_cells[str(key)] = self.cell_name

#==========TIMER===================

        #variable storing time
        self.seconds = 0
        #timer object
        self.loop = tk.Label(root)
        self.loop.place(x=0,y=0,width=0,height=0)
        # start the timer
        self.loop.after(100, self.timer)

    loop_state = 0 # 0 off/on 1
    def timer(self):
        global wmx, autosave_max, autosave_inc
        get_mouse_pos()
        try:
            if wmx >= 260:
                master_x = -269
                root.geometry("270x%i+%i+0" % (scr_height, master_x))
        except:
            pass

        # increment the time
        if self.loop_state == 1:
            self.seconds += 1
            # increment time label, for specific row
            self.increment_time_label()
            #convert the time into a 00:00:00 format
            self.conv_seconds = convert(self.seconds)
            # display the new time
            self.loop.configure(text=self.conv_seconds)
            # increment and activate autosave
            autosave_inc += 1
            if autosave_inc == autosave_max:
                save_data()
                autosave_inc = 0
            else:
                pass
        # request tkinter to call self.timer after 1s (the delay is given in ms)
        self.loop.after(1000, self.timer)

#==========TIMER===================

    def on_off(self, event, row):
        global loop_state, filename, task_accumulated_time # loop state - 0 off/on 1

        # check the current day
        self.day_check = datetime.datetime.now()
        # get name of task
        self.selected_task_name = self.ui_grid.grid_slaves(row=row)[4]
        # self.selected_task_name["text"] # selected task name string

        if self.loop_state == 1:
            if self.selected_task_name["text"] == active_task["name"]:
                self.loop_state = 0 # turn timer off
                #deact rec lbl
                self.active_rec_lbl = self.ui_grid.grid_slaves(row=row, column=6)[0]
                self.active_rec_lbl.configure(bg="#162554")

            elif self.selected_task_name["text"] != active_task["name"]:
                #deactivate prev rec lbl
                old_row = active_task["row"]
                self.active_rec_lbl = self.ui_grid.grid_slaves(row=old_row, column=6)[0]
                self.active_rec_lbl.configure(bg="#162554")
                #set task as currently active
                active_task["name"] = self.selected_task_name["text"]
                active_task["row"] = row
                #activate rec lbl
                self.active_rec_lbl = self.ui_grid.grid_slaves(row=row, column=6)[0]
                self.active_rec_lbl.configure(bg="red")

        elif self.loop_state == 0:
            if self.day_check.strftime("%d %B %Y") != filename.strftime("%d %B %Y"):
            # if != then change filename to new day and empty accumulated time for all tasks
                filename = self.day_check
                task_accumulated_time = {}
                # set back the timer
                self.seconds = 0
                # nullify all time labels
                for row in self.ui_grid:
                    try:
                        self.nullify = self.ui_grid.grid_slaves(row=row, column=2)[0]
                        self.nullify.configure(text="00:00:00")
                    except:
                        print("No widget to null on row %i" % (row))

            self.loop_state = 1 # turn timer on
            active_task["name"] = self.selected_task_name["text"] #set task as currently active
            active_task["row"] = row
            #activate rec lbl
            self.active_rec_lbl = self.ui_grid.grid_slaves(row=row, column=6)[0]
            self.active_rec_lbl.configure(bg="red")
        save_data()

    def increment_time_label(self):
        # check for the currently selected active task name
        self.currently_selected_task_name = active_task.get("name")
        # if no task is selected, dont run timer
        # add this time to dictionary as value to task name as key
        if not self.currently_selected_task_name in task_accumulated_time:
            task_accumulated_time[self.currently_selected_task_name] = 1
        else:
            task_accumulated_time[self.currently_selected_task_name] += 1
        # refresh time label with new accumulated time from the dict
        self.time_row = active_task.get("row")
        self.time_label_to_refresh = self.ui_grid.grid_slaves(row=self.time_row, column=2)[0]
        # convert the time into a 00:00:00 format
        self.conv_time = convert(task_accumulated_time[self.currently_selected_task_name])
        self.time_label_to_refresh.configure(text=self.conv_time)

    def add_new(self, *args):
        global grid_cells
        self.task_name = tk.simpledialog.askstring(title="Add new task", prompt="Please enter task name.\nUp to 10 characters long.")
        if self.task_name != None:
            # get next empty grid row
            for key, value in grid_cells.items():
                if value == "empty":
                    self.task = tk.Label(self.ui_grid, text=str(self.task_name), width=12, bg="#162554", relief="ridge", foreground="white", font=("Helvetica", 12))
                    self.task.grid(row=int(key), column=1)
                    self.task.bind("<Button-1>", lambda event, row=int(key): self.on_off(event, row))
                    tk.Label(self.ui_grid, text="00:00:00", bg="#162554", foreground="white", font=("Helvetica", 12)).grid(row=int(key), column=2)
                    self.add = tk.Label(self.ui_grid, text="+", bg="#3c4757", foreground="white", font=("Helvetica", 12)).grid(row=int(key), column=3)
                    # self.add.bind("<Button-1>", add_time_postmortem)
                    tk.Label(self.ui_grid, text="", bg="#162554").grid(row=int(key), column=4)
                    self.delete = tk.Label(self.ui_grid, text="Del", bg="#3c4757", foreground="white", font=("Helvetica", 12))
                    self.delete.grid(row=int(key), column=5)
                    self.delete.bind("<Button-1>", lambda event, row=int(key): self.delete_row(event, row))

                    grid_cells[key] = str(self.task_name)
                    break

    # delete this specific row of buttons
    def delete_row(self, event, row):
        this_row = self.ui_grid.grid_slaves(row=row)[4]
        if tkMessageBox.askokcancel("Alert!", "Do you really wish to delete %s from the list?" % (this_row["text"])):
            widget_to_delete = self.ui_grid.grid_slaves(row=row)[4]
            widget_to_delete.destroy()  #task_name
            widget_to_delete = self.ui_grid.grid_slaves(row=row)[3]
            #print(widget_to_delete, widget_to_delete['text'])
            widget_to_delete.destroy()  #time_label
            widget_to_delete = self.ui_grid.grid_slaves(row=row)[2]
            widget_to_delete.destroy()  #add_time
            widget_to_delete = self.ui_grid.grid_slaves(row=row)[1]
            widget_to_delete.destroy()  #blank label
            widget_to_delete = self.ui_grid.grid_slaves(row=row)[0]
            widget_to_delete.destroy()  #delete_button
            grid_cells[str(row)] = "empty"

    def settings_win(self, event):
        global autosave, autosave_max

        self.top = tk.Toplevel()
        self.top.resizable(0,0)
        self.top.configure(background="yellow")
        self.top.wm_attributes("-transparentcolor", "yellow")
        self.top.attributes("-alpha", 0.95)
        self.top.overrideredirect(True) # removes title bar
        self.top.title("Settings")
        self.top.wm_attributes("-topmost", 1)
        self.top.geometry("270x%i+270+0" % (scr_height)) #WidthxHeight and x+y of main window

        self.bg_sett = tk.Frame(self.top, bg="#00134d")
        self.bg_sett.pack(fill="both", expand=True)
        #==================================================================================================================================
        self.top_name = tk.Label(self.bg_sett, text="Settings", bg="#162554", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.top_name.pack(fill="x")

        tk.Label(self.bg_sett, text="Autosave (sec): ", bg="#162554", font=("Helvetica", 12), foreground="white", relief="ridge").pack()

        autosave = tk.StringVar()
        tk.Entry(self.bg_sett, width=5, textvariable=autosave).pack()
        autosave.set(autosave_max)

        # ADD STARTUP AND DESKTOP SHORTCUTS FUNCTIONS

        #==================================================================================================================================
        self.top_close = tk.Label(self.bg_sett, text="Close", bg="#5100ba", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.top_close.pack(fill="x", side="bottom")
        self.top_close.bind("<Button-1>", self.close_settings_callback)

    def close_settings_callback(self, event):
        global autosave, autosave_max

        autosave_max = int(autosave.get())
        save_settings()
        self.top.destroy()

    def logs_win(self, event):
        self.top2 = tk.Toplevel()
        self.top2.resizable(0,0)
        self.top2.configure(background="yellow")
        self.top2.wm_attributes("-transparentcolor", "yellow")
        self.top2.attributes("-alpha", 0.95)
        self.top2.overrideredirect(True) # removes title bar
        self.top2.title("Logs")
        self.top2.wm_attributes("-topmost", 1)
        self.top2.geometry("270x%i+270+0" % (scr_height)) #WidthxHeight and x+y of main window

        self.bg_logs = tk.Frame(self.top2, bg="#00134d")
        self.bg_logs.pack(fill="both", expand=True)
        #==================================================================================================================================
        self.top_name = tk.Label(self.bg_logs, text="Logs", bg="#162554", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.top_name.pack(fill="x")

        ## LOGS CODE HERE
        ## PREVENT LOGS WINDOW FROM OPENING WHILE ITS ALREADY OPENED

        #==================================================================================================================================
        self.top_close = tk.Label(self.bg_logs, text="Close", bg="#5100ba", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.top_close.pack(fill="x", side="bottom")
        self.top_close.bind("<Button-1>", self.close_logs_callback)

    def close_logs_callback(self, event):
        self.top2.destroy()

if __name__ == "__main__":
    required_dir_check()
    root = tk.Tk()
    # root.option_add('*background', "#00134d")
    # # root.option_add('*Entry*background', '#FFFFFF')
    # root.option_add('*foreground', '#FFFFFF')
    root.option_add('*font', ("Helvetica", 12))
    root.configure(background="yellow")
    root.wm_attributes("-topmost", 1)
    root.wm_attributes("-transparentcolor", "yellow")
    root.attributes("-alpha", 0.95)
    root.overrideredirect(True) # removes title bar
    root.geometry("270x%i+%i+0" % (scr_height, master_x)) #WidthxHeight and x+y of main window
    load_settings()
    UI(root).place(relwidth=1, relheight=1)
    try:
        version_check()
    except:
        print("Cannot establish connection with website!")
    root.mainloop()
