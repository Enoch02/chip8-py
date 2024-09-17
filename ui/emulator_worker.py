import pathlib
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from emulator import Emulator

class EmulatorWorker(QThread):
    error = pyqtSignal(Exception)

    def __init__(self, parent: QObject, rom_path: pathlib.Path) -> None:
        super().__init__(parent)
        self.rom_path = rom_path
        self.emulator = Emulator()

    def stop_running(self) -> None:
        self.emulator.stop()
        self.terminate()
        self.wait()

    def run(self) -> None:
        try:
            self.emulator.run(self.rom_path)
        except Exception as e:
            self.error.emit(e)
