import os
import pathlib


def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.2f} GB"


def get_file_type_description(path: pathlib.Path) -> str:
    suffix = path.suffix.lower()
    type_map = {
        ".txt": "Text File", ".py": "Python Script", ".json": "JSON File",
        ".md": "Markdown File", ".html": "HTML File", ".css": "CSS File",
        ".js": "JavaScript File", ".ts": "TypeScript File", ".c": "C Source",
        ".cpp": "C++ Source", ".h": "C/C++ Header", ".java": "Java Source",
        ".rs": "Rust Source", ".go": "Go Source", ".rb": "Ruby Script",
        ".sh": "Shell Script", ".bat": "Batch File", ".ps1": "PowerShell Script",
        ".xml": "XML File", ".yaml": "YAML File", ".yml": "YAML File",
        ".toml": "TOML File", ".ini": "INI File", ".cfg": "Config File",
        ".log": "Log File", ".csv": "CSV File", ".tsv": "TSV File",
        ".pdf": "PDF Document", ".doc": "Word Document", ".docx": "Word Document",
        ".xls": "Excel Spreadsheet", ".xlsx": "Excel Spreadsheet",
        ".ppt": "PowerPoint", ".pptx": "PowerPoint",
        ".png": "PNG Image", ".jpg": "JPEG Image", ".jpeg": "JPEG Image",
        ".gif": "GIF Image", ".bmp": "Bitmap Image", ".svg": "SVG Image",
        ".ico": "Icon File", ".webp": "WebP Image",
        ".mp3": "MP3 Audio", ".wav": "WAV Audio", ".flac": "FLAC Audio",
        ".mp4": "MP4 Video", ".avi": "AVI Video", ".mkv": "MKV Video",
        ".mov": "QuickTime Video", ".wmv": "WMV Video",
        ".zip": "ZIP Archive", ".tar": "TAR Archive", ".gz": "GZ Archive",
        ".tar.gz": "TAR.GZ Archive", ".tgz": "TAR.GZ Archive",
        ".bz2": "BZ2 Archive", ".xz": "XZ Archive",
        ".7z": "7-Zip Archive", ".rar": "RAR Archive",
        ".exe": "Executable", ".msi": "MSI Installer",
        ".deb": "Debian Package", ".rpm": "RPM Package",
        ".dmg": "macOS Disk Image", ".iso": "Disk Image",
        ".lock": "Lock File", ".env": "Environment File",
    }
    if path.is_dir():
        return "Folder"
    if suffix == ".gz" and path.name.endswith(".tar.gz"):
        return "TAR.GZ Archive"
    return type_map.get(suffix, f"File ({suffix})" if suffix else "File")


def is_image_file(path: pathlib.Path) -> bool:
    return path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".webp"}


def is_text_file(path: pathlib.Path) -> bool:
    text_exts = {
        ".txt", ".py", ".json", ".md", ".html", ".css", ".js", ".ts",
        ".c", ".cpp", ".h", ".java", ".rs", ".go", ".rb", ".sh", ".bat",
        ".ps1", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".log",
        ".csv", ".tsv", ".lock", ".env", ".sql", ".r", ".lua", ".php",
        ".swift", ".kt", ".scala", ".pl", ".ex", ".exs", ".erl", ".hs",
        ".vue", ".jsx", ".tsx", ".scss", ".sass", ".less", ".makefile",
        ".cmake", ".dockerfile", ".gitignore", ".editorconfig",
    }
    name_lower = path.name.lower()
    if name_lower in {"makefile", "dockerfile", "readme", "license", "changelog"}:
        return True
    return path.suffix.lower() in text_exts


def is_archive_file(path: pathlib.Path) -> bool:
    if path.suffix.lower() == ".gz" and path.name.endswith(".tar.gz"):
        return True
    return path.suffix.lower() in {".zip", ".tar", ".tgz", ".bz2", ".xz", ".7z", ".rar"}


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg", ".ico", ".webp"}
ARCHIVE_EXTENSIONS = {".zip", ".tar", ".tar.gz", ".tgz", ".gz", ".bz2", ".xz"}
