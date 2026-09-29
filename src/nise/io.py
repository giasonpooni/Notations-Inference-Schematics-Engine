"""Bounded JSON file I/O for NISE."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile

from .contracts import MAX_BYTES, json_tree


def _pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise ValueError("Duplicate JSON key")
        value[key] = item
    return value


def load_json(path: Path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError("NISE input must be a regular file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if not raw or len(raw) > MAX_BYTES:
        raise ValueError("NISE input exceeds 2 MiB or is empty")
    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_pairs,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    json_tree(value)
    return value


def save_new(path: Path, value) -> None:
    json_tree(value)
    raw = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("NISE output exceeds 2 MiB")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".nise-", dir=path.parent) as directory:
        staged = Path(directory) / "schematic.json"
        with staged.open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(staged, path)
