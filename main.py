import sys
import tkinter as tk
from tkinter import filedialog

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

"""# TODO: create proper interface with pyqt
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(filetypes=[("Chip8 ROMS", "*.ch8")])
emulator = Emulator(set_vx_to_vy=True)
emulator.run(filename=file_path)"""

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
