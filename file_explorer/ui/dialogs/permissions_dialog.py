import pathlib
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QGroupBox, QGridLayout, QMessageBox
)
from core.fs_operations import FileSystemOperations


class PermissionsDialog(QDialog):
    def __init__(self, file_path: pathlib.Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Permissions - {file_path.name}")
        self.setMinimumWidth(350)
        self.file_path = file_path
        self.fs_ops = FileSystemOperations()
        self.checkboxes = {}

        layout = QVBoxLayout(self)

        info = QLabel(f"File: {file_path}")
        info.setWordWrap(True)
        info.setStyleSheet("font-weight: bold;")
        layout.addWidget(info)

        groups = [
            ("Owner", ["owner_read", "owner_write", "owner_exec"]),
            ("Group", ["group_read", "group_write", "group_exec"]),
            ("Others", ["other_read", "other_write", "other_exec"]),
        ]

        for group_name, keys in groups:
            box = QGroupBox(group_name)
            grid = QGridLayout()
            labels = ["Read", "Write", "Execute"]
            for i, (key, label) in enumerate(zip(keys, labels)):
                cb = QCheckBox(label)
                self.checkboxes[key] = cb
                grid.addWidget(cb, 0, i)
            box.setLayout(grid)
            layout.addWidget(box)

        self._load_permissions()

        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_permissions)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(apply_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _load_permissions(self):
        try:
            perms = self.fs_ops.get_permissions(self.file_path)
            for key, cb in self.checkboxes.items():
                cb.setChecked(perms.get(key, False))
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _apply_permissions(self):
        perms = {key: cb.isChecked() for key, cb in self.checkboxes.items()}
        try:
            self.fs_ops.set_permissions(self.file_path, perms)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
