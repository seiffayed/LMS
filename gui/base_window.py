import tkinter as tk

class BaseWindow:
    def center_window(self, win, w, h):
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        win.geometry(f"{w}x{h}+{(sw//2)-(w//2)}+{(sh//2)-(h//2)}")

    def maximize_window(self, win):
        try:
            win.state('zoomed') # Windows
        except:
             # Linux/Mac fallback
            w, h = win.winfo_screenwidth(), win.winfo_screenheight()
            win.geometry(f"{w}x{h}+0+0")
