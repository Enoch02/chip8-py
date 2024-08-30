import tkinter as tk
from tkinter import filedialog

from emulator import Emulator

# TODO: create proper interface with pyqt
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(filetypes=[("Chip8 ROMS", "*.ch8")])
emulator = Emulator(set_vx_to_vy=True)
emulator.run(filename=file_path)
