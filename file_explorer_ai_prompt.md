# System Prompt & Specification: Advanced File Explorer (PyQt6 + Python)

> **Instructions for AI:** You are an expert Python and GUI software engineer. Follow the specifications, project structure, and step-by-step implementation plan below to build a fully functional, highly polished File Explorer application using **Python 3.10+** and **PyQt6**.

---

## 1. Project Overview & Architecture

### Goal
Build a cross-platform desktop File Explorer application with a modern user interface, asynchronous background processing for heavy I/O operations, and advanced features such as archive browsing, file hashing, and media previews.

### Target Tech Stack
* **Language:** Python 3.10+
* **GUI Framework:** `PyQt6`
* **File System Operations:** `pathlib.Path`, `os`, `shutil`
* **Concurrency:** `PyQt6.QtCore.QThread`, `QRunnable`, `QThreadPool`
* **Archive Handling:** `zipfile`, `tarfile`
* **Hashing & Security:** `hashlib`

---

## 2. Core & Advanced Feature Matrix

| Category | Feature | Technical Implementation Requirements |
| :--- | :--- | :--- |
| **Navigation** | Dual-Pane Layout | Left tree view (`QTreeView`) for quick navigation; Right table view (`QTableView`) for folder contents. |
| **Navigation** | Navigation Bar | Back, Forward, Up directory buttons, plus an interactive address bar (`QLineEdit`). |
| **File Operations** | CRUD Actions | Create folder/file, Rename, Delete (Send to Trash / Permanent), Copy, Cut, Paste. |
| **File Operations** | Async Operations | Use `QThread` or `QThreadPool` for Copy, Move, and Recursive Search with progress dialogs. |
| **View Modes** | Details & Icon Views | Sortable table columns: *Name*, *Size*, *Type*, *Date Modified*. |
| **Advanced** | Media & File Preview | Dedicated side panel showing text previews, image thumbnails, and basic metadata. |
| **Advanced** | Archive Explorer | Browse `.zip` and `.tar` archives as virtual folders and extract selected files. |
| **Advanced** | File Integrity | Context menu action to calculate MD5, SHA-1, and SHA-256 checksums in a background thread. |
| **Advanced** | Advanced Search | Multithreaded recursive search with extension filtering and regex support. |
| **Advanced** | Permissions Editor | Dialog to view/modify POSIX file permissions (`chmod`) and read-only attributes. |

---

## 3. Recommended Project Structure

```text
file_explorer/
│
├── main.py                    # Application entry point
├── requirements.txt           # Project dependencies (PyQt6, send2trash, etc.)
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py         # Main Window layout & signal connections
│   ├── navigation_bar.py      # Address bar, Back/Forward controls
│   ├── tree_view.py           # Directory Tree Panel
│   ├── detail_view.py         # File Table Panel
│   ├── preview_panel.py       # Live preview panel for text, images & metadata
│   └── dialogs/               # Modals (Checksum, Permissions, Progress)
│       ├── __init__.py
│       ├── checksum_dialog.py
│       └── permissions_dialog.py
│
├── core/
│   ├── __init__.py
│   ├── fs_operations.py       # Core filesystem wrapper (copy, move, delete, archive)
│   ├── async_workers.py       # QThread/QRunnable tasks for non-blocking I/O
│   └── search_engine.py       # Multi-threaded recursive search
│
└── utils/
    ├── __init__.py
    ├── helpers.py             # Human-readable file size formatters, icon mappers
    └── styles.py              # Dark/Light QSS stylesheets
```

---

## 4. Implementation Steps for the AI Developer

### Phase 1: Environment & Base UI Layout
1. Set up `main.py` to instantiate `QApplication` with standard settings.
2. Build `MainWindow` in `ui/main_window.py` using a `QSplitter` to divide:
   * Left panel: `QTreeView` attached to `QFileSystemModel`.
   * Center panel: `QTableView` using `QFileSystemModel` for directory listing.
   * Right panel: `PreviewPanel` (initially collapsible/hidden).
3. Add a top `QToolBar` containing Back, Forward, Up Level, Refresh, and an Address LineEdit.

### Phase 2: Core Operations & Context Menus
1. Implement double-click handling on `QTableView` to navigate into directories or open files with the default OS handler (`QDesktopServices.openUrl`).
2. Add a custom context menu (`Qt.ContextMenuPolicy.CustomContextMenu`) on the file table for:
   * **Copy / Cut / Paste** (Manage state via an internal application clipboard object).
   * **Rename** (`F2` shortcut or inline editing).
   * **Delete** (Support `send2trash` library if available, with fallback to `os.remove`/`shutil.rmtree`).
   * **New Folder / File**.

### Phase 3: Background Multithreading (`async_workers.py`)
1. **File Transfer Worker:** Create a `QThread` subclass `FileCopyWorker` that uses `shutil.copy2` or chunked read/write streams to emit `progress(int percentage)` and `finished()` signals.
2. **Progress Dialog:** Display a modal `QProgressDialog` during file transfers with a "Cancel" button that stops the worker thread gracefully.

### Phase 4: Advanced Features

#### A. File Integrity Checksum Calculator
* Create `ChecksumWorker` (`QThread`) that reads a selected file in 64KB chunks using `hashlib.md5()` and `hashlib.sha256()`.
* Show progress in a popup dialog (`ChecksumDialog`) and offer a "Copy Hash" button.

#### B. Live File Preview
* Connect `selectionChanged` signal on `QTableView` to `PreviewPanel`.
* If selected item is an image (`.png`, `.jpg`, `.svg`), scale and render it inside a `QLabel`.
* If selected item is plain text / code (`.txt`, `.py`, `.json`, `.md`), load the first 10,000 bytes into a `QTextEdit`.
* Display file size, created date, modified date, and permissions flags.

#### C. In-App Archive Browsing
* Create a virtual filesystem abstraction layer in `fs_operations.py`.
* Detect `.zip` or `.tar.gz` extensions when clicked; read archive contents using Python's native `zipfile.ZipFile` or `tarfile.open()`.
* Display archive entries inside `QTableView` with an "Extract All" or "Extract Selected" button in the toolbar.

#### D. Multithreaded Search Engine
* Build a search bar widget with options (Match Case, Regex, Extension filter).
* Run search in a background thread using `os.walk` or `pathlib.Path.rglob`. Emitting found paths dynamically to update the results table in real time without UI freezing.

#### E. File Permissions & Attributes Editor
* Build `PermissionsDialog` displaying read, write, execute checkboxes for Owner, Group, and Others on POSIX systems.
* Apply permissions using `os.chmod()` upon confirmation.

---

## 5. UI Polish & Quality Guidelines

1. **Modern Styling:** Use custom Qt Style Sheets (QSS) for clean padding, rounded borders, hover states, and subtle background highlights.
2. **Icons:** Use `QFileIconProvider` to display native OS icons for files and folders.
3. **Responsive UI:** Never execute raw disk operations like `shutil.copytree` or recursive searches directly on the main GUI thread.
4. **Error Handling:** Wrap all filesystem interactions in `try-except` blocks. Present clear, user-friendly error dialogs (`QMessageBox.critical`) when encountering `PermissionError`, `FileNotFoundError`, or disk space issues.

---

## 6. Prompt to Give to AI Code Generators

> *"Act as an expert Python desktop developer. Using the system architecture and implementation specs above, write a complete, runnable modular File Explorer project using Python 3 and PyQt6. Start by providing `requirements.txt` and `main.py`, then generate the `ui/` and `core/` modules step by step with non-blocking threading, proper signal/slot wiring, and clean QSS styling."*
