from tkinter import *
from tkinter.filedialog import askdirectory
from tkinter.scrolledtext import ScrolledText

import moltools3

from tapetovac import resize_all_images


class Application(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.config = moltools3.load_or_create_app_config("tapetovac")
        self.path = StringVar(value=self.config.get("path"))
        self.trash_resized = BooleanVar(value=self.config.get("trash", default=False))

        self.pack(fill=X, expand=1)
        self.create_widgets()

    def create_widgets(self):
        Label(self, text='Folder:').pack(fill=X,expand=0)
        Entry(self, textvariable=self.path).pack(fill=BOTH, expand=1)
        Button(self, text="Change folder", command=self.change_folder).pack(fill=BOTH, expand=1)

        Checkbutton(self, text="Move files to trash after resizing", variable=self.trash_resized).pack(fill=BOTH, expand=1)

        Button(self, text="Run", command=self.run).pack(fill=BOTH, expand=1)

        quit_button = Button(self)
        quit_button["text"] = "QUIT"
        quit_button["fg"]   = "red"
        quit_button["command"] = self.winfo_toplevel().destroy
        quit_button.pack(fill=BOTH, expand=1)

        self.log = ScrolledText(self)
        self.log.pack(fill=BOTH, expand=1)

    def change_folder(self):
        path = askdirectory(initialdir=self.path)
        if path:
            self.config.set_and_save("path", path)
            self.path.set(path)

    def run(self):
        self.config.set_and_save("path", self.path.get())
        self.config.set_and_save("trash", self.trash_resized.get())
        # if self.log.get():
        self.log.config(state="normal")
        self.log.delete(1.0, END)
        try:
            sys.stdout = self
            sys.stderr = self
            resize_all_images(path=self.path.get(), trash=self.trash_resized.get())
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
