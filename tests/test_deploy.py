#!/usr/bin/env python3
"""Regression tests for project structure, the deployment ZIP and the live check.

Run: python3 tests/test_deploy.py

Every test builds a real project in a temporary folder, runs the real scripts as a subprocess and inspects the
real ZIP it produces (extracted and served over HTTP). Nothing here only asserts that a folder exists.
"""
from __future__ import annotations

import hashlib
import http.server
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / 'skills' / 'client-website-studio' / 'scripts'
FIXTURE = REPO / 'tests' / 'fixtures' / 'good-site'
TEMPLATE = REPO / 'workspace-template'
sys.path.insert(0, str(SCRIPTS))
from audit_site import audit  # noqa: E402
from verify_zip import verify_zip  # noqa: E402

SITE_FILES = {'index.html'}


def run(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args],
                          capture_output=True, text=True, encoding='utf-8')


def errors_of(result: dict) -> str:
    return '\n'.join(f'{e["file"]}: {e["problem"]}' for e in result['errors'])


def tree_hash(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob('*')) if p.is_file()}


def force_rmtree(path: Path) -> None:
    def onerror(func, target, _exc):
        os.chmod(target, stat.S_IWRITE)
        func(target)
    shutil.rmtree(path, onerror=onerror)


class ProjectCase(unittest.TestCase):
    """A client project the way START.md leaves it: website files at the root, working folders beside them."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(force_rmtree, self.tmp)
        self.project = self.tmp / 'al-noor-trading'
        self.project.mkdir()
        self.build_project(self.project)

    def build_project(self, root: Path, website_in: str = '') -> None:
        site = root / website_in if website_in else root
        shutil.copytree(FIXTURE, site, dirs_exist_ok=True)
        for item in TEMPLATE.iterdir():
            shutil.copy(item, root / item.name)
        for folder in ('client/inbox', 'client/documents', 'client/approvals', 'brand', 'concepts',
                       'review', 'feedback', 'handover'):
            (root / folder).mkdir(parents=True, exist_ok=True)
        (root / 'client' / 'brief.md').write_text('# brief\nregistration number 123\n', encoding='utf-8')
        (root / 'client' / 'documents' / 'registration.pdf').write_bytes(b'%PDF private papers')
        (root / 'brand' / 'logo-original.png').write_bytes(b'\x89PNG original logo')
        (root / 'feedback' / 'log.md').write_text('# سجل الملاحظات\n', encoding='utf-8')

    def package(self, *args: str) -> subprocess.CompletedProcess:
        return run('package_site.py', str(self.project), *args)

    @property
    def zip_path(self) -> Path:
        return self.project / 'handover' / 'DEPLOY-READY.zip'

    def edit(self, rel: str, old: str, new: str) -> None:
        path = self.project / rel
        text = path.read_text(encoding='utf-8')
        self.assertIn(old, text, f'fixture text not found in {rel}: {old}')
        path.write_text(text.replace(old, new, 1), encoding='utf-8')


class TestA_NewBilingualProject(ProjectCase):
    def test_release_zip_has_only_the_website_at_its_root(self):
        before = tree_hash(self.project)
        result = self.package('--approval', 'Client OK on WhatsApp')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        names = zipfile.ZipFile(self.zip_path).namelist()
        self.assertEqual(set(names), SITE_FILES)
        self.assertEqual(len(names), len(set(names)), 'no entry may be listed twice')
        self.assertTrue(all('\\' not in n for n in names))
        after = tree_hash(self.project)
        for rel, digest in before.items():
            self.assertEqual(after[rel], digest, f'packaging changed {rel}')

    def test_zip_extracts_straight_into_httpdocs_and_works_over_http(self):
        self.assertEqual(self.package('--approval', 'x').returncode, 0)
        httpdocs = self.tmp / 'httpdocs'
        with zipfile.ZipFile(self.zip_path) as archive:
            archive.extractall(httpdocs)
        self.assertTrue((httpdocs / 'index.html').is_file(), 'index.html must be directly in httpdocs')
        self.assertEqual(verify_zip(self.zip_path), [])
        server = serve(httpdocs)
        self.addCleanup(stop, server)
        port = server.server_address[1]
        live = run('check_live.py', f'http://127.0.0.1:{port}/', '--allow-http', '--zip', str(self.zip_path))
        self.assertEqual(live.returncode, 0, live.stdout + live.stderr)
        self.assertIn('LIVE CHECK PASSED', live.stdout)

    def test_root_page_is_functional_and_links_both_languages(self):
        text = (self.project / 'index.html').read_text(encoding='utf-8')
        self.assertIn('href="#arabic"', text)
        self.assertIn('href="#english"', text)
        self.assertEqual(audit(self.project, 'release')['errors'], [])


class TestB_ExistingCorrectProject(ProjectCase):
    def test_second_build_is_identical_and_working_files_are_untouched(self):
        self.assertEqual(self.package('--approval', 'x').returncode, 0)
        first = self.zip_path.read_bytes()
        before = tree_hash(self.project)
        self.assertEqual(self.package('--approval', 'x').returncode, 0)
        self.assertEqual(self.zip_path.read_bytes(), first)
        after = tree_hash(self.project)
        self.assertEqual({k: v for k, v in after.items() if not k.startswith('handover/')},
                         {k: v for k, v in before.items() if not k.startswith('handover/')})

    def test_private_material_never_ships(self):
        self.assertEqual(self.package('--approval', 'x').returncode, 0)
        names = ' '.join(zipfile.ZipFile(self.zip_path).namelist())
        for private in ('client', 'brand', 'registration', 'logo-original', 'brief', 'PROJECT-STATUS', 'AGENTS', 'handover'):
            self.assertNotIn(private, names)

    def test_normalize_has_nothing_to_do(self):
        result = run('normalize_project.py', str(self.project))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Nothing to fix', result.stdout)


class TestC_NestedSiteFolder(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(force_rmtree, self.tmp)
        self.project = self.tmp / 'test'
        self.project.mkdir()
        helper = ProjectCase('run')
        helper.build_project(self.project, website_in='site')

    def test_audit_and_packager_block_the_nested_layout(self):
        result = audit(self.project, 'release')
        self.assertIn('wrapper folder', errors_of(result))
        out = run('package_site.py', str(self.project), '--approval', 'x')
        self.assertNotEqual(out.returncode, 0)
        self.assertFalse((self.project / 'handover' / 'DEPLOY-READY.zip').exists())

    def test_dry_run_changes_nothing(self):
        before = tree_hash(self.project)
        result = run('normalize_project.py', str(self.project))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Dry run', result.stdout)
        self.assertEqual(tree_hash(self.project), before)

    def test_normalize_moves_site_up_with_a_backup_and_then_packages(self):
        before = tree_hash(self.project)
        result = run('normalize_project.py', str(self.project), '--apply')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.project / 'index.html').is_file())
        self.assertFalse((self.project / 'site').exists())
        backups = [p for p in self.tmp.iterdir() if p.name.startswith('test-backup-')]
        self.assertEqual(len(backups), 1, 'one full backup next to (not inside) the project')
        self.assertEqual(tree_hash(backups[0]), before)
        after = tree_hash(self.project)
        for rel, digest in before.items():
            if not rel.startswith('site/'):
                self.assertEqual(after[rel], digest, f'{rel} must be preserved')
        for rel in SITE_FILES:
            self.assertEqual(after[rel], before['site/' + rel])
        built = run('package_site.py', str(self.project), '--approval', 'x')
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        self.assertEqual(set(zipfile.ZipFile(self.project / 'handover' / 'DEPLOY-READY.zip').namelist()), SITE_FILES)


class TestD_ClonedSkillInProject(ProjectCase):
    def plant_skill(self):
        kit = self.project / '.studio-kit'
        (kit / '.git' / 'objects').mkdir(parents=True)
        locked = kit / '.git' / 'objects' / 'pack.idx'
        locked.write_bytes(b'x')
        os.chmod(locked, stat.S_IREAD)
        (kit / 'START.md').write_text('kit', encoding='utf-8')
        for agent in ('.claude', '.agents'):
            skill = self.project / agent / 'skills' / 'client-website-studio'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('---\nname: client-website-studio\n---\n', encoding='utf-8')
        (self.project / '.claude' / 'settings.local.json').write_text('{}', encoding='utf-8')

    def test_audit_blocks_and_packager_refuses(self):
        self.plant_skill()
        result = audit(self.project, 'release')
        text = errors_of(result)
        self.assertIn('.studio-kit', text)
        self.assertIn('.claude/skills/', text)
        self.assertIn('.agents/skills/', text)
        out = self.package('--approval', 'x')
        self.assertNotEqual(out.returncode, 0)
        self.assertFalse(self.zip_path.exists())

    def test_normalize_removes_only_the_skill_copies(self):
        self.plant_skill()
        result = self.project / 'client' / 'brief.md'
        before_brief = result.read_bytes()
        out = run('normalize_project.py', str(self.project), '--apply')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertFalse((self.project / '.studio-kit').exists())
        self.assertFalse((self.project / '.claude' / 'skills').exists())
        self.assertFalse((self.project / '.agents').exists(), 'empty agent folder is cleaned up')
        self.assertTrue((self.project / '.claude' / 'settings.local.json').is_file(), 'unrelated agent settings stay')
        self.assertEqual(result.read_bytes(), before_brief)
        built = self.package('--approval', 'x')
        self.assertEqual(built.returncode, 0, built.stdout + built.stderr)
        names = ' '.join(zipfile.ZipFile(self.zip_path).namelist())
        for forbidden in ('SKILL', '.studio-kit', '.claude', '.agents', 'START.md'):
            self.assertNotIn(forbidden, names)

    def test_loose_skill_file_needs_a_person(self):
        (self.project / 'audit_site.py').write_text('# copied by mistake', encoding='utf-8')
        out = run('normalize_project.py', str(self.project), '--apply')
        self.assertNotEqual(out.returncode, 0)
        self.assertIn('needs a person', out.stdout)
        self.assertTrue((self.project / 'audit_site.py').exists())


class TestE_BrokenAssetPaths(ProjectCase):
    def test_broken_paths_block_the_zip(self):
        self.edit('index.html', '</head>', '<link rel="stylesheet" href="assets/css/site.css"></head>')
        self.assertIn('Broken local reference', errors_of(audit(self.project)))
        self.assertNotEqual(self.package('--approval', 'x').returncode, 0)
        self.assertFalse(self.zip_path.exists())

    def test_local_computer_paths_and_development_folder_references_block(self):
        self.edit('index.html', '</head>', '<link rel="stylesheet" href="brand/logo-original.png"></head>')
        self.edit('index.html', '</body>', '<!-- file:///Users/marketer/site.css --></body>')
        text = errors_of(audit(self.project))
        self.assertIn('local computer', text)
        self.assertIn('development or wrapper folder', text)


class TestF_MissingLocalizedPages(ProjectCase):
    def drop_english(self):
        path = self.project / 'index.html'
        text = path.read_text(encoding='utf-8')
        text = re.sub(r'<section lang="en".*?</section>', '', text, flags=re.S)
        text = re.sub(r'<a href="#english".*?</a>', '', text)
        path.write_text(text, encoding='utf-8')

    def test_missing_language_page_blocks_release_but_not_preview(self):
        self.drop_english()
        self.assertIn('English content is missing', errors_of(audit(self.project, 'release')))
        self.assertEqual(audit(self.project, 'preview')['errors'], [])
        self.assertNotEqual(self.package('--approval', 'x').returncode, 0)

    def test_single_language_is_an_explicit_choice(self):
        self.drop_english()
        self.assertEqual(audit(self.project, 'release', single_language=True)['errors'], [])
        out = self.package('--approval', 'x', '--single-language')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_language_switch_must_not_lead_to_a_missing_page(self):
        self.edit('index.html', 'id="english"', 'id="missing"')
        self.assertIn('No in-page link to the English content', errors_of(audit(self.project)))

    def test_missing_switch_between_languages_blocks_release(self):
        self.edit('index.html', '<a href="#arabic" lang="ar">العربية</a>', '')
        self.assertIn('No in-page link to the Arabic content', errors_of(audit(self.project, 'release')))


class TestG_ZipWithWrapperDirectory(ProjectCase):
    def make_zip(self, prefix: str, backslash: bool = False) -> Path:
        out = self.tmp / 'bad.zip'
        sep = '\\' if backslash else '/'
        with zipfile.ZipFile(out, 'w') as archive:
            for rel in SITE_FILES:
                name = (prefix + rel).replace('/', sep) if prefix else rel.replace('/', sep)
                info = zipfile.ZipInfo('placeholder')
                info.filename = name  # set after creation: ZipInfo itself rewrites os.sep on Windows
                archive.writestr(info, (self.project / rel).read_bytes())
        return out

    def test_wrapper_directory_is_rejected(self):
        for prefix in ('al-noor-trading/', 'test/site/', 'site/'):
            problems = verify_zip(self.make_zip(prefix))
            self.assertTrue(any('not at the ZIP root' in p for p in problems), (prefix, problems))

    def test_cli_exit_code_and_message(self):
        out = run('verify_zip.py', str(self.make_zip('site/')))
        self.assertEqual(out.returncode, 1)
        self.assertIn('wrapped inside "site/"', out.stdout)

    def test_a_correct_zip_passes(self):
        self.assertEqual(verify_zip(self.make_zip('')), [])

    def test_backslash_names_are_rejected(self):
        out = self.make_zip('')
        with zipfile.ZipFile(out, 'a') as archive:
            info = zipfile.ZipInfo('placeholder')
            info.filename = 'assets' + chr(92) + 'site.css'
            archive.writestr(info, 'body{}')
        self.assertTrue(any('Unsafe path' in p for p in verify_zip(out)))

    def test_skill_and_private_files_in_a_zip_are_rejected(self):
        out = self.make_zip('')
        with zipfile.ZipFile(out, 'a') as archive:
            archive.writestr('.studio-kit/START.md', 'x')
            archive.writestr('client/brief.md', 'x')
            archive.writestr('handover/old.zip', 'x')
            archive.writestr('web.config', '<configuration/>')
        text = '\n'.join(verify_zip(out))
        for expected in ('.studio-kit', 'client/brief.md', 'handover/old.zip', 'web.config'):
            self.assertIn(expected, text)


class TestH_OldArchivesAndDevelopmentFiles(ProjectCase):
    def test_noise_is_left_out_of_the_zip(self):
        (self.project / 'handover' / 'old-20260101.zip').write_bytes(b'PK old')
        (self.project / 'old-site.zip').write_bytes(b'PK old')
        (self.project / 'notes.md').write_text('internal', encoding='utf-8')
        (self.project / 'debug.log').write_text('x', encoding='utf-8')
        (self.project / 'index.html.bak').write_text('x', encoding='utf-8')
        (self.project / '.git').mkdir()
        (self.project / '.git' / 'config').write_text('[core]', encoding='utf-8')
        (self.project / '__pycache__').mkdir()
        (self.project / 'web.config').write_text('<configuration/>', encoding='utf-8')
        (self.project / 'preview').mkdir()
        (self.project / 'preview' / 'index.html').write_text('<!doctype html><title>x</title>', encoding='utf-8')
        out = self.package('--approval', 'x')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertEqual(set(zipfile.ZipFile(self.zip_path).namelist()), SITE_FILES)
        self.assertIn('server configuration', out.stdout)

    def test_build_files_block_the_release(self):
        (self.project / 'package.json').write_text('{}', encoding='utf-8')
        self.assertIn('package.json', errors_of(audit(self.project, 'release')))
        self.assertNotEqual(self.package('--approval', 'x').returncode, 0)

    def test_duplicate_and_unused_files_block_the_release(self):
        shutil.copy(self.project / 'index.html', self.project / 'copy.html')
        (self.project / 'forgotten.png').write_bytes(b'forgotten')
        text = errors_of(audit(self.project))
        self.assertIn('Duplicate of', text)
        self.assertIn('forgotten.png: File is not used', text)
        self.assertIn('single-file', errors_of(audit(self.project, 'preview')))


class TestI_ExistingProductionProject(unittest.TestCase):
    """An old project whose website sits in site/ next to unrelated files that must survive."""

    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(force_rmtree, self.tmp)
        self.project = self.tmp / 'sarab'
        self.project.mkdir()
        ProjectCase('run').build_project(self.project, website_in='site')
        (self.project / 'client' / 'contract.txt').write_text('signed contract', encoding='utf-8')
        (self.project / 'client' / 'inbox' / 'whatsapp.png').write_bytes(b'\x89PNG chat')

    def test_unrelated_files_survive_normalisation(self):
        before = tree_hash(self.project)
        out = run('normalize_project.py', str(self.project), '--apply')
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        after = tree_hash(self.project)
        for rel, digest in before.items():
            if not rel.startswith('site/'):
                self.assertEqual(after.get(rel), digest, f'{rel} must survive')

    def test_name_clash_stops_everything_and_changes_nothing(self):
        (self.project / 'index.html').write_text('customised', encoding='utf-8')
        before = tree_hash(self.project)
        out = run('normalize_project.py', str(self.project), '--apply')
        self.assertNotEqual(out.returncode, 0)
        self.assertRegex(out.stdout, 'already exist|two|Both|both')
        self.assertEqual(tree_hash(self.project), before)
        self.assertEqual([p for p in self.tmp.iterdir() if 'backup' in p.name], [])

    def test_two_copies_of_the_site_need_a_person(self):
        shutil.copy(self.project / 'site' / 'index.html', self.project / 'index.html')
        before = tree_hash(self.project)
        out = run('normalize_project.py', str(self.project), '--apply')
        self.assertNotEqual(out.returncode, 0)
        self.assertEqual(tree_hash(self.project), before)


class TestRootPageRules(ProjectCase):
    def test_empty_placeholder_and_redirect_only_roots_are_blocked(self):
        page = self.project / 'index.html'
        cases = {
            'empty': '<!doctype html><html lang="ar" dir="rtl"><head><title>x</title></head><body></body></html>',
            'placeholder': '<!doctype html><html lang="ar" dir="rtl"><head><title>x</title></head>'
                           '<body><main><h1>Under construction</h1><p><a href="ar/index.html">x</a> '
                           'coming soon to this domain</p></main></body></html>',
            'redirect': '<!doctype html><html lang="ar" dir="rtl"><head><title>x</title>'
                        '<meta http-equiv="refresh" content="0;url=ar/index.html"></head><body>'
                        '<a href="ar/index.html">ar</a></body></html>',
        }
        for name, html in cases.items():
            page.write_text(html, encoding='utf-8')
            text = errors_of(audit(self.project, 'release'))
            self.assertIn('index.html:', text, name)
            self.assertTrue(re.search(r'empty|placeholder|only redirects', text), (name, text))

    def test_separate_english_folder_is_rejected(self):
        # Legacy separate language pages must now fail rather than silently ship.
        english = self.project / 'en'
        english.mkdir()
        shutil.copy(self.project / 'index.html', english / 'index.html')
        self.assertIn('single-file', errors_of(audit(self.project)))
        self.assertNotEqual(self.package('--approval', 'x').returncode, 0)


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args) -> None:
        pass


def stop(server: http.server.ThreadingHTTPServer) -> None:
    server.shutdown()
    server.server_close()


def serve(root: Path, handler=None) -> http.server.ThreadingHTTPServer:
    import functools
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(handler or Handler, directory=str(root)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


class IisError(Handler):
    def do_GET(self):
        body = b'<html><head><title>403 - Forbidden: Access is denied.</title></head><body>403</body></html>'
        self.send_response(403)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class TestLiveCheck(ProjectCase):
    def setUp(self) -> None:
        super().setUp()
        self.assertEqual(self.package('--approval', 'x').returncode, 0)

    def live(self, server, *extra: str) -> subprocess.CompletedProcess:
        self.addCleanup(stop, server)
        return run('check_live.py', f'http://127.0.0.1:{server.server_address[1]}/', '--allow-http', *extra)

    def test_host_error_page_is_reported_as_a_hosting_problem(self):
        out = self.live(serve(self.tmp, IisError))
        self.assertEqual(out.returncode, 1)
        self.assertIn('403', out.stdout)
        self.assertIn('hosting configuration', out.stdout)

    def test_files_extracted_into_a_subfolder_are_detected(self):
        httpdocs = self.tmp / 'httpdocs'
        with zipfile.ZipFile(self.zip_path) as archive:
            archive.extractall(httpdocs / 'site')
        (httpdocs / 'index.html').write_text('<!doctype html><html><body>Hosting default page placeholder text '
                                             'that is not the website</body></html>', encoding='utf-8')
        out = self.live(serve(httpdocs), '--zip', str(self.zip_path))
        self.assertEqual(out.returncode, 1)
        self.assertIn('differs from the ZIP', out.stdout + 'x')

    def test_https_is_required_by_default(self):
        server = serve(self.tmp)
        self.addCleanup(stop, server)
        out = run('check_live.py', f'http://127.0.0.1:{server.server_address[1]}/')
        self.assertEqual(out.returncode, 1)
        self.assertIn('https://', out.stdout)


class TestRepoRules(unittest.TestCase):
    def test_start_md_never_installs_the_skill_into_the_project(self):
        text = (REPO / 'START.md').read_text(encoding='utf-8')
        self.assertNotRegex(text, r'clone[^\n]*\.studio-kit')
        self.assertIn('Do not create `.studio-kit/`', text)
        self.assertNotRegex(text, r'into both of these folders')
        self.assertIn('never goes into the client', text.lower().replace("client's", 'client'))
        for doc in ('README.md', 'STARTING-PROMPT.md'):
            self.assertNotIn('.studio-kit', (REPO / doc).read_text(encoding='utf-8'), doc)

    def test_skill_documents_the_root_index_and_single_zip_rules(self):
        text = (REPO / 'skills' / 'client-website-studio' / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn('DEPLOY-READY.zip', text)
        self.assertIn('never create a `site/`', text.lower())
        self.assertNotRegex(text, r'site/\s+the website source')

    def test_workspace_template_has_no_skill_paths_inside_the_project(self):
        for name in ('AGENTS.md', 'CLAUDE.md'):
            text = (TEMPLATE / name).read_text(encoding='utf-8')
            self.assertNotIn('.claude/skills', text)
            self.assertNotIn('.agents/skills', text)

    def test_fixture_is_clean(self):
        self.assertEqual(audit(FIXTURE, 'release')['errors'], [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
