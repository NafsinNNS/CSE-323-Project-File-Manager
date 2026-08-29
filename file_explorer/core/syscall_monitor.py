import os
import io
import time
import builtins
import threading

SYSCALLS_TO_PATCH = [
    "close", "read", "write", "lseek",
    "stat", "lstat", "listdir", "mkdir", "makedirs",
    "rmdir", "unlink", "rename", "chmod", "getcwd",
    "chdir", "scandir", "remove", "replace",
]

MAX_ENTRIES = 2000


def _shorten(value, limit=120):
    text = str(value).replace("\n", "\\n")
    if len(text) > limit:
        return text[:limit] + "..."
    return text


def _format_args(args, kwargs):
    parts = [_shorten(repr(a), 60) for a in args]
    parts += [f"{k}={_shorten(repr(v), 60)}" for k, v in kwargs.items()]
    return ", ".join(parts)


class SyscallMonitor:
    _instance = None

    def __init__(self):
        self.entries = []
        self.call_counts = {}
        self.lock = threading.Lock()
        self.enabled = True
        self.listeners = []
        self.patched = False
        self.sequence = 0

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_listener(self, fn):
        self.listeners.append(fn)

    def clear(self):
        with self.lock:
            self.entries.clear()
            self.call_counts.clear()

    def _log(self, name, args_repr, result_repr, error=None, start=None):
        duration_us = int((time.perf_counter() - start) * 1_000_000) if start else 0
        now = time.time()
        with self.lock:
            self.sequence += 1
            self.call_counts[name] = self.call_counts.get(name, 0) + 1
            entry = {
                "seq": self.sequence,
                "time": time.strftime("%H:%M:%S", time.localtime(now))
                        + f".{int((now % 1) * 1000):03d}",
                "thread": threading.current_thread().name,
                "pid": os.getpid(),
                "syscall": name,
                "args": args_repr,
                "result": result_repr,
                "error": error,
                "duration_us": duration_us,
            }
            self.entries.append(entry)
            if len(self.entries) > MAX_ENTRIES:
                del self.entries[: len(self.entries) - MAX_ENTRIES]
        for fn in list(self.listeners):
            try:
                fn(entry)
            except Exception:
                pass


def _make_wrapper(monitor, name, func):
    def wrapper(*args, **kwargs):
        if not monitor.enabled:
            return func(*args, **kwargs)
        started = time.perf_counter()
        args_repr = _format_args(args, kwargs)
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            monitor._log(name, args_repr, "-", error=f"{type(exc).__name__}: {exc}", start=started)
            raise
        monitor._log(name, args_repr, _shorten(repr(result)), start=started)
        return result

    wrapper.__name__ = getattr(func, "__name__", name)
    return wrapper


class _FileProxy:
    def __init__(self, fobj, monitor, label):
        self._f = fobj
        self._monitor = monitor
        self._label = label

    def read(self, *args):
        started = time.perf_counter()
        data = self._f.read(*args)
        size = len(data) if isinstance(data, (bytes, str)) else 0
        self._monitor._log("read", f"{self._label}, {_shorten(args[0]) if args else 'EOF'}",
                           f"{size} bytes", start=started)
        return data

    def write(self, data):
        started = time.perf_counter()
        written = self._f.write(data)
        self._monitor._log("write", f"{self._label}, {len(data)} bytes",
                           f"{written} bytes", start=started)
        return written

    def close(self):
        started = time.perf_counter()
        self._f.close()
        self._monitor._log("close", self._label, "fd closed", start=started)

    def __getattr__(self, name):
        return getattr(self._f, name)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def __iter__(self):
        return iter(self._f)


def _install_open_patch(monitor):
    real_open = builtins.open

    def open_wrapper(file, mode="r", *args, **kwargs):
        started = time.perf_counter()
        fobj = real_open(file, mode, *args, **kwargs)
        label = f"{_shorten(file)}, '{mode}'"
        if isinstance(fobj, io.IOBase):
            monitor._log("open", label, "fd allocated", start=started)
            return _FileProxy(fobj, monitor, _shorten(file))
        monitor._log("open", label, _shorten(repr(fobj)), start=started)
        return fobj

    open_wrapper.__name__ = "open"
    builtins.open = open_wrapper


def install_syscall_monitor():
    monitor = SyscallMonitor.instance()
    if monitor.patched:
        return monitor
    for name in SYSCALLS_TO_PATCH:
        original = getattr(os, name, None)
        if original is None or not callable(original):
            continue
        setattr(monitor, f"_orig_{name}", original)
        setattr(os, name, _make_wrapper(monitor, name, original))
    _install_open_patch(monitor)
    monitor.patched = True
    return monitor
