import hashlib
import pathlib
import threading
from PyQt6.QtCore import QThread, pyqtSignal


class FileCopyWorker(QThread):
    progress = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, sources: list, dest_dir: pathlib.Path, move_mode: bool = False):
        super().__init__()
        self.sources = sources
        self.dest_dir = dest_dir
        self.move_mode = move_mode
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        threading.current_thread().name = "FileCopyWorker"
        import shutil
        try:
            total = len(self.sources)
            for i, src in enumerate(self.sources):
                if self._cancelled:
                    self.finished_signal.emit(False, "Cancelled")
                    return
                src_path = pathlib.Path(src)
                if self.move_mode:
                    shutil.move(str(src_path), str(self.dest_dir))
                else:
                    if src_path.is_dir():
                        shutil.copytree(src_path, self.dest_dir / src_path.name)
                    else:
                        shutil.copy2(src_path, self.dest_dir)
                self.progress.emit(int((i + 1) * 100 / total))
            self.finished_signal.emit(True, "Success")
        except Exception as e:
            self.finished_signal.emit(False, str(e))


class ChecksumWorker(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str, str)
    finished_signal = pyqtSignal()

    def __init__(self, file_path: pathlib.Path):
        super().__init__()
        self.file_path = file_path
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        threading.current_thread().name = "ChecksumWorker"
        try:
            from core.lru_cache import cached_stat
            from core.syscall_monitor import SyscallMonitor
            st = cached_stat(str(self.file_path), monitor=SyscallMonitor.instance())
            total_size = st.st_size
            chunk_size = 64 * 1024
            md5 = hashlib.md5()
            sha1 = hashlib.sha1()
            sha256 = hashlib.sha256()
            read_so_far = 0

            with open(self.file_path, "rb") as f:
                while True:
                    if self._cancelled:
                        return
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    md5.update(chunk)
                    sha1.update(chunk)
                    sha256.update(chunk)
                    read_so_far += len(chunk)
                    if total_size > 0:
                        self.progress.emit(int(read_so_far * 100 / total_size))

            self.result.emit("MD5", md5.hexdigest())
            self.result.emit("SHA-1", sha1.hexdigest())
            self.result.emit("SHA-256", sha256.hexdigest())
        except Exception:
            pass
        finally:
            self.finished_signal.emit()


class SearchWorker(QThread):
    result_found = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, root_path: str, query: str, case_sensitive: bool = False,
                 use_regex: bool = False, extension_filter: str = "",
                 recursive: bool = False):
        super().__init__()
        self.root_path = root_path
        self.query = query
        self.case_sensitive = case_sensitive
        self.use_regex = use_regex
        self.extension_filter = extension_filter
        self.recursive = recursive
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        threading.current_thread().name = "SearchWorker"
        import re
        import os
        try:
            search_term = self.query if self.case_sensitive else self.query.lower()
            pattern = None
            if self.use_regex:
                flags = 0 if self.case_sensitive else re.IGNORECASE
                pattern = re.compile(self.query, flags)

            if self.recursive:
                for dirpath, dirnames, filenames in os.walk(self.root_path):
                    if self._cancelled:
                        return
                    for name in filenames + dirnames:
                        if self._cancelled:
                            return
                        if self.extension_filter:
                            ext = pathlib.Path(name).suffix.lower()
                            if ext != self.extension_filter.lower():
                                continue
                        if pattern:
                            if pattern.search(name):
                                self.result_found.emit(os.path.join(dirpath, name))
                        else:
                            compare_name = name if self.case_sensitive else name.lower()
                            if search_term in compare_name:
                                self.result_found.emit(os.path.join(dirpath, name))
            else:
                try:
                    entries = os.listdir(self.root_path)
                except PermissionError:
                    return
                for name in entries:
                    if self._cancelled:
                        return
                    if self.extension_filter:
                        ext = pathlib.Path(name).suffix.lower()
                        if ext != self.extension_filter.lower():
                            continue
                    if pattern:
                        if pattern.search(name):
                            self.result_found.emit(os.path.join(self.root_path, name))
                    else:
                        compare_name = name if self.case_sensitive else name.lower()
                        if search_term in compare_name:
                            self.result_found.emit(os.path.join(self.root_path, name))
        except Exception:
            pass
        finally:
            self.finished_signal.emit()
