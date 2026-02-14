#!/usr/bin/env python3
import argparse
import re
from pathlib import Path


def gen_install_modules_steps(readme: Path):
    if not readme.is_file():
        raise FileNotFoundError(readme)
    lines = readme.read_text(
        encoding="utf-8", errors="surrogateescape", newline=""
    ).splitlines(keepends=True)
    env_lines = []
    state = 0
    blank = 0
    first_module_build_tiny = True
    for line in lines:
        if state == 0:
            if line.startswith("INSTALLING MODULES"):
                state = 1
        elif state == 1:
            m = re.match(r"([0-9A-Za-z:-]+)\s+([0-9.]+)(\s+\((.*)\))?\s*", line)
            if m:
                module_name = m.group(1)
                module_ver = m.group(2)
                comment1 = m.group(3)
                comment2 = m.group(4)

                comment = comment1 if comment1 is not None else ""

                file_name = module_name.replace("::", "-")
                var_name = file_name.replace("-", "_").upper() + "_VERSION"
                var_ref = "${{ env." + var_name + " }}"

                if comment2 is not None:
                    m2 = re.match(
                        r"^file ([0-9A-Za-z:-]+?)(-[0-9.]+\.tar\.gz)?$", comment2
                    )
                    if m2:
                        file_name = m2.group(1).replace("::", "-")

                if comment2 == "no tests":
                    make_commands = "perl Makefile.PL && nmake && nmake install"
                else:
                    make_commands = (
                        "perl Makefile.PL && nmake && nmake test && nmake install"
                    )

                if module_name == "Module::Build::Tiny":
                    if first_module_build_tiny:
                        first_module_build_tiny = False
                        continue
                    make_commands = (
                        "perl Build.PL && Build && Build test && Build install"
                    )

                if blank == 1:
                    print("")
                    print("      #")
                blank = 0
                print("")
                print(f"      - name: Install {module_name} {var_ref}{comment}")
                if module_name == "Win32::WinError":
                    print(
                        "        run: cp sources/WinError.pm work/inst/site/lib/Win32/"
                    )
                else:
                    print("        shell: cmd")
                    print(f"        working-directory: work\\{file_name}-{var_ref}")
                    print(f"        run: {make_commands}")

                    env_lines += [f'  {var_name}: "{module_ver}"']

            elif line.startswith("MODIFICATIONS FOR TEXLIVE"):
                state = 2
            elif line.rstrip() == "":
                if blank == 0:
                    blank = 1
            else:
                if blank != 2:
                    print("")
                print("      # " + line.rstrip())
                blank = 2
        elif state == 2:
            pass

    print("")
    print("env:")
    for line in env_lines:
        print(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("readme", type=Path, help="tlperl.README file")
    args = parser.parse_args()

    readme: Path = args.readme.expanduser().resolve()

    gen_install_modules_steps(readme)


if __name__ == "__main__":
    main()
