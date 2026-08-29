import pathlib
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton,
    QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from core.async_workers import ChecksumWorker


class ChecksumDialog(QDialog):
    def __init__(self, file_path: pathlib.Path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Checksums - {file_path.name}")
        self.setMinimumWidth(450)
        self.file_path = file_path
        self.results = {}
        self._worker = None

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.progress = QProgressBar()
        layout.addWidget(QLabel(f"Calculating checksums for: {file_path.name}"))
        layout.addWidget(self.progress)

        self.result_labels = {}
        for algo in ["MD5", "SHA-1", "SHA-256"]:
            row = QHBoxLayout()
            lbl_name = QLabel(f"{algo}:")
            lbl_name.setStyleSheet("font-weight: bold;")
            lbl_value = QLabel("Calculating...")
            lbl_value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            copy_btn = QPushButton("Copy")
            copy_btn.setFixedWidth(60)
            copy_btn.clicked.connect(lambda checked, a=algo: self._copy_hash(a))
            row.addWidget(lbl_name)
            row.addWidget(lbl_value, 1)
            row.addWidget(copy_btn)
            layout.addLayout(row)
            self.result_labels[algo] = lbl_value

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self._start_worker()

    def _start_worker(self):
        self._worker = ChecksumWorker(self.file_path)
        self._worker.progress.connect(self.progress.setValue)
        self._worker.result.connect(self._on_result)
        self._worker.finished_signal.connect(self._on_finished)
        self._worker.start()

    def _on_result(self, algo: str, value: str):
        self.results[algo] = value
        if algo in self.result_labels:
            self.result_labels[algo].setText(value)

    def _on_finished(self):
        self.progress.setValue(100)

    def _copy_hash(self, algo: str):
        if algo in self.results:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(self.results[algo])
            QMessageBox.information(self, "Copied", f"{algo} hash copied to clipboard.")

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
        super().closeEvent(event)
