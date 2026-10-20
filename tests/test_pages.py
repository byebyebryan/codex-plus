"""Offline checks of public environment routing and site integrity."""
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('pages_builder', str(ROOT / 'scripts/build-pages'))
spec = importlib.util.spec_from_loader(loader.name, loader)
pages = importlib.util.module_from_spec(spec)
loader.exec_module(pages)


class PagesTests(unittest.TestCase):
    def test_environment_guide_is_public_and_keeps_fragment(self):
        self.assertEqual(pages.rewrite_link('environments.md#selection-and-overrides', '../'),
                         '../environments/#selection-and-overrides')
        self.assertEqual(pages.rewrite_link(pages.SOURCE + 'environments.md', './'), './environments/')
        nav = pages.guide_page('environments.md', 'environments', 'Environments', '<h1>Homes</h1>', '')
        self.assertIn('aria-current="page">Environments</a>', nav)

    def test_historical_guides_remain_on_github(self):
        self.assertEqual(pages.rewrite_link('implementation-history.md#earlier-implementation-history', '../'),
                         pages.SOURCE + 'implementation-history.md#earlier-implementation-history')

    def test_worker_guide_is_public_and_keeps_fragment(self):
        self.assertEqual(pages.rewrite_link('workers.md#choose-a-workflow', '../'),
                         '../workers/#choose-a-workflow')
        self.assertEqual(pages.rewrite_link(pages.SOURCE + 'workers.md', './'), './workers/')
        nav = pages.guide_page('workers.md', 'workers', 'Luna & workers', '<h1>Workers</h1>', '')
        self.assertIn('aria-current="page">Luna &amp; workers</a>', nav)

    def test_github_accessible_table_keeps_attributes_inside_scroll_container(self):
        body = '<markdown-accessiblity-table><table role="table"><tr><td>Wide</td></tr></table></markdown-accessiblity-table>'
        result = pages.guide_page('architecture.md', 'architecture', 'How it works', body, '')
        self.assertIn('<div class="table-scroll"><table role="table">', result)
        self.assertIn('</table></div></markdown-accessiblity-table>', result)

    def test_duplicate_heading_slugs_are_distinct(self):
        result = pages.headings('<h2>Same home</h2><h2>Same home</h2>')
        self.assertIn('id="same-home"', result)
        self.assertIn('id="same-home-1"', result)

    def validate_site(self, landing, target=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text(landing)
            if target is not None:
                (root / 'environments').mkdir()
                (root / 'environments/index.html').write_text(target)
            return pages.validate(root)

    def test_relative_guide_and_anchor_resolve(self):
        self.assertEqual(self.validate_site('<a href="environments/#work">Work</a>', '<h2 id="work">Work</h2>'), 1)

    def test_missing_anchor_refuses_publication(self):
        with self.assertRaisesRegex(ValueError, 'broken site anchor'):
            self.validate_site('<a href="environments/#work">Work</a>', '<h2 id="oss">OSS</h2>')

    def test_missing_guide_refuses_publication(self):
        with self.assertRaisesRegex(ValueError, 'broken site link'):
            self.validate_site('<a href="environments/">Homes</a>')

    def test_duplicate_control_id_refuses_publication(self):
        with self.assertRaisesRegex(ValueError, 'duplicate site id'):
            self.validate_site('<button id="select">OSS</button><button id="select">Work</button>')

    def test_escaping_site_root_refuses_publication(self):
        with self.assertRaisesRegex(ValueError, 'broken site link'):
            self.validate_site('<a href="../outside.html">Outside</a>')


if __name__ == '__main__':
    unittest.main()
