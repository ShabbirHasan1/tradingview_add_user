import sys

import tkinter as tk
from tkinter import simpledialog


def get_row_to_begin():
    window = tk.Tk()
    window.withdraw()
    start_raw = simpledialog.askstring(title="GoogleSheet", prompt="Start row:")
    if start_raw is None or start_raw == '':
        sys.exit(3)
    return start_raw


def window_error():
    win = tk.Tk(className=' Error')
    win.geometry("700x100")
    tk.Label(win, text="The program got an error while connecting to trading view\nContact support", font=("Arial", 25)).pack()
    win.wait_window()


def show_conclusion(users_not_found, users_added_successfully, users_with_unexpected_error):
    win = tk.Tk(className=' Conclusion')
    win.geometry("700x600")

    if users_not_found:
        tk.Label(win, text="- Those users don't exist:", anchor='w', font=("Arial", 25)).pack(fill='both')
        users_str = ''
        for user in users_not_found:
            users_str += user + '\n'
        tk.Label(win, text=users_str, fg='red', font=("Arial", 17)).pack()
        tk.Label(win, text="You should check manually if those users exist", anchor='w', font=("Arial", 20)).pack(fill='both')

    if users_with_unexpected_error:
        tk.Label(win, text="\n\n- Those users got an unexpected error, need to check logs", anchor='w', font=("Arial", 25)).pack(fill='both')
        users_str = ''
        for user in users_with_unexpected_error:
            users_str += user + '\n'
        tk.Label(win, text=users_str, fg='red', font=("Arial", 17)).pack()

    if users_added_successfully:
        tk.Label(win, text="\n\n- Those users have been completely added successfully:", anchor='w', font=("Arial", 25)).pack(fill='both')
        users_str = ''
        for user in users_added_successfully:
            users_str += user + '\n'
        tk.Label(win, text=users_str, fg='green', font=("Arial", 17)).pack()
    win.wait_window()
