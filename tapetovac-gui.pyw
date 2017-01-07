from collections import namedtuple
from contextlib import contextmanager
from pathlib import Path

from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Combobox

import moltools3
from tapetovac import Tapetovac


class Resolution(namedtuple("Resolution", "width height bottom orientation")):

    def __str__(self):
        description = "{}×{} {}".format(self.width, self.height, self.orientation)
        if self.bottom:
            description += " with {} px bottom margin".format(self.bottom)
        return description


POSSIBLE_RESOLUTIONS = [
    Resolution(1920, 1200, 60, 'horizontal'),
    Resolution(1920, 1080, 0,  'vertical'),
]


class Config:
    KEY_PATH_HISTORY = "path_history"
    KEY_PATH = "path"
    KEY_RESOLUTION = "resolution_index"
    KEY_SAVE_CONFIG_IN_FOLDER = "save_config_in_folder"
    KEY_TRASH = "trash"

    def __init__(self):
        self.config = moltools3.load_or_create_app_config("tapetovac")

    def save(self):
        self.config.save()

    @property
    def path(self):
        return self.config.get(Config.KEY_PATH)

    @path.setter
    def path(self, value):
        self.config.set(Config.KEY_PATH, value)

    @property
    def path_history(self):
        return self.config.get_list(Config.KEY_PATH_HISTORY)

    @path_history.setter
    def path_history(self, value):
        self.config.set_list(Config.KEY_PATH_HISTORY, value)

    @property
    def resolution(self):
        return self.config.get_int(Config.KEY_RESOLUTION)

    @resolution.setter
    def resolution(self, value):
        self.config.set(Config.KEY_RESOLUTION, value)

    @property
    def save_config_in_folder(self):
        return self.config.get_bool(Config.KEY_SAVE_CONFIG_IN_FOLDER, default=True)

    @save_config_in_folder.setter
    def save_config_in_folder(self, value):
        self.config.set(Config.KEY_SAVE_CONFIG_IN_FOLDER, value)

    @property
    def trash(self):
        return self.config.get_bool(Config.KEY_TRASH, default=False)

    @trash.setter
    def trash(self, value):
        self.config.set(Config.KEY_TRASH, value)


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.config = Config()
        self.path = StringVar(value=self.config.path)
        self.path_history = self.config.path_history
        if not self.path_history:
            self.path_history = []
        resolution = POSSIBLE_RESOLUTIONS[int(self.config.resolution)]
        self.resolution = StringVar(value=str(resolution))
        self.trash_resized = BooleanVar(value=self.config.trash)
        self.save_config_in_folder = BooleanVar(value=self.config.save_config_in_folder)

        self.pack(fill=X, expand=1)
        self.create_widgets()
        self.grid(sticky=NSEW)
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        self.load_folder_config()

    def create_widgets(self):
        current_row = 0
        Label(self, text='Folder:').grid(row=current_row, column=0, sticky=E)
        self.path_combo = Combobox(self, textvariable=self.path)
        self.set_path_history()
        self.path_combo.grid(row=current_row, column=1, sticky=EW)
        self.path_combo.bind('<<ComboboxSelected>>', lambda _: self.load_folder_config())
        Button(self, text="Change folder", command=self.change_folder).grid(row=current_row, column=2, sticky=W)

        current_row += 1
        Label(self, text="Resolution").grid(row=current_row, column=0, sticky=E)
        self.resolutions = Combobox(self, textvariable=self.resolution)
        self.resolutions['values'] = [str(r) for r in POSSIBLE_RESOLUTIONS]
        self.resolutions.config(state="readonly")
        # self.resolutions.bind('<<ComboboxSelected>>', lambda _: self.resolutions.select_clear())
        self.resolutions.grid(row=current_row, column=1, sticky=EW)

        current_row += 1
        Checkbutton(self, text="Move files to trash after resizing", variable=self.trash_resized).grid(row=current_row, columnspan=3, sticky=EW)

        current_row += 1
        Button(self, text="Run", command=self.run).grid(row=current_row, column=1)

        current_row += 1
        Checkbutton(self, text="Save setting in the folder", variable=self.save_config_in_folder).grid(row=current_row, columnspan=3, sticky=EW)

        current_row += 1
        self.log = ScrolledText(self)
        self.log.grid(row=current_row, columnspan=3, sticky=NSEW)
        self.grid_rowconfigure(current_row, weight=1)

        self.grid_columnconfigure(1, weight=1)

    def set_path_history(self):
        self.path_history.sort()
        self.path_combo['values'] = self.path_history

    def change_folder(self):
        path = askdirectory(initialdir=self.path)
        if path:
            self.config.path = path
            self.config.save()
            self.path.set(path)
            for old_path in self.path_history:
                if path == old_path: break
            else:
                self.path_history.append(path)
                self.set_path_history()
            self.load_folder_config()

    def load_folder_config(self):
        folder_config_path = Path(self.path.get()) / "tapetovac.ini"
        if folder_config_path.exists():
            folder_config = moltools3.MolConfig(folder_config_path)
            width  = folder_config.get_int("width")
            height = folder_config.get_int("height")
            bottom = folder_config.get_int("bottom")
            self.trash_resized.set(folder_config.get_bool("trash"))
            for i, resolution in enumerate(POSSIBLE_RESOLUTIONS):
                if resolution.width  == width and resolution.height == height and resolution.bottom == bottom:
                    self.resolutions.current(i)
                    return

    def run(self):
        resolution = POSSIBLE_RESOLUTIONS[self.resolutions.current()]
        self.save_config(resolution)
        self.clear_log()
        try:
            sys.stdout = self
            sys.stderr = self
            tapetovac = Tapetovac(trash_after_resize=self.trash_resized.get())
            if resolution.orientation == "horizontal":
                width = resolution.width
                height = resolution.height
            else:
                height = resolution.width
                width = resolution.height
            tapetovac.final_width = width
            tapetovac.final_height = height
            tapetovac.image_net_height = height - resolution.bottom
            tapetovac.resize_all_images(path=self.path.get())
        finally:
            self.write("DONE\n")
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    def save_config(self, resolution):
        self.config.path = self.path.get()
        self.config.path_history = self.path_history
        self.config.trash = self.trash_resized.get()
        self.config.save_config_in_folder = self.save_config_in_folder.get()
        self.config.resolution_index = self.resolutions.current()
        self.config.save()
        if self.save_config_in_folder.get():
            folder_config_path = Path(self.path.get()) / "tapetovac.ini"
            if folder_config_path.exists():
                existing_folder_config = moltools3.MolConfig(folder_config_path)
                if      existing_folder_config.get_int("width")  == resolution.width  and \
                        existing_folder_config.get_int("height") == resolution.height and \
                        existing_folder_config.get_int("bottom") == resolution.bottom and \
                        existing_folder_config.get_bool("trash") == self.trash_resized.get():
                    return
            current_folder_config = moltools3.MolConfig(folder_config_path)
            current_folder_config.set("width",  resolution.width)
            current_folder_config.set("height", resolution.height)
            current_folder_config.set("bottom", resolution.bottom)
            current_folder_config.set("trash",  self.trash_resized.get())
            current_folder_config.save()


    def clear_log(self):
        with self.enable_log():
            self.log.delete(1.0, END)

    # For stdout/stderr redirection
    def write(self, msg):
        with self.enable_log():
            self.log.insert(END, msg)
            self.log.see(END)
        self.update_idletasks()

    @contextmanager
    def enable_log(self):
        self.log.config(state="normal")
        yield
        self.log.config(state="disabled")


root = Tk()
app = Application(master=root)
root.title('Tapetovač -- background resizer')
app.mainloop()
