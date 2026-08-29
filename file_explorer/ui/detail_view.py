import pathlib
from PyQt6.QtWidgets import (
    QTableView, QAbstractItemView, QMenu, QMessageBox,
    QInputDialog, QHeaderView, QProgressDialog
)
from PyQt6.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt6.QtGui import QAction, QFileSystemModel
from core.fs_operations import FileSystemOperations, ClipboardData
from core.lru_cache import get_cache, cached_stat
from core.syscall_monitor import SyscallMonitor


class DetailTableView(QTableView):
    directory_changed = pyqtSignal(str)
    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.fs_ops = FileSystemOperations()
        self.clipboard = ClipboardData()
        self.current_path = pathlib.Path.home()
        self._workers = []
        self._filter_text = ""
        self._setup_model()
        self._setup_view()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.doubleClicked.connect(self._on_double_click)
        self.selectionModel().selectionChanged.connect(self._on_selection_changed)

    def _setup_model(self):
        self.model = QFileSystemModel()
        self.model.setReadOnly(False)
        self.model.setNameFilterDisables(False)
        self.setModel(self.model)
        root_idx = self.model.setRootPath(str(self.current_path))
        self.setRootIndex(root_idx)
        self.model.directoryLoaded.connect(self._on_directory_loaded)

    def _setup_view(self):
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setShowGrid(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, 4):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.verticalHeader().setVisible(False)
        self.setColumnWidth(0, 300)

    def _on_directory_loaded(self, path: str):
        if self._filter_text and path == str(self.current_path):
            self._apply_filter()

    def navigate_to(self, path: str):
        p = pathlib.Path(path)
        if p.is_dir():
            self.current_path = p
            self._filter_text = ""
            root_idx = self.model.setRootPath(str(p))
            self.setRootIndex(root_idx)
            self.directory_changed.emit(str(p))

    def refresh(self):
        root_idx = self.model.setRootPath(str(self.current_path))
        self.setRootIndex(root_idx)

    def filter_by_name(self, query: str):
        self._filter_text = query.lower()
        self._apply_filter()

    def clear_filter(self):
        self._filter_text = ""
        for row in range(self.model.rowCount(self.rootIndex())):
            self.setRowHidden(row, False)

    def _apply_filter(self):
        root = self.rootIndex()
        for row in range(self.model.rowCount(root)):
            idx = self.model.index(row, 0, root)
            name = self.model.data(idx, Qt.ItemDataRole.DisplayRole)
            if name is None:
                self.setRowHidden(row, False)
                continue
            if self._filter_text in name.lower():
                self.setRowHidden(row, False)
            else:
                self.setRowHidden(row, True)

    def _on_double_click(self, index: QModelIndex):
        path = self.model.filePath(index)
        p = pathlib.Path(path)
        if p.is_dir():
            self.navigate_to(path)
        elif p.is_file():
            from PyQt6.QtCore import QUrl
            from PyQt6.QtGui import QDesktopServices
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(p)))

    def _on_selection_changed(self):
        indexes = self.selectionModel().selectedRows()
        if indexes:
            path = self.model.filePath(indexes[0])
            self.file_selected.emit(path)

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        selected_indexes = self.selectionModel().selectedRows()
        has_selection = len(selected_indexes) > 0

        act_open = menu.addAction("Open")
        act_open.setEnabled(has_selection)
        act_open.triggered.connect(self._open_selected)

        menu.addSeparator()
        act_copy = menu.addAction("Copy\tCtrl+C")
        act_copy.setEnabled(has_selection)
        act_copy.triggered.connect(self._copy_selected)

        act_cut = menu.addAction("Cut\tCtrl+X")
        act_cut.setEnabled(has_selection)
        act_cut.triggered.connect(self._cut_selected)

        act_paste = menu.addAction("Paste\tCtrl+V")
        act_paste.setEnabled(bool(self.clipboard.paths))
        act_paste.triggered.connect(self._paste)

        menu.addSeparator()
        act_rename = menu.addAction("Rename\tF2")
        act_rename.setEnabled(len(selected_indexes) == 1)
        act_rename.triggered.connect(self._rename_selected)

        act_delete = menu.addAction("Delete\tDel")
        act_delete.setEnabled(has_selection)
        act_delete.triggered.connect(self._delete_selected)

        menu.addSeparator()
        menu.addAction("New Folder...").triggered.connect(self._new_folder)
        menu.addAction("New File...").triggered.connect(self._new_file)

        if has_selection and len(selected_indexes) == 1:
            p = pathlib.Path(self.model.filePath(selected_indexes[0]))
            if p.is_file():
                menu.addSeparator()
                menu.addAction("Calculate Checksums...").triggered.connect(
                    lambda: self._calc_checksums(p))
                menu.addAction("Properties...").triggered.connect(
                    lambda: self._show_permissions(p))

        menu.exec(self.viewport().mapToGlobal(pos))

    def _get_selected_paths(self) -> list[pathlib.Path]:
        return [pathlib.Path(self.model.filePath(idx))
                for idx in self.selectionModel().selectedRows()]

    def _open_selected(self):
        for path in self._get_selected_paths():
            if path.is_dir():
                self.navigate_to(str(path))
            else:
                from PyQt6.QtCore import QUrl
                from PyQt6.QtGui import QDesktopServices
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _copy_selected(self):
        self.clipboard.paths = self._get_selected_paths()
        self.clipboard.cut_mode = False

    def _cut_selected(self):
        self.clipboard.paths = self._get_selected_paths()
        self.clipboard.cut_mode = True

    def _paste(self):
        if not self.clipboard.paths:
            return
        from core.async_workers import FileCopyWorker
        worker = FileCopyWorker(self.clipboard.paths, self.current_path, self.clipboard.cut_mode)
        self._workers.append(worker)
        progress = QProgressDialog("Processing files...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setAutoClose(True)

        def on_progress(value):
            progress.setValue(value)

        def on_finished(ok, msg):
            if not ok and msg != "Cancelled":
                QMessageBox.critical(self, "Paste Error", msg)
            progress.close()
            if worker in self._workers:
                self._workers.remove(worker)
            worker.deleteLater()
            self.refresh()

        worker.progress.connect(on_progress)
        worker.finished_signal.connect(on_finished)
        progress.canceled.connect(worker.cancel)
        worker.start()
        if self.clipboard.cut_mode:
            self.clipboard.paths = []

    def _rename_selected(self):
        indexes = self.selectionModel().selectedRows()
        if len(indexes) != 1:
            return
        path = pathlib.Path(self.model.filePath(indexes[0]))
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=path.name)
        if ok and new_name and new_name != path.name:
            try:
                cache = get_cache()
                cache.invalidate_prefix(str(path.parent))
                self.fs_ops.rename(path, new_name)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _delete_selected(self):
        paths = self._get_selected_paths()
        if not paths:
            return
        names = "\n".join(p.name for p in paths[:10])
        if len(paths) > 10:
            names += f"\n... and {len(paths) - 10} more"
        reply = QMessageBox.question(
            self, "Delete", f"Delete the following?\n\n{names}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            cache = get_cache()
            for path in paths:
                try:
                    cache.invalidate_prefix(str(path.parent))
                    self.fs_ops.delete(path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
            self.refresh()

    def _new_folder(self):
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            try:
                get_cache().invalidate_prefix(str(self.current_path))
                self.fs_ops.create_folder(self.current_path, name)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _new_file(self):
        name, ok = QInputDialog.getText(self, "New File", "File name:")
        if ok and name:
            try:
                get_cache().invalidate_prefix(str(self.current_path))
                self.fs_ops.create_file(self.current_path, name)
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def _calc_checksums(self, path: pathlib.Path):
        from ui.dialogs.checksum_dialog import ChecksumDialog
        dialog = ChecksumDialog(path, self)
        dialog.exec()

    def _show_permissions(self, path: pathlib.Path):
        from ui.dialogs.permissions_dialog import PermissionsDialog
        dialog = PermissionsDialog(path, self)
        dialog.exec()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self._delete_selected()
        elif event.key() == Qt.Key.Key_F2:
            self._rename_selected()
        elif event.key() == Qt.Key.Key_C and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._copy_selected()
        elif event.key() == Qt.Key.Key_X and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._cut_selected()
        elif event.key() == Qt.Key.Key_V and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self._paste()
        else:
            super().keyPressEvent(event)
