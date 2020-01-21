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

master_x = -199
scr_height = win32api.GetSystemMetrics(1)
wmx = None

def callback_quit(event):
    raise SystemExit

def callback_show_hide_ui(event):
    global master_x, root, wmx
    get_mouse_pos()
    
    if wmx >= 190:
        master_x = -199
        root.geometry("200x%i+%i+0" % (scr_height, master_x))
    else:
        master_x = 0
        root.geometry("200x%i+%i+0" % (scr_height, master_x))

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
        self.quit.place(relx=0.88, rely=0.005, relwidth=0.1, relheight=0.02)
        self.quit.bind("<Button-1>", callback_quit)

        self.new = tk.Label(backgr, bg="#5100ba", text="New", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.new.place(relx=0.15, rely=0.02, relwidth=0.7, relheight=0.02)

        self.logs = tk.Label(backgr, bg="#5100ba", text="Logs", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.logs.place(relx=0.15, rely=0.90, relwidth=0.7, relheight=0.02)

        self.settings = tk.Label(backgr, bg="#5100ba", text="Settings", font=("Helvetica", 12), foreground="white", relief="ridge")
        self.settings.place(relx=0.15, rely=0.95, relwidth=0.7, relheight=0.02)


        #timer object
        self.loop = tk.Label(parent)
        self.loop.place(x=0,y=0,width=0,height=0)
        # start the timer
        self.loop.after(100, self.timer)

    def timer(self):
        # callback_show_hide_ui("<Button-1>")
        # request tkinter to call self.timer after 1s (the delay is given in ms)
        self.loop.after(100, self.timer)

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(background="yellow")
    root.wm_attributes("-topmost", 1)
    root.wm_attributes("-transparentcolor", "yellow")
    root.attributes("-alpha", 0.9)
    root.overrideredirect(True) # removes title bar
    root.geometry("200x%i+%i+0" % (scr_height, master_x)) #WidthxHeight and x+y of main window
    UI(root).pack(fill="both", expand=True)
    root.mainloop()
