import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from core.syscall_monitor import install_syscall_monitor

install_syscall_monitor()

from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("File Explorer")
    app.setOrganizationName("FileExplorer")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
