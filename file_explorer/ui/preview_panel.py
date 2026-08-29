import pathlib
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from utils.helpers import is_image_file, is_text_file, format_size, get_file_type_description
from core.lru_cache import cached_stat
from core.syscall_monitor import SyscallMonitor


class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(250)
        self.setMaximumWidth(400)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(8, 8, 8, 8)
        self._layout.setSpacing(8)

        self.file_name_label = QLabel("No file selected")
        self.file_name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.file_name_label.setWordWrap(True)

        self.file_info_label = QLabel("")
        self.file_info_label.setStyleSheet("color: #a6adc8; font-size: 11px;")
        self.file_info_label.setWordWrap(True)

        self.preview_area = QLabel()
        self.preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setVisible(False)

        self._layout.addWidget(self.file_name_label)
        self._layout.addWidget(self.file_info_label)
        self._layout.addWidget(self.preview_area)
        self._layout.addWidget(self.text_preview)

        self.clear_preview()

    def clear_preview(self):
        self.file_name_label.setText("No file selected")
        self.file_info_label.setText("")
        self.preview_area.clear()
        self.preview_area.setText("Select a file to preview")
        self.text_preview.setVisible(False)
        self.preview_area.setVisible(True)

    def show_preview(self, path: str):
        p = pathlib.Path(path)
        if not p.exists():
            self.clear_preview()
            return

        self.file_name_label.setText(p.name)
        info_lines = [get_file_type_description(p)]
        try:
            monitor = SyscallMonitor.instance()
            st = cached_stat(str(p), monitor=monitor)
            if p.is_file():
                info_lines.append(f"Size: {format_size(st.st_size)}")
            info_lines.append(f"Modified: {__import__('datetime').datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')}")
            if hasattr(st, 'st_mode'):
                import stat
                mode = st.st_mode
                perms = []
                for label, flag in [("r", stat.S_IRUSR), ("w", stat.S_IWUSR), ("x", stat.S_IXUSR)]:
                    perms.append(label if mode & flag else "-")
                info_lines.append(f"Owner: {''.join(perms)}")
        except Exception:
            pass
        self.file_info_label.setText("\n".join(info_lines))

        if is_image_file(p) and p.is_file():
            self.text_preview.setVisible(False)
            self.preview_area.setVisible(True)
            try:
                data = p.read_bytes()
                image = QImage.fromData(data)
                pixmap = QPixmap.fromImage(image) if not image.isNull() else QPixmap()
            except Exception:
                pixmap = QPixmap()
            if not pixmap.isNull():
                scaled = pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                self.preview_area.setPixmap(scaled)
            else:
                self.preview_area.setText("Cannot load image")
        elif is_text_file(p) and p.is_file():
            self.preview_area.setVisible(False)
            self.text_preview.setVisible(True)
            try:
                content = p.read_text(errors="replace")[:10000]
                self.text_preview.setText(content)
            except Exception as e:
                self.text_preview.setText(f"Cannot read: {e}")
        else:
            self.text_preview.setVisible(False)
            self.preview_area.setVisible(True)
            self.preview_area.setText("No preview available")
