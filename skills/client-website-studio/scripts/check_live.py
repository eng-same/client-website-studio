#!/usr/bin/env python3
"""Check the live website with plain read-only GET requests. Standard library only.

  check_live.py https://example.ly/
  check_live.py https://example.ly/ --zip handover/DEPLOY-READY.zip

Reports whether the home page opens, whether it is a real website page rather than a host error or default
page, whether every local file the pages use loads, and (with --zip) whether the live files are byte for byte
the ones in the deployment ZIP. It changes nothing. Only say "published" after this passes.
Exit code 1 when anything fails.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlsplit

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from audit_site import utf8_stdout  # noqa: E402

REF = re.compile(r'''(?:href|src|poster)\s*=\s*["']([^"'#][^"']*)["']''', re.I)
CSS_REF = re.compile(r'''url\(\s*["']?([^"')]+)''', re.I)
HOST_PAGES = (
    (r'Server Error in .{0,40}Application', 'an ASP.NET error page from the server (existing IIS/ASP.NET configuration problem)'),
    (r'Runtime Error', 'an ASP.NET runtime error page from the server'),
    (r'<title>\s*403', 'a "403 Forbidden" page (no default document, or the folder is not readable)'),
    (r'<title>\s*404', 'a "404 Not Found" page'),
    (r'<title>\s*500', 'a "500" server error page'),
    (r'<title>\s*IIS Windows Server', 'the default IIS welcome page'),
    (r'Web Server.s Default Page|Default Web Site Page', 'the host\'s default placeholder page'),
    (r'Index of /', 'a folder listing instead of a website'),
)
UA = {'User-Agent': 'client-website-studio-check/1 (read-only)'}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def fetch(url: str, follow: bool = True, limit: int = 5):
    """Return (status, headers, body, final_url, redirect_count). Never raises for HTTP errors."""
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    request = urllib.request.Request(url, headers=UA)
    try:
        with opener.open(request, timeout=20) as response:
            return response.status, response.headers, response.read(), response.geturl(), 0
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers, exc.read() if exc.fp else b'', url, 0
    except OSError as exc:
        return 0, {}, str(exc).encode(), url, 0


def main() -> None:
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('url', help='the live address, for example https://example.ly/')
    parser.add_argument('--zip', type=Path, help='compare the live files with this deployment ZIP')
    parser.add_argument('--allow-http', action='store_true', help='testing only: accept an http:// address')
    args = parser.parse_args()

    base = args.url if args.url.endswith('/') else args.url + '/'
    host = urlsplit(base).netloc
    problems: list[str] = []
    notes: list[str] = []
    if not base.startswith('https://') and not args.allow_http:
        problems.append('The address does not use https://')

    status, headers, body, final, _ = fetch(base)
    if status == 0:
        raise SystemExit(f'Could not reach {base}: {body.decode(errors="replace")}')
    text = body.decode('utf-8', errors='replace')
    print(f'Home page: HTTP {status} {headers.get("Content-Type", "")}')
    if urlsplit(final).netloc != host or urlsplit(final).path not in ('', '/', '/index.html'):
        problems.append(f'The home page redirects somewhere else: {final}')
    if status != 200:
        problems.append(f'The home page answers HTTP {status}, not 200')
    for pattern, meaning in HOST_PAGES:
        if re.search(pattern, text, re.I) and (status != 200 or len(text) < 3000):
            problems.append(f'The home page shows {meaning}. This comes from the hosting configuration, '
                            'not from the website files')
            break
    if status == 200 and '<html' not in text.lower():
        problems.append('The home page is not an HTML page')

    seen: set[str] = set()
    queue = ['/']
    while queue and status == 200:
        path = queue.pop(0)
        if path in seen:
            continue
        seen.add(path)
        if path == '/':
            code, hdrs, content = status, headers, body
        else:
            code, hdrs, content, _, _ = fetch(urljoin(base, path.lstrip('/')))
            if code != 200:
                problems.append(f'HTTP {code} for {path}')
                continue
        kind = hdrs.get('Content-Type', '') if hdrs else ''
        if 'html' not in kind and 'css' not in kind:
            continue
        page = content.decode('utf-8', errors='replace')
        for ref in (REF.findall(page) if 'html' in kind else CSS_REF.findall(page)):
            parts = urlsplit(ref.strip())
            if parts.scheme or ref.startswith('//') or not parts.path:
                continue
            queue.append(urlsplit(urljoin(urljoin(base, path.lstrip('/')), parts.path)).path)
    print(f'Followed {len(seen)} local address(es) from the home page.')

    code = fetch(urljoin(base, 'site/index.html'))[0]
    if code == 200:
        notes.append('An old copy of the site is still online at /site/index.html; delete that folder from the hosting.')

    if args.zip:
        with zipfile.ZipFile(args.zip) as archive:
            for name in archive.namelist():
                if name.endswith('/'):
                    continue
                want = hashlib.sha256(archive.read(name)).hexdigest()
                code, _, content, _, _ = fetch(urljoin(base, name))
                if code != 200:
                    problems.append(f'{name}: HTTP {code} (not uploaded or in the wrong folder)')
                elif hashlib.sha256(content).hexdigest() != want:
                    problems.append(f'{name}: the live file differs from the ZIP (an old version is still online)')
        print(f'Compared the live files with {args.zip.name}.')

    for note in notes:
        print(f'Note: {note}')
    if problems:
        print('LIVE CHECK FAILED')
        for item in problems:
            print(f'  - {item}')
        raise SystemExit(1)
    print('LIVE CHECK PASSED: the home page and every local file it uses answer 200' + (' over HTTPS.' if base.startswith('https://') else '.'))
    print('This does not test layout on phones, translation quality or email.')


if __name__ == '__main__':
    main()
