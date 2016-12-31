from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText

import moltools3

from tapetovac import Tapetovac


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.config = moltools3.load_or_create_app_config("tapetovac")
        self.path = StringVar(value=self.config.get("path"))
        self.trash_resized = BooleanVar(value=self.config.get("trash", default=False))

        self.pack(fill=X, expand=1)
        self.create_widgets()
        self.grid(sticky=NSEW)
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

    def create_widgets(self):
        Label(self, text='Folder:').grid(row=0, column=0, sticky=E)
        Entry(self, textvariable=self.path).grid(row=0, column=1, sticky=EW)
        Button(self, text="Change folder", command=self.change_folder).grid(row=0, column=2, sticky=W)

        Checkbutton(self, text="Move files to trash after resizing", variable=self.trash_resized).grid(row=1, columnspan=3, sticky=EW)

        Button(self, text="Run", command=self.run).grid(row=2, column=1)

        self.log = ScrolledText(self)
        self.log.grid(row=3, columnspan=3, sticky=NSEW)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

    def change_folder(self):
        path = askdirectory(initialdir=self.path)
        if path:
            self.config.set_and_save("path", path)
            self.path.set(path)

    def run(self):
        self.config.set_and_save("path", self.path.get())
        self.config.set_and_save("trash", self.trash_resized.get())
        self.log.config(state="normal")
        self.log.delete(1.0, END)
        try:
            sys.stdout = self
            sys.stderr = self
            tapetovac = Tapetovac(trash_after_resize=self.trash_resized.get())
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
