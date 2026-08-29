import threading
from PyQt6.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QTabWidget, QTreeWidget,
    QTreeWidgetItem, QHeaderView, QLabel, QCheckBox, QAbstractItemView,
    QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QColor
from core.syscall_monitor import SyscallMonitor
from core.lru_cache import get_cache

MAX_TABLE_ROWS = 500

COLUMNS = ["#", "Time", "Thread", "Syscall", "Arguments", "Result", "\u00b5s"]


class MonitorBridge(QObject):
    entry_logged = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        SyscallMonitor.instance().add_listener(self._forward)

    def _forward(self, entry):
        self.entry_logged.emit(entry)


class SyscallPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("System Call Monitor", parent)
        self.setAllowedAreas(
            Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea
        )
        self._paused = False

        tabs = QTabWidget()
        tabs.addTab(self._build_log_tab(), "Syscalls")
        tabs.addTab(self._build_threads_tab(), "Threads")
        tabs.addTab(self._build_cache_tab(), "Cache")
        self.setWidget(tabs)

        self.bridge = MonitorBridge(self)
        self.bridge.entry_logged.connect(self._on_entry)

        self.thread_timer = QTimer(self)
        self.thread_timer.timeout.connect(self._refresh_threads)
        self.thread_timer.start(1000)

        self.cache_timer = QTimer(self)
        self.cache_timer.timeout.connect(self._refresh_cache)
        self.cache_timer.start(500)

    def _build_log_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        controls = QHBoxLayout()
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setCheckable(True)
        self.pause_btn.setFixedWidth(70)
        self.pause_btn.toggled.connect(self._toggle_pause)
        controls.addWidget(self.pause_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setFixedWidth(70)
        clear_btn.clicked.connect(self._clear)
        controls.addWidget(clear_btn)

        self.autoscroll_cb = QCheckBox("Auto-scroll")
        self.autoscroll_cb.setChecked(True)
        controls.addWidget(self.autoscroll_cb)
        controls.addStretch()

        self.stats_label = QLabel("0 calls")
        self.stats_label.setStyleSheet("color: #a6adc8;")
        controls.addWidget(self.stats_label)

        layout.addLayout(controls)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        header = self.table.horizontalHeader()
        header.resizeSection(0, 45)
        header.resizeSection(1, 90)
        header.resizeSection(2, 110)
        header.resizeSection(3, 80)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.resizeSection(6, 60)
        layout.addWidget(self.table)
        return widget

    def _build_threads_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)

        self.threads_tree = QTreeWidget()
        self.threads_tree.setHeaderLabels(["Thread Name", "Thread ID", "Daemon"])
        self.threads_tree.setColumnWidth(0, 220)
        self.threads_tree.setColumnWidth(1, 120)
        layout.addWidget(self.threads_tree)
        return widget

    def _build_cache_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(4)

        row1 = QHBoxLayout()
        self.cache_toggle = QPushButton("Disable")
        self.cache_toggle.setCheckable(True)
        self.cache_toggle.setFixedWidth(70)
        self.cache_toggle.toggled.connect(self._toggle_cache)
        row1.addWidget(self.cache_toggle)

        row1.addStretch()
        reset_btn = QPushButton("Reset")
        reset_btn.setFixedWidth(55)
        reset_btn.clicked.connect(self._reset_cache_stats)
        row1.addWidget(reset_btn)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(12)
        self.cache_hit_label = QLabel("0")
        self.cache_hit_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")
        self.cache_miss_label = QLabel("0")
        self.cache_miss_label.setStyleSheet("color: #f38ba8; font-weight: bold;")
        self.cache_hitrate_label = QLabel("0%")
        self.cache_hitrate_label.setStyleSheet("color: #89b4fa; font-weight: bold;")
        self.cache_size_label = QLabel("0/2048")
        self.cache_evict_label = QLabel("0")
        row2.addWidget(QLabel("Hits:"))
        row2.addWidget(self.cache_hit_label)
        row2.addWidget(QLabel("Misses:"))
        row2.addWidget(self.cache_miss_label)
        row2.addWidget(QLabel("Rate:"))
        row2.addWidget(self.cache_hitrate_label)
        row2.addWidget(QLabel("Size:"))
        row2.addWidget(self.cache_size_label)
        row2.addWidget(QLabel("Evict:"))
        row2.addWidget(self.cache_evict_label)
        row2.addStretch()
        layout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.setSpacing(6)
        self.cache_bar = QProgressBar()
        self.cache_bar.setRange(0, 100)
        self.cache_bar.setValue(0)
        self.cache_bar.setFixedHeight(16)
        self.cache_bar.setFormat("%p% hit rate")
        row3.addWidget(self.cache_bar, 1)
        self.savings_label = QLabel("0 saved (0%)")
        self.savings_label.setFixedWidth(140)
        self.savings_label.setStyleSheet("font-size: 11px;")
        row3.addWidget(self.savings_label)
        layout.addLayout(row3)

        layout.addStretch()
        return widget

    def _on_entry(self, entry):
        if self._paused:
            return
        row = self.table.rowCount()
        if row >= MAX_TABLE_ROWS:
            self.table.removeRow(0)
            row -= 1
        self.table.insertRow(row)

        values = [
            str(entry["seq"]),
            entry["time"],
            entry["thread"],
            entry["syscall"],
            entry["args"],
            entry["error"] or entry["result"],
            str(entry["duration_us"]),
        ]
        is_error = bool(entry["error"])
        is_cache_hit = entry["syscall"] == "cache_hit"
        for col, text in enumerate(values):
            item = QTableWidgetItem(text)
            if is_error:
                item.setBackground(QColor("#5c2b2b"))
                if col == 5:
                    item.setForeground(QColor("#f38ba8"))
            elif is_cache_hit:
                if col == 3:
                    item.setForeground(QColor("#a6e3a1"))
                elif col == 5:
                    item.setForeground(QColor("#a6e3a1"))
            elif col == 3:
                item.setForeground(QColor("#89b4fa"))
            elif col == 2 and entry["thread"] != "MainThread":
                item.setForeground(QColor("#a6e3a1"))
            self.table.setItem(row, col, item)

        monitor = SyscallMonitor.instance()
        total = sum(monitor.call_counts.values())
        top = sorted(monitor.call_counts.items(), key=lambda kv: -kv[1])[:3]
        summary = ", ".join(f"{k}({v})" for k, v in top) if top else ""
        self.stats_label.setText(f"{total} calls | {summary}")

        if self.autoscroll_cb.isChecked():
            self.table.scrollToBottom()

    def _refresh_cache(self):
        cache = get_cache()
        self.cache_hit_label.setText(str(cache.stats["hits"]))
        self.cache_miss_label.setText(str(cache.stats["misses"]))
        rate = cache.hit_rate
        self.cache_hitrate_label.setText(f"{rate:.1f}%")
        self.cache_bar.setValue(int(rate))
        self.cache_size_label.setText(f"{cache.size}/{cache.capacity}")
        self.cache_evict_label.setText(str(cache.stats["evictions"]))
        total = cache.stats["hits"] + cache.stats["misses"]
        self.savings_label.setText(f"{cache.stats['hits']} saved ({rate:.1f}%)")

    def _toggle_cache(self, checked):
        cache = get_cache()
        cache.enabled = not checked
        self.cache_toggle.setText("Enable Cache" if checked else "Disable Cache")

    def _reset_cache_stats(self):
        get_cache().reset_stats()
        get_cache().clear()

    def _toggle_pause(self, checked):
        self._paused = checked
        self.pause_btn.setText("Resume" if checked else "Pause")

    def _clear(self):
        self.table.setRowCount(0)
        SyscallMonitor.instance().clear()
        self.stats_label.setText("0 calls")

    def _refresh_threads(self):
        threads = threading.enumerate()
        self.threads_tree.clear()
        for t in threads:
            item = QTreeWidgetItem([t.name, str(t.ident), str(t.daemon)])
            self.threads_tree.addTopLevelItem(item)
