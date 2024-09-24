import sys

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

# TODO: add documentation
# TODO: fix audio and delay timer
# TODO: fix program slowing down after i run multiple
# games without fully exiting the program 
# (probably not closing some resources properly in the new widgets)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
