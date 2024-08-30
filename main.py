import tkinter as tk
from tkinter import filedialog

from emulator import Emulator


root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename()
emulator = Emulator()
emulator.run(filename=file_path)
