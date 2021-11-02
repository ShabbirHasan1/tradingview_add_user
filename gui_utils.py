import tkinter as tk
from tkinter import simpledialog


def get_row_to_begin():
    window = tk.Tk()
    window.withdraw()
    start_raw = simpledialog.askstring(title="GoogleSheet", prompt="Start row:")
    if start_raw is None or start_raw == '':
        sys.exit(3)
    return start_raw
