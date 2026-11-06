"""Bounded local reads; never import or execute target code."""

import os
import stat
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

EXCLUDED_DIRECTORIES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".ssh",
    ".aws",
    ".azure",
    ".gnupg",
    ".kube",
}
SENSITIVE_NAMES = {
    ".netrc",
    ".npmrc",
    "credentials.json",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "id_dsa",
    ".pypirc",
    ".git-credentials",
    "credentials",
}


@dataclass(frozen=True)
class SourceFile:
    path: str
    text: str
    sha256: str
    size: int


@dataclass
class Inventory:
    root: Path
    files: list[SourceFile]
    skipped: list[dict[str, str]]
    bytes_read: int = 0

    def coverage(self) -> dict[str, Any]:
        return {
            "files_read": len(self.files),
            "bytes_read": self.bytes_read,
            "text_bytes_admitted": sum(f.size for f in self.files),
            "skipped_count": len(self.skipped),
            "skipped": self.skipped,
            "runtime_observed": False,
            "snapshot_atomic": False,
        }


def reparse(path: Path) -> bool:
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def sensitive(name: str) -> bool:
    lower = name.lower()
    return (
        lower.startswith(".env")
        or lower in SENSITIVE_NAMES
        or lower.endswith((".pem", ".key", ".p12", ".pfx"))
    )


def collect(
    target: str | Path,
    *,
    max_files: int = 10000,
    max_bytes: int = 1_000_000,
    max_total_bytes: int = 32_000_000,
) -> Inventory:
    if min(max_files, max_bytes, max_total_bytes) < 1:
        raise ValueError("Inventory limits must be positive")
    supplied = Path(target).absolute()
    if not supplied.is_dir() or reparse(supplied):
        raise ValueError("Target must be an existing directory, not a link")
    root = supplied.resolve()
    inventory = Inventory(root, [], [])
    stack = [(root, 0)]
    examined = 0
    total = 0
    while stack:
        directory, depth = stack.pop()
        try:
            entries = []
            remaining = max_files * 4 - examined
            with os.scandir(directory) as iterator:
                for entry in iterator:
                    entries.append(Path(entry.path))
                    if len(entries) > remaining:
                        break
            entries.sort(key=lambda p: p.name)
        except OSError:
            inventory.skipped.append(
                {"path": str(directory.relative_to(root)), "reason": "unreadable-directory"}
            )
            continue
        for path in entries:
            examined += 1
            rel = path.relative_to(root).as_posix()
            if examined > max_files * 4 or len(inventory.files) >= max_files:
                inventory.skipped.append(
                    {"path": rel, "reason": "entry-budget-exhausted; remaining entries unknown"}
                )
                return inventory
            try:
                if reparse(path) or not path.resolve().is_relative_to(root):
                    reason = "link-or-reparse-point"
                elif path.is_dir():
                    if path.name in EXCLUDED_DIRECTORIES or depth >= 32:
                        inventory.skipped.append(
                            {"path": rel, "reason": "excluded-directory-or-depth-limit"}
                        )
                    else:
                        stack.append((path, depth + 1))
                    continue
                elif not path.is_file():
                    reason = "special-file"
                elif sensitive(path.name):
                    reason = "credential-file-excluded"
                else:
                    before = path.lstat()
                    if before.st_nlink > 1:
                        reason = "hardlinked-file"
                    elif before.st_size > max_bytes or total + before.st_size > max_total_bytes:
                        reason = "byte-budget"
                    else:
                        flags = (
                            os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
                        )
                        fd = os.open(path, flags)
                        with os.fdopen(fd, "rb") as stream:
                            opened = os.fstat(stream.fileno())
                            if not stat.S_ISREG(opened.st_mode) or (
                                opened.st_dev,
                                opened.st_ino,
                            ) != (before.st_dev, before.st_ino):
                                raise OSError("File identity changed")
                            raw = stream.read(max_bytes + 1)
                            total += len(raw)
                            inventory.bytes_read += len(raw)
                            after = os.fstat(stream.fileno())
                        if len(raw) > max_bytes or (after.st_mtime_ns, after.st_size) != (
                            before.st_mtime_ns,
                            before.st_size,
                        ):
                            reason = "changed-during-read-or-limit"
                        else:
                            try:
                                text = raw.decode("utf-8-sig")
                                if "\x00" in text:
                                    raise UnicodeError("binary")
                            except UnicodeError:
                                reason = "binary-or-unsupported-encoding"
                            else:
                                inventory.files.append(
                                    SourceFile(rel, text, sha256(raw).hexdigest(), len(raw))
                                )
                                continue
                inventory.skipped.append({"path": rel, "reason": reason})
            except OSError:
                inventory.skipped.append({"path": rel, "reason": "read-or-identity-error"})
    inventory.files.sort(key=lambda item: item.path)
    inventory.skipped.sort(key=lambda item: (item["path"], item["reason"]))
    return inventory
