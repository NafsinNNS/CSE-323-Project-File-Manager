# Advanced File Explorer with System Call Monitoring

A desktop file manager built with Python and PyQt6 that provides real-time visibility into operating system file I/O operations, demonstrating core OS concepts from the CSE 323 course.

## Features

| Feature | Description |
|---------|-------------|
| **Dual-Pane Navigation** | Directory tree + sortable file table with back/forward/up/home |
| **File Operations** | Copy, move, rename, delete, new folder/file with async progress |
| **System Call Monitor** | Real-time log of `stat`, `open`, `read`, `write`, `close`, `unlink` syscalls with timing |
| **LRU Metadata Cache** | Caches `stat()`/`listdir()` results — watch cache hits replace syscalls live |
| **Thread Visibility** | See worker threads (copy, checksum, search) making syscalls independently |
| **Checksum Calculator** | MD5, SHA-1, SHA-256 on background thread |
| **Live Search** | Type to filter files instantly, recursive search for subdirectories |
| **File Preview** | Image thumbnails, text preview, metadata display |
| **Permissions Editor** | POSIX chmod dialog for Owner/Group/Others |
| **Dark/Light Theme** | Catppuccin Mocha and Latte color schemes |

## Screenshots

```
┌──────────────┬──────────────────────────────┬────────────┐
│              │  [Back][Fwd][Up] [path bar]  │            │
│  Directory   ├──────────────────────────────┤  Preview   │
│  Tree        │  File Table (sortable)        │  Panel     │
│              │  Name | Size | Type | Date    │            │
│              ├──────────────────────────────┤            │
│              │  Search Results               │            │
├──────────────┴──────────────────────────────┴────────────┤
│  Syscalls Tab │ Threads Tab │ Cache Tab                  │
│  [12] open  /home/nafsin/file.txt  3.2µs                 │
│  [13] read  3, 65536  → 65536  1.1µs                     │
│  [cache_hit] stat('/home/nafsin/file.txt')                │
└──────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/NafsinNNS/CSE-323-Project-File-Manager.git
cd CSE-323-Project-File-Manager

# Install dependencies
pip install PyQt6 send2trash

# Run
python main.py
```

**Requirements:** Python 3.10+, Linux (tested on Ubuntu/Fedora)

## Project Structure

```
file_explorer/
├── main.py                     # Entry point — installs syscall monitor
├── core/
│   ├── syscall_monitor.py      # Patches os.* + builtins.open with logging
│   ├── lru_cache.py            # LRU metadata cache with TTL + eviction
│   ├── async_workers.py        # QThread workers for copy, checksum, search
│   ├── fs_operations.py        # File CRUD, archive, permissions, trash
│   └── search_engine.py        # Recursive search with worker thread
├── ui/
│   ├── main_window.py          # Layout, signals, toolbar, dock panels
│   ├── detail_view.py          # File table with live filter + context menus
│   ├── preview_panel.py        # Image/text preview + metadata
│   ├── navigation_bar.py       # Back/forward + address bar
│   ├── tree_view.py            # Left panel directory tree
│   ├── syscall_panel.py        # Syscalls/Threads/Cache tabs
│   └── dialogs/                # Checksum, permissions dialogs
└── utils/
    ├── helpers.py              # File type detection, format helpers
    └── styles.py               # Dark/Light Catppuccin QSS themes
```

## How the Syscall Monitor Works

The monitor patches Python's file I/O at two levels:

1. **`os.*` functions** — `os.open`, `os.read`, `os.write`, `os.close`, `os.stat`, `os.listdir`, `os.unlink`, `os.rename`, `os.mkdir`, `os.rmdir`, `os.access`, `os.chmod`
2. **`builtins.open`** — Returns a proxy wrapper that intercepts `read()`, `write()`, `close()` calls

Each intercepted call is logged with: timestamp, thread name, syscall name, arguments, return value, duration in microseconds, and any error.

## How the Cache Works

- Stores `stat()` and `listdir()` results in an in-memory LRU cache (2048 entries)
- TTL: 2 seconds (auto-expires stale entries)
- Cache hits appear as green `cache_hit` entries in the syscall log
- Cache tab shows hit rate, misses, evictions, and syscalls saved
- Invalidation on file delete, rename, new file/folder operations

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Copy |
| `Ctrl+X` | Cut |
| `Ctrl+V` | Paste |
| `F2` | Rename |
| `Delete` | Delete to trash |
| `F5` | Refresh |
| `Enter` (in search bar) | Recursive search |

## License

Academic project — CSE 323 Operating Systems Design
