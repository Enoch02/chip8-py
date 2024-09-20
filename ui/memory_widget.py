from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
)


class Chip8MemoryWidget(QWidget):
    def __init__(self, memory_size=4096, bytes_per_row=8, parent=None):
        super().__init__(parent)

        self.memory_size = memory_size
        self.bytes_per_row = bytes_per_row

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setRowCount(self.memory_size // self.bytes_per_row)
        self.table.setColumnCount(self.bytes_per_row + 1)  # Add extra column for meaning
        headers = [f"0x{col:X}" for col in range(self.bytes_per_row)] + ["Meaning"]
        self.table.setHorizontalHeaderLabels(headers)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.table.resizeColumnsToContents()
        meaning_header_index = headers.index("Meaning")
        self.table.setColumnWidth(meaning_header_index, 140)

        # Initialize with empty memory
        self.update([0] * self.memory_size)

    def update(self, memory: list[int]):
        self.table.setUpdatesEnabled(False)
        for i in range(self.memory_size // self.bytes_per_row):
            for j in range(self.bytes_per_row):
                address = i * self.bytes_per_row + j
                byte_value = memory[address]
                meaning = self.get_meaning(memory, address)

                item = QTableWidgetItem(f"{byte_value:02X}")
                item.setFlags(item.flags() & Qt.ItemFlag.ItemIsEditable)  # Make it read-only
                self.table.setItem(i, j, item)

                meaning_item = QTableWidgetItem(meaning)
                meaning_item.setFlags(meaning_item.flags() & Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(i, self.bytes_per_row, meaning_item)
                
        self.table.setUpdatesEnabled(True)
        self.table.viewport().update()

    def get_meaning(self, memory: list[int], address: int):
        # Interpret memory content based on Chip-8 instruction set or data type
        byte_value = memory[address]
        value_as_int = byte_value

        if 32 <= byte_value <= 126:  # Printable ASCII range
            return chr(byte_value)

        # Attempt to interpret 2-byte sequences as integers
        if address % 2 == 0 and address + 1 < self.memory_size:
            word_value = memory[address] << 8 | memory[address + 1]
            return f"Int: {word_value}"

        if byte_value == 0x00:
            return "No operation"
        elif byte_value == 0x1:
            return "Jump to address"
        elif byte_value == 0x2:
            return "Call subroutine"
        elif byte_value == 0x3:
            return "Skip next instruction if equal"
        elif byte_value == 0x4:
            return "Skip next instruction if not equal"
        elif byte_value == 0x5:
            return "Skip next instruction if registers are equal"
        elif byte_value == 0x6:
            return "Set register to value"
        elif byte_value == 0x7:
            return "Add value to register"
        elif byte_value == 0x8:
            return "Arithmetic and logic operations"
        elif byte_value == 0x9:
            return "Skip next instruction if registers are not equal"
        elif byte_value == 0xA:
            return "Set index register"
        elif byte_value == 0xB:
            return "Jump to address plus V0"
        elif byte_value == 0xC:
            return "Set register to random value AND mask"
        elif byte_value == 0xD:
            return "Draw sprite"
        elif byte_value == 0xE:
            return "Key press instructions"
        elif byte_value == 0xF:
            return "Miscellaneous instructions"
        elif 0x20 <= byte_value < 0x30:
            return "Instruction (custom logic)"
        else:
            return f"Data: {byte_value:02X}"
