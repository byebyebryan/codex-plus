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
    def release_fixture(self, directory, *, source='0.1.0-preview.12',
                        published='0.1.0-preview.12', managed='0.1.0-preview.12'):
        root = Path(directory)
        published_short = published.split('-', 1)[-1]
        managed_short = managed.split('-', 1)[-1]
        files = {
            'README.md': (f'## Current status\n\n**v{published}** includes released features.\n\n'
                          f'Snap, Starship and Carbon select **v{managed}** for all components.\n'),
            'docs/getting-started.md': f'**v{published}** supplies the released workflows.\n',
            'docs/architecture.md': (f'Codex Plus `v{published}` unifies components.\n'
                                     f'Snap, Starship and Carbon select {managed_short} artifacts.\n'),
            'docs/runtime-distribution.md': (
                f'[v{published}](https://github.com/byebyebryan/codex-plus/releases/tag/v{published})\n\n'
                f'| Workers | `codex-plus-workers-{published}.tar.gz` |\n'
                f'| Monitoring | `codex-plus-runtime-{published}.tar.gz` |\n'
                f'| Reporting | `codex-plus-report-{published}.tar.gz` |\n\n'
                f'Snap, Starship and Carbon select workers, monitoring and reporting **{managed_short}**.\n'),
            'docs/presentation/index.html': f'Codex Plus {published_short}. Available in {published_short}\n',
            'docs/workers.md': '$luna-task $luna-goal-loop $worker-task $worker-goal-loop skills/html-report\n',
            'codex_plus/__init__.py': f'VERSION = {source!r}\n',
        }
        for name, text in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        return root

    def test_current_guide_claims_match_their_documented_anchors(self):
        self.assertEqual(pages.validate_current_guides(), 15)

    def test_release_transitions_allow_independent_versions(self):
        cases = (
            ('0.1.0-preview.12', '0.1.0-preview.12', '0.1.0-preview.12'),
            ('0.1.0-preview.13', '0.1.0-preview.12', '0.1.0-preview.12'),
            ('0.1.0-preview.13', '0.1.0-preview.13', '0.1.0-preview.12'),
            ('0.1.0-preview.14', '0.1.0-preview.13', '0.1.0-preview.12'),
            ('0.1.0-preview.13', '0.1.0-preview.13', '0.1.0-preview.11'),
            ('0.2.0-preview.1', '0.1.0-preview.13', '0.1.0-preview.12'),
            ('0.3.0-preview.1', '0.1.0-preview.13', '0.2.0-preview.12'),
        )
        for source, published, managed in cases:
            with self.subTest(source=source, published=published, managed=managed), tempfile.TemporaryDirectory() as directory:
                root = self.release_fixture(directory, source=source, published=published, managed=managed)
                self.assertEqual(pages.validate_current_guides(root), 13)

    def test_guide_consistency_does_not_require_a_source_version_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            (root / 'codex_plus/__init__.py').unlink()
            self.assertEqual(pages.validate_current_guides(root), 13)

    def test_stale_setup_claim_is_rejected_without_rejecting_historical_features(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/getting-started.md'
            path.write_text(path.read_text().replace('**v0.1.0-preview.12** supplies', '**v0.0.0-preview.0** supplies'))
            with self.assertRaisesRegex(ValueError, 'inconsistent published release claim in docs/getting-started.md.*expected 0.1.0-preview.12'):
                pages.validate_current_guides(root)

    def test_stale_managed_architecture_claim_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/architecture.md'
            path.write_text(path.read_text().replace('and Carbon select preview.12', 'and Carbon select preview.0'))
            with self.assertRaisesRegex(ValueError, 'inconsistent managed release claim in docs/architecture.md.*expected 0.1.0-preview.12'):
                pages.validate_current_guides(root)

    def test_release_link_label_target_and_each_archive_are_checked(self):
        claims = ('[v0.1.0-preview.12]', '/tag/v0.1.0-preview.12)',
                  'workers-0.1.0-preview.12.tar.gz', 'runtime-0.1.0-preview.12.tar.gz',
                  'report-0.1.0-preview.12.tar.gz')
        for claim in claims:
            with self.subTest(claim=claim), tempfile.TemporaryDirectory() as directory:
                root = self.release_fixture(directory)
                path = root / 'docs/runtime-distribution.md'
                path.write_text(path.read_text().replace(claim, claim.replace('preview.12', 'preview.0')))
                with self.assertRaisesRegex(ValueError, 'inconsistent published release claim in docs/runtime-distribution.md'):
                    pages.validate_current_guides(root)

    def test_managed_installation_claim_uses_managed_anchor(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory, published='0.1.0-preview.13')
            path = root / 'docs/runtime-distribution.md'
            path.write_text(path.read_text().replace('**preview.12**', '**preview.13**'))
            with self.assertRaisesRegex(ValueError, 'inconsistent managed release claim in docs/runtime-distribution.md.*expected 0.1.0-preview.12'):
                pages.validate_current_guides(root)

    def test_missing_duplicate_and_malformed_anchors_are_rejected(self):
        anchors = {
            'published': '**v0.1.0-preview.12** includes released features.',
            'managed': 'Snap, Starship and Carbon select **v0.1.0-preview.12** for all components.',
        }
        for domain, anchor in anchors.items():
            replacements = {
                'missing': '',
                'ambiguous': anchor + '\n' + anchor,
                'malformed': anchor.replace('0.1.0-preview.12', 'not-a-version'),
            }
            for reason, replacement in replacements.items():
                with self.subTest(domain=domain, reason=reason), tempfile.TemporaryDirectory() as directory:
                    root = self.release_fixture(directory)
                    path = root / 'README.md'
                    path.write_text(path.read_text().replace(anchor, replacement))
                    with self.assertRaisesRegex(ValueError, f'{reason} {domain} release anchor in README.md'):
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
            with self.assertRaisesRegex(ValueError, 'published release claim missing'):
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

    def test_self_site_links_work_in_local_previews_and_raw_guide(self):
        self.assertEqual(pages.rewrite_link(pages.SITE + 'manage.md', '../'), '../manage.md')
        self.assertEqual(pages.rewrite_link(pages.SITE + 'installation/#upgrade-rollback-and-activation', '../'),
                         '../installation/#upgrade-rollback-and-activation')
        self.assertEqual(pages.rewrite_link('https://example.invalid/codex-plus/manage.md', '../'),
                         'https://example.invalid/codex-plus/manage.md')

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
        pages.write_raw_guides(root)
        return root

    def test_raw_agent_guide_is_exact_and_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.publication_fixture(directory)
            raw = root / 'manage.md'
            self.assertEqual(raw.read_bytes(), (ROOT / 'docs/manage-agent.md').read_bytes())
            raw.write_text('stale instructions')
            with self.assertRaisesRegex(ValueError, 'raw guide differs'):
                pages.validate_publication(root)
            raw.unlink()
            with self.assertRaisesRegex(ValueError, 'public file inventory differs'):
                pages.validate_publication(root)

    def test_agent_requests_share_authored_text_and_keep_manual_copy(self):
        requests = pages.lifecycle_requests((ROOT / 'docs/manage-agent.md').read_text())
        self.assertEqual(len(requests), 7)
        self.assertIn(requests['Install'], pages.action_cards(requests))
        body = '<h1>Manage</h1><table>' + ''.join(
            '<tr><td>' + name + '</td><td>' + request + '</td></tr>'
            for name, request in requests.items()) + '</table>'
        page = pages.guide_page('manage-agent.md', 'manage', 'Manage', body, '', requests)
        self.assertIn('hidden data-copy-request="' + requests['Install'] + '"', page)
        self.assertIn('Plain Markdown for your agent', page)
        self.assertIn('copy it manually', page)
        self.assertIn('<td>' + requests['Install'], page)
        self.assertEqual(pages.rewrite_link('manage-agent.md#roll-back', '../'), '../manage/#roll-back')

    def test_rendered_agent_requests_preserve_table_attributes_and_markup(self):
        requests = pages.lifecycle_requests((ROOT / 'docs/manage-agent.md').read_text())
        body = '<table>' + ''.join(
            '<tr><td align="left">\n<span>' + request + '</span>\n</td></tr>'
            for request in requests.values()) + '</table>'
        result = pages.action_table(body, requests)
        self.assertEqual(result.count('<td align="left">'), 7)
        self.assertEqual(result.count('data-copy-request='), 7)
        self.assertIn('<span>' + requests['Upgrade'] + '</span>', result)

    def test_rendered_agent_requests_refuse_missing_duplicate_or_changed_cells(self):
        requests = pages.lifecycle_requests((ROOT / 'docs/manage-agent.md').read_text())
        cells = ['<td>' + request + '</td>' for request in requests.values()]
        for invalid in (cells[:-1], cells + cells[:1],
                        [cell.replace('installation.', 'installation today.') for cell in cells]):
            with self.subTest(body=invalid):
                with self.assertRaisesRegex(ValueError, 'rendered agent action requests'):
                    pages.action_table('<table><tr>' + ''.join(invalid) + '</tr></table>', requests)

    def test_agent_copy_controls_have_distinct_accessible_names(self):
        requests = pages.lifecycle_requests((ROOT / 'docs/manage-agent.md').read_text())
        body = '<table>' + ''.join('<tr><td>' + request + '</td></tr>'
                                  for request in requests.values()) + '</table>'
        result = pages.action_table(body, requests)
        for name in requests:
            self.assertIn('aria-label="Copy ' + name.lower() + ' request"', result)
        self.assertIn('aria-label="Copy install request"', pages.action_cards(requests))

    def test_agent_requests_refuse_missing_actions_or_another_guide(self):
        text = (ROOT / 'docs/manage-agent.md').read_text()
        for changed in (text.replace('| Upgrade | Read', '| Other | Read'),
                        text.replace(pages.SITE + 'manage.md', pages.SITE + 'wrong.md')):
            with self.assertRaisesRegex(ValueError, 'canonical Markdown guide'):
                pages.lifecycle_requests(changed)

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
