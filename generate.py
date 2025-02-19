#!/usr/bin/env python3

"""
Generate a basic HTML directory listing.
"""

import argparse
import subprocess
import sys
from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import quote as urlquote

TEMPLATE = """\
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Directory listing for {dirname}</title>
  <style>html {{ color-scheme: light dark; }}</style>
</head>
<body>
<h1>Directory listing for <code>{dirname}</code></h1>
<hr>
<pre>
{paths}
</pre>
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
  <style>html {{ color-scheme: light dark; }}</style>
</head>
<body>
<h1>Page not found</h1>
<p>Root directory: <a href="{prefix}">{prefix}</a></p>
</body>
</html>
"""


def html_escape(s: str) -> str:
    return (
        s
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


PATH_MAX_WIDTH = 50


def path_mtime(path: Path) -> datetime:
    """
    Get modification date of path from git, falling back to system mtime if not
    tracked in git.
    """
    r = subprocess.run(
        ("git", "log", "-1", "--pretty=format:%ct", "--", path),
        check=True,
        stdout=subprocess.PIPE,
    )
    if not r.stdout or r.stdout.isspace():
        timestamp = path.stat().st_mtime
        print(
            f"Warning: cannot find git modification time for '{path}'",
            file=sys.stderr,
        )
    else:
        timestamp = int(r.stdout)

    return datetime.fromtimestamp(timestamp, UTC)


def html_path_listing(path: Path, is_dir: bool) -> str:
    name = path.name
    width = PATH_MAX_WIDTH - 1 if is_dir else PATH_MAX_WIDTH
    if len(name) > width:
        display_name = f"{name[:width - 3]}..."
    else:
        display_name = name
    if is_dir:
        display_name = f"{display_name}/"

    link = (
        f'<a href="{urlquote(name)}" '
        f'title="{html_escape(name)}{'/' if is_dir else ''}">'
        f'{html_escape(display_name)}</a>'
    )
    date = path_mtime(path).strftime("%Y-%m-%d %H:%M:%S %Z")
    padding = ' ' * (PATH_MAX_WIDTH - len(display_name))
    size = "" if is_dir else f" {path.stat().st_size:>10}"
    return f"{link}{padding} {date}{size}"


def generate_dir_listing(
    prefix: str,
    root: Path,
    dir: Path,
    dirs: Iterable[str],
    files: Iterable[str],
):
    html_paths = [html_path_listing(dir / f, False) for f in files]
    html_paths.extend(html_path_listing(dir / d, True) for d in dirs)
    html_paths.sort()
    reldir = dir.relative_to(root)
    if reldir == Path():
        dirname = prefix
    else:
        html_paths = ['<a href="..">../</a>', *html_paths]
        dirname = f"{prefix}{reldir}"

    html = TEMPLATE.format(dirname=dirname, paths='\n'.join(html_paths))
    index_path = (dir / "index.html")
    index_path.write_text(html)
    print(f"Generated {index_path}", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("rootdir")
    parser.add_argument("--prefix", default="/")
    parser.add_argument(
        "--404",
        default="404.html",
        help=(
            "Path to 404 file relative to rootdir; "
            "does not generate if empty."
        ),
    )
    args = parser.parse_args()
    rootdir = Path(args.rootdir)
    prefix = f"{args.prefix.rstrip('/')}/"
    filename_404 = getattr(args, "404")
    if filename_404:
        path_404 = rootdir / filename_404
        if not path_404.resolve().is_relative_to(rootdir.resolve()):
            raise ValueError("--404 path must be inside rootdir")
    else:
        path_404 = None

    for dir, subdirs, files in rootdir.walk():
        try:
            files.remove("index.html")
            if not (files or subdirs):
                continue
        except ValueError:
            pass
        generate_dir_listing(prefix, rootdir, dir, subdirs, files)

    if path_404:
        path_404.write_text(HTML_404.format(prefix=prefix))
        print(f"Generated {path_404}", file=sys.stderr)


if __name__ == '__main__':
    main()
