from collections import namedtuple

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
    def resolution(self):
        return self.config.get(Config.KEY_RESOLUTION, default=0)

    @resolution.setter
    def resolution(self, value):
        self.config.set(Config.KEY_RESOLUTION, value)

    @property
    def save_config_in_folder(self):
        return self.config.get(Config.KEY_SAVE_CONFIG_IN_FOLDER, default=True)

    @save_config_in_folder.setter
    def save_config_in_folder(self, value):
        self.config.set(Config.KEY_SAVE_CONFIG_IN_FOLDER, value)

    @property
    def trash(self):
        return self.config.get(Config.KEY_TRASH, default=False)

    @trash.setter
    def trash(self, value):
        self.config.set(Config.KEY_TRASH, value)


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.config = Config()
        self.path = StringVar(value=self.config.path)
        resolution = POSSIBLE_RESOLUTIONS[int(self.config.resolution)]
        self.resolution = StringVar(value=str(resolution))
        self.trash_resized = BooleanVar(value=self.config.trash)
        self.save_config_in_folder = BooleanVar(value=self.config.save_config_in_folder)

        self.pack(fill=X, expand=1)
        self.create_widgets()
        self.grid(sticky=NSEW)
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

    def create_widgets(self):
        current_row = 0
        Label(self, text='Folder:').grid(row=current_row, column=0, sticky=E)
        Entry(self, textvariable=self.path).grid(row=current_row, column=1, sticky=EW)
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

    def change_folder(self):
        path = askdirectory(initialdir=self.path)
        if path:
            self.config.path = path
            self.config.save()
            self.path.set(path)

    def run(self):
        self.config.path = self.path.get()
        self.config.trash = self.trash_resized.get()
        self.config.save_config_in_folder = self.save_config_in_folder.get()
        self.config.resolution_index = self.resolutions.current()
        self.config.save()
        self.log.config(state="normal")
        self.log.delete(1.0, END)
        try:
            sys.stdout = self
            sys.stderr = self
            tapetovac = Tapetovac(trash_after_resize=self.trash_resized.get())
            resolution = POSSIBLE_RESOLUTIONS[self.resolutions.current()]
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
            self.log.config(state="disabled")
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

    # For stdout/stderr redirection
    def write(self, msg):
        self.log.config(state="normal")
        self.log.insert(END, msg)
        self.log.see(END)
        self.log.config(state="disabled")
        self.update_idletasks()


root = Tk()
app = Application(master=root)
root.title('Tapetovač -- background resizer')
app.mainloop()
