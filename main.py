import sys

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

# TODO: add documentation
# TODO: fix audio and delay timer
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
