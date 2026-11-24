"""Offline checks of public environment routing and site integrity."""
import importlib.machinery
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('pages_builder', str(ROOT / 'scripts/build-pages'))
spec = importlib.util.spec_from_loader(loader.name, loader)
pages = importlib.util.module_from_spec(spec)
loader.exec_module(pages)

THEME_STYLE = (
    '<style id="site-theme">:root{color-scheme:dark;--paper:#142A3B;--ink:#F4F7F8}'
    '.note{color:var(--ink)}</style>')
THEME_SCRIPT = '<script id="site-appearance">/* test control */</script>'
THEMED_LANDING = '<!doctype html><html><head>' + THEME_STYLE + THEME_SCRIPT + '</head><body></body></html>'
THEME = pages.site_theme(THEMED_LANDING)


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
            'docs/presentation/index.html': f'Codex Plus {published_short}.\n',
            'docs/workers.md': ('$luna-task $luna-goal-loop $adaptive-task $adaptive-goal-loop '
                                '$sol-task $astra-task $terra-task skills/html-report\n\n'
                                '## Installation\n'
                                '[Select a release](manage-agent.md#resolve-and-verify-one-published-release)\n'),
            'codex_plus/__init__.py': f'VERSION = {source!r}\n',
        }
        for name, text in files.items():
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        return root

    def test_current_guide_claims_match_their_documented_anchors(self):
        self.assertEqual(pages.validate_current_guides(), 12)

    def test_presentation_pages_keep_overview_and_walkthrough_canonical_routes(self):
        self.assertEqual(pages.PRESENTATION_PAGES, {
            'index.html': pages.SITE,
            'walkthrough/index.html': pages.SITE + 'walkthrough/',
        })
        self.assertEqual(
            {name: route for name, (route, _title) in pages.GUIDES.items()},
            {
                'getting-started.md': 'start',
                'manage-agent.md': 'manage',
                'daily-use.md': 'daily-use',
                'session-communication.md': 'sessions',
                'workers.md': 'workers',
                'architecture.md': 'architecture',
                'environments.md': 'environments',
                'soak-checklist.md': 'soak-checklist',
                'routing-diagnostics.md': 'routing-diagnostics',
                'html-report-usage.md': 'reports',
                'runtime-distribution.md': 'installation',
            })

    def test_each_feature_has_a_request_and_its_own_guide_on_the_overview(self):
        source = (ROOT / 'docs/presentation/overview.html').read_text()
        overview = pages.links(source, './')
        sections = re.findall(r'<section class="feature"[^>]*>(.*?)</section>', overview, re.S)
        self.assertEqual(len(sections), 4)
        guide_links = []
        for section in sections:
            self.assertIn('<code>', section)
            guide = re.search(r'href="\./([a-z-]+)/"', section)
            self.assertIsNotNone(guide)
            guide_links.append(guide[1])
        self.assertCountEqual(guide_links, ['daily-use', 'reports', 'sessions', 'workers'])

    def test_workflow_steps_and_task_choices_reach_the_same_examples(self):
        source = (ROOT / 'docs/presentation/overview.html').read_text()
        choices = re.findall(r'<a id="choose-[^"]+" href="#([^"]+)" aria-controls="([^"]+)">', source)
        panels = re.findall(r'<section class="feature" id="([^"]+)" aria-labelledby="([^"]+)">', source)
        self.assertEqual(len(choices), 4)
        self.assertCountEqual(choices, [(heading, panel) for panel, heading in panels])
        workflow = re.search(r'<ol class="sequence"[^>]*>(.*?)</ol>', source, re.S)
        self.assertIsNotNone(workflow)
        self.assertCountEqual(re.findall(r'href="#([^"]+)"', workflow[1]),
                              [heading for heading, _ in choices])

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
                self.assertEqual(pages.validate_current_guides(root), 12)

    def test_guide_consistency_does_not_require_a_source_version_module(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            (root / 'codex_plus/__init__.py').unlink()
            self.assertEqual(pages.validate_current_guides(root), 12)

    def test_worker_installation_requires_the_canonical_release_selector(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/workers.md'
            path.write_text(path.read_text().replace(
                'manage-agent.md#resolve-and-verify-one-published-release',
                'manage-agent.md#install-or-upgrade-through-the-configuration-owner'))
            message = 'worker installation must link to the canonical release selector'
            with self.assertRaisesRegex(ValueError, message):
                pages.validate_current_guides(root)

    def test_worker_installation_rejects_a_numbered_preview_archive_pin(self):
        phrases = (
            'Use the verified preview.18 worker release archive.',
            "Use preview.18's verified archive.",
        )
        for phrase in phrases:
            with self.subTest(phrase=phrase), tempfile.TemporaryDirectory() as directory:
                root = self.release_fixture(directory)
                path = root / 'docs/workers.md'
                path.write_text(path.read_text() + f'\n{phrase}\n')
                message = 'worker installation must not pin a numbered preview archive'
                with self.assertRaisesRegex(ValueError, message):
                    pages.validate_current_guides(root)

    def test_worker_installation_rejects_a_versioned_worker_archive_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/workers.md'
            path.write_text(path.read_text() + '\nInstall codex-plus-workers-0.1.0-preview.18.tar.gz.\n')
            message = 'worker installation must not pin a numbered preview archive'
            with self.assertRaisesRegex(ValueError, message):
                pages.validate_current_guides(root)

    def test_worker_migration_note_can_mention_a_prior_release_near_selector(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/workers.md'
            note = ('\nFor preview.18 installs, use the [release selector]'
                    '(manage-agent.md#resolve-and-verify-one-published-release).\n')
            path.write_text(path.read_text() + note)
            self.assertEqual(pages.validate_current_guides(root), 12)

    def test_worker_installation_pin_check_ignores_historical_release_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory)
            path = root / 'docs/workers.md'
            path.write_text(path.read_text() + '\n## Historical release notes\nUsed the preview.18 worker release archive.\n')
            self.assertEqual(pages.validate_current_guides(root), 12)

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

    def test_managed_source_selection_can_report_a_partial_fleet_rollout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.release_fixture(directory, source='0.1.0-preview.19',
                                        published='0.1.0-preview.19', managed='0.1.0-preview.19')
            substitutions = {
                'README.md': ('Snap, Starship and Carbon select', 'Managed configuration selects'),
                'docs/architecture.md': ('Snap, Starship and Carbon select', 'Managed source selects'),
                'docs/runtime-distribution.md': ('Snap, Starship and Carbon select workers', 'Managed source selects workers'),
            }
            for name, (old, new) in substitutions.items():
                path = root / name
                path.write_text(path.read_text().replace(old, new) +
                    '\nVerified host receipts: Snap/Starship preview.19; Carbon offline, last verified preview.18.\n')
            self.assertEqual(pages.validate_current_guides(root), 12)
            path = root / 'docs/runtime-distribution.md'
            path.write_text(path.read_text().replace('**preview.19**', '**preview.18**'))
            with self.assertRaisesRegex(ValueError, 'inconsistent managed release claim'):
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
        nav = pages.guide_page('environments.md', 'environments', 'Environments', '<h1>Homes</h1>', '', THEME)
        self.assertIn('<span aria-current="page">Environments</span>', nav)

    def test_historical_guides_remain_on_github(self):
        self.assertEqual(pages.rewrite_link('implementation-history.md#earlier-implementation-history', '../'),
                         pages.SOURCE + 'implementation-history.md#earlier-implementation-history')

    def test_worker_guide_is_public_and_keeps_fragment(self):
        self.assertEqual(pages.rewrite_link('workers.md#choose-a-workflow', '../'),
                         '../workers/#choose-a-workflow')
        self.assertEqual(pages.rewrite_link(pages.SOURCE + 'workers.md', './'), './workers/')
        nav = pages.guide_page('workers.md', 'workers', 'Worker workflows', '<h1>Workers</h1>', '', THEME)
        self.assertIn('<nav class="guide-nav"', nav)
        self.assertIn('<a href="../">Overview</a>', nav)
        self.assertIn('<a href="../walkthrough/">Walkthrough</a>', nav)
        self.assertIn('<a href="../#guide-directory">Guides</a>', nav)
        self.assertIn('<a href="../manage/">Install</a>', nav)
        self.assertIn('<p class="guide-trail">', nav)
        self.assertIn('<span aria-current="page">Worker workflows</span>', nav)

    def test_presentation_links_use_the_new_public_routes(self):
        cases = (
            ('presentation.md#scenes', './', './walkthrough/#scenes'),
            ('presentation/index.html#workers', '../', '../walkthrough/#workers'),
            ('presentation/overview.html#guide-directory', '../', '../#guide-directory'),
            (pages.SOURCE + 'presentation.md#scenes', './', './walkthrough/#scenes'),
            (pages.SOURCE + 'presentation/index.html', '../', '../walkthrough/'),
            (pages.SOURCE + 'presentation/overview.html#guide-directory', '../', '../#guide-directory'),
        )
        for url, prefix, expected in cases:
            with self.subTest(url=url, prefix=prefix):
                self.assertEqual(pages.rewrite_link(url, prefix), expected)

    def test_walkthrough_fragment_fallback_uses_only_moved_actual_ids(self):
        overview = (
            '<main id="main"><h1 id="title">Overview</h1>'
            '<section id="package"><h2 id="package-title">Package</h2></section></main>')
        walkthrough = (
            '<main id="main"><h1 id="title">Walkthrough</h1>'
            '<section id="package"><h2 id="package-title">Package</h2></section>'
            '<section id="scenes"><h2 id="scene-title">Scenes</h2></section>'
            '<button id="next">Next</button></main>')
        result = pages.walkthrough_fragment_links(overview, walkthrough)
        self.assertIn('<aside class="fragment-entry wrap" id="scenes">', result)
        self.assertIn('<aside class="fragment-entry wrap" id="scene-title">', result)
        self.assertIn('<aside class="fragment-entry wrap" id="next">', result)
        self.assertNotIn('id="package"', result)
        self.assertNotIn('id="package-title"', result)
        hrefs = re.findall(r'href="([^"]+)"', result)
        self.assertTrue(hrefs)
        self.assertTrue(all(href.startswith('./walkthrough/#') for href in hrefs), hrefs)
        self.assertNotIn('<script', result)
        self.assertNotIn('onclick=', result)

    def test_prepared_guide_figures_decorate_only_the_first_list_in_the_selected_section(self):
        workers = (
            '<h2 id="working-in-parallel">Working in parallel</h2>'
            '<p>Introductory text.</p>'
            '<ol><li>First step<ul class="fanout"><li>Native branch</li></ul></li></ol>'
            '<ul><li>Later list stays native.</li></ul>'
            '<h2 id="next-section">Next section</h2><ol><li>Next section stays native.</li></ol>')
        result = pages.guide_figure('workers.md', workers)
        self.assertIn('<ol class="guide-figure guide-steps"', result)
        self.assertEqual(result.count('class="guide-figure guide-steps"'), 1)
        self.assertIn('<ul class="fanout"><li>Native branch</li></ul>', result)
        self.assertIn('<ul><li>Later list stays native.</li></ul>', result)
        self.assertIn('<h2 id="next-section">Next section</h2><ol><li>Next section stays native.</li></ol>', result)

        getting_started = (
            '<h2 id="choose-what-to-install">Choose what to install</h2>'
            '<p>Choose a component.</p><ul><li>Workers</li><li>Monitoring</li></ul>')
        result = pages.guide_figure('getting-started.md', getting_started)
        self.assertIn('<ul class="guide-figure guide-choices"', result)
        self.assertEqual(result.count('class="guide-figure guide-choices"'), 1)

    def test_guide_figures_leave_missing_sections_and_unknown_guides_unchanged(self):
        body = '<h2 id="not-prepared">A section without a selected figure</h2><ul><li>Choice</li></ul>'
        self.assertEqual(pages.guide_figure('workers.md', body), body)
        self.assertEqual(pages.guide_figure('unknown-guide.md', body), body)

    def test_github_accessible_table_keeps_attributes_inside_scroll_container(self):
        body = '<markdown-accessiblity-table><table role="table"><tr><td>Wide</td></tr></table></markdown-accessiblity-table>'
        result = pages.guide_page('architecture.md', 'architecture', 'How it works', body, '', THEME)
        self.assertIn('tabindex="0" role="region" aria-label="Scrollable table"><table role="table">', result)
        self.assertIn('</table></div></markdown-accessiblity-table>', result)

    def test_duplicate_heading_slugs_are_distinct(self):
        result = pages.headings('<h2>Same home</h2><h2>Same home</h2>')
        self.assertIn('id="same-home"', result)
        self.assertIn('id="same-home-1"', result)

    def test_authored_github_anchor_survives_heading_rename(self):
        rendered = ('<a id="user-content-former-heading"></a><h3>Renamed heading</h3>'
                    '<a href="#former-heading">Saved link</a>')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'index.html').write_text(pages.headings(pages.links(rendered, './')))
            self.assertEqual(pages.validate(root), 1)

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
        body = pages.headings('<h1>Workers</h1>\n<p dir="auto">Choose a worker.</p>'
                              '<h2>Choose &amp; review</h2><h2>Choose &amp; review</h2>')
        result = pages.guide_page('workers.md', 'workers', 'Luna & workers', body, '', THEME)
        self.assertIn('Choose a worker.</p><details class="toc">', result)
        self.assertIn('<a class="skip" href="#main">', result)
        self.assertIn('<main id="main" tabindex="-1">', result)
        self.assertIn('aria-label="On this page"', result)
        self.assertIn('href="#choose--review-1">Choose &amp; review</a>', result)
        self.assertIn('aria-label="Related guides"', result)

    def test_guide_uses_source_theme_and_matches_metadata_color(self):
        style, paper = THEME
        result = pages.guide_page(
            'workers.md', 'workers', 'Luna & workers', '<h1>Workers</h1>', '', THEME)
        self.assertEqual(style, THEME_STYLE + THEME_SCRIPT)
        self.assertIn(style, result)
        self.assertIn(f'<meta name="theme-color" content="{paper}">', result)
        self.assertEqual(paper, '#142a3b')

    def test_public_templates_share_dark_default_metadata_and_appearance_script(self):
        overview = (ROOT / 'docs/presentation/overview.html').read_text()
        walkthrough = (ROOT / 'docs/presentation/index.html').read_text()
        theme = pages.site_theme(walkthrough)
        for page in (pages.overview_page(overview, walkthrough, '', theme, 'Install request'),
                     pages.presentation_page(walkthrough, 'walkthrough/', theme[1]),
                     pages.guide_page('workers.md', 'workers', 'Workers', '<h1>Workers</h1>', '', theme)):
            head = page.split('</head>')[0]
            self.assertIn('<meta name="theme-color" content="#111213">', head)
            self.assertEqual(page.count('id="site-appearance"'), 1)
            self.assertIn('id="site-appearance"', head)

    def test_metadata_escapes_titles_and_uses_public_route(self):
        result = pages.metadata(
            pages.SITE + 'workers/', 'Luna & "review"', 'Choose <workers>.', THEME[1])
        self.assertIn('Luna &amp; &quot;review&quot;', result)
        self.assertIn('Choose &lt;workers&gt;.', result)
        self.assertIn('rel="canonical" href="' + pages.SITE + 'workers/"', result)

    def publication_fixture(self, directory):
        root = Path(directory)
        presentation_labels = {
            'index.html': ('Codex Plus', 'Overview of workers and watches.'),
            'walkthrough/index.html': ('Interactive walkthrough', 'Illustrated Codex Plus workflows.'),
        }
        for name, url in pages.PRESENTATION_PAGES.items():
            title, description = presentation_labels[name]
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(pages.metadata(url, title, description, THEME[1]) +
                              f'<main><h1>{title}</h1></main>')
        for name, (route, title) in pages.GUIDES.items():
            (root / route).mkdir()
            (root / route / 'index.html').write_text(
                pages.guide_page(name, route, title, '<h1>Guide</h1>', '', THEME))
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

    def test_overview_offers_the_canonical_install_request_before_the_feature_guides(self):
        request = pages.lifecycle_requests((ROOT / 'docs/manage-agent.md').read_text())['Install']
        source = (ROOT / 'docs/presentation/overview.html').read_text()
        page = pages.overview_page(source, THEMED_LANDING, '', THEME, request)
        first_screen = page.split('<section class="feature"', 1)[0]
        self.assertRegex(first_screen, r'<textarea\b[^>]*\breadonly\b[^>]*>' + re.escape(request) + r'</textarea>')
        self.assertIn(f'data-copy-request="{request}"', first_screen)
        self.assertIn(pages.COPY_SCRIPT, page)

    def test_agent_requests_share_authored_text_and_keep_manual_copy(self):
        requests = pages.lifecycle_requests((ROOT / 'docs/manage-agent.md').read_text())
        self.assertEqual(len(requests), 7)
        self.assertIn(requests['Install'], pages.action_cards(requests))
        body = '<h1>Manage</h1><table>' + ''.join(
            '<tr><td>' + name + '</td><td>' + request + '</td></tr>'
            for name, request in requests.items()) + '</table>'
        page = pages.guide_page('manage-agent.md', 'manage', 'Manage', body, '', THEME, requests)
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

    def test_publication_requires_both_presentation_pages(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.publication_fixture(directory)
            (root / 'walkthrough/index.html').unlink()
            with self.assertRaisesRegex(ValueError, 'public file inventory differs'):
                pages.validate_publication(root)

    def test_public_sitemap_requires_walkthrough_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.publication_fixture(directory)
            path = root / 'sitemap.xml'
            entry = '<url><loc>' + pages.SITE + 'walkthrough/</loc></url>'
            sitemap = path.read_text()
            self.assertIn(entry, sitemap)
            path.write_text(sitemap.replace(entry, ''))
            with self.assertRaisesRegex(ValueError, 'public sitemap differs'):
                pages.validate_publication(root)

    def test_publication_refuses_wrong_walkthrough_canonical_route(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.publication_fixture(directory)
            path = root / 'walkthrough/index.html'
            path.write_text(path.read_text().replace(pages.SITE + 'walkthrough/', pages.SITE + 'wrong/'))
            with self.assertRaisesRegex(ValueError, 'public URL metadata differs'):
                pages.validate_publication(root)

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
            (root / 'index.html').write_text(pages.metadata(pages.SITE, 'Codex Plus', '', THEME[1]) +
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

    def test_raw_agent_guide_links_resolve_from_the_exported_markdown_address(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'workers').mkdir()
            (root / 'workers/index.html').write_text('<h2 id="named-task">Named task</h2>')
            for href, error in (
                ('workers.md#named-task', 'broken site link'),
                (pages.SITE + 'workers/#missing', 'broken site anchor'),
                (pages.SITE + 'workers/#named-task', None),
            ):
                with self.subTest(href=href):
                    raw = {'manage.md': f'<a href="{href}">Worker guide</a>'}
                    if error:
                        with self.assertRaisesRegex(ValueError, error + ' in manage.md'):
                            pages.validate(root, raw)
                    else:
                        self.assertEqual(pages.validate(root, raw), 1)

    def test_duplicate_control_id_refuses_publication(self):
        with self.assertRaisesRegex(ValueError, 'duplicate site id'):
            self.validate_site('<button id="select">OSS</button><button id="select">Work</button>')

    def test_escaping_site_root_refuses_publication(self):
        with self.assertRaisesRegex(ValueError, 'broken site link'):
            self.validate_site('<a href="../outside.html">Outside</a>')


if __name__ == '__main__':
    unittest.main()
