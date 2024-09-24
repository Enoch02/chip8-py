import email
import pathlib

from emulator import Emulator
from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal
from ui.registers_widget import RegisterData


class EmulatorWorker(QThread):
    error = pyqtSignal(Exception)
    memory_changed = pyqtSignal(list)
    register_changed = pyqtSignal(RegisterData)

    def __init__(
        self, parent: QObject, rom_path: pathlib.Path, freq: int = 1000
    ) -> None:
        super().__init__(parent)
        self.timer = QTimer(self)
        self
        self.timer.timeout.connect(self.send_memory_content)
        self.timer.timeout.connect(self.send_register_content)

        self.rom_path = rom_path
        self.frequency = freq  # in ms
        self.emulator = Emulator()

    def stop_running(self) -> None:
        self.timer.stop()
        self.emulator.stop()
        self.terminate()
        self.wait()

    def emu_running(self): return not self.emulator.pause_execution

    def pause_emu(self):
        self.emulator.pause_execution = True

    def resume_emu(self):
        self.emulator.pause_execution = False

    def run(self) -> None:
        self.timer.start(self.frequency)

        try:
            self.emulator.run(self.rom_path)
        except Exception as e:
            self.error.emit(e)

    def send_memory_content(self):
        self.memory_changed.emit(self.emulator.memory)

    #TODO: use a separate timer and maybe make the frequency configurable
    def send_register_content(self):
        data = RegisterData(
            pc=self.emulator.program_counter,
            i=self.emulator.index_register,
            dt=self.emulator.delay_timer,
            st=self.emulator.sound_timer,
            v=self.emulator.variable_register
        )

        self.register_changed.emit(data)
