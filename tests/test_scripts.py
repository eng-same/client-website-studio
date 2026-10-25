#!/usr/bin/env python3
"""Tests for the audit and packaging scripts. Run: python3 tests/test_scripts.py"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / 'skills' / 'client-website-studio' / 'scripts'
FIXTURE = REPO / 'tests' / 'fixtures' / 'good-site'
sys.path.insert(0, str(SCRIPTS))
from audit_site import audit  # noqa: E402


def problems(result: dict, level: str) -> str:
    return '\n'.join(f'{item["file"]}: {item["problem"]}' for item in result[level])


class SiteCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.site = self.tmp / 'project'
        shutil.copytree(FIXTURE, self.site)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def edit(self, rel: str, old: str, new: str) -> None:
        path = self.site / rel
        text = path.read_text(encoding='utf-8')
        self.assertIn(old, text, f'fixture text not found in {rel}: {old}')
        path.write_text(text.replace(old, new, 1), encoding='utf-8')

    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding='utf-8')


class AuditTests(SiteCase):
    def test_fixture_passes_cleanly(self):
        result = audit(self.site, 'release')
        self.assertEqual(result['errors'], [], problems(result, 'errors'))
        self.assertEqual(result['warnings'], [], problems(result, 'warnings'))

    def test_needs_marker_blocks_both_preview_and_release(self):
        self.edit('index.html', '<li>النقل داخل بنغازي</li>', '<li>[[NEEDS: ساعات العمل]]</li>')
        self.assertIn('[[', problems(audit(self.site, 'preview'), 'errors'))
        self.assertIn('[[', problems(audit(self.site, 'release'), 'errors'))

    def test_bank_claims_are_errors_in_both_languages(self):
        self.edit('index.html', '<h2>الخدمات</h2>', '<h2>موقع متوافق مع متطلبات مصرف ليبيا المركزي</h2>')
        self.edit('index.html', '<h2>Services</h2>', '<h2>CBL-compliant company website</h2>')
        errors = problems(audit(self.site, 'preview'), 'errors')
        self.assertIn('index.html', errors)

    def test_plain_bank_mention_is_only_a_warning(self):
        self.edit('index.html', '<h2>Services</h2>', '<h2>We bank with the Central Bank branch nearby</h2>')
        result = audit(self.site, 'release')
        self.assertEqual(result['errors'], [], problems(result, 'errors'))
        self.assertIn('Central Bank', problems(result, 'warnings'))

    def test_root_relative_path_is_an_error(self):
        self.edit('index.html', '</head>', '<link rel="stylesheet" href="/assets/css/site.css"></head>')
        self.assertIn('starts with "/"', problems(audit(self.site, 'release'), 'errors'))

    def test_broken_css_url_is_an_error(self):
        self.edit('index.html', '</style>', 'body{background:url(missing.svg)}</style>')
        self.assertIn('missing.svg', problems(audit(self.site, 'release'), 'errors'))

    def test_broken_image_and_missing_alt(self):
        self.edit('index.html', 'src="data:image/svg+xml;base64,PHN2Zy8+" alt="The company warehouse"',
                  'src="assets/images/nope.png"')
        errors = problems(audit(self.site, 'release'), 'errors')
        self.assertIn('Broken local reference', errors)
        self.assertIn('no alt', errors)

    def test_contact_link_checks(self):
        self.edit('index.html', 'tel:+218911234567', 'tel:0911234567')
        self.edit('index.html', 'https://wa.me/218911234567', 'https://wa.me/+218911234567')
        self.edit('index.html', 'mailto:info@example-trading.ly', 'mailto:company@gmail.com')
        warnings = problems(audit(self.site, 'release'), 'warnings')
        self.assertIn('country code', warnings)
        self.assertIn('WhatsApp', warnings)
        self.assertIn('gmail.com', warnings)

    def test_wrong_direction_and_missing_language_switch(self):
        self.edit('index.html', 'lang="en" dir="ltr"', 'lang="en" dir="rtl"')
        self.edit('index.html', '<a href="#arabic" lang="ar">العربية</a>', '')
        result = audit(self.site, 'release')
        self.assertIn('English content is missing', problems(result, 'errors'))
        self.assertIn('No in-page link to the Arabic content', problems(result, 'errors'))

    def test_dead_links_and_secrets(self):
        self.edit('index.html', 'href="#english"', 'href="#"')
        self.edit('index.html', '</body>', '<!-- api_key = "abcd1234efgh5678" --></body>')
        errors = problems(audit(self.site, 'release'), 'errors')
        self.assertIn('goes nowhere', errors)
        self.assertIn('password, key or token', errors)

    def test_noindex_blocks_release_only(self):
        self.edit('index.html', '<meta charset="utf-8">', '<meta charset="utf-8"><meta name="robots" content="noindex">')
        self.assertEqual(audit(self.site, 'preview')['errors'], [])
        self.assertIn('noindex', problems(audit(self.site, 'release'), 'errors'))

    def test_section_names_and_sensitive_files(self):
        self.edit('index.html', '<footer data-section="Footer">', '<footer>')
        (self.site / '.env').write_text('SECRET=1', encoding='utf-8')
        result = audit(self.site, 'release')
        self.assertIn('data-section', problems(result, 'warnings'))
        self.assertIn('.env', problems(result, 'errors'))


class PackageTests(SiteCase):
    def package(self, *args: str) -> subprocess.CompletedProcess:
        return self.run_script(str(SCRIPTS / 'package_site.py'), str(self.site), *args)

    def test_release_requires_approval(self):
        result = self.package(str(self.tmp / 'out.zip'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('--approval', result.stderr)

    def test_release_zip_layout_and_record(self):
        (self.site / 'notes.md').write_text('internal', encoding='utf-8')
        out = self.tmp / 'handover' / 'example-trading-ly.zip'
        result = self.package(str(out), '--approval', 'Client OK on WhatsApp')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        names = zipfile.ZipFile(out).namelist()
        self.assertEqual(names, ['index.html'])
        self.assertNotIn('notes.md', names)
        record = json.loads(out.with_suffix('.json').read_text(encoding='utf-8'))
        self.assertEqual(record['approval'], 'Client OK on WhatsApp')
        self.assertEqual(len(record['sha256']), 64)
        html = zipfile.ZipFile(out).read('index.html').decode('utf-8')
        self.assertNotIn('data-review-mode', html)

    def test_release_zip_is_reproducible(self):
        a, b = self.tmp / 'a.zip', self.tmp / 'b.zip'
        self.package(str(a), '--approval', 'x')
        self.package(str(b), '--approval', 'x')
        self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_release_refused_when_audit_fails(self):
        self.edit('index.html', '<li>النقل داخل بنغازي</li>', '<li>[[NEEDS: ساعات العمل]]</li>')
        out = self.tmp / 'out.zip'
        result = self.package(str(out), '--approval', 'x')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(out.exists())

    def test_preview_folder_adds_noindex_without_touching_site(self):
        before = (self.site / 'index.html').read_text(encoding='utf-8')
        out = self.tmp / 'preview'
        result = self.package(str(out), '--preview')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        html = (out / 'index.html').read_text(encoding='utf-8')
        self.assertIn('noindex', html)
        self.assertEqual((self.site / 'index.html').read_text(encoding='utf-8'), before)
        rebuild = self.package(str(out), '--preview')
        self.assertEqual(rebuild.returncode, 0, rebuild.stderr)

    def test_preview_refuses_to_replace_unrelated_folder(self):
        out = self.tmp / 'precious'
        out.mkdir()
        (out / 'keep.txt').write_text('do not delete', encoding='utf-8')
        result = self.package(str(out), '--preview')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((out / 'keep.txt').exists())

    def test_output_inside_site_is_refused(self):
        result = self.package(str(self.site / 'out.zip'), '--approval', 'x')
        self.assertNotEqual(result.returncode, 0)


class RepoTests(unittest.TestCase):
    def test_skill_frontmatter_is_portable(self):
        text = (REPO / 'skills' / 'client-website-studio' / 'SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(text.startswith('---\n'))
        front = text.split('---\n')[1]
        keys = {line.split(':', 1)[0] for line in front.splitlines() if line and not line.startswith(' ')}
        self.assertLessEqual(keys, {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'})
        name = next(line.split(':', 1)[1].strip() for line in front.splitlines() if line.startswith('name:'))
        self.assertEqual(name, 'client-website-studio')
        description = next(line.split(':', 1)[1].strip() for line in front.splitlines() if line.startswith('description:'))
        self.assertLessEqual(len(description), 1024)
        self.assertLess(len(text.splitlines()), 500)

    def test_versions_match(self):
        version = (REPO / 'VERSION').read_text(encoding='utf-8').strip()
        skill = (REPO / 'skills' / 'client-website-studio' / 'SKILL.md').read_text(encoding='utf-8')
        self.assertIn(f'version: "{version}"', skill)
        self.assertIn(f'## {version}', (REPO / 'CHANGELOG.md').read_text(encoding='utf-8'))

    def test_referenced_files_exist(self):
        skill_dir = REPO / 'skills' / 'client-website-studio'
        text = (skill_dir / 'SKILL.md').read_text(encoding='utf-8')
        for rel in ('references/intake.md', 'references/design-rules.md', 'references/implementation.md',
                    'references/localization.md', 'references/review-rounds.md', 'references/quality.md',
                    'references/publishing.md', 'references/handover.md', 'assets/brief-template.md'):
            self.assertIn(rel.split('/')[-1], text)
            self.assertTrue((skill_dir / rel).is_file(), rel)
        for script in ('serve_preview.py', 'verify_zip.py', 'normalize_project.py', 'check_live.py', 'audit_site.py', 'package_site.py'):
            self.assertTrue((skill_dir / 'scripts' / script).is_file(), script)


class LayoutCheckTests(unittest.TestCase):
    def run_check(self, body):
        import tempfile
        sys.path.insert(0, str(REPO / 'skills' / 'client-website-studio' / 'scripts'))
        import check_layout
        if not check_layout.find_browser():
            self.skipTest('no Edge/Chrome installed')
        tmp = Path(tempfile.mkdtemp())
        (tmp / 'index.html').write_text('<!doctype html><meta name=viewport content="width=device-width"><body>' + body, encoding='utf-8')
        before = sorted(p.name for p in tmp.iterdir())
        result = subprocess.run([sys.executable, str(REPO / 'skills' / 'client-website-studio' / 'scripts' / 'check_layout.py'), str(tmp)],
                                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(sorted(p.name for p in tmp.iterdir()), before, 'check must not write into the site folder')
        if result.returncode == 2:
            self.skipTest('browser could not run here')
        return result

    def test_detects_overflow(self):
        self.assertEqual(self.run_check('<div style="width:900px;height:20px">x</div>').returncode, 1)

    def test_passes_clean_page(self):
        self.assertEqual(self.run_check('<p>hello</p>').returncode, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
