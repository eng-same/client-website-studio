#!/usr/bin/env python3
"""Verify a deployment ZIP the way the host will use it. Standard library only.

  verify_zip.py handover/DEPLOY-READY.zip

Checks that index.html sits at the archive root with no wrapper folder, that no skill, agent, private or
development files are inside, that the extracted site passes the release audit, and that the extracted
files really work when served over HTTP (home page, every page and every local file they reference).
Exit code 1 when anything fails.
"""
from __future__ import annotations

import argparse
import functools
import http.server
import re
import sys
import tempfile
import threading
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urljoin, urlsplit

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from audit_site import (HOST_CONFIG, PRIVATE_DIRS, SKILL_DIRS, SKILL_FILES, SKIP_EXT, SOURCE_EXT,  # noqa: E402
                        SOURCE_NAMES, WRAPPER_DIRS, audit, utf8_stdout)

REF = re.compile(r'''(?:href|src|poster)\s*=\s*["']([^"'#][^"']*)["']''', re.I)
CSS_REF = re.compile(r'''url\(\s*["']?([^"')]+)''', re.I)


def check_names(names: list[str]) -> list[str]:
    problems: list[str] = []
    files = [n for n in names if not n.endswith('/')]
    if set(files) != {'index.html'}:
        problems.append('A single-file website ZIP must contain only root index.html')
    if len(set(names)) != len(names):
        dupes = sorted({n for n in names if names.count(n) > 1})
        problems.append(f'The ZIP lists the same file twice: {", ".join(dupes[:5])}')
    if 'index.html' not in files:
        tops = {PurePosixPath(n).parts[0] for n in files if PurePosixPath(n).parts}
        if len(tops) == 1 and any(n.endswith('/index.html') for n in files):
            problems.append(f'index.html is not at the ZIP root: everything is wrapped inside "{next(iter(tops))}/". '
                            'Build the ZIP from the website files themselves, not from their parent folder')
        else:
            problems.append('index.html is not at the ZIP root')
    for name in files:
        parts = PurePosixPath(name).parts
        if '\\' in name or name.startswith('/') or '..' in parts or (parts and ':' in parts[0]):
            problems.append(f'Unsafe path inside the ZIP: {name}')
            continue
        low = [p.lower() for p in parts]
        if any(p in SKILL_DIRS for p in parts) or parts[-1] in SKILL_FILES:
            problems.append(f'Skill or agent file inside the ZIP: {name}')
        elif parts[0] in PRIVATE_DIRS:
            problems.append(f'Private project folder inside the ZIP: {name}')
        elif parts[0].lower() in WRAPPER_DIRS and len(parts) > 1 and parts[0].lower() != 'assets':
            problems.append(f'Wrapper folder "{parts[0]}/" inside the ZIP: {name}')
        elif any(p.startswith('.') for p in parts) or parts[-1] in HOST_CONFIG or 'web.config' in low:
            problems.append(f'Hidden or server configuration file inside the ZIP: {name}')
        elif parts[-1] in SOURCE_NAMES or PurePosixPath(name).suffix.lower() in SOURCE_EXT:
            problems.append(f'Source or build file inside the ZIP: {name}')
        elif PurePosixPath(name).suffix.lower() in SKIP_EXT:
            problems.append(f'Documentation, backup or archive file inside the ZIP: {name}')
    return problems


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:  # keep the report readable
        pass


def http_check(root: Path) -> list[str]:
    """Serve the extracted site and fetch the home page, every page and every local file they use."""
    handler = functools.partial(QuietHandler, directory=str(root))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f'http://127.0.0.1:{server.server_address[1]}'
    problems: list[str] = []
    seen: set[str] = set()
    queue = ['/']
    try:
        while queue:
            path = queue.pop(0)
            if path in seen:
                continue
            seen.add(path)
            try:
                with urllib.request.urlopen(base + path, timeout=10) as response:
                    body = response.read()
                    kind = response.headers.get('Content-Type', '')
            except urllib.error.HTTPError as exc:
                problems.append(f'HTTP {exc.code} for {path}')
                continue
            except OSError as exc:
                problems.append(f'Could not fetch {path}: {exc}')
                continue
            is_html = 'html' in kind
            is_css = 'css' in kind
            if not (is_html or is_css):
                continue
            text = body.decode('utf-8', errors='replace')
            refs = REF.findall(text) if is_html else CSS_REF.findall(text)
            for ref in refs:
                parts = urlsplit(ref.strip())
                if parts.scheme or ref.startswith('//') or not parts.path:
                    continue
                target = urlsplit(urljoin(base + path, parts.path)).path
                queue.append(target)
    finally:
        server.shutdown()
        server.server_close()
    if '/' not in seen:
        problems.append('Home page was not requested')
    return problems


def verify_zip(zip_path: Path, mode: str = 'release', single_language: bool = False, http: bool = True) -> list[str]:
    zip_path = Path(zip_path)
    if not zip_path.is_file():
        return [f'ZIP not found: {zip_path}']
    try:
        archive = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        return ['The file is not a valid ZIP']
    with archive:
        bad = archive.testzip()
        if bad:
            return [f'Corrupt entry in the ZIP: {bad}']
        problems = check_names(archive.namelist())
        # zipfile rewrites backslashes on Windows, so look at the names exactly as stored in the archive
        backslashed = [i.orig_filename for i in archive.infolist() if '\\' in i.orig_filename]
        if backslashed:
            problems.append('Unsafe path inside the ZIP (backslash separators; Linux and some panels would '
                            f'extract flat files with odd names): {backslashed[0]}')
        if any(p.startswith('Unsafe path') for p in problems):
            return problems
        with tempfile.TemporaryDirectory(prefix='studio-verify-') as tmp:
            root = Path(tmp)
            archive.extractall(root)
            if (root / 'index.html').is_file():
                result = audit(root, mode, single_language)
                problems += [f'Audit of the extracted ZIP: {e["file"]}: {e["problem"]}' for e in result['errors']]
                if http:
                    problems += [f'Served over HTTP: {p}' for p in http_check(root)]
    return problems


def main() -> None:
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('zip', type=Path)
    parser.add_argument('--preview', action='store_true', help='verify a preview ZIP (noindex allowed)')
    parser.add_argument('--single-language', action='store_true')
    parser.add_argument('--no-http', action='store_true', help='skip the local HTTP test')
    args = parser.parse_args()
    problems = verify_zip(args.zip, 'preview' if args.preview else 'release', args.single_language, not args.no_http)
    if problems:
        print(f'ZIP check FAILED: {args.zip}')
        for item in problems:
            print(f'  - {item}')
        raise SystemExit(1)
    print(f'ZIP check passed: {args.zip}')
    print('  index.html is at the archive root; no skill, private or development files inside;')
    print('  the extracted site passes the audit' + ('' if args.no_http else ' and every file loads over HTTP') + '.')
    print('  It can be extracted straight into httpdocs (or public_html) without moving anything afterwards.')


if __name__ == '__main__':
    main()
