import pathlib

from emulator import Emulator
from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal


class EmulatorWorker(QThread):
    error = pyqtSignal(Exception)
    memory_changed = pyqtSignal(list)

    def __init__(
        self, parent: QObject, rom_path: pathlib.Path, freq: int = 1000
    ) -> None:
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.send_memory_content)

        self.rom_path = rom_path
        self.frequency = freq  # in ms
        self.emulator = Emulator()

    def stop_running(self) -> None:
        self.timer.stop()
        self.emulator.stop()
        self.terminate()
        self.wait()

    def run(self) -> None:
        self.timer.start(self.frequency)

        try:
            self.emulator.run(self.rom_path)
        except Exception as e:
            self.error.emit(e)

    def send_memory_content(self):
        self.memory_changed.emit(self.emulator.memory)
