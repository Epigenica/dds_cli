#!/usr/bin/env python3
"""Rewrite default DDS endpoints in dds_cli/__init__.py (CI / local fork builds only).

Reads:
  DDS_API_BASE   — required, e.g. https://example.com/api/v1
  DDS_PUBLIC_URL — optional __url__ value; if unset, derived from DDS_API_BASE.
"""
from __future__ import annotations

import os
import pathlib
import re
import sys


def main() -> None:
    api = os.environ.get("DDS_API_BASE", "").strip()
    if not api:
        print("DDS_API_BASE is required (API base including /api/v1 if applicable).", file=sys.stderr)
        sys.exit(1)

    public = os.environ.get("DDS_PUBLIC_URL", "").strip()
    if not public:
        if "/api/v1" in api:
            public = api.split("/api/v1", 1)[0].rstrip("/") + "/"
        else:
            public = api.rstrip("/") + "/"

    path = pathlib.Path("dds_cli/__init__.py")
    if not path.is_file():
        print(f"Missing {path}", file=sys.stderr)
        sys.exit(1)

    text = path.read_text(encoding="utf-8")
    text, n_url = re.subn(
        r"^__url__\s*=\s*\"[^\"]*\"",
        f'__url__ = "{public}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, n_remote = re.subn(
        r"^(\s*)BASE_ENDPOINT_REMOTE\s*=\s*\"[^\"]*\"",
        rf'\1BASE_ENDPOINT_REMOTE = "{api}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n_url != 1 or n_remote != 1:
        print(
            f"Expected single __url__ and BASE_ENDPOINT_REMOTE assignment; got {n_url=}, {n_remote=}",
            file=sys.stderr,
        )
        sys.exit(1)

    path.write_text(text, encoding="utf-8")
    print(f"Patched __url__ -> {public!r}")
    print(f"Patched BASE_ENDPOINT_REMOTE -> {api!r}")


if __name__ == "__main__":
    main()
