# import tkinter
try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

class Timer:
    def __init__(self, parent):
        self.button = tk.Button(root, text="On/Off", command=self.state).pack()
        # variable storing time
        self.seconds = 0
        # label displaying time
        self.label = tk.Label(parent, text="0 s", font="Arial 30", width=10)
        self.label.pack()
        # start the timer
        self.label.after(1000, self.refresh_label)

    def refresh_label(self):
        #refresh the content of the label every second
        # increment the time
        if self.loop_state == 0:
            self.seconds += 1

        # display the new time
        self.label.configure(text="%i s" % self.seconds)
        # request tkinter to call self.refresh after 1s (the delay is given in ms)
        self.label.after(1000, self.refresh_label)



    loop_state = 0 # 1 on/off 0
    def state(self):
        # variable storing the on/off state
        global loop_state
        # switcher
        if self.loop_state == 0:
            self.loop_state = 1
        elif self.loop_state == 1:
            self.loop_state = 0
        print(self.loop_state)




if __name__ == "__main__":
    root = tk.Tk()
    timer = Timer(root)
    root.mainloop()