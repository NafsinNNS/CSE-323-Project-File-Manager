import pathlib
from PyQt6.QtWidgets import QTreeView
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFileSystemModel


class DirectoryTreeView(QTreeView):
    directory_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.model.setReadOnly(False)
        self.setModel(self.model)
        self.setRootIndex(self.model.index(""))
        for col in range(1, self.model.columnCount()):
            self.hideColumn(col)
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setExpandsOnDoubleClick(True)
        self.clicked.connect(self._on_clicked)

    def set_root(self, path: str):
        idx = self.model.setRootPath(path)
        self.setRootIndex(idx)
        self.setCurrentIndex(idx)

    def _on_clicked(self, index):
        path = self.model.filePath(index)
        if pathlib.Path(path).is_dir():
            self.directory_selected.emit(path)
