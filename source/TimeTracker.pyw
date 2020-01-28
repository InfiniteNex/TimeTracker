import tkinter as tk
from tkinter import messagebox as tkMessageBox
from tkinter import simpledialog
from tkcalendar import Calendar, DateEntry
import win32api
import win32gui
import win32process
import os
from os import path
import sys
import datetime
import time
import psutil
import json
import winshell
import urllib
from urllib import request
import webbrowser


settings_check = 0 # 0 closed, 1 opened
logs_check = 0 # 0 closed, 1 opened
check = 1
master_x = -269
scr_width = win32api.GetSystemMetrics(0)
scr_height = win32api.GetSystemMetrics(1)
wmx = None
website = "https://infinitenex.github.io/TimeTracker/"
website_ver = "https://raw.githubusercontent.com/InfiniteNex/TimeTracker/master/changelog.txt"
current_version = "1.4.2"
entry_text = ""
current_year = datetime.datetime.now()
# autosave and save location
autosave_inc = 0
autosave_max = 20 # save automatically every 20(Default) seconds/cycles
currentDirectory = os.getcwd()
path_to_logs = currentDirectory+"\\logs\\"
autosave = ""
activity_rem_time = 0 # 0 minutes by default
art_time = 0
rec_multiples = 0 # 0 off, 1 on

#name and row of the currently selected active task
active_task = {}

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
# def webcallback():
#     webbrowser.open_new(website)

def version_check():
    link = None
    try:
        link = urllib.request.urlopen(website_ver).readlines()
    except:
        print("Cannot establish connection.")

    if link != None:
        aa = str(link[0]).split(" ")
        aaa = str(aa[2]).split("-")
        #print(aaa[0])
        if aaa[0] != current_version:
            if tkMessageBox.askokcancel(title="New version available!", message="A new version of TimeTracker is available!\nCurrent version: "+current_version+"\nNew version: "+aaa[0]+"\nDo you wish to update now?"):
                os.startfile("updater.exe")
                # quit the current process so the file can be replaced
                save_settings()
                save_data()
                raise SystemExit

        else:
            print("Running latest version.")

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
        save_data()
        raise SystemExit

def load_settings():
    global autosave_max, activity_rem_time, rec_multiples
    file = open(currentDirectory+"\\" + "config.txt", "r")
    contents = file.readlines()
    file.close

    try:
        for line in contents:
            if "autosave" in line:
                x = line.split(sep="=")
                autosave_max = int(x[1])
            if "activity_rem_time" in line:
                x = line.split(sep="=")
                activity_rem_time = int(x[1])
            if "rec_multiples" in line:
                x = line.split(sep="=")
                rec_multiples = int(x[1])
    except:
        print("Probable crash. Files are empty. default values will be used instead.")

def save_settings():
    file = open(currentDirectory+"\\" + "config.txt", "w")
    file.write("autosave=" + str(autosave_max))
    file.write("\nactivity_rem_time=" + str(activity_rem_time))
    file.write("\nrec_multiples=" + str(rec_multiples))
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
        print("No mouse coords found.")

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

        tk.Label(backgr, text="TimeTracker v%s" % (current_version), bg="#00134d", foreground="#656075", font=("Helvetica", 10)).place(x=1, y=1)

        self.quit = tk.Label(backgr, bg="#5100ba", text="☼", foreground="white", relief="ridge")
        self.quit.place(relx=0.85, rely=0.005, relwidth=0.1, relheight=0.02)
        self.quit.bind("<Button-1>", callback_quit)

        self.new = tk.Label(backgr, bg="#5100ba", text="Add New Task", font=("Helvetica", 12), foreground="white", relief="ridge")
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
            try:
                grid_cells_load = eval(inf.read())
            except:
                pass
    
        #parse loaded grid data
        try:
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
                    self.add = tk.Label(self.ui_grid, text="+", bg="#3c4757", foreground="white", font=("Helvetica", 12))
                    self.add.grid(row=int(key), column=3)
                    self.add.bind("<Button-1>", lambda event, row=int(key): self.add_time_postmortem(event, row))
                    tk.Label(self.ui_grid, text="", bg="#162554").grid(row=int(key), column=4)
                    self.delete = tk.Label(self.ui_grid, text="Del", bg="#3c4757", foreground="white", font=("Helvetica", 12))
                    self.delete.grid(row=int(key), column=5)
                    self.delete.bind("<Button-1>", lambda event, row=int(key): self.delete_row(event, row))
                    grid_cells[str(key)] = self.cell_name
        except:
            print("No grid data. Potential crash. Default values will be used instead.")

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
        global wmx, autosave_max, autosave_inc, check, classname, activity_rem_time, art_time, active_task
        
        if int(activity_rem_time) != 0:
            art_time += 1
            if art_time/60 == int(activity_rem_time):
                tk.messagebox.showinfo("Reminder!", "Currently tracking.\nPlease make sure you're tracking the right activity.\nThank you!") # 1.4.1 removed saying what is currently tracked. add this in the future
                art_time = 0
            elif not active_task and art_time/60 == int(activity_rem_time):
                tk.messagebox.showinfo("Reminder!", "You are NOT tracking at the moment!\nPlease make sure you're tracking the right activity.\nThank you!")
                art_time = 0
        
        try:
            self.w=win32gui                                # detect window every second
            self.w.GetWindowText (self.w.GetForegroundWindow()) # get active window code
            self.pid = win32process.GetWindowThreadProcessId(self.w.GetForegroundWindow()) # get process name.exe
            self.classname = self.w.GetClassName (self.w.GetForegroundWindow()) # get process class name
            # print(self.classname, psutil.Process(self.pid[-1]).name())
        except:
            pass

        get_mouse_pos()
        try:
            if wmx >= 260:
                master_x = -269
                root.geometry("270x%i+%i+0" % (scr_height, master_x))
        except:
            print("No mouse coords found.")

        # stop recording if the PC is locked
        if str(self.classname) == "Windows.UI.Core.CoreWindow" and str(psutil.Process(self.pid[-1]).name()) != "SearchUI.exe" and check == 1:
            # print('Locked')
            row = next(iter(active_task.items()))
            self.on_off(event=None, row=row[1])
            check = 0
        else:
            pass #print("unlocked")

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
        global loop_state, filename, task_accumulated_time, check, active_task, rec_multiples # loop state - 0 off/on 1
        check = 1
        # check the current day
        self.day_check = datetime.datetime.now()
        # get name of task
        self.selected_task_name = self.ui_grid.grid_slaves(row=row)[4]
        # self.selected_task_name["text"] # selected task name string

        if self.loop_state == 1:
            if self.selected_task_name["text"] in active_task:
                if rec_multiples == 0: #if rec multiples is off
                    self.loop_state = 0 # turn timer off
                #deact rec lbl
                self.active_rec_lbl = self.ui_grid.grid_slaves(row=row, column=6)[0]
                self.active_rec_lbl.configure(bg="#162554")
                active_task.pop(self.selected_task_name["text"])

            elif not self.selected_task_name["text"] in active_task:
                if rec_multiples == 0: #if rec multiples is off
                    #deactivate prev rec lbl
                    old_row = next(iter(active_task.items()))
                    self.active_rec_lbl = self.ui_grid.grid_slaves(row=old_row[1], column=6)[0]
                    self.active_rec_lbl.configure(bg="#162554")
                    #set task as currently active
                    active_task = {}
                    active_task[self.selected_task_name["text"]] = row #set task as currently active with row as value
                    #activate rec lbl
                    self.active_rec_lbl = self.ui_grid.grid_slaves(row=row, column=6)[0]
                    self.active_rec_lbl.configure(bg="red")
                elif rec_multiples == 1: #if rec multiples is on
                    # add selected task to the list
                    active_task[self.selected_task_name["text"]] = row
                    # activate its rec lbl
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
                for i in range(15):
                    try:
                        self.nullify = self.ui_grid.grid_slaves(row=i, column=2)[0]
                        self.nullify.configure(text="00:00:00")
                    except:
                        print("No widget to null on row %i" % (i))

            self.loop_state = 1 # turn timer on
            active_task[self.selected_task_name["text"]] = row #set task as currently active
            #activate rec lbl
            self.active_rec_lbl = self.ui_grid.grid_slaves(row=row, column=6)[0]
            self.active_rec_lbl.configure(bg="red")
        save_data()

    def increment_time_label(self):
        # add times of all active tasks to the time dict
        for key in active_task:
            if not key in task_accumulated_time:
                task_accumulated_time[key] = 1
            else:
                task_accumulated_time[key] += 1
            # refresh time label with new accumulated time from the dict
            self.time_row = active_task.get(key)
            self.time_label_to_refresh = self.ui_grid.grid_slaves(row=self.time_row, column=2)[0]
            # convert the time into a 00:00:00 format
            self.conv_time = convert(task_accumulated_time[key])
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
                    self.add = tk.Label(self.ui_grid, text="+", bg="#3c4757", foreground="white", font=("Helvetica", 12))
                    self.add.grid(row=int(key), column=3)
                    self.add.bind("<Button-1>", lambda event, row=int(key): self.add_time_postmortem(event, row))
                    tk.Label(self.ui_grid, text="", bg="#162554").grid(row=int(key), column=4)
                    self.delete = tk.Label(self.ui_grid, text="Del", bg="#3c4757", foreground="white", font=("Helvetica", 12))
                    self.delete.grid(row=int(key), column=5)
                    self.delete.bind("<Button-1>", lambda event, row=int(key): self.delete_row(event, row))

                    grid_cells[key] = str(self.task_name)
                    break

    # delete this specific row of buttons
    def delete_row(self, event, row):
        global active_task
        this_row = self.ui_grid.grid_slaves(row=row)[4]
        if tkMessageBox.askokcancel("Alert!", "Do you really wish to delete %s from the list?" % (this_row["text"])):
            # REMOVE TASK FROM ACTIVE TASKS LIST
            try:
                active_task.pop(this_row["text"])
            except:
                pass
            # DEACTIVATE REC LBL FOR THIS ROW
            rec = self.ui_grid.grid_slaves(row=row, column=6)[0]
            rec.configure(bg="#162554")
            #delete widgets
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
            save_data()

    def settings_win(self, event):
        global autosave, autosave_max, settings_check, logs_check, art, activity_rem_time, rec_multiples, rec_multiples_state

        if logs_check == 1:
            self.close_logs_callback(event=None)
        else:
            pass

        if settings_check == 1:
            pass
        else:
            settings_check = 1
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

            tk.Label(self.bg_sett, bg="#00134d", height=2).pack()


            self.desktop_shortcut_state = tk.IntVar(self.bg_sett)
            self.startup_shortcut_state = tk.IntVar(self.bg_sett)

            tk.Checkbutton(self.bg_sett, text="Start with Windows", variable=self.startup_shortcut_state, command=startup_shortcut, onvalue = 1, offvalue = 0, bg="#a1accc", font=("Helvetica", 12), relief="ridge").pack()
            tk.Checkbutton(self.bg_sett, text="Desktop Shortcut", variable=self.desktop_shortcut_state ,command=desktop_shortcut, onvalue = 1, offvalue = 0, bg="#a1accc", font=("Helvetica", 12), relief="ridge").pack()

            tk.Label(self.bg_sett, bg="#00134d", height=2).pack()


            #check if a desktop shortcut exists and set the control state
            desktop = winshell.desktop()
            if path.exists(os.path.join(desktop, "TimeTracker.lnk")):
                self.desktop_shortcut_state.set(1)
            else:
                self.desktop_shortcut_state.set(0)


            tk.Label(self.bg_sett, bg="#00134d", height=2).pack()


            #check if a startup shortcut exists and set the control state
            startup = winshell.startup()
            if path.exists(os.path.join(startup, "TimeTracker.lnk")):
                self.startup_shortcut_state.set(1)
            else:
                self.startup_shortcut_state.set(0)

            tk.Label(self.bg_sett, bg="#00134d", height=2).pack()

            # task activity reminder
            tk.Label(self.bg_sett, text="Activity reminder(in minutes).\nSet to 0 if you dont want to be reminded.", bg="#162554", font=("Helvetica", 12), foreground="white", relief="ridge").pack()
            ## entry for the time
            art = tk.StringVar()
            tk.Entry(self.bg_sett, width=5, textvariable=art).pack()
            art.set(activity_rem_time)

            tk.Label(self.bg_sett, bg="#00134d", height=2).pack()

            # record multiple tasks
            rec_multiples_state = tk.IntVar(self.bg_sett)
            tk.Checkbutton(self.bg_sett, text="Record multiple tasks at once.", variable=rec_multiples_state, onvalue = 1, offvalue = 0, bg="#a1accc", font=("Helvetica", 12), relief="ridge").pack()
            rec_multiples_state.set(rec_multiples)

            #==================================================================================================================================
            self.top_close = tk.Label(self.bg_sett, text="Close", bg="#5100ba", font=("Helvetica", 12), foreground="white", relief="ridge")
            self.top_close.pack(fill="x", side="bottom")
            self.top_close.bind("<Button-1>", self.close_settings_callback)

            # about section
            tk.Button(self.bg_sett, text="About", bg="#5100ba", font=("Helvetica", 12), foreground="white", relief="ridge", command=self.about).pack(fill="x", side="bottom")

    def close_settings_callback(self, event):
        global autosave, autosave_max, settings_check, art, activity_rem_time, rec_multiples, rec_multiples_state

        activity_rem_time = int(art.get())
        rec_multiples = int(rec_multiples_state.get())

        settings_check = 0
        autosave_max = int(autosave.get())
        save_settings()
        self.top.destroy()

    def logs_win(self, event):
        global logs_check, settings_check

        if settings_check == 1:
            self.close_settings_callback(event=None)
        else:
            pass

        if logs_check == 1:
            pass
        else:
            logs_check = 1
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

            # calendar widget
            self.cal = DateEntry(self.bg_logs, width=12, background='darkblue', foreground='white', borderwidth=2, year=current_year.year)
            self.cal.pack()
            tk.Button(self.bg_logs, text="Load", bg="#5100ba", relief="ridge", foreground="white", command=self.load_date_log).pack()

            self.logs_frame = tk.Frame(self.bg_logs, bg="#162554")
            self.logs_frame.place(relx=0.025, rely=0.15, relwidth=0.95, relheight=0.75)

            #==================================================================================================================================
            self.top_close = tk.Label(self.bg_logs, text="Close", bg="#5100ba", font=("Helvetica", 12), foreground="white", relief="ridge")
            self.top_close.pack(fill="x", side="bottom")
            self.top_close.bind("<Button-1>", self.close_logs_callback)

    def close_logs_callback(self, event):
        global logs_check
        logs_check = 0
        self.top2.destroy()

    def load_date_log(self):
        # tk.Label(self.logs_frame, text="Showing logs for:").pack()
        self.get_cal_date = self.cal.get_date()
        # tk.Label(self.logs_frame, text=self.get_cal_date).pack()
        
        # empty any old loaded logs
        try:
            for i in range(15):
                dest0 = self.logs_frame.grid_slaves(row=i, column=0)[0]
                dest0.destroy()
                dest1 = self.logs_frame.grid_slaves(row=i, column=1)[0]
                dest1.destroy()
        except:
            pass

        try:
            self.no_recs.destroy()
        except:
            pass

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
                    tk.Label(self.logs_frame, text=key, bg="#162554", font=("Helvetica", 12), foreground="white", relief="ridge").grid(row=self.index_rows, column=0, pady=5)
                    tk.Label(self.logs_frame, text=task_time_conv, bg="#162554", font=("Helvetica", 12), foreground="white", relief="ridge").grid(row=self.index_rows, column=1, padx=60)
                    self.index_rows += 1
        except:
            self.no_recs = tk.Label(self.logs_frame, text="No log data for chosen date.")
            self.no_recs.pack()

    def about(self):
        self.top3 = tk.Toplevel()
        self.top3.resizable(0,0)
        self.top3.title("About")
        self.top3.iconbitmap("icon_OKt_icon.ico")
        self.top3.wm_attributes("-topmost", 1)

        tk.Label(self.top3, text="Version: "+current_version+"\n2019-2020\nCreated by:\nSimeon P. Todorov\nthe_nexus@mail.bg\nWebsite:\n"+website).pack()

    def add_time_postmortem(self, event, row):
        #prompt for time input
        self.time_to_add = tk.simpledialog.askstring(title="asktime", prompt="How much time do you want to add?\n(ex.: 00:30:00)")
        #get row/task name of pressed button
        self.taskID_to_add_to = self.ui_grid.grid_slaves(row=row, column=1)[0]
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
        self.time_label = self.ui_grid.grid_slaves(row=row, column=2)[0]
        self.converttosec = convert(task_accumulated_time[self.taskname_to_add_to])
        self.time_label['text'] = self.converttosec




class Splash():
    def __init__(self, parent):
            self.splash = tk.Toplevel()
            self.splash.resizable(0,0)
            self.splash.configure(background="yellow")
            self.splash.wm_attributes("-transparentcolor", "yellow")
            self.splash.attributes("-alpha", 0.95)
            self.splash.overrideredirect(True) # removes title bar
            self.splash.title("Splash")
            self.splash.wm_attributes("-topmost", 1)
            self.splash.geometry("%ix%i+%i+%i" % (scr_width/5, scr_height/5, scr_width/2.5, scr_height/2)) #WidthxHeight and x+y of main window

            self.bg_splash = tk.Frame(self.splash, bg="#00134d")
            self.bg_splash.pack(fill="both", expand=True)

            

            tk.Label(self.splash, text="TimeTracker started.\nOpen it from the left edge of the screen.", foreground="white", font=("Helvetica", 16), bg="#00134d").place(relwidth=1, relheight=1)
            tk.Button(self.splash, text="X", foreground="white", font=("Helvetica", 16), bg="#00134d", command=self.splash.destroy).place(relx=0.9, y=1)

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
    version_check()
    Splash(root)
    root.mainloop()
