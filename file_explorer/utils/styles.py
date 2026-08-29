DARK_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    padding: 4px;
    spacing: 4px;
}
QToolBar QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    color: #cdd6f4;
    font-size: 13px;
}
QToolBar QToolButton:hover { background-color: #313244; }
QToolBar QToolButton:pressed { background-color: #45475a; }
QLineEdit {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 10px;
    color: #cdd6f4;
    font-size: 13px;
    selection-background-color: #585b70;
}
QLineEdit:focus { border: 1px solid #89b4fa; }
QTreeView, QTableView {
    background-color: #1e1e2e;
    alternate-background-color: #181825;
    border: none;
    border-radius: 8px;
    padding: 4px;
    color: #cdd6f4;
    font-size: 13px;
    outline: none;
    gridline-color: #313244;
}
QTreeView::item, QTableView::item { padding: 4px 8px; border-radius: 4px; }
QTreeView::item:selected, QTableView::item:selected { background-color: #45475a; color: #cdd6f4; }
QTreeView::item:hover, QTableView::item:hover { background-color: #313244; }
QHeaderView::section {
    background-color: #181825;
    color: #a6adc8;
    border: none;
    border-bottom: 1px solid #313244;
    border-right: 1px solid #313244;
    padding: 6px 12px;
    font-weight: bold;
    font-size: 12px;
}
QHeaderView::section:hover { background-color: #313244; color: #cdd6f4; }
QSplitter::handle { background-color: #585b70; }
QSplitter::handle:horizontal { width: 6px; }
QSplitter::handle:vertical { height: 6px; }
QSplitter::handle:hover { background-color: #89b4fa; }
QMainWindow::separator { background-color: #585b70; }
QMainWindow::separator:horizontal { width: 6px; }
QMainWindow::separator:vertical { height: 6px; }
QMainWindow::separator:hover { background-color: #89b4fa; }
QScrollBar:vertical { background-color: #1e1e2e; width: 10px; margin: 0; }
QScrollBar::handle:vertical { background-color: #45475a; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background-color: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal { background-color: #1e1e2e; height: 10px; margin: 0; }
QScrollBar::handle:horizontal { background-color: #45475a; border-radius: 5px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background-color: #585b70; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
QTextEdit {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 6px;
    padding: 8px;
    color: #cdd6f4;
    font-family: 'Consolas', 'Fira Code', monospace;
    font-size: 12px;
}
QLabel { color: #cdd6f4; }
QPushButton {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 16px;
    color: #cdd6f4;
    font-size: 13px;
}
QPushButton:hover { background-color: #45475a; border-color: #585b70; }
QPushButton:pressed { background-color: #585b70; }
QPushButton:disabled { background-color: #1e1e2e; color: #6c7086; border-color: #313244; }
QProgressBar {
    background-color: #313244;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #cdd6f4;
    height: 20px;
}
QProgressBar::chunk { background-color: #89b4fa; border-radius: 4px; }
QMessageBox { background-color: #1e1e2e; color: #cdd6f4; }
QCheckBox { color: #cdd6f4; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 4px;
    border: 1px solid #45475a;
    background-color: #313244;
}
QCheckBox::indicator:checked { background-color: #89b4fa; border-color: #89b4fa; }
QComboBox {
    background-color: #313244;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px 8px;
    color: #cdd6f4;
}
QComboBox:hover { border-color: #585b70; }
QComboBox::drop-down { border: none; }
QMenu {
    background-color: #1e1e2e;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 4px;
    color: #cdd6f4;
}
QMenu::item { padding: 6px 24px 6px 12px; border-radius: 4px; }
QMenu::item:selected { background-color: #45475a; }
QMenu::separator { height: 1px; background-color: #313244; margin: 4px 8px; }
"""

LIGHT_STYLESHEET = """
QMainWindow, QDialog {
    background-color: #eff1f5;
    color: #4c4f69;
}
QToolBar {
    background-color: #e6e9ef;
    border-bottom: 1px solid #ccd0da;
    padding: 4px;
    spacing: 4px;
}
QToolBar QToolButton {
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    color: #4c4f69;
    font-size: 13px;
}
QToolBar QToolButton:hover { background-color: #ccd0da; }
QLineEdit {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 6px 10px;
    color: #4c4f69;
    font-size: 13px;
}
QLineEdit:focus { border: 1px solid #1e66f5; }
QTreeView, QTableView {
    background-color: #ffffff;
    alternate-background-color: #f5f5f9;
    border: none;
    border-radius: 8px;
    padding: 4px;
    color: #4c4f69;
    font-size: 13px;
    gridline-color: #ccd0da;
}
QTreeView::item, QTableView::item { padding: 4px 8px; }
QTreeView::item:selected, QTableView::item:selected { background-color: #bcc0cc; color: #4c4f69; }
QTreeView::item:hover, QTableView::item:hover { background-color: #e6e9ef; }
QHeaderView::section {
    background-color: #e6e9ef;
    color: #5c5f77;
    border: none;
    border-bottom: 1px solid #ccd0da;
    border-right: 1px solid #ccd0da;
    padding: 6px 12px;
    font-weight: bold;
    font-size: 12px;
}
QSplitter::handle { background-color: #9ca0b0; }
QSplitter::handle:horizontal { width: 6px; }
QSplitter::handle:vertical { height: 6px; }
QSplitter::handle:hover { background-color: #1e66f5; }
QMainWindow::separator { background-color: #9ca0b0; }
QMainWindow::separator:horizontal { width: 6px; }
QMainWindow::separator:vertical { height: 6px; }
QMainWindow::separator:hover { background-color: #1e66f5; }
QTextEdit {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 8px;
    color: #4c4f69;
    font-family: 'Consolas', monospace;
    font-size: 12px;
}
QLabel { color: #4c4f69; }
QPushButton {
    background-color: #e6e9ef;
    border: 1px solid #ccd0da;
    border-radius: 6px;
    padding: 6px 16px;
    color: #4c4f69;
    font-size: 13px;
}
QPushButton:hover { background-color: #ccd0da; }
QPushButton:pressed { background-color: #bcc0cc; }
QProgressBar {
    background-color: #e6e9ef;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: #4c4f69;
    height: 20px;
}
QProgressBar::chunk { background-color: #1e66f5; border-radius: 4px; }
QCheckBox { color: #4c4f69; spacing: 8px; }
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 4px;
    border: 1px solid #ccd0da;
    background-color: #ffffff;
}
QCheckBox::indicator:checked { background-color: #1e66f5; border-color: #1e66f5; }
QMenu {
    background-color: #ffffff;
    border: 1px solid #ccd0da;
    border-radius: 8px;
    padding: 4px;
    color: #4c4f69;
}
QMenu::item { padding: 6px 24px 6px 12px; border-radius: 4px; }
QMenu::item:selected { background-color: #e6e9ef; }
QMenu::separator { height: 1px; background-color: #ccd0da; margin: 4px 8px; }
"""
