import pathlib
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QToolButton, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon


class NavigationBar(QWidget):
    path_changed = pyqtSignal(str)
    go_home_requested = pyqtSignal()
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self.btn_back = QToolButton()
        self.btn_back.setText("\u25C0")
        self.btn_back.setToolTip("Back")
        self.btn_back.setFixedSize(32, 32)
        self.btn_back.clicked.connect(self._on_back)

        self.btn_forward = QToolButton()
        self.btn_forward.setText("\u25B6")
        self.btn_forward.setToolTip("Forward")
        self.btn_forward.setFixedSize(32, 32)
        self.btn_forward.clicked.connect(self._on_forward)

        self.btn_up = QToolButton()
        self.btn_up.setText("\u25B2")
        self.btn_up.setToolTip("Up One Level")
        self.btn_up.setFixedSize(32, 32)
        self.btn_up.clicked.connect(self._on_up)

        self.btn_home = QToolButton()
        self.btn_home.setText("\u2302")
        self.btn_home.setToolTip("Home")
        self.btn_home.setFixedSize(32, 32)
        self.btn_home.clicked.connect(self.go_home_requested.emit)

        self.btn_refresh = QToolButton()
        self.btn_refresh.setText("\u21BB")
        self.btn_refresh.setToolTip("Refresh")
        self.btn_refresh.setFixedSize(32, 32)
        self.btn_refresh.clicked.connect(self.refresh_requested.emit)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Enter path...")
        self.address_bar.returnPressed.connect(self._on_address_submit)

        layout.addWidget(self.btn_back)
        layout.addWidget(self.btn_forward)
        layout.addWidget(self.btn_up)
        layout.addWidget(self.btn_home)
        layout.addWidget(self.btn_refresh)
        layout.addWidget(self.address_bar)

        self._history: list[str] = []
        self._history_index: int = -1

    def navigate_to(self, path: str, add_to_history: bool = True):
        if add_to_history:
            if self._history_index < len(self._history) - 1:
                self._history = self._history[:self._history_index + 1]
            self._history.append(path)
            self._history_index = len(self._history) - 1
        self.address_bar.setText(path)
        self._update_buttons()
        self.path_changed.emit(path)

    def _on_back(self):
        if self._history_index > 0:
            self._history_index -= 1
            path = self._history[self._history_index]
            self.navigate_to(path, add_to_history=False)

    def _on_forward(self):
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            path = self._history[self._history_index]
            self.navigate_to(path, add_to_history=False)

    def _on_up(self):
        current = self.address_bar.text()
        parent = str(pathlib.Path(current).parent)
        if parent != current:
            self.navigate_to(parent)

    def _on_address_submit(self):
        import pathlib as _pl
        path = self.address_bar.text().strip()
        if not path:
            return
        p = _pl.Path(path).expanduser().resolve()
        if p.is_dir():
            self.navigate_to(str(p))
        else:
            self.address_bar.setText(str(self._history[self._history_index]) if self._history_index >= 0 else "")

    def _update_buttons(self):
        self.btn_back.setEnabled(self._history_index > 0)
        self.btn_forward.setEnabled(self._history_index < len(self._history) - 1)
