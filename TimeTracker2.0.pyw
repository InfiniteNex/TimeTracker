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
#=========================================================================

class UI:
    def __init__(self, parent):
        tk.Button(root, text="Settings").place(relx=0.75, rely=0.025, relwidth=0.2)
        tk.Button(root, text="+", command=self.addnew).place(relx=0.02, rely=0.1, relwidth=0.1)
        tk.Entry(root).place(relx=0.13, rely=0.1, relheight=0.07, relwidth=0.6)
        tk.Button(root, text="On").place(relx=0.75, rely=0.1, relwidth=0.1)
        tk.Button(root, text="Off").place(relx=0.85, rely=0.1, relwidth=0.1)

        frame = tk.Frame(root, bg="red").place(relx=0.018, rely=0.2, relwidth=0.94, relheight=0.7)
        
    def addnew(self):
        self.new = tk.Button(root, text="new").place(relx=0.1)
        self.new2 = tk.Button(root, text="new2").place(relx=0.3)

#=========================================================================

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(0,0)
    title = root.title("Time Tracker")
    root.wm_attributes("-topmost", 1)
    root.geometry("400x400+800+150") #WidthxHeight and x+y of main window
    #load_settings()
    UI(root)
    root.mainloop()