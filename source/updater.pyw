import requests, zipfile, io
import urllib
import tkinter as tk
import win32api
import win32gui
import win32process
from tkinter import messagebox as tkMessageBox
import os

scr_width = win32api.GetSystemMetrics(0) / 2.5
scr_height = win32api.GetSystemMetrics(1) / 2

website = "https://infinitenex.github.io/TimeTracker/"

# check website for latest version available
def version_check():
    global aaa
    link = urllib.request.urlopen(website).read()
    lnk = link.split()
    aa = str(lnk[115]).split("v")
    aaa = str(aa[1]).split("<")
    update()
    
    
#download the latest zip and unpack it
def update():
    r = requests.get("https://github.com/InfiniteNex/TimeTracker/releases/download/v%s/TimeTracker.zip" % (aaa[0]))
    z = zipfile.ZipFile(io.BytesIO(r.content))
    # z.extractall()
    z.extract("TimeTracker.exe")
    print("Finished")

    



#=====================================================

root = tk.Tk()
root.configure(background="yellow")
root.wm_attributes("-transparentcolor", "yellow")
root.overrideredirect(True) # removes title bar

version_check()

if tkMessageBox.showinfo(title="TimeTracker", message="TimeTracker has been updated to version %s" % (aaa[0])):
    os.startfile("TimeTracker.exe")
    raise SystemExit

root.mainloop()