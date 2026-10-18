#!/usr/bin/env python3
"""Static source audit for client websites. Standard library only.

Reads source files; it is not a visual, accessibility or compliance test.

Modes:
  release (default)  [[NEEDS]] markers and noindex tags are errors.
  preview            they are warnings, so work-in-progress previews can be built.

Exit code 1 when any error is found.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

SKIP_DIRS = {'.git', '.svn', 'node_modules', '__pycache__'}
# Working folders of a client project. They live next to the website files but are never part of the site.
PRIVATE_DIRS = {'client', 'brand', 'concepts', 'review', 'feedback', 'handover', 'preview', 'versions'}
# Folders and files that belong to the skill or to an agent. They must never sit inside a client project.
SKILL_DIRS = {'.studio-kit', 'client-website-studio', '.claude', '.agents', '.codex'}
SKILL_FILES = {'SKILL.md', 'START.md', 'STARTING-PROMPT.md', 'audit_site.py', 'package_site.py',
               'serve_preview.py', 'check_layout.py', 'verify_zip.py', 'normalize_project.py'}
# Names a wrapper around the real website tends to have.
WRAPPER_DIRS = {'site', 'www', 'public', 'public_html', 'httpdocs', 'dist', 'build', 'test', 'website'}
SKIP_NAMES = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}
SKIP_EXT = {'.md', '.log', '.bak', '.tmp', '.zip', '.map'}
HOST_CONFIG = {'web.config', '.htaccess'}
LOCAL_PATH = re.compile(r'(?<![A-Za-z0-9])[A-Za-z]:[\\/](?![\\/])[\w .-]+[\\/]|file:///')
REDIRECT = re.compile(r'''(?i)<meta[^>]+http-equiv=["']?refresh|location\.(?:href|replace|assign)|location\s*=''')
PLACEHOLDER_PAGE = re.compile(
    r'(?i)\b(?:hello,?\s+world|coming soon|under construction|it works!?|welcome to nginx|'
    r'default web site page|site is being built)\b')
VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
             'param', 'source', 'track', 'wbr'}
SECTION_TAGS = {'header', 'section', 'footer'}
IMAGE_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.avif', '.svg'}

MARKER = re.compile(r'\[\[[^\]]*\]\]')
PLACEHOLDER = re.compile(
    r'(?i)\blorem ipsum\b|\b(?:todo|tbd|fixme)\b|\bexample\.(?:com|org|net)\b|\b123456789\b|x{4,}')
BANK_CLAIM = re.compile(
    r'(?i)'
    r'\bcbl[\s-]*(?:compliant|approved|certified|accredited)'
    r'|central\s+bank(?:\s+of\s+libya)?[\s-]*(?:compliant|approved|certified|accredited)'
    r'|(?:approved|certified|accredited)\s+by\s+(?:the\s+)?central\s+bank'
    r'|compl(?:y|ies|iant|iance)\s+with\s+(?:the\s+)?(?:requirements\s+of\s+(?:the\s+)?)?central\s+bank'
    r'|متوافق\S*\s+(?:مع\s+)?(?:متطلبات|شروط|اشتراطات|معايير)\s+(?:مصرف\s+ليبيا|المصرف)\s+المركزي'
    r'|(?:معتمد|مُعتمد|مرخص)\S*\s+(?:من|لدى)\s+(?:قبل\s+)?(?:مصرف\s+ليبيا|المصرف)\s+المركزي'
    r'|(?:حسب|وفق|وفقا\S*)\s+(?:متطلبات|شروط|اشتراطات)\s+(?:مصرف\s+ليبيا|المصرف)\s+المركزي')
BANK_MENTION = re.compile(r'(?i)central\s+bank|\bcbl\b|مصرف\s+ليبيا\s+المركزي|المصرف\s+المركزي')
SECRET = re.compile(
    r'(?i)-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'
    r'|(?:password|passwd|secret|api[_-]?key|access[_-]?token)\s*[:=]\s*["\']?[A-Za-z0-9_!@$#%^&*.-]{8,}')
CSS_URL = re.compile(r'url\(\s*(["\']?)(.*?)\1\s*\)', re.I | re.S)
CSS_IMPORT = re.compile(r'@import\s+(["\'])(.*?)\1', re.I)
FREE_MAIL = {'gmail.com', 'googlemail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com',
             'icloud.com', 'aol.com', 'yandex.com', 'mail.com', 'proton.me', 'protonmail.com'}
SENSITIVE_EXT = {'.env', '.pem', '.key', '.p12', '.pfx', '.kdbx'}
SENSITIVE_NAMES = {'.htpasswd', 'id_rsa', 'id_ed25519', 'credentials.json'}
SOURCE_EXT = {'.ts', '.tsx', '.jsx', '.vue', '.svelte', '.scss', '.sass', '.less', '.php', '.py'}
SOURCE_NAMES = {'package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'composer.json'}
LIMITATIONS = ('Source files only. Not a visual check, accessibility certification, translation review, '
               'security scan, live publishing test or regulatory compliance check.')


def utf8_stdout() -> None:
    """Avoid crashes when printing Arabic on a Windows console."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass


def walk_site(root: Path, include_hidden: bool = False) -> tuple[list[Path], list[str]]:
    """Files that belong to the website, and notes about what was left out.

    Project working folders, skill and agent folders, hidden files and non-website files are never included.
    The packager ships exactly this list, and the audit checks exactly this list.
    """
    files: list[Path] = []
    notes: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        here = Path(dirpath)
        top = here == root
        keep = []
        for name in sorted(dirnames):
            if name in SKIP_DIRS or name in SKILL_DIRS:
                continue
            if top and name in PRIVATE_DIRS:
                continue
            if name.startswith('.') and not include_hidden:
                notes.append(f'{(here / name).relative_to(root).as_posix()}/ (hidden folder)')
                continue
            keep.append(name)
        dirnames[:] = keep
        for name in sorted(filenames):
            path = here / name
            relpath = path.relative_to(root).as_posix()
            if name in SKIP_NAMES:
                continue
            if name in HOST_CONFIG:
                notes.append(f'{relpath} (server configuration; never shipped, handle it with the host)')
                continue
            if name.startswith('.') and not include_hidden:
                notes.append(f'{relpath} (hidden file)')
                continue
            if path.suffix.lower() in SKIP_EXT and not include_hidden:
                notes.append(f'{relpath} (not a website file)')
                continue
            files.append(path)
    return files, notes


def find_skill_contamination(root: Path) -> list[str]:
    """Skill or agent files found anywhere inside the project (the skill must live outside it)."""
    found: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        here = Path(dirpath)
        keep = []
        for name in sorted(dirnames):
            if name in ('.git', 'node_modules', '__pycache__'):
                continue
            if name in ('.claude', '.agents', '.codex'):
                if (here / name / 'skills').is_dir():
                    found.append((here / name / 'skills').relative_to(root).as_posix() + '/')
                continue
            if name in SKILL_DIRS:
                found.append((here / name).relative_to(root).as_posix() + '/')
                continue
            keep.append(name)
        dirnames[:] = keep
        for name in filenames:
            if name in SKILL_FILES:
                found.append((here / name).relative_to(root).as_posix())
    return found


def find_nested_site(root: Path) -> list[str]:
    """Top-level folders that look like a second copy of the website (e.g. site/index.html)."""
    nested = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith('.') or child.name in PRIVATE_DIRS or child.name in SKIP_DIRS:
            continue
        if child.name in ('ar', 'en', 'assets'):
            continue
        if (child / 'index.html').is_file() and (child.name in WRAPPER_DIRS or (child / 'assets').is_dir()):
            nested.append(child.name)
    return nested


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: Counter = Counter()
        self.stack: list[str] = []
        self.refs: list[tuple[str, str, str, dict]] = []
        self.images: list[dict] = []
        self.anchors: list[dict] = []
        self.ids: Counter = Counter()
        self.lang = None
        self.direction = None
        self.has_viewport = False
        self.noindex = False
        self.sections = 0
        self.sections_named = 0
        self.text: list[str] = []
        self.attr_text: list[str] = []
        self.styles: list[str] = []
        self._skip_text = 0
        self._in_style = False

    def handle_starttag(self, tag, attrs):
        d = {k: (v or '') for k, v in attrs}
        self.tags[tag] += 1
        if tag == 'html':
            self.lang = d.get('lang') or None
            self.direction = (d.get('dir') or '').lower() or None
        if tag == 'meta':
            name = d.get('name', '').lower()
            if name == 'viewport':
                self.has_viewport = True
            if name == 'robots' and 'noindex' in d.get('content', '').lower():
                self.noindex = True
        if d.get('id'):
            self.ids[d['id']] += 1
        if tag in SECTION_TAGS:
            if not any(t in SECTION_TAGS or t in ('article', 'aside', 'nav') for t in self.stack):
                self.sections += 1
                if d.get('data-section', '').strip():
                    self.sections_named += 1
        if tag == 'img':
            self.images.append(d)
        if tag == 'a':
            self.anchors.append(d)
        for key in ('href', 'src', 'poster', 'data', 'action'):
            if d.get(key) and tag in ('a', 'link', 'script', 'img', 'source', 'video', 'audio',
                                      'iframe', 'embed', 'object', 'track', 'form', 'area'):
                self.refs.append((tag, key, d[key].strip(), d))
        if d.get('srcset') and tag in ('img', 'source'):
            for part in d['srcset'].split(','):
                url = part.strip().split(' ')[0]
                if url:
                    self.refs.append((tag, 'srcset', url, d))
        if d.get('style'):
            self.styles.append(d['style'])
        for key in ('alt', 'title', 'aria-label', 'content', 'placeholder', 'value'):
            if d.get(key):
                self.attr_text.append(d[key])
        if tag in ('script', 'style', 'noscript', 'template'):
            self._skip_text += 1
        if tag == 'style':
            self._in_style = True
        if tag not in VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS and self.stack and self.stack[-1] == tag:
            self.stack.pop()
            if tag in ('script', 'style', 'noscript', 'template'):
                self._skip_text -= 1

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript', 'template') and self._skip_text:
            self._skip_text -= 1
        if tag == 'style':
            self._in_style = False
        if tag in self.stack:
            while self.stack:
                if self.stack.pop() == tag:
                    break

    def handle_data(self, data):
        if self._in_style:
            self.styles.append(data)
        elif not self._skip_text:
            self.text.append(data)


class Report:
    def __init__(self, root: Path, mode: str) -> None:
        self.root = root
        self.mode = mode
        self.errors: list[dict] = []
        self.warnings: list[dict] = []
        self.pages: list[str] = []
        self.referenced: set[Path] = set()

    def error(self, file: str, problem: str) -> None:
        self.errors.append({'file': file, 'problem': problem})

    def warn(self, file: str, problem: str) -> None:
        self.warnings.append({'file': file, 'problem': problem})

    def by_mode(self, file: str, problem: str) -> None:
        (self.error if self.mode == 'release' else self.warn)(file, problem)

    def result(self) -> dict:
        return {
            'site': str(self.root),
            'mode': self.mode,
            'status': 'FAIL' if self.errors else 'PASS',
            'pages_checked': self.pages,
            'errors': self.errors,
            'warnings': self.warnings,
            'limitations': LIMITATIONS,
        }


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def points_into_dev_folder(target: Path, root: Path) -> bool:
    try:
        first = target.resolve().relative_to(root.resolve()).parts[0]
    except (ValueError, IndexError):
        return False
    return first in PRIVATE_DIRS or first in SKILL_DIRS or first in WRAPPER_DIRS


def resolve_local(raw: str, base: Path, root: Path):
    """Return (target_path, problem) for a local reference, or (None, None) if not local."""
    parts = urlsplit(raw)
    if parts.scheme or raw.startswith('//'):
        return None, None
    path = unquote(parts.path)
    if not path:
        return None, None
    if path.startswith('/'):
        target = root / path.lstrip('/')
    else:
        target = base / path
    try:
        target.resolve().relative_to(root.resolve())
    except ValueError:
        return target, 'escapes'
    if target.is_dir():
        target = target / 'index.html'
    return target, None


def check_ref(report: Report, file: Path, tag: str, key: str, raw: str, attrs: dict) -> None:
    root = report.root
    name = rel(file, root)
    low = raw.lower()
    if low.startswith('javascript:'):
        report.error(name, f'Link that does nothing: {raw[:80]}')
        return
    if low.startswith(('data:', 'blob:', 'sms:', 'whatsapp:')):
        return
    if low.startswith('mailto:'):
        address = unquote(raw[7:].split('?')[0]).strip()
        domain = address.rsplit('@', 1)[-1].lower() if '@' in address else ''
        if not address or '@' not in address:
            report.error(name, f'Email link without an address: {raw[:80]}')
        elif domain in FREE_MAIL:
            report.warn(name, f'Email uses {domain}; prefer a mailbox on the client\'s own domain: {address}')
        return
    if low.startswith('tel:'):
        number = re.sub(r'[\s().-]', '', unquote(raw[4:]))
        if not number.startswith('+'):
            report.warn(name, f'Phone link without country code (+218…): {raw}')
        if not re.fullmatch(r'\+?\d{6,15}', number):
            report.error(name, f'Phone link is not a valid number: {raw}')
        return
    if raw.startswith('#'):
        return
    parts = urlsplit(raw)
    if parts.scheme in ('http', 'https') or raw.startswith('//'):
        host = (parts.netloc or '').lower()
        if host in ('wa.me', 'www.wa.me'):
            number = parts.path.strip('/')
            if number and not re.fullmatch(r'[1-9]\d{6,14}', number):
                report.warn(name, f'WhatsApp link should be digits only with country code, no + or leading 0: {raw}')
        elif host.endswith('whatsapp.com') and 'phone' in parse_qs(parts.query):
            number = parse_qs(parts.query)['phone'][0]
            if not re.fullmatch(r'[1-9]\d{6,14}', number):
                report.warn(name, f'WhatsApp link phone should be digits only with country code: {raw}')
        rel_attr = attrs.get('rel', '').lower()
        if tag == 'link' and any(r in rel_attr for r in ('canonical', 'alternate')):
            return
        if tag != 'a' and key != 'action':
            report.warn(name, f'External resource needs the client\'s approval and an online test: {raw[:120]}')
        return
    if parts.scheme:
        return
    target, problem = resolve_local(raw, file.parent, root)
    if target is None:
        return
    if problem == 'escapes':
        report.error(name, f'Path leaves the site folder: {raw}')
        return
    report.referenced.add(target.resolve())
    if points_into_dev_folder(target, root):
        report.error(name, f'Points into a development or wrapper folder that is not part of the website: {raw}')
    if parts.path.startswith('/'):
        report.error(name, f'Path starts with "/"; use a relative path so previews in a subfolder work: {raw}')
    elif tag == 'a' and parts.path.endswith('/'):
        report.warn(name, f'Link points to a folder; link to the file (…/index.html) so a preview opened from disk works: {raw}')
    if not target.is_file():
        report.error(name, f'Broken local reference: {raw}')


def check_css_text(report: Report, css: str, base: Path, owner: str) -> None:
    urls = [m.group(2).strip() for m in CSS_URL.finditer(css)]
    urls += [m.group(2).strip() for m in CSS_IMPORT.finditer(css)]
    for raw in urls:
        if not raw or raw.startswith(('#', 'data:')):
            continue
        parts = urlsplit(raw)
        if parts.scheme in ('http', 'https') or raw.startswith('//'):
            report.warn(owner, f'Stylesheet loads an external file; self-host it or get approval: {raw[:120]}')
            continue
        if parts.scheme:
            continue
        target, problem = resolve_local(raw, base, report.root)
        if target is None:
            continue
        if not problem:
            report.referenced.add(target.resolve())
            if points_into_dev_folder(target, report.root):
                report.error(owner, f'Stylesheet points into a development folder: {raw}')
        if problem == 'escapes':
            report.error(owner, f'Stylesheet path leaves the site folder: {raw}')
        elif parts.path.startswith('/'):
            report.error(owner, f'Stylesheet path starts with "/"; use a relative path: {raw}')
            if not target.is_file():
                report.error(owner, f'Stylesheet references a missing file: {raw}')
        elif not target.is_file():
            report.error(owner, f'Stylesheet references a missing file: {raw}')


def links_to(page: Page, file: Path, target: Path, root: Path) -> bool:
    for anchor in page.anchors:
        href = anchor.get('href', '')
        resolved, problem = resolve_local(href, file.parent, root) if href else (None, None)
        if resolved is not None and not problem and resolved.resolve() == target.resolve():
            return True
    return False


def check_page(report: Report, file: Path) -> Page:
    root = report.root
    name = rel(file, root)
    report.pages.append(name)
    data = file.read_text(encoding='utf-8-sig', errors='replace')
    page = Page()
    try:
        page.feed(data)
        page.close()
    except Exception as exc:  # html.parser rarely raises, but never crash the audit
        report.error(name, f'HTML could not be read: {exc}')
        return page

    if not re.search(r'<!doctype\s+html', data, re.I):
        report.warn(name, 'Missing <!doctype html>')
    if not page.lang:
        report.error(name, 'Missing lang on <html>')
    else:
        base = page.lang.split('-')[0].lower()
        if base in ('ar', 'en'):
            want = 'rtl' if base == 'ar' else 'ltr'
            if page.direction != want:
                report.error(name, f'Expected dir="{want}" for lang="{page.lang}"')
    if page.tags['title'] != 1:
        report.error(name, f'Expected one <title>, found {page.tags["title"]}')
    if not page.has_viewport:
        report.warn(name, 'Missing viewport meta tag')
    if page.tags['main'] == 0 and name != 'index.html':
        report.warn(name, 'No <main> landmark')
    if page.tags['h1'] != 1 and name != 'index.html':
        report.warn(name, f'Expected one <h1>, found {page.tags["h1"]}')
    dupes = [i for i, n in page.ids.items() if n > 1]
    if dupes:
        report.warn(name, f'Duplicate id values: {", ".join(sorted(dupes)[:8])}')
    if page.sections and page.sections_named < page.sections:
        report.warn(name, f'{page.sections - page.sections_named} of {page.sections} top-level '
                          'header/section/footer elements have no data-section name (used in review notes)')
    for i, img in enumerate(page.images, 1):
        if 'alt' not in img:
            report.error(name, f'Image {i} ({img.get("src", "?")[:60]}) has no alt attribute')
    for anchor in page.anchors:
        href = anchor.get('href', '').strip()
        if not href or href == '#':
            report.error(name, f'Link that goes nowhere: href="{href}"')
        elif href.startswith('#') and unquote(href[1:]) not in page.ids:
            report.warn(name, f'On-page link target not found: {href}')

    for tag, key, raw, attrs in page.refs:
        check_ref(report, file, tag, key, raw, attrs)
    for css in page.styles:
        check_css_text(report, css, file.parent, name)

    visible = ' '.join(page.text + page.attr_text)
    markers = sorted(set(MARKER.findall(visible)))
    if markers:
        report.by_mode(name, f'Unresolved [[…]] markers: {"; ".join(m[:60] for m in markers[:5])}')
    if PLACEHOLDER.search(visible):
        report.warn(name, f'Possible placeholder text: "{PLACEHOLDER.search(visible).group(0)}"')
    claim = BANK_CLAIM.search(visible)
    if claim:
        report.error(name, f'Central Bank compliance or approval claim is not allowed: "{claim.group(0)}"')
    elif BANK_MENTION.search(visible):
        report.warn(name, 'Mentions the Central Bank; make sure the wording makes no compliance claim')
    if SECRET.search(data):
        report.error(name, 'Possible password, key or token in the page; remove it')
    if page.noindex:
        report.by_mode(name, 'Page tells search engines not to index it (noindex); remove before release')
    return page


def visible_text(page: Page) -> str:
    return re.sub(r'\s+', ' ', ' '.join(page.text)).strip()


def check_structure(report: Report, root: Path) -> None:
    """Project-level safeguards: skill files, wrapper folders and a real root page."""
    for item in find_skill_contamination(root):
        report.error(item, 'Skill or agent files must never be inside the client project. '
                           'Run normalize_project.py, or move them out of the project')
    nested = find_nested_site(root)
    for name in nested:
        if (root / 'index.html').is_file():
            report.error(f'{name}/index.html', 'A second copy of the website sits in a wrapper folder. '
                                               'The website must live directly in the project root; run normalize_project.py')
        else:
            report.error(f'{name}/index.html', 'The website is inside a wrapper folder instead of the project root. '
                                               'Run normalize_project.py to move it up safely')
    if not (root / 'index.html').is_file() and not nested:
        report.error('index.html', 'Missing index.html at the site root')
    if root.name.lower() in WRAPPER_DIRS and not (root / 'index.html').is_file():
        report.warn('.', f'The folder is named "{root.name}"; check that this is the real project root')


def check_root_page(report: Report, page: Page, data: str) -> None:
    text = visible_text(page)
    if len(text) < 15 or (not page.anchors and page.sections == 0 and page.tags['main'] == 0):
        report.error('index.html', 'The root index.html looks empty; it must be a real, working page')
    if PLACEHOLDER_PAGE.search(text):
        report.error('index.html', f'The root index.html is a placeholder page: "{PLACEHOLDER_PAGE.search(text).group(0)}"')
    if REDIRECT.search(data) and len(text) < 60:
        report.error('index.html', 'The root index.html only redirects. Make it a real page '
                                   '(the main-language homepage or a language chooser) instead of a redirect')


def check_languages(report: Report, root: Path, pages: dict, single_language: bool) -> None:
    by_lang: dict[str, tuple[str, Path]] = {}
    for code in ('ar', 'en'):
        path = root / code / 'index.html'
        if path.is_file():
            by_lang[code] = (f'{code}/index.html', path)
        elif 'index.html' in pages and (pages['index.html'].lang or '').split('-')[0].lower() == code:
            by_lang[code] = ('index.html', root / 'index.html')
    if single_language:
        return
    for code in ('ar', 'en'):
        if code not in by_lang:
            report.by_mode(f'{code}/index.html',
                           'Language page is missing (needed for a bilingual site; pass --single-language only '
                           'if the client agreed to one language)')
    if len(by_lang) < 2:
        return
    names = {'ar': 'Arabic', 'en': 'English'}
    for code, (name, path) in by_lang.items():
        other = 'en' if code == 'ar' else 'ar'
        if not links_to(pages[name], path, by_lang[other][1], root):
            report.by_mode(name, f'No link to the {names[other]} page ({by_lang[other][0]})')


def check_duplicates_and_unused(report: Report, root: Path, files: list[Path], texts: dict[Path, str]) -> None:
    seen: dict[str, Path] = {}
    for file in files:
        if file.stat().st_size == 0:
            continue
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        if digest in seen:
            report.by_mode(rel(file, root), f'Duplicate of {rel(seen[digest], root)}; keep one copy')
        else:
            seen[digest] = file
    blob = '\n'.join(texts.values())
    exempt_names = {'robots.txt', 'sitemap.xml', 'manifest.webmanifest', '404.html', 'ads.txt', 'humans.txt'}
    checked_ext = IMAGE_EXT | {'.css', '.js', '.woff', '.woff2', '.ttf', '.otf', '.ico', '.mp4', '.webm'}
    for file in files:
        suffix = file.suffix.lower()
        if suffix not in checked_ext or file.name.lower() in exempt_names or file.name.lower().startswith('favicon'):
            continue
        if file.resolve() in report.referenced or file.name in blob:
            continue
        report.by_mode(rel(file, root), 'File is not used by any page; remove it so the ZIP stays clean')


def audit(root: Path, mode: str = 'release', single_language: bool = False) -> dict:
    root = root.resolve()
    report = Report(root, mode)
    check_structure(report, root)

    files, _ = walk_site(root)
    everything, _ = walk_site(root, include_hidden=True)
    pages: dict[str, Page] = {}
    texts: dict[Path, str] = {}
    for file in files:
        suffix = file.suffix.lower()
        if suffix in ('.html', '.htm'):
            pages[rel(file, root)] = check_page(report, file)
            texts[file] = file.read_text(encoding='utf-8-sig', errors='replace')
        elif suffix in ('.css', '.js'):
            texts[file] = file.read_text(encoding='utf-8-sig', errors='replace')
            if suffix == '.css':
                check_css_text(report, texts[file], file.parent, rel(file, root))
            elif SECRET.search(texts[file]):
                report.error(rel(file, root), 'Possible password, key or token in a script; remove it')
        if suffix in ('.html', '.htm', '.css', '.js') and LOCAL_PATH.search(texts[file]):
            report.error(rel(file, root), f'Contains a path on a local computer: "{LOCAL_PATH.search(texts[file]).group(0)}"')

    if not pages:
        report.error('.', 'No HTML pages found')
    if 'index.html' in pages:
        check_root_page(report, pages['index.html'], texts[root / 'index.html'])
    check_languages(report, root, pages, single_language)
    check_duplicates_and_unused(report, root, files, texts)

    for file in everything:
        name = rel(file, root)
        suffix = file.suffix.lower()
        if suffix in SENSITIVE_EXT or file.name in SENSITIVE_NAMES or file.name.lower().startswith('.env'):
            report.error(name, 'Private or sensitive file must not be in the site folder')
        if suffix in SOURCE_EXT or file.name in SOURCE_NAMES:
            report.error(name, 'Source or build file does not belong in a static site')
        if any(part.startswith('.') for part in file.relative_to(root).parts):
            report.warn(name, 'Hidden file; it will not be included in the ZIP')
        if suffix == '.pdf':
            report.warn(name, 'PDF will be public; confirm it is meant to be published')
        if suffix in SKIP_EXT:
            continue
        size = file.stat().st_size
        if suffix in IMAGE_EXT and size > 600_000:
            report.warn(name, f'Large image ({size // 1000} KB); compress to about 300 KB or less')
        elif size > 3_000_000:
            report.warn(name, f'Large file ({size // 1_000_000} MB); check it is needed')
    for file in walk_site(root)[1]:
        if 'server configuration' in file:
            report.warn(file.split(' ')[0], 'Server configuration is never shipped; agree any change with the host')
    result = report.result()
    result['shipped_files'] = sorted(rel(f, root) for f in files)
    return result


def format_report(result: dict) -> str:
    lines = [f'Audit ({result["mode"]} mode): {result["status"]} — '
             f'{len(result["errors"])} errors, {len(result["warnings"])} warnings, '
             f'{len(result["pages_checked"])} pages']
    for title, items in (('ERRORS', result['errors']), ('WARNINGS', result['warnings'])):
        if items:
            lines.append(title)
            lines.extend(f'  {item["file"]}: {item["problem"]}' for item in items)
    lines.append(f'Limits: {result["limitations"]}')
    return '\n'.join(lines)


def main() -> None:
    utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('site', type=Path, help='the project folder; the website files sit directly in it')
    parser.add_argument('--mode', choices=('release', 'preview'), default='release')
    parser.add_argument('--single-language', action='store_true',
                        help='the client agreed to a one-language site (skips the Arabic/English pair checks)')
    parser.add_argument('--report', type=Path, help='also write the result as JSON to this file')
    parser.add_argument('--json', action='store_true', help='print JSON instead of a summary')
    args = parser.parse_args()
    if not args.site.is_dir():
        parser.error(f'site folder not found: {args.site}')
    result = audit(args.site, args.mode, args.single_language)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else format_report(result))
    raise SystemExit(1 if result['errors'] else 0)


if __name__ == '__main__':
    main()
