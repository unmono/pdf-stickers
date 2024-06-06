import os
import tkinter
from typing import Iterable
from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pypdf import PaperSize

from app.main import compose_stickers, UnprocessableArgumentsError

PAPER_SIZES = [s for s in dir(PaperSize) if not s.startswith('__')]


class StickersUI:
    def __init__(self, keeper):
        self.root = tk.Tk()
        self.root.title('Sticker stacker')
        self.root.minsize(width=600, height=300)
        self.root.eval('tk::PlaceWindow . center')

        # State variables:
        self.paper_size = tk.StringVar(value='A4')
        self.stickers_in_width = tk.IntVar(value=2)
        self.stickers_in_height = tk.IntVar(value=3)
        self.browse_mode = tk.IntVar()
        self.keep_ratio = tk.BooleanVar(value=True)
        self.sticker_margin = tk.IntVar(value=0)
        # This list needed to pick right function based on browse_mode state.
        # Values of radio buttons correspond to indexes in this list.
        self.browse_functions = [self.browse_directory, self.browse_files]
        self.initial_browse_dir = Path()
        self.initial_browse_files_dir = Path()
        self.initial_save_dir = Path()
        self._file_list = []

        # Frames:
        # Main frames
        self.frm_radios = tk.Frame(master=self.root, padx=1, pady=5)
        self.frm_buttons = tk.Frame(master=self.root, padx=10, pady=5)
        self.frm_file_list = tk.Frame(master=self.root, height=100, padx=10, pady=5, bd=1, relief=tk.SUNKEN)
        # Frames of layout settings
        self.frm_layout = tk.Frame(master=self.root, padx=10, pady=10)
        self.frm_grid = tk.Frame(master=self.frm_layout)
        self.frm_paper_size = tk.Frame(master=self.frm_layout)
        # Options frames
        self.frm_options = tk.Frame(master=self.root, padx=10, pady=10)

        self.frm_layout.pack(fill=tk.X)
        self.frm_options.pack(fill=tk.X)
        self.frm_radios.pack(fill=tk.X)
        self.frm_buttons.pack(fill=tk.X)
        self.frm_file_list.pack(fill=tk.BOTH, expand=True)
        self.frm_grid.pack(side=tk.LEFT)
        self.frm_paper_size.pack(side=tk.RIGHT, fill=tk.BOTH, pady=2)

        # Layout parameters:
        self.cbx_paper_size = ttk.Combobox(master=self.frm_paper_size,
                                           values=PAPER_SIZES,
                                           width=5,
                                           textvariable=self.paper_size, )
        self.sbx_stickers_in_width = tk.Spinbox(master=self.frm_grid, from_=1, to=40, width=2,
                                                textvariable=self.stickers_in_width)
        self.sbx_stickers_in_height = tk.Spinbox(master=self.frm_grid, from_=1, to=40, width=2,
                                                 textvariable=self.stickers_in_height)

        self.sbx_stickers_in_width.grid(column=0, row=0)
        tk.Label(master=self.frm_grid, text='stickers across the page').grid(column=1, row=0, sticky='w', padx=3)

        self.sbx_stickers_in_height.grid(column=0, row=1)
        tk.Label(master=self.frm_grid, text='stickers down the page').grid(column=1, row=1, sticky='w', padx=3)

        self.cbx_paper_size.grid(column=1, row=0)
        tk.Label(master=self.frm_paper_size, text='Pape size:').grid(column=0, row=0, padx=3)

        # Additional options
        self.cbt_keep_ratio = tk.Checkbutton(master=self.frm_options, text='Rotate to keep original ratio',
                                             variable=self.keep_ratio)
        self.sbx_sticker_margin = tk.Spinbox(master=self.frm_options, from_=-100, to=100, width=5,
                                             textvariable=self.sticker_margin)

        self.cbt_keep_ratio.pack(side=tk.LEFT)
        self.sbx_sticker_margin.pack(side=tk.RIGHT)
        tk.Label(master=self.frm_options, text='Margins around the stickers in mm:').pack(side=tk.RIGHT, padx=2)

        # Radios:
        self.rbn_browse_dir = tk.Radiobutton(master=self.frm_radios,
                                             variable=self.browse_mode,
                                             value=0,
                                             text='Select directory')
        self.rbn_browse_files = tk.Radiobutton(master=self.frm_radios,
                                               variable=self.browse_mode,
                                               value=1,
                                               text='Select individual files')
        self.rbn_browse_dir.grid(column=0, row=0, sticky='nw')
        self.rbn_browse_files.grid(column=0, row=1, sticky='nw')

        # Buttons
        self.btn_browse = tk.Button(master=self.frm_buttons, text='Browse', command=self.browse)
        self.btn_clear = tk.Button(master=self.frm_buttons, text='Clear', command=self.clear, state=tk.DISABLED)
        self.btn_save = tk.Button(master=self.frm_buttons, text='Save', command=self.save, state=tk.DISABLED)
        self.btn_browse.pack(side=tk.LEFT)
        self.btn_clear.pack(side=tk.LEFT, padx=4)
        self.btn_save.pack(side=tk.RIGHT)

        # Set preferences to keep between runs
        # Pass attribute names to method
        if keeper:
            self.keeper = keeper(
                obj=self,
                attrs=(
                    'paper_size',
                    'stickers_in_width',
                    'stickers_in_height',
                    'browse_mode',
                    'keep_ratio',
                    'sticker_margin',
                    'initial_browse_dir',
                    'initial_browse_files_dir',
                    'initial_save_dir',
                ),
            )
            keeper.converters[tk.Variable] = lambda v: v.get()
            keeper.setters[tk.Variable] = lambda obj, n, v: getattr(obj, n).set(v)
        else:
            self.keeper = None

    @property
    def file_list(self) -> list[Path]:
        return self._file_list

    @file_list.setter
    def file_list(self, value) -> None:
        """
        Whenever file_list is setted, this function re-renders the list of selected files in the window
        and manages the state of the buttons accordingly
        :param value: new list to set
        """
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

    def browse_files(self) -> Iterable[Path]:
        """
        Get list of files from file dialog window.
        :return: list of Paht objects of these files
        """
        files = tk.filedialog.askopenfilenames(
            defaultextension='.pdf',
            filetypes=[('PDF', ('*.pdf', '*.PDF')), ],
            initialdir=self.initial_browse_files_dir
        )
        if not files:
            return []
        paths = [Path(f) for f in files]
        self.initial_browse_files_dir = paths[-1].parent
        return paths

    def browse_directory(self) -> Iterable[Path]:
        """
        Get a list of .pdf files contained in a directory selected with directory dialog window
        :return: list of Paht objects of these files
        """
        dir_name = tk.filedialog.askdirectory(initialdir=self.initial_browse_dir)
        if not dir_name:
            return []
        self.initial_browse_dir = Path(dir_name)
        return [self.initial_browse_dir / f for f in os.listdir(dir_name) if f.endswith(('.pdf', '.PDF',))]

    def browse(self) -> None:
        """
        Append a list of files received from the browse function picked based on browse_mode state
        """
        self.file_list += self.browse_functions[self.browse_mode.get()]()

    def clear(self) -> None:
        self.file_list = []

    def save(self) -> None:
        file_to_save = tk.filedialog.asksaveasfilename(
            defaultextension='.pdf',
            filetypes=[('PDF', ('*.pdf', '*.PDF')), ],
            initialdir=self.initial_save_dir,
        )
        if file_to_save:
            path_to_save = Path(file_to_save)
            # Keep chosen directory to save it in preferences
            self.initial_save_dir = path_to_save.parent
            kwargs = {
                'stickers_in_width': self.stickers_in_width.get(),
                'stickers_in_height': self.stickers_in_height.get(),
                'paper_format': self.paper_size.get(),
                'sticker_margin': self.sticker_margin.get(),
                'keep_ratio': self.keep_ratio.get(),
            }
            try:
                compose_stickers(self.file_list, path_to_save, **kwargs)
            except UnprocessableArgumentsError as e:
                messagebox.showerror(message=str(e))
            # Save used preferences
            if self.keeper:
                self.keeper.save()

    def run(self) -> None:
        """
        Start method. Runs UI and sets saved preferences if they exist
        """
        if self.keeper:
            self.keeper.setup()
        self.root.mainloop()
