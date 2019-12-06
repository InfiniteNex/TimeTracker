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

gindex = 1
entry_text = ""

#=========================================================================
def callback():
    if tkMessageBox.askokcancel("Quit", "Do you really wish to quit?"):
        root.destroy()

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
        global index
        global entry_text
        global entry

        tk.Button(root, text="Settings", command=self.settings_window).place(relx=0.75, rely=0.025, relwidth=0.2)
        tk.Button(root, text="Add", command=self.addnew).place(relx=0.02, rely=0.1, relwidth=0.1)

        entry = tk.StringVar()
        self.entry_space = tk.Entry(root, textvariable=entry)
        self.entry_space.place(relx=0.13, rely=0.1, relheight=0.07, relwidth=0.6)
        entry.set(entry_text)
        
        self.onoffgridframe = tk.Label(root, text="On              Off", bg="gray", relief=tk.RIDGE).place(relx=0.75, rely=0.1, relwidth=0.2, relheight=0.064)
        self.on_tb_destroyed = tk.Button(root, text="On", command=self.on_off)
        self.on_tb_destroyed.place(relx=0.75, rely=0.1, relwidth=0.1)

        self.frame = tk.LabelFrame(root)
        self.frame.place(relx=0.018, rely=0.2, relwidth=0.9, relheight=0.75)

        task = tk.Button(self.frame, text="Resting", width=40)
        task.grid(row=0, column=0)
        time_elapsed = tk.Label(self.frame, text="[Time elapsed]", width=15, bg="gray")
        time_elapsed.grid(row=0, column=1)
        
        # variable storing time
        self.seconds = 0
        # label displaying time
        self.label = tk.Label(parent, text="0 s", font="Arial 20", width=10)
        self.label.pack()
        # start the timer
        self.label.after(1000, self.refresh_label)

    loop_state = 0 # 0 off/on 1
    def refresh_label(self):
        #refresh the content of the label every second
        # increment the time
        if self.loop_state == 1:
            self.seconds += 1
            #convert the time into a 00:00:00 format
            self.conv_seconds = convert(self.seconds)
            # display the new time
            self.label.configure(text=self.conv_seconds)
            # request tkinter to call self.refresh after 1s (the delay is given in ms)
        self.label.after(1000, self.refresh_label)

    def addnew(self):
        global gindex
        global entry_text
        entry_text = entry.get()
        self.entry_space.delete(0, "end")

        if gindex <= 10 and entry_text != "":
            task = tk.Button(self.frame, text=entry_text, width=40)
            task.grid(row=gindex, column=0)
            time_elapsed = tk.Label(self.frame, text="[Time elapsed]", width=15, bg="gray")
            time_elapsed.grid(row=gindex, column=1)
            self.delete_b = tk.Button(self.frame, text="delete", command=lambda index=gindex: self.printOnClick(index), width=10)
            self.delete_b.grid(row=gindex, column=2)
            gindex += 1

    def printOnClick(self, index):
        global gindex
        widget = self.frame.grid_slaves(row=index)[2]
        #print(widget, widget['text'])
        widget.grid_forget()
        widget = self.frame.grid_slaves(row=index)[1]
        #print(widget, widget['text'])
        widget.grid_forget()
        widget = self.frame.grid_slaves(row=index)[0]
        #print(widget, widget['text'])
        widget.grid_forget()
        gindex -= 1

    def settings_window(self):
        self.top = tk.Toplevel()
        self.top.resizable(0,0)
        self.top.title("Settings")
        self.top.protocol("WM_DELETE_WINDOW", self.settings_callback)
        self.top.wm_attributes("-topmost", 1)
        self.top.geometry("300x200+850+250") #WidthxHeight and x+y
        root.iconify()
        tk.Label(self.top, text="Nothing in here yet.").pack()

    def settings_callback(self):
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
            self.off.place(relx=0.85, rely=0.1, relwidth=0.1)
            try:
                self.on.destroy()
            except:
                pass
        elif self.loop_state == 1: #stop timer
            self.loop_state -= 1
            self.on = tk.Button(root, text="On", command=self.on_off)
            self.on.place(relx=0.75, rely=0.1, relwidth=0.1)
            self.off.destroy()








        
#=========================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    title = root.title("Time Tracker")
    root.wm_attributes("-topmost", 1)
    root.geometry("600x400+800+150") #WidthxHeight and x+y of main window
    root.protocol("WM_DELETE_WINDOW", callback)
    #load_settings()
    UI(root)
    root.mainloop()
