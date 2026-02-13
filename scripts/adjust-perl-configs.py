#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


def get_eol(line: str) -> str:
    if line.endswith("\r\n"):
        eol = "\r\n"
    elif line.endswith("\r"):
        eol = "\r"
    else:
        eol = "\n"
    return eol


def perl_escape(s: str) -> str:
    s = s.replace("\\", "\\\\")
    s = s.replace("@", "\\@")
    s = s.replace("$", "\\$")
    return s


def adjust_config_pm(instdir: Path):
    config_pm = instdir / "lib" / "Config.pm"
    if not config_pm.is_file():
        raise FileNotFoundError(config_pm)
    old_lines = config_pm.read_text(
        encoding="utf-8", errors="surrogateescape", newline=""
    ).splitlines(keepends=True)
    new_lines = []
    state = 0
    instdir_escaped = perl_escape(str(instdir))
    for line in old_lines:
        if state == 0 and line.startswith("# tie returns the object"):
            state = 1
            eol = get_eol(line)
            new_lines += [
                R"my $rootdir = __FILE__;" + eol,
                R"$rootdir =~ s![\\/][^\\/]*[\\/][^\\/]*$!!;" + eol,
                R"$rootdir =~ s!/!\\!g;" + eol,
                eol,
            ]
        if state == 1 and line.startswith("tie %Config"):
            state = 2
        if state == 2:
            if instdir_escaped in line:
                line = line.replace(instdir_escaped, "$rootdir")
                line = line.replace("'", '"')

        new_lines += [line]

    config_pm.with_suffix(".pm.orig").write_text(
        "".join(old_lines), encoding="utf-8", errors="surrogateescape", newline=""
    )
    config_pm.write_text(
        "".join(new_lines), encoding="utf-8", errors="surrogateescape", newline=""
    )


def adjust_config_heavy_pl(instdir: Path):
    config_heavy_pl = instdir / "lib" / "Config_heavy.pl"
    if not config_heavy_pl.is_file():
        raise FileNotFoundError(config_heavy_pl)
    old_lines = config_heavy_pl.read_text(
        encoding="utf-8", errors="surrogateescape", newline=""
    ).splitlines(keepends=True)
    new_lines = []
    state = 0
    instdir_escaped = perl_escape(str(instdir))
    for line in old_lines:
        if state == 0:
            if line.startswith(R"local *_ = \my $a;"):
                eol = get_eol(line)
                new_lines += [
                    R"my $rootdir = __FILE__;" + eol,
                    R"$rootdir =~ s![\\/][^\\/]*[\\/][^\\/]*$!!;" + eol,
                    R"$rootdir =~ s!/!\\!g;" + eol,
                    eol,
                ]
                state = 1
        elif state == 1:
            if line.startswith("$_ = <<'!END!';"):
                line = line.replace("'!END!'", '"!END!"')
                state = 2
        elif state == 2:
            if line.startswith("!END!"):
                state = 3
            else:
                line = perl_escape(line)
                if instdir_escaped in line:
                    line = line.replace(instdir_escaped, "$rootdir")
        elif state == 3:
            if line.startswith("ldflags_nolargefiles"):
                line = line.replace("\\", "\\\\")
                line = line.replace('"', '\\"')
                line = line.replace(instdir_escaped, "$rootdir")
                line = line.replace("'", '"')
                state = 4

        new_lines += [line]

    config_heavy_pl.with_suffix(".pl.orig").write_text(
        "".join(old_lines), encoding="utf-8", errors="surrogateescape", newline=""
    )
    config_heavy_pl.write_text(
        "".join(new_lines), encoding="utf-8", errors="surrogateescape", newline=""
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("instdir", type=Path, help="Install directory")
    args = parser.parse_args()

    instdir: Path = args.instdir.expanduser().resolve()

    if not instdir.is_dir():
        print(f"[ERROR] Not a directory: {instdir}", file=sys.stderr)
        return 1

    adjust_config_pm(instdir)
    adjust_config_heavy_pl(instdir)


if __name__ == "__main__":
    main()
