import pandas as pd
from glob import glob
import os
import tkinter
import csv
import tkinter as tk
from tkinter import *
from tkinter import ttk

def subjectchoose(text_to_speech):
    def load_dates():
        Subject = tx.get().strip()
        if Subject == "":
            text_to_speech("Please enter the subject name.")
            return

        path = f"Attendance\\{Subject}\\{Subject}*.csv"
        files = glob(path)

        if not files:
            text_to_speech(f"No attendance records found for {Subject}.")
            return

        dates.clear()
        for f in files:
            basename = os.path.basename(f)
            parts = basename.split("_")
            if len(parts) >= 2:
                date_part = parts[1]
                dates.append((date_part, f))  # (display date, full path)

        date_combobox['values'] = [d[0] for d in dates]
        if dates:
            date_combobox.current(0)

    def show_attendance():
        if not dates:
            text_to_speech("No date selected or no attendance records found.")
            return

        idx = date_combobox.current()
        if idx == -1:
            text_to_speech("Please select a date.")
            return

        csv_file = dates[idx][1]
        if not os.path.exists(csv_file):
            text_to_speech("Selected attendance file does not exist.")
            return

        root = tkinter.Tk()
        root.title("Attendance")
        root.configure(background="black")

        with open(csv_file) as file:
            reader = csv.reader(file)
            for r, col in enumerate(reader):
                for c, row in enumerate(col):
                    label = tkinter.Label(
                        root,
                        width=10,
                        height=1,
                        fg="yellow",
                        font=("times", 15, " bold "),
                        bg="black",
                        text=row,
                        relief=tkinter.RIDGE,
                    )
                    label.grid(row=r, column=c)
        root.mainloop()

    # GUI setup
    subject = Tk()
    subject.title("Select Subject & Date")
    subject.geometry("600x400")
    subject.configure(background="black")

    tk.Label(subject, text="Subject Attendance Viewer", bg="black", fg="green", font=("arial", 25)).pack(pady=10)

    # Subject Entry
    tk.Label(subject, text="Enter Subject", bg="black", fg="yellow", font=("times new roman", 15)).place(x=50, y=80)
    tx = tk.Entry(subject, width=15, bd=5, bg="black", fg="yellow", font=("times", 20, "bold"))
    tx.place(x=220, y=80)

    # Load Dates Button
    load_btn = tk.Button(subject, text="Load Dates", command=load_dates, bd=7, font=("times new roman", 15),
                         bg="black", fg="yellow", width=12)
    load_btn.place(x=420, y=75)

    # Date Selector
    tk.Label(subject, text="Select Date", bg="black", fg="yellow", font=("times new roman", 15)).place(x=50, y=150)
    date_combobox = ttk.Combobox(subject, state="readonly", font=("times", 15))
    date_combobox.place(x=220, y=150)

    # View Attendance Button
    view_btn = tk.Button(subject, text="View Attendance", command=show_attendance, bd=7, font=("times new roman", 15),
                         bg="black", fg="yellow", width=15)
    view_btn.place(x=220, y=220)

    # List to store dates and file paths
    dates = []

    subject.mainloop()
