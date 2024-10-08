import configparser
import pathlib
from typing import Dict

from ui.emulator_worker import EmulatorWorker
from PyQt6.QtCore import QFileInfo
from PyQt6.QtGui import QAction, QCloseEvent, QKeyEvent, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

ROMS_FOLDER_CONFIG_KEY = "current_rom_folder"
PREVIOUS_FILE_DIR_KEY = "prev_file_dir"


def exit_application():
    QApplication.quit()


# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.game_thread = None
        self.emulator = None
        self.list_widget = None
        self.main_layout = None
        self.central_widget = None
        self.config = configparser.ConfigParser()
        self.roms: Dict[str, pathlib.Path] = {}

        self.check_config()

        self.roms_folder = self.load_config(
            key=ROMS_FOLDER_CONFIG_KEY, default=str(pathlib.Path.cwd().absolute())
        )
        self.previous_dir = self.load_config(key=PREVIOUS_FILE_DIR_KEY, default="/")

        self.init_ui()

    def check_config(self):
        self.config.read("config.ini")
        if not self.config.has_section("Settings"):
            self.config.add_section("Settings")
            self.save_config(
                key=ROMS_FOLDER_CONFIG_KEY, value=str(pathlib.Path.cwd().absolute())
            )
            self.save_config(key=PREVIOUS_FILE_DIR_KEY, value="/")

    def load_config(self, key: str, name: str = "Settings", default: str = None):
        if not self.config.has_section(name):
            raise ValueError(f"Section '{name}' does not exist.")
        return self.config[name].get(key, default)

    def save_config(self, key: str, value: str, name: str = "Settings"):
        if not self.config.has_section(name):
            self.config.add_section(name)
        self.config.set(name, key, value)

        with open("config.ini", "w") as configFile:
            self.config.write(configFile)

    def init_ui(self):
        self.setMinimumSize(600, 400)
        self.setWindowTitle("Enoch's Cheap8 Emulator")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.setup_main_window()
        self.setup_menubar()
        self.show()

    def setup_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        open_rom_action = QAction("Open ROM", self)
        open_rom_action.setShortcut("Ctrl+O")
        open_rom_action.triggered.connect(self.open_rom_file)
        file_menu.addAction(open_rom_action)

        set_rom_folder_action = QAction("Set ROM Folder", self)
        set_rom_folder_action.setShortcut("Ctrl+L")
        set_rom_folder_action.triggered.connect(self.get_roms_folder)
        file_menu.addAction(set_rom_folder_action)
        file_menu.addSeparator()

        quit_action = QAction("Close Application", self)
        quit_action.triggered.connect(exit_application)
        file_menu.addAction(quit_action)

    def setup_main_window(self):
        self.main_layout = QVBoxLayout(self.central_widget)

        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemClicked.connect(self.on_list_item_clicked)
        self.load_roms(self.roms_folder)
        self.add_roms_to_list()

        self.main_layout.addWidget(self.list_widget)

    def open_rom_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", self.previous_dir, "CHIP-8 ROMS (*.ch8)"
        )
        self.previous_dir = QFileInfo(file_name).absolutePath()
        self.save_config(key=PREVIOUS_FILE_DIR_KEY, value=self.previous_dir)

        file_path = pathlib.Path(file_name)
        self.run_rom(file_path)

    def get_roms_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select ROM Folder")

        if folder_path:
            self.roms.clear()
            self.list_widget.clear()
            self.roms_folder = folder_path
            self.save_config(key=ROMS_FOLDER_CONFIG_KEY, value=folder_path)
            self.load_roms(folder_path)
        else:
            QMessageBox.warning(self, "No Folder Selected", "No folder was selected")

        self.add_roms_to_list()

    def load_roms(self, folder_path: str):
        folder = pathlib.Path(folder_path)
        content = folder.iterdir()

        for item in content:
            if not item.is_dir():
                if item.suffix == ".ch8":
                    self.roms[f"{item.name}"] = item

    def add_roms_to_list(self):
        for rom in self.roms.keys():
            list_item = QListWidgetItem()
            list_item.setText(rom)
            self.list_widget.addItem(list_item)

    def on_list_item_clicked(self, item: QListWidgetItem):
        file = self.roms[item.text()]

        self.run_rom(file.absolute())

    def run_rom(self, rom_path: pathlib.Path):
        """try:
            self.emulator = Emulator()
            self.game_thread = threading.Thread(target=self.emulator.run(rom_path))
            self.game_thread.start()
        except Exception as e:
            print(e)"""
        self.emulator_worker = EmulatorWorker(parent=self, rom_path=rom_path)
        self.emulator_worker.error.connect(lambda x: print(x))
        self.emulator_worker.run()

    def closeEvent(self, event: QCloseEvent | None) -> None:
        if self.emulator_worker:
            self.emulator_worker.stop_running()
        
        event.accept()
