import os
from typing import Iterable, Callable
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pypdf import PaperSize

from app.__main__ import compose_stickers, UnporcessableArgumentsError


PAPER_SIZES = [s for s in dir(PaperSize) if not s.startswith('__')]


def browse_files() -> Iterable[Path]:
    return tk.filedialog.askopenfilenames(
        defaultextension='.pdf',
        filetypes=[('PDF', ('*.pdf', '*.PDF')), ]
    )


def browse_directory() -> Iterable[Path]:
    dir_name = tk.filedialog.askdirectory()
    return [Path(dir_name) / f for f in os.listdir(dir_name) if f.endswith(('.pdf', '.PDF', ))] \
        if dir_name \
        else []


class StickersUI:
    def __init__(self, browse_functions: list[Callable[[], Iterable[Path]]]):
        self.root = tk.Tk()
        self.root.title('Sticker stacker')
        self.root.minsize(width=500, height=300)
        self.root.eval('tk::PlaceWindow . center')

        # State variables
        self.paper_size = tk.StringVar()
        self.stickers_in_width = tk.IntVar()
        self.stickers_in_height = tk.IntVar()
        self._browse_mode = tk.IntVar()
        self._file_list = []
        self.browse_functions = browse_functions

        self.stickers_in_width.set(2)
        self.stickers_in_height.set(3)

        # Frames:
        self.frm_radios = tk.Frame(master=self.root, pady=5)
        self.frm_buttons = tk.Frame(master=self.root, padx=10, pady=5)
        self.frm_file_list = tk.Frame(master=self.root, height=100, padx=10, pady=5, bd=1, relief=tk.SUNKEN)

        self.frm_layout = tk.Frame(master=self.root, padx=10, pady=10)
        self.frm_grid = tk.Frame(master=self.frm_layout)
        self.frm_paper_size = tk.Frame(master=self.frm_layout)

        self.frm_layout.pack(fill=tk.X)
        self.frm_radios.pack(fill=tk.X)
        self.frm_buttons.pack(fill=tk.X)
        self.frm_file_list.pack(fill=tk.BOTH, expand=True)

        self.frm_grid.pack(side=tk.LEFT)
        self.frm_paper_size.pack(side=tk.RIGHT, fill=tk.BOTH, pady=2)

        # Layout parameters:
        self.cbx_paper_size = ttk.Combobox(master=self.frm_paper_size,
                                           values=PAPER_SIZES,
                                           width=5,
                                           textvariable=self.paper_size,)
        self.cbx_paper_size.current(PAPER_SIZES.index('A4'))

        self.sbx_stickers_in_width = tk.Spinbox(master=self.frm_grid, from_=1, to=40, width=2,
                                                textvariable=self.stickers_in_width)
        self.sbx_stickers_in_heigth = tk.Spinbox(master=self.frm_grid, from_=1, to=40, width=2,
                                                 textvariable=self.stickers_in_height)

        self.sbx_stickers_in_width.grid(column=0, row=0)
        tk.Label(master=self.frm_grid, text='stickers across the page').grid(column=1, row=0, sticky='w', padx=3)
        self.sbx_stickers_in_heigth.grid(column=0, row=1)
        tk.Label(master=self.frm_grid, text='stickers down the page').grid(column=1, row=1, sticky='w', padx=3)

        tk.Label(master=self.frm_paper_size, text='Pape size:').grid(column=0, row=0, padx=3)
        self.cbx_paper_size.grid(column=1, row=0)

        # Radios:
        self.rbtn1 = tk.Radiobutton(master=self.frm_radios,
                                    variable=self._browse_mode,
                                    value=0,
                                    text='Select directory')
        self.rbtn2 = tk.Radiobutton(master=self.frm_radios,
                                    variable=self._browse_mode,
                                    value=1,
                                    text='Select individual files')
        self.rbtn1.grid(column=0, row=0, sticky='nw')
        self.rbtn2.grid(column=0, row=1, sticky='nw')

        # Buttons
        self.btn_browse = tk.Button(master=self.frm_buttons, text='Browse', command=self.browse)
        self.btn_clear = tk.Button(master=self.frm_buttons, text='Clear', command=self.clear, state=tk.DISABLED)
        self.btn_save = tk.Button(master=self.frm_buttons, text='Save', command=self.save, state=tk.DISABLED)
        self.btn_browse.pack(side=tk.LEFT)
        self.btn_clear.pack(side=tk.LEFT, padx=4)
        self.btn_save.pack(side=tk.RIGHT)

        # Run mainloop
        self.root.mainloop()

    @property
    def browse_mode(self) -> int:
        return self._browse_mode.get()

    @property
    def file_list(self) -> list[Path]:
        return self._file_list

    @file_list.setter
    def file_list(self, value):
        self._file_list = value
        for w in self.frm_file_list.winfo_children():
            w.destroy()
        if self._file_list:
            self.btn_clear.config(state=tk.ACTIVE)
            self.btn_save.config(state=tk.ACTIVE)
            for i, f in enumerate(self._file_list):
                tk.Label(master=self.frm_file_list, text=str(f.resolve())).grid(column=0, row=i, sticky='nw')
        else:
            self.btn_clear.config(state=tk.DISABLED)
            self.btn_save.config(state=tk.DISABLED)

    def browse(self):
        chosen_files = self.browse_functions[self.browse_mode]()
        self.file_list += [Path(f) for f in chosen_files]

    def clear(self):
        self.file_list = []

    def save(self):
        file_to_save = tk.filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF', ('*.pdf', '*.PDF')), ]
        )
        if file_to_save:
            kwargs = {
                'stickers_in_width': self.stickers_in_width.get(),
                'stickers_in_height': self.stickers_in_height.get(),
                'paper_format': self.paper_size.get(),
            }
            try:
                compose_stickers(self.file_list, file_to_save, **kwargs)
            except UnporcessableArgumentsError as e:
                messagebox.showerror(message=str(e))
