from dataclasses import dataclass

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


@dataclass
class RegisterData:
    """Holds emulator register data in a single object"""

    pc: int
    i: int
    dt: int
    st: int
    v: list[int]


class Chip8RegistersWidget(QWidget):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.v = [0] * 16

        self.v_labels: list[QLabel] = []

        layout = QVBoxLayout(self)

        frame1 = QFrame()
        frame1.setFrameShape(QFrame.Shape.Box)
        row1 = QHBoxLayout()
        self.pc_lbl = QLabel(f"PC \n 512")
        self.pc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.i_lbl = QLabel(f"I \n 000")
        self.i_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dt_lbl = QLabel(f"DT \n 000")
        self.dt_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.st_lbl = QLabel(f"ST \n 000")
        self.st_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        row1.addWidget(self.pc_lbl)
        row1.addWidget(self.create_v_line())

        row1.addWidget(self.i_lbl)
        row1.addWidget(self.create_v_line())

        row1.addWidget(self.dt_lbl)
        row1.addWidget(self.create_v_line())

        row1.addWidget(self.st_lbl)

        frame1.setLayout(row1)
        layout.addWidget(frame1)

        frame2 = QFrame()
        frame2.setFrameShape(QFrame.Shape.Box)
        row2 = QHBoxLayout()

        for i in range(0, 8):
            lbl = QLabel(f"V{i} \n {self.v[i]:03d}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row2.addWidget(lbl)
            self.v_labels.append(lbl)
            if i < 7:
                row2.addWidget(self.create_v_line())

        frame2.setLayout(row2)
        layout.addWidget(frame2)

        frame3 = QFrame()
        frame3.setFrameShape(QFrame.Shape.Box)
        row3 = QHBoxLayout()

        for i in range(8, 16):
            lbl = QLabel(f"V{i} \n {self.v[i]:03d}")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.v_labels.append(lbl)
            row3.addWidget(lbl)
            if i < 15:
                row3.addWidget(self.create_v_line())

        frame3.setLayout(row3)
        layout.addWidget(frame3)

    def update(self, data: RegisterData) -> None:
        self.pc_lbl.setText(f"PC \n {data.pc:03d}")
        self.i_lbl.setText(f"I \n {data.i:03d}")
        self.dt_lbl.setText(f"DT \n {data.dt:03d}")
        self.st_lbl.setText(f"ST \n {data.st:03d}")

        for i, label in enumerate(self.v_labels):
            label.setText(f"V{i} \n {data.v[i]:03d}")

    def create_v_line(self) -> QFrame:
        v_line = QFrame()
        v_line.setFrameShape(QFrame.Shape.VLine)
        v_line.setFrameShadow(QFrame.Shadow.Plain)

        return v_line
