#!/usr/bin/env python3

"""
Generate a basic HTML directory listing.
"""

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Directory listing for {dirname}</title>
</head>
<body>
<h1>Directory listing for <code>{dirname}</code></h1>
<hr>
<ul>
{paths}
</ul>
<hr>
</body>
</html>
"""

HTML_404 = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Not found</title>
</head>
<body>
<h1>Page not found</h1>
</body>
</html>
"""


def html_path_li(path: str, is_dir: bool) -> str:
    if is_dir:
        path = f"{path.rstrip('/')}/"
    return f'<li><code><a href="{path}">{path}</a></code></li>'


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
    if reldir == Path():
        dirname = prefix
    else:
        html_paths = [html_path_li("..", True), *html_paths]
        dirname = f"{prefix}{reldir}"

    html = TEMPLATE.format(dirname=dirname, paths='\n'.join(html_paths))
    index_path = (dir / "index.html")
    index_path.write_text(html)
    print(f"Generated {index_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rootdir")
    parser.add_argument("--prefix", default="/")
    parser.add_argument("--add-404", action="store_true")
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

    if args.add_404:
        path_404 = rootdir / "404.html"
        path_404.write_text(HTML_404)
        print(f"Generated {path_404}", file=sys.stderr)


if __name__ == '__main__':
    main()
