# File Explorer - 5 Minute Presentation Script

## [0:00 - 0:30] Introduction
"Hello, this is my CSE 323 Operating Systems project — an Advanced File Explorer built with Python and PyQt6. It's a fully functional desktop file manager with OS-level monitoring, caching optimization, and multithreaded operations. Let me walk you through all the features."

## [0:30 - 1:15] Basic Navigation & UI
"The interface has a dual-pane layout. On the left is a directory tree for quick navigation. On the right is a file table showing Name, Size, Type, and Date Modified — all sortable by clicking column headers.

The toolbar has navigation buttons — Back, Forward, Up, Home, and Refresh — plus an address bar where you can type any path directly. There's a live filter bar that filters files as you type, and a search button for recursive search with case sensitivity and subfolder options.

The right panel is the file table, and below that is the syscall monitor. The preview panel on the far right shows file metadata, image thumbnails, and text previews when you select a file."

## [1:15 - 2:00] File Operations & Context Menu
"Right-click on any file to get a full context menu — Open, Copy, Cut, Paste, Rename, Delete, New Folder, and New File. Keyboard shortcuts work too: Ctrl+C, Ctrl+X, Ctrl+V, F2 for rename, Delete key, and F5 to refresh.

When you paste, a progress dialog appears with a cancel button. The copy operation runs in a background thread so the UI stays responsive — you can keep browsing while files copy.

You can also Calculate Checksums for any file — MD5, SHA-1, and SHA-256 — computed in a background thread. And there's a Properties dialog to view and modify POSIX file permissions — read, write, execute for Owner, Group, and Others."

## [2:00 - 2:45] Search & Recycle Bin
"The search system has two modes. Type in the filter bar and the file table filters instantly as you type — only matching files are shown. Press Enter to also search recursively through subfolders, with results appearing in the small tab below.

The recycle bin button opens the Linux Trash directory. When you delete files, they're sent to trash if possible, otherwise permanently deleted. The delete operation is logged in the syscall monitor so you can see exactly what system calls were made."

## [2:45 - 3:30] System Call Monitor
"This is the key OS feature. The system call monitor intercepts every operating system call in real time. It patches Python's built-in open, read, write, close, stat, listdir, unlink, rename, chmod, and more.

Every syscall is logged with a timestamp, thread name, arguments, return value, and execution duration in microseconds. You can see the full chain: when you copy a file, it shows stat, open with read mode, open with write mode, multiple read and write calls, close, and chmod.

There are three tabs: Syscalls shows the live log with color coding — blue for syscall names, green for worker threads, red for errors, and green text for cache hits. Threads shows all active threads with their IDs. And Cache shows the optimization statistics."

## [3:30 - 4:15] LRU Cache Optimization
"The cache tab shows the LRU metadata cache — this is my optimization feature. It caches stat and listdir results so repeated accesses don't need to go to disk.

The first time you click a file, it's a cache miss — the stat syscall fires. Click the same file again and it's a cache hit — instant, no syscall. You can watch the hit rate climb in real time as you browse.

The cache has a capacity of 2048 entries with 2-second TTL expiry. When the cache is full, Least Recently Used entries are evicted. Cache hits appear as green entries in the syscall log, and the statistics panel shows hits, misses, hit rate, evictions, and total syscalls saved.

You can enable or disable the cache from the Cache tab to see the difference — with cache off, every click triggers a syscall. With cache on, repeated accesses are served from memory."

## [4:15 - 4:45] Multithreading
"Three operations run on background threads: file copy, checksum calculation, and recursive search. Each thread is named in the syscall monitor — FileCopyWorker, ChecksumWorker, SearchWorker — so you can see which thread is making which syscalls.

The threads tab shows all active threads in real time. When you calculate checksums, you'll see the ChecksumWorker thread appear with dozens of read calls processing 64KB chunks. The UI stays completely responsive during all these operations."

## [4:45 - 5:00] Conclusion
"To summarize: this project demonstrates system calls, multithreading, LRU caching, file system operations, and POSIX permissions — all core operating systems concepts. The syscall monitor provides real-time visibility into what happens at the OS level. Thank you."
