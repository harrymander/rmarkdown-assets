#!/usr/bin/env python3

"""
Generate a basic HTML directory listing.
"""

import argparse
import sys
from pathlib import Path
from collections.abc import Iterable


TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Directory listing for {dirname}</title>
</head>
<body>
<h1>Directory listing for {dirname}</h1>
<hr>
<ul>
{paths}
</ul>
<hr>
</body>
</html>
"""


def html_path_li(path: str, is_dir: bool) -> str:
    if is_dir:
        path = f"{path.rstrip('/')}/"
    return f'<li><a href="{path}">{path}</a></li>'


def generate_dir_listing(
    prefix: str,
    root: Path,
    dir: Path,
    dirs: Iterable[str],
    files: Iterable[str],
):
    html_paths = [html_path_li(f, False) for f in files]
    html_paths.extend(html_path_li(d, True) for d in dirs)
    html_paths.sort()
    reldir = dir.relative_to(root)
    dirname = f"{prefix}{'' if reldir == Path() else reldir}"
    html = TEMPLATE.format(dirname=dirname, paths='\n'.join(html_paths))
    index_path = (dir / "index.html")
    index_path.write_text(html)
    print(f"Generated {index_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rootdir")
    parser.add_argument("--prefix", default="/")
    args = parser.parse_args()
    rootdir = Path(args.rootdir)
    prefix = f"{args.prefix.rstrip('/')}/"
    for dir, subdirs, files in rootdir.walk():
        try:
            files.remove("index.html")
            if not (files or subdirs):
                continue
        except ValueError:
            pass
        generate_dir_listing(prefix, rootdir, dir, subdirs, files)


if __name__ == '__main__':
    main()
