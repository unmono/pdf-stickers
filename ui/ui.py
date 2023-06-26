import os
from typing import Iterable
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog

from app.__main__ import compose_stickers

root = tk.Tk()
root.title("NP stickers")

# Variables:
file_list: list[Path] = []
cvar_radios = tk.IntVar()

# Frames:
frm_radios = tk.Frame(
    master=root,
    width=500,
    pady=5,
)
frm_buttons = tk.Frame(
    master=root,
    width=500,
    padx=10,
    pady=5,
)
frm_file_list = tk.Frame(
    master=root,
    width=500,
    height=100,
    padx=10,
    pady=5,
    bd=1,
    relief=tk.SUNKEN,
)

frm_radios.pack(fill=tk.X)
frm_buttons.pack(fill=tk.X)
frm_file_list.pack(fill=tk.BOTH, expand=True)


# Radios:
rbtn1 = tk.Radiobutton(
    master=frm_radios,
    variable=cvar_radios,
    value=0,
    text='Select directory',
)
rbtn2 = tk.Radiobutton(
    master=frm_radios,
    variable=cvar_radios,
    value=1,
    text='Select individual files',
)
rbtn1.grid(column=0, row=0, sticky='nw')
rbtn2.grid(column=0, row=1, sticky='nw')


def browse_files() -> Iterable:
    return tk.filedialog.askopenfilenames(
        defaultextension='.pdf',
        filetypes=[('PDF', ('*.pdf', '*.PDF')), ]
    )


def browse_directory() -> Iterable:
    dir_name = tk.filedialog.askdirectory()
    return [Path(dir_name) / f for f in os.listdir(dir_name) if f.endswith(('.pdf', '.PDF', ))] \
        if dir_name \
        else []


browse_functions = [
    browse_directory,
    browse_files,
]


def list_files(fl: list[Path]):
    for w in frm_file_list.winfo_children():
        w.destroy()

    for i, f in enumerate(fl):
        tk.Label(
            master=frm_file_list,
            text=str(f.resolve()),
        ).grid(column=0, row=i, sticky='nw')


def browse():
    global file_list

    browsing_mode = cvar_radios.get()
    chosen_files = browse_functions[browsing_mode]()

    file_list += [Path(f) for f in chosen_files]

    if file_list:
        list_files(file_list)


def clear():
    global file_list

    file_list = []
    list_files(file_list)


def save():
    global file_list

    file_to_save = tk.filedialog.asksaveasfilename(
        defaultextension='.pdf',
        filetypes=[('PDF', ('*.pdf', '*.PDF')), ]
    )
    compose_stickers(file_list, file_to_save)


btn_browse = tk.Button(
    master=frm_buttons,
    text='Browse',
    command=browse,
)
btn_clear = tk.Button(
    master=frm_buttons,
    text='Clear',
    command=clear,
)
btn_save = tk.Button(
    master=frm_buttons,
    text='Save',
    command=save,
)

btn_browse.pack(side=tk.LEFT)
btn_clear.pack(side=tk.LEFT, padx=4)
btn_save.pack(side=tk.RIGHT)

root.mainloop()
