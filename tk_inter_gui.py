import tkinter as tk
import sqlite3
from tkinter import messagebox
from tkcalendar import DateEntry
import tkinter.font as tkfont
from tkinter import ttk
from tkinter import Label
import os
import subprocess


# Constants for pagination
RESULTS_PER_PAGE = 15

# Variable to keep track of the current page number
current_page = 0
total_pages = 0
variable_name = []


def calculate_total_pages():
    global total_pages, variable_name

    total_records = len(variable_name)
    total_pages = (total_records - 1) // RESULTS_PER_PAGE + 1

def searchByID():
    global variable_name
    _id = z.get()
    z.set("")
    selected = drop.get()
    # Clear the existing records
    clearRecords()

    connection = sqlite3.connect('logs.db')
    cur = connection.cursor()
    if selected == "Choose ID Type...":
        if _id == '' :
            cur.execute("SELECT path , added FROM logs ")
            variable_name = cur.fetchall()
        else:
            messagebox.showinfo("Επιλέξτε Τύπο ID", "Επιλέξτε τύπο ΙD")
    if selected == "Bank ID":
        if _id == '':
            cur.execute("SELECT path , added FROM logs ")
            variable_name = cur.fetchall()
        else:
            cur.execute("SELECT path , added FROM logs WHERE bank_id = ?", (_id,))
            variable_name = cur.fetchall()
    if selected == "Terminal ID":
        if _id == '':
            cur.execute("SELECT path , added FROM logs ")
            variable_name = cur.fetchall()
        else:
            cur.execute("SELECT path , added FROM logs WHERE tid = ?", (_id,))
            variable_name = cur.fetchall()

    connection.close()

    if not variable_name:
        messagebox.showinfo("Search Results", "Δεν βρέθηκαν στοιχεία")
    else:
        displayRecords(variable_name)
        calculate_total_pages()

def searchByDate():
    global variable_name
    selected_date = date_entry.get_date()
    formatted_date = selected_date.strftime("%d/%m/%Y")

    # Clear the existing records
    clearRecords()

    connection = sqlite3.connect('logs.db')
    cur = connection.cursor()
    cur.execute("SELECT path , added FROM logs WHERE date = ?", (formatted_date,))
    variable_name = cur.fetchall()
    connection.close()

    if not variable_name:
        messagebox.showinfo("Search Results", "Δεν βρέθηκαν στοιχεία")
    else:
        displayRecords(variable_name)
        calculate_total_pages()

def clearRecords():
    for widget in frame_2.winfo_children():
        widget.destroy()


def displayRecords(records):
    # Clear previous records
    clearRecords()

    global current_page, total_pages

    start_index = current_page * RESULTS_PER_PAGE
    end_index = (current_page + 1) * RESULTS_PER_PAGE

    for i, record in enumerate(records[start_index:end_index], start=start_index):
        if os.path.exists(record[0]):  # ελέγχει πρώτα αν το path υπάρχει ακόμα στον υπολογιστή
            path, added = record
            Label(frame_2, text=f"added: {added}", font=custom_font, background="lightgray",\
                                    fg="blue").grid(row=i, column=1)
            Label(frame_2, text="EXIST", font=custom_font, fg="green").grid(row=i, column=2)
            label_path = ttk.Label(frame_2, text=f"Path: {path}  ", font=custom_font, background="lightgray", \
                                   foreground="blue", cursor="hand2")
            label_path.grid(row=i, column=0)
            label_path.bind("<Button-1>", lambda e, p=path: open_path(p))
            label_path.bind("<Enter>", lambda e, label=label_path: label.config(background="lightblue"))
            label_path.bind("<Leave>", lambda e, l=label_path: l.config(background="lightgray"))
        else:
            path, added = record
            Label(frame_2, text=f"Path: {path}  ", font=custom_font, bg="yellow", fg="blue").grid(row=i, column=0)
            Label(frame_2, text=f"added: {added}", font=custom_font, bg="yellow", fg="green").grid(row=i, column=1)
            Label(frame_2, text="DOES NOT EXIST", font=custom_font, bg='yellow', fg="red").grid(row=i, column=2)

        # Add "Previous" , "* of *" and "Next" buttons for pagination
        prev_btn = tk.Button(frame_2, text="Previous", command=show_previous_page)
        prev_btn.grid(row=end_index, column=0, sticky=tk.W)

        next_btn = tk.Button(frame_2, text="Next", command=show_next_page)
        next_btn.grid(row=end_index, column=1)

        message_label = ttk.Label(frame_2, text=f"page {current_page+1} of {total_pages}",font=("Arial", 12))
        message_label.grid(row=end_index + 1, column=0, columnspan=3)

def show_previous_page():
        global current_page, variable_name
        if current_page > 0:
            current_page -= 1
            displayRecords(variable_name)

def show_next_page():
        global current_page, variable_name

        if total_pages - current_page >1 :
            current_page += 1
            displayRecords(variable_name)

def open_path(path):
    subprocess.Popen(f'explorer /select,"{path}"')


root = tk.Tk()
root.title("Search database by ID or Date")
custom_font = tkfont.Font(size=16)

z = tk.StringVar()
frame_1 = tk.Frame(root)
frame_1.pack()
frame_2 = tk.Frame(root)
frame_2.config(highlightbackground="lightblue", highlightthickness=6)
frame_2.pack()


# Label for ID search
tk.Label(frame_1, font=custom_font, text="ID:").grid(row=0, column=0)

# Textbox for ID search
bankSearchEntry = tk.Entry(frame_1, font=custom_font, textvariable=z)
bankSearchEntry.grid(row=0, column=1)

# Dropbox to choose Bank.id or T.id
drop = ttk.Combobox(frame_1, values=["Bank ID", "Terminal ID"])
drop.grid(row=0, column=2)
drop.set("Choose ID Type...")

# Button for Bank ID search
bankSearchButton = tk.Button(frame_1, text="Search ", command=searchByID)
bankSearchButton.grid(row=0, column=3)

# Label for Date search
tk.Label(frame_1, font=custom_font, text="Date:").grid(row=1, column=0)

# DateEntry for Date search
date_entry = DateEntry(frame_1, date_pattern="dd/mm/yyyy")
date_entry.grid(row=1, column=1)

# Button for Date search
dateSearchButton = tk.Button(frame_1, text="Search", command=searchByDate)
dateSearchButton.grid(row=1, column=2)


root.mainloop()
