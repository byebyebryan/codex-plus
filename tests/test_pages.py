"""Offline checks of public environment routing and site integrity."""
import importlib.machinery
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest

from codex_plus import VERSION

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('pages_builder', str(ROOT / 'scripts/build-pages'))
spec = importlib.util.spec_from_loader(loader.name, loader)
pages = importlib.util.module_from_spec(spec)
loader.exec_module(pages)


class PagesTests(unittest.TestCase):
    def release_fixture(self, directory):
        root = Path(directory)
        for name in (*pages.CURRENT_RELEASE_CLAIMS, 'docs/workers.md', 'codex_plus/__init__.py'):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        return root

    def test_current_guide_claims_match_the_authoritative_version(self):
        self.assertGreater(pages.validate_current_guides(), 0)

    def test_stale_setup_claim_is_rejected_without_rejecting_historical_features(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/getting-started.md'
            path.write_text(path.read_text().replace(f'**v{VERSION}** supplies', '**v0.0.0-preview.0** supplies'))
            with self.assertRaisesRegex(ValueError, 'stale current-release claim in docs/getting-started.md'):
                pages.validate_current_guides(root)

    def test_stale_managed_architecture_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/architecture.md'
            path.write_text(path.read_text().replace('and Carbon select ' + VERSION.split('-', 1)[-1], 'and Carbon select preview.0'))
            with self.assertRaisesRegex(ValueError, 'stale current-release claim in docs/architecture.md'):
                pages.validate_current_guides(root)

    def test_historical_release_evidence_is_allowed_outside_current_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/getting-started.md'
            path.write_text(path.read_text() + '\nHistorical preview.11 used v0.1.0-preview.11.\n')
            pages.validate_current_guides(root)

    def test_missing_current_claim_and_named_worker_workflow_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/workers.md'
            original = path.read_text()
            path.write_text(original.replace('$luna-goal-loop', '$other-loop'))
            with self.assertRaisesRegex(ValueError, 'named workflow missing.*luna-goal-loop'):
                pages.validate_current_guides(root)
            path.write_text(original)
            path = root / 'docs/getting-started.md'
            path.write_text(path.read_text().replace('supplies the released workflows', 'supplies workflows'))
            with self.assertRaisesRegex(ValueError, 'current-release claim missing'):
                pages.validate_current_guides(root)

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
        self.assertIn('tabindex="0" role="region" aria-label="Scrollable table"><table role="table">', result)
        self.assertIn('</table></div></markdown-accessiblity-table>', result)

    def test_duplicate_heading_slugs_are_distinct(self):
        result = pages.headings('<h2>Same home</h2><h2>Same home</h2>')
        self.assertIn('id="same-home"', result)
        self.assertIn('id="same-home-1"', result)

    def test_setup_links_stay_on_public_site(self):
        self.assertEqual(pages.rewrite_link('getting-started.md#choose-what-to-install', './'),
                         './start/#choose-what-to-install')

    def test_guide_contents_links_and_skip_target_are_accessible(self):
        body = pages.headings('<h1>Workers</h1><h2>Choose &amp; review</h2><h2>Choose &amp; review</h2>')
        result = pages.guide_page('workers.md', 'workers', 'Luna & workers', body, '')
        self.assertIn('<a class="skip" href="#main">', result)
        self.assertIn('<main id="main" tabindex="-1">', result)
        self.assertIn('aria-label="On this page"', result)
        self.assertIn('href="#choose--review-1">Choose &amp; review</a>', result)
        self.assertIn('aria-label="Related guides"', result)

    def test_metadata_escapes_titles_and_uses_public_route(self):
        result = pages.metadata(pages.SITE + 'workers/', 'Luna & "review"', 'Choose <workers>.')
        self.assertIn('Luna &amp; &quot;review&quot;', result)
        self.assertIn('Choose &lt;workers&gt;.', result)
        self.assertIn('rel="canonical" href="' + pages.SITE + 'workers/"', result)

    def publication_fixture(self, directory):
        root = Path(directory)
        (root / 'index.html').write_text(pages.metadata(pages.SITE, 'Codex Plus', 'Workers and watches') +
                                        '<main><h1>Codex Plus</h1></main>')
        for name, (route, title) in pages.GUIDES.items():
            (root / route).mkdir()
            (root / route / 'index.html').write_text(pages.guide_page(name, route, title, '<h1>Guide</h1>', ''))
        (root / 'assets').mkdir()
        (root / 'assets/architecture.svg').write_text('<svg/>')
        (root / '.nojekyll').write_text('')
        pages.write_sitemap(root)
        return root

    def test_publication_has_exact_route_inventory_and_sitemap(self):
        with tempfile.TemporaryDirectory() as directory:
            pages.validate_publication(self.publication_fixture(directory))

    def test_publication_refuses_wrong_canonical_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.publication_fixture(directory)
            path = root / 'workers/index.html'
            path.write_text(path.read_text().replace(pages.SITE + 'workers/', pages.SITE + 'wrong/'))
            with self.assertRaisesRegex(ValueError, 'public URL metadata differs'):
                pages.validate_publication(root)

    def test_publication_refuses_missing_description(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.publication_fixture(directory)
            (root / 'index.html').write_text(pages.metadata(pages.SITE, 'Codex Plus', '') +
                                           '<main><h1>Codex Plus</h1></main>')
            with self.assertRaisesRegex(ValueError, 'public description'):
                pages.validate_publication(root)

    def test_publication_refuses_unselected_export(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.publication_fixture(directory)
            (root / 'private-note.txt').write_text('fixture')
            with self.assertRaisesRegex(ValueError, 'public file inventory differs'):
                pages.validate_publication(root)

    def test_publication_refuses_stale_sitemap(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.publication_fixture(directory)
            path = root / 'sitemap.xml'
            path.write_text(path.read_text().replace(pages.SITE + 'workers/', pages.SITE + 'wrong/'))
            with self.assertRaisesRegex(ValueError, 'public sitemap differs'):
                pages.validate_publication(root)

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
