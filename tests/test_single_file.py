"""Single-file output contract regressions."""
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/client-website-studio/scripts'))
from audit_site import audit
from verify_zip import check_names

HTML = '''<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width"><title>شركة النور | Al Noor Trading</title>
<meta name="description" content="Al Noor Trading services in Benghazi — شركة النور للتجارة في بنغازي">
<meta property="og:title" content="Al Noor Trading"><meta property="og:description" content="Trading in Benghazi">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Organization","name":"Al Noor Trading"}</script>
<style>body{margin:0}</style></head><body><main id="main">
<section lang="ar" dir="rtl" id="arabic" data-section="العربية"><h1>شركة النور</h1><p>خدمات التجارة في بنغازي</p><a href="#english" lang="en">English</a></section>
<section lang="en" dir="ltr" id="english" data-section="English"><h2>Al Noor Trading</h2><p>Trading services in Benghazi</p><a href="#arabic" lang="ar">العربية</a></section>
</main></body></html>'''

class SingleFileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write(HTML)
    def write(self, html):
        (self.root / 'index.html').write_text(html, encoding='utf-8')
    def errors(self):
        return '\n'.join(x['problem'] for x in audit(self.root)['errors'])
    def test_complete_embedded_bilingual_page_passes(self):
        self.assertEqual(audit(self.root)['errors'], [])
    def test_extra_asset_is_blocked(self):
        (self.root / 'photo.svg').write_text('<svg/>')
        self.assertIn('single-file', self.errors())
    def test_remote_resource_is_blocked_but_contact_link_is_allowed(self):
        self.write(HTML.replace('</body>', '<img src="https://example.org/a.png" alt="Office"></body>'))
        self.assertIn('embedded', self.errors())
    def test_missing_seo_blocks_release(self):
        self.write(HTML.replace('name="description"', 'name="other"'))
        self.assertIn('description', self.errors())
    def test_missing_translation_blocks_release(self):
        self.write(HTML.replace('lang="en" dir="ltr"', 'lang="fr" dir="ltr"'))
        self.assertIn('English', self.errors())
    def test_invalid_structured_data_blocks_release(self):
        self.write(HTML.replace('"@type":"Organization"', '"@type":invalid'))
        self.assertIn('JSON', self.errors())
    def test_remote_css_asset_is_blocked(self):
        self.write(HTML.replace('body{margin:0}', 'body{background:url(https://example.org/photo.jpg)}'))
        self.assertIn('CSS assets must be embedded', self.errors())
    def test_embedded_css_asset_and_contact_link_pass(self):
        self.write(HTML.replace('body{margin:0}', 'body{background:url(data:image/png;base64,YQ==)}')
                   .replace('</main>', '<a href="https://wa.me/218911234567">WhatsApp</a></main>'))
        self.assertEqual(audit(self.root)['errors'], [])
    def test_legacy_language_pages_cannot_bypass_with_single_language(self):
        (self.root / 'en').mkdir()
        (self.root / 'en/index.html').write_text(HTML)
        errors = audit(self.root, single_language=True)['errors']
        self.assertTrue(any('single-file' in item['problem'] for item in errors))
    def test_arabic_first_agent_instructions(self):
        repo = Path(__file__).resolve().parents[1]
        for name in ('skills/client-website-studio/SKILL.md', 'workspace-template/AGENTS.md', 'workspace-template/CLAUDE.md'):
            text = (repo / name).read_text()
            self.assertIn('Arabic is the primary experience by default', text)
            self.assertIn('html lang="ar" dir="rtl"', text)
        seo = (repo / 'skills/client-website-studio/references/seo.md').read_text()
        self.assertIn('Prioritise Arabic search phrases', seo)
    def test_missing_markers_block_preview_too(self):
        self.write(HTML.replace('Trading services in Benghazi', '[[NEEDS: hours]]'))
        self.assertTrue(any('Unresolved' in item['problem'] for item in audit(self.root, 'preview')['errors']))
    def test_zip_rejects_every_file_besides_index(self):
        self.assertTrue(check_names(['index.html', 'assets/site.css']))
    def test_zip_accepts_exactly_index(self):
        self.assertEqual(check_names(['index.html']), [])

if __name__ == '__main__': unittest.main()
