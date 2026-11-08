"""Read-only privacy gate for public release documentation, folders and ZIPs."""
import argparse
import re
import sys
import stat
import zipfile
from pathlib import Path

TEXT_SUFFIXES = {".md", ".rst", ".txt", ".html", ".htm", ".json"}
PATTERNS = (
    ("personal attribution", re.compile(r"\b\u004d\u0065\u0064\u0068\u0061\u0074\b|\u0645\u062f\u062d\u062a", re.I)),
    ("private home path", re.compile(r"/Users/[^/<>\s]+/|/home/(?!runner/)[^/<>\s]+/|[A-Z]:[\\/]+Users[\\/]+[^\\/<>%\s]+[\\/]", re.I)),
    ("private workspace", re.compile(r"owner workspace|Documents[/\\]+Codex|work/(?:release[\w/-]*|windows\d+|export\d+|watermark\d+|website-release)|outputs/Agmad[\w./-]*Review", re.I)),
)

def is_document(name):
    path = Path(name)
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", "NOTICE", "SHA256SUMS"}

def check_text(label, data):
    text = data.decode("utf-8-sig")
    failures = []
    for number, line in enumerate(text.splitlines(), 1):
        for kind, pattern in PATTERNS:
            if pattern.search(line):
                # Do not echo private text into public CI logs.
                failures.append(f"{label}:{number}: {kind}")
    return failures

def check_zip(archive):
    failures = []
    for entry in archive.infolist():
        if entry.is_dir():
            continue
        for kind, pattern in PATTERNS:
            if pattern.search(entry.filename):
                failures.append(f"archive member name: {kind}")
        if is_document(entry.filename):
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError("Archive documentation must not be a symlink")
            failures.extend(check_text(entry.filename, archive.read(entry)))
    return failures

def check_paths(paths):
    failures = []
    for path in map(Path, paths):
        if not path.exists():
            raise ValueError(f"Missing release documentation input: {path.name}")
        if path.is_symlink():
            raise ValueError(f"Documentation input must not be a symlink: {path.name}")
        if path.is_dir():
            for item in sorted(path.rglob("*")):
                if ".git" in item.relative_to(path).parts:
                    continue
                if item.is_symlink():
                    # Mac packages intentionally link to Applications. Never follow directory links.
                    if is_document(item.name):
                        raise ValueError("Release documentation must not be a symlink")
                    continue
                if item.is_file() and is_document(item.name):
                    failures.extend(check_text(item.relative_to(path).as_posix(), item.read_bytes()))
        elif path.suffix.lower() == ".zip":
            with zipfile.ZipFile(path) as archive:
                failures.extend(check_zip(archive))
        elif is_document(path.name):
            failures.extend(check_text(path.name, path.read_bytes()))
        else:
            raise ValueError(f"Unsupported documentation input: {path.name}")
    if failures:
        raise ValueError("Release documentation check failed:\n" + "\n".join(failures))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        check_paths(args.paths)
    except (ValueError, UnicodeError, OSError, zipfile.BadZipFile) as error:
        print(error, file=sys.stderr)
        return 1
    print("Release documentation check passed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
