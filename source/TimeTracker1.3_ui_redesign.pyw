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

#Convert seconds into hours, minutes and seconds to be displayed
def convert(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds) 

def callback_quit(event):
    raise SystemExit

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
    mpos = win32gui.GetCursorInfo()
    mposxy = mpos[2]
    wmx = mposxy[0]

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

        self.settings = tk.Label(backgr, bg="#5100ba", text="Settings", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.settings.place(relx=0.15, rely=0.95, relwidth=0.7, relheight=0.02)


        self.ui_grid = tk.Frame(root, bg="#162554")
        self.ui_grid.place(relx=0.05, rely=0.075, relwidth=0.9, relheight=0.8)
        for row in range(15):
            tk.Label(self.ui_grid, bg="#162554", height=2).grid(row=row, column=0, pady=10)
        
        #timer object
        self.loop = tk.Label(root)
        self.loop.place(x=0,y=0,width=0,height=0)
        # start the timer
        self.loop.after(100, self.timer)

    def timer(self):
        global wmx
        get_mouse_pos()
        if wmx >= 260:
            master_x = -269
            root.geometry("270x%i+%i+0" % (scr_height, master_x))
        # request tkinter to call self.timer after 1s (the delay is given in ms)
        self.loop.after(100, self.timer)

    def add_new(self, *args):
        global grid_cells
        self.task_name = tk.simpledialog.askstring(title="Add new task", prompt="Please enter task name.\nUp to 10 characters long.")
        if self.task_name != None:
            # get next empty grid row
            for key, value in grid_cells.items():
                if value == "empty":
                    self.task = tk.Label(self.ui_grid, text=str(self.task_name), width=12, bg="#162554", relief="ridge", foreground="white", font=("Helvetica", 12)).grid(row=int(key), column=1)
                    # self.task.bind("<Button-1>", task_activate)
                    tk.Label(self.ui_grid, text="00:00:00", bg="#162554", foreground="white", font=("Helvetica", 12)).grid(row=int(key), column=2)
                    self.add = tk.Label(self.ui_grid, text="+", bg="#3c4757", foreground="white", font=("Helvetica", 12)).grid(row=int(key), column=3)
                    # self.add.bind("<Button-1>", add_time_postmortem)
                    tk.Label(self.ui_grid, text="", bg="#162554").grid(row=int(key), column=4)
                    self.delete = tk.Label(self.ui_grid, text="Del", bg="#3c4757", foreground="white", font=("Helvetica", 12)).grid(row=int(key), column=5)
                    # self.delete.bind("<Button-1>", delete_row)
                    tk.Label(self.ui_grid, bg="red").grid(row=int(key), column=6) #"#162554"

                    grid_cells[key] = "full"
                    break



if __name__ == "__main__":
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
    UI(root).place(relwidth=1, relheight=1)
    root.mainloop()
