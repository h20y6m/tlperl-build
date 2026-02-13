#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


def adjust_makefile(srcdir: Path, instdir: Path):
    makefile = srcdir / "win32" / "Makefile"
    if not makefile.is_file():
        raise FileNotFoundError(makefile)
    old_lines = makefile.read_text(
        encoding="utf-8", errors="surrogateescape", newline=""
    ).splitlines(keepends=True)
    new_lines = []
    for line in old_lines:
        line = re.sub(r"^INST_DRV\s*=.*$", f"INST_DRV = {instdir.drive}", line)
        line = re.sub(r"^INST_TOP\s*=.*$", lambda _: f"INST_TOP = {instdir}", line)

        line = re.sub(r"^#USE_NO_REGISTRY\s*=.*$", "USE_NO_REGISTRY = define", line)
        line = re.sub(r"^#CCTYPE\s*=\s*MSVC143\s*$", "CCTYPE = MSVC143", line)
        line = re.sub(r"^#EMAIL\s*=.*$", "EMAIL = tex-live@tug.org", line)

        new_lines += [line]

    makefile.write_text(
        "".join(new_lines), encoding="utf-8", errors="surrogateescape", newline=""
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("srcdir", type=Path, help="Source directory to process")
    parser.add_argument("instdir", type=Path, help="Install directory")
    args = parser.parse_args()

    srcdir: Path = args.srcdir.expanduser().resolve(strict=True)
    instdir: Path = args.instdir.expanduser().resolve()

    if not srcdir.is_dir():
        print(f"[ERROR] Not a directory: {srcdir}", file=sys.stderr)
        return 1

    adjust_makefile(srcdir, instdir)


if __name__ == "__main__":
    main()
