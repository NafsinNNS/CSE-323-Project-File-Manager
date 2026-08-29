import os
import shutil
import pathlib
import zipfile
import tarfile
import stat

try:
    from send2trash import send2trash as _send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False


class ClipboardData:
    def __init__(self):
        self.paths: list[pathlib.Path] = []
        self.cut_mode: bool = False


class FileSystemOperations:
    @staticmethod
    def create_folder(path: pathlib.Path, name: str) -> pathlib.Path:
        new_path = path / name
        new_path.mkdir(exist_ok=False)
        return new_path

    @staticmethod
    def create_file(path: pathlib.Path, name: str) -> pathlib.Path:
        new_path = path / name
        new_path.touch()
        return new_path

    @staticmethod
    def rename(old_path: pathlib.Path, new_name: str) -> pathlib.Path:
        new_path = old_path.parent / new_name
        old_path.rename(new_path)
        return new_path

    @staticmethod
    def delete(path: pathlib.Path, use_trash: bool = True) -> bool:
        from core.syscall_monitor import SyscallMonitor
        monitor = SyscallMonitor.instance()
        if use_trash and HAS_SEND2TRASH:
            try:
                _send2trash(str(path))
                monitor._log("trash", str(path), "moved to recycle bin")
                return True
            except Exception:
                pass
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        return True

    @staticmethod
    def copy_file(src: pathlib.Path, dst_dir: pathlib.Path, callback=None) -> pathlib.Path:
        dst = dst_dir / src.name
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        if callback:
            callback(100)
        return dst

    @staticmethod
    def move_file(src: pathlib.Path, dst_dir: pathlib.Path, callback=None) -> pathlib.Path:
        dst = dst_dir / src.name
        shutil.move(str(src), str(dst))
        if callback:
            callback(100)
        return dst

    @staticmethod
    def copy_with_progress(src: pathlib.Path, dst_dir: pathlib.Path, progress_callback=None) -> pathlib.Path:
        if src.is_dir():
            dst = dst_dir / src.name
            shutil.copytree(src, dst)
            if progress_callback:
                progress_callback(100)
            return dst
        dst = dst_dir / src.name
        total_size = src.stat().st_size if src.exists() else 0
        copied = 0
        chunk_size = 64 * 1024
        with open(src, "rb") as fsrc, open(dst, "wb") as fdst:
            while True:
                chunk = fsrc.read(chunk_size)
                if not chunk:
                    break
                fdst.write(chunk)
                copied += len(chunk)
                if total_size > 0 and progress_callback:
                    progress_callback(int(copied * 100 / total_size))
        return dst

    @staticmethod
    def get_archive_contents(path: pathlib.Path) -> list[dict]:
        entries = []
        name_lower = path.name.lower()
        try:
            if name_lower.endswith(".zip"):
                with zipfile.ZipFile(path, "r") as zf:
                    for info in zf.infolist():
                        entries.append({
                            "name": info.filename,
                            "size": info.file_size,
                            "is_dir": info.is_dir(),
                        })
            elif name_lower.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz")):
                mode = "r:*" if name_lower.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz")) else "r"
                with tarfile.open(path, mode) as tf:
                    for member in tf.getmembers():
                        entries.append({
                            "name": member.name,
                            "size": member.size,
                            "is_dir": member.isdir(),
                        })
        except Exception:
            pass
        return entries

    @staticmethod
    def extract_archive(path: pathlib.Path, dest_dir: pathlib.Path) -> bool:
        name_lower = path.name.lower()
        try:
            if name_lower.endswith(".zip"):
                with zipfile.ZipFile(path, "r") as zf:
                    zf.extractall(dest_dir)
            elif name_lower.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tar.xz")):
                mode = "r:*" if name_lower.endswith((".tar.gz", ".tgz", ".tar.bz2", ".tar.xz")) else "r"
                with tarfile.open(path, mode) as tf:
                    tf.extractall(dest_dir)
            return True
        except Exception:
            return False

    @staticmethod
    def get_permissions(path: pathlib.Path) -> dict:
        st = path.stat()
        mode = st.st_mode
        return {
            "owner_read": bool(mode & stat.S_IRUSR),
            "owner_write": bool(mode & stat.S_IWUSR),
            "owner_exec": bool(mode & stat.S_IXUSR),
            "group_read": bool(mode & stat.S_IRGRP),
            "group_write": bool(mode & stat.S_IWGRP),
            "group_exec": bool(mode & stat.S_IXGRP),
            "other_read": bool(mode & stat.S_IROTH),
            "other_write": bool(mode & stat.S_IWOTH),
            "other_exec": bool(mode & stat.S_IXOTH),
        }

    @staticmethod
    def set_permissions(path: pathlib.Path, perms: dict) -> None:
        mode = 0
        if perms.get("owner_read"): mode |= stat.S_IRUSR
        if perms.get("owner_write"): mode |= stat.S_IWUSR
        if perms.get("owner_exec"): mode |= stat.S_IXUSR
        if perms.get("group_read"): mode |= stat.S_IRGRP
        if perms.get("group_write"): mode |= stat.S_IWGRP
        if perms.get("group_exec"): mode |= stat.S_IXGRP
        if perms.get("other_read"): mode |= stat.S_IROTH
        if perms.get("other_write"): mode |= stat.S_IWOTH
        if perms.get("other_exec"): mode |= stat.S_IXOTH
        os.chmod(path, mode)
