#!/usr/bin/env python3
import argparse
import re
import requests
import time
from pathlib import Path


META_URL = "https://fastapi.metacpan.org/v1/module/{}"


def gen_install_modules_steps(readme: Path):
    if not readme.is_file():
        raise FileNotFoundError(readme)
    lines = readme.read_text(
        encoding="utf-8", errors="surrogateescape", newline=""
    ).splitlines(keepends=True)
    state = 0
    for line in lines:
        if state == 0:
            if line.startswith("INSTALLING MODULES"):
                state = 1
        elif state == 1:
            m = re.match(r"([0-9A-Za-z:-]+)\s+([0-9.]+)(\s+\((.*)\))?\s*", line)
            if m:
                module_name = m.group(1)
                module_ver = m.group(2)

                if module_name.startswith("ExtUtils-"):
                    module_name = module_name.replace("-", "::")

                api_url = META_URL.format(module_name)
                print(f"API: {api_url}")
                time.sleep(1)
                res = requests.get(api_url)
                if res.status_code != 200:
                    print(f"SKIP: {module_name} {res.status_code}")
                    continue

                data = res.json()
                version = data.get("version")
                download_url = data.get("download_url")

                if not version or not download_url:
                    print(f"SKIP: {module_name}")
                    continue

                if module_ver != version:
                    print(f"UPDATE: {module_name} {module_ver} => {version}")
                    print(f"UPDATE: {module_name} {download_url}")

            elif line.startswith("MODIFICATIONS FOR TEXLIVE"):
                state = 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("readme", type=Path, help="tlperl.README file")
    args = parser.parse_args()

    readme: Path = args.readme.expanduser().resolve()

    gen_install_modules_steps(readme)


if __name__ == "__main__":
    main()
