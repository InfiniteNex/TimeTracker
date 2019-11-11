import win32api
import win32gui
import time
import psutil
import win32process
import getpass
import json
import datetime

export_iterator = 0
export_iterator_max = 20 # save automatically every 60 seconds/cycles
filename = datetime.datetime.now()
username = getpass.getuser()
classname = str()
i = 0      
dictionary = {
        "Idle": 0,
}
idle_time_max = 300.0 # 5 minutes max idle time
idle_state = "below 0" # 0 - below idle_time_max, 1 - above idle_time_max once, 2 - increment by seconds
#starttimer = time.time() # timer for the sceduled file export

def getIdleTime():
        global idle_state
        idle_time = (win32api.GetTickCount() - win32api.GetLastInputInfo()) / 1000.0
        print(idle_time)
        if idle_time >= idle_time_max:
                print("5 minutes passed")
                add_idle_max()
        else:
                idle_state = "below 0"


def add_idle_max():
        global idle_state
        if idle_state == "below 0":
                idle_state = "add max time"
                dictionary["Idle"] += idle_time_max
                dictionary[classname] -= 1
                idle_state = "add seconds"
        elif idle_state == "add seconds":
                dictionary["Idle"] += 1
                dictionary[classname] -= 1

def export():
        with open("export "+filename.strftime("%d %B %Y")+".txt", "w") as outputfile:
                json.dump(dictionary, outputfile)
                print("Exported data to file!")

def main_loop_counter():
        global classname
        global export_iterator
        while i == 0:
                time.sleep(1)                                                           # detect window every second
                w=win32gui
                w.GetWindowText (w.GetForegroundWindow())                               # get active window code
                pid = win32process.GetWindowThreadProcessId(w.GetForegroundWindow())    # get process name.exe
                classname = w.GetClassName (w.GetForegroundWindow())                    # get process class name
                print(username, classname, psutil.Process(pid[-1]).name())

                # add window class name to dictionary if missing and iterate its value by 1 second
                if not classname in dictionary:
                        dictionary[classname] = 1
                else:
                        dictionary[classname] += 1
                
                print(dictionary)
                getIdleTime()
                export_iterator += 1
                if export_iterator == export_iterator_max:
                        export()
                        export_iterator -= export_iterator_max


# Run main function===========================

main_loop_counter()