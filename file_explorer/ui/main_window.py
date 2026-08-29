import pathlib
import os
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QToolBar, QLineEdit, QWidget,
    QVBoxLayout, QHBoxLayout, QToolButton, QMessageBox,
    QLabel, QPushButton, QStatusBar, QListWidget, QListWidgetItem,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer
from ui.tree_view import DirectoryTreeView
from ui.detail_view import DetailTableView
from ui.preview_panel import PreviewPanel
from ui.navigation_bar import NavigationBar
from ui.syscall_panel import SyscallPanel
from core.fs_operations import FileSystemOperations, ClipboardData
from core.search_engine import SearchEngine
from utils.styles import DARK_STYLESHEET


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Explorer")
        self.setMinimumSize(1000, 600)
        self.fs_ops = FileSystemOperations()
        self.clipboard = ClipboardData()
        self.search_engine = SearchEngine()
        self._search_results = []

        self._setup_ui()
        self._connect_signals()
        self._apply_style()
        QTimer.singleShot(100, self._initial_navigate)
        self.statusBar().showMessage("Ready")

    def _initial_navigate(self):
        self.nav_bar.navigate_to(str(pathlib.Path.home()))

    def _setup_ui(self):
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.nav_bar = NavigationBar()
        toolbar.addWidget(self.nav_bar)

        toolbar.addSeparator()

        search_label = QLabel(" Search: ")
        toolbar.addWidget(search_label)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filter files...")
        self.search_input.setFixedWidth(200)
        self.search_input.returnPressed.connect(self._on_search_enter)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        toolbar.addWidget(self.search_input)

        self.search_case = QToolButton()
        self.search_case.setText("Aa")
        self.search_case.setCheckable(True)
        self.search_case.setToolTip("Match Case")
        toolbar.addWidget(self.search_case)

        self.search_recursive = QToolButton()
        self.search_recursive.setText("\u2195")
        self.search_recursive.setCheckable(True)
        self.search_recursive.setToolTip("Search Subfolders (Recursive)")
        toolbar.addWidget(self.search_recursive)

        btn_search = QToolButton()
        btn_search.setText("\u2315")
        btn_search.setToolTip("Search (Enter)")
        btn_search.clicked.connect(self._on_search_enter)
        toolbar.addWidget(btn_search)

        toolbar.addSeparator()

        btn_theme = QToolButton()
        btn_theme.setText("\u263E")
        btn_theme.setToolTip("Toggle Theme")
        btn_theme.clicked.connect(self._toggle_theme)
        toolbar.addWidget(btn_theme)

        btn_trash = QToolButton()
        btn_trash.setText("\u267B")
        btn_trash.setToolTip("Recycle Bin")
        btn_trash.clicked.connect(self._open_trash)
        toolbar.addWidget(btn_trash)

        btn_syscalls = QToolButton()
        btn_syscalls.setText("\u2699 Syscalls")
        btn_syscalls.setCheckable(True)
        btn_syscalls.setChecked(True)
        btn_syscalls.setToolTip("Toggle System Call Monitor")
        btn_syscalls.toggled.connect(self._toggle_syscall_panel)
        toolbar.addWidget(btn_syscalls)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.tree = DirectoryTreeView()
        self.tree.setMinimumWidth(200)
        self.tree.setMaximumWidth(350)

        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)

        center_splitter = QSplitter(Qt.Orientation.Vertical)

        self.detail_view = DetailTableView()
        center_splitter.addWidget(self.detail_view)

        self.search_results_widget = QWidget()
        search_layout = QVBoxLayout(self.search_results_widget)
        search_layout.setContentsMargins(4, 2, 4, 2)
        search_layout.setSpacing(2)
        search_header = QHBoxLayout()
        self.search_results_label = QLabel("Search Results")
        self.search_results_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        search_header.addWidget(self.search_results_label)
        search_header.addStretch()
        btn_close_search = QToolButton()
        btn_close_search.setText("\u2716")
        btn_close_search.setFixedSize(18, 18)
        btn_close_search.setToolTip("Close")
        btn_close_search.clicked.connect(self._close_search_results)
        search_header.addWidget(btn_close_search)
        search_layout.addLayout(search_header)

        self.search_results_list = QListWidget()
        self.search_results_list.setAlternatingRowColors(True)
        self.search_results_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.search_results_list.itemDoubleClicked.connect(self._on_search_result_clicked)
        self.search_results_list.itemClicked.connect(self._on_search_result_clicked)
        search_layout.addWidget(self.search_results_list, 1)
        self.search_results_widget.hide()
        self.search_results_widget.setMaximumHeight(180)
        center_splitter.addWidget(self.search_results_widget)

        center_splitter.setSizes([500, 150])
        center_splitter.setCollapsible(1, True)

        self.preview_panel = PreviewPanel()
        self.preview_panel.hide()

        self.toggle_preview_btn = QPushButton("\u25B6 Preview")
        self.toggle_preview_btn.setCheckable(True)
        self.toggle_preview_btn.setFixedWidth(80)
        self.toggle_preview_btn.toggled.connect(self._toggle_preview)
        center_layout.addWidget(self.toggle_preview_btn)
        center_layout.addWidget(center_splitter, 1)

        splitter.addWidget(self.tree)
        splitter.addWidget(center_widget)
        splitter.addWidget(self.preview_panel)
        splitter.setSizes([250, 500, 200])

        main_layout.addWidget(splitter)

        self.syscall_panel = SyscallPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.syscall_panel)
        self.resizeDocks([self.syscall_panel], [220], Qt.Orientation.Vertical)

    def _toggle_syscall_panel(self, checked: bool):
        self.syscall_panel.setVisible(checked)

    def _connect_signals(self):
        self._updating = False
        self.nav_bar.path_changed.connect(self._on_nav_path_changed)
        self.nav_bar.go_home_requested.connect(self._go_home)
        self.nav_bar.refresh_requested.connect(self._refresh)
        self.tree.directory_selected.connect(self._on_tree_directory_selected)
        self.detail_view.directory_changed.connect(self._on_directory_changed)
        self.detail_view.file_selected.connect(self._on_file_selected)

    def _apply_style(self):
        self.setStyleSheet(DARK_STYLESHEET)

    def _on_nav_path_changed(self, path: str):
        if self._updating:
            return
        self._updating = True
        p = pathlib.Path(path)
        if p.is_dir():
            self.tree.set_root(path)
            self.detail_view.navigate_to(path)
            self.detail_view.clear_filter()
            self.search_input.clear()
            self.statusBar().showMessage(path)
        else:
            self.statusBar().showMessage(f"Not a directory: {path}")
        self._updating = False

    def _on_tree_directory_selected(self, path: str):
        if self._updating:
            return
        self._updating = True
        self.nav_bar.navigate_to(path)
        self.detail_view.navigate_to(path)
        self.detail_view.clear_filter()
        self.search_input.clear()
        self.statusBar().showMessage(path)
        self._updating = False

    def _on_directory_changed(self, path: str):
        if self._updating:
            return
        self._updating = True
        self.nav_bar.navigate_to(path)
        self.tree.set_root(path)
        self.detail_view.clear_filter()
        self.search_input.clear()
        self.statusBar().showMessage(path)
        self._updating = False

    def _on_file_selected(self, path: str):
        self.preview_panel.show_preview(path)
        self.statusBar().showMessage(f"Selected: {path}")

    def _go_home(self):
        self.nav_bar.navigate_to(str(pathlib.Path.home()))

    def _refresh(self):
        self.detail_view.refresh()

    def _toggle_preview(self, checked: bool):
        self.preview_panel.setVisible(checked)

    def _toggle_theme(self):
        from utils.styles import LIGHT_STYLESHEET
        if self.styleSheet() == DARK_STYLESHEET:
            self.setStyleSheet(LIGHT_STYLESHEET)
        else:
            self.setStyleSheet(DARK_STYLESHEET)

    def _open_trash(self):
        trash_path = pathlib.Path.home() / ".local" / "share" / "Trash" / "files"
        if trash_path.is_dir():
            self.nav_bar.navigate_to(str(trash_path))
        else:
            QMessageBox.information(self, "Recycle Bin", "Trash folder not found.")

    def _on_search_text_changed(self, text: str):
        query = text.strip()
        if query:
            self.detail_view.filter_by_name(query)
        else:
            self.detail_view.clear_filter()

    def _on_search_enter(self):
        query = self.search_input.text().strip()
        if not query:
            return
        self.detail_view.filter_by_name(query)
        self._run_recursive_search(query)

    def _run_recursive_search(self, query: str):
        case_sensitive = self.search_case.isChecked()
        recursive = self.search_recursive.isChecked()
        root_path = self.detail_view.current_path
        self.search_results_widget.show()
        self.search_results_list.clear()
        self.search_results_list.addItem("Searching...")
        self._search_results = []

        def on_result(path):
            self._search_results.append(path)
            name = os.path.basename(path)
            parent = os.path.dirname(path)
            self.search_results_list.addItem(f"{name}  \u2190  {parent}")

        def on_finished():
            count = len(self._search_results)
            self.search_results_label.setText(f"Search Results ({count})")
            if count == 0:
                self.search_results_list.clear()
                self.search_results_list.addItem("No results found")

        self.search_engine.start_search(
            str(root_path), query, case_sensitive=case_sensitive,
            recursive=recursive,
            result_callback=on_result, finished_callback=on_finished
        )

    def _on_search_result_clicked(self, item: QListWidgetItem):
        row = self.search_results_list.row(item)
        if row < len(self._search_results):
            selected_path = self._search_results[row]
            p = pathlib.Path(selected_path)
            if p.is_dir():
                self.nav_bar.navigate_to(str(p))
            elif p.is_file():
                self.nav_bar.navigate_to(str(p.parent))

    def _close_search_results(self):
        self.search_results_widget.hide()
        self.search_results_list.clear()
        self._search_results = []

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F5:
            self._refresh()
        elif event.key() == Qt.Key.Key_Escape:
            self.search_input.clear()
            self._close_search_results()
        else:
            super().keyPressEvent(event)
