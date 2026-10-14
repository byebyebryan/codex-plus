"""Observable publication, concurrency, recovery and delivery invariants."""

from concurrent.futures import ThreadPoolExecutor
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch

from codex_plus.reports import config, hosting
from codex_plus.reports.store import Store, canonical


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bundle = self.root / "source"; self.bundle.mkdir()
        (self.bundle / "index.html").write_text('<link rel="stylesheet" href="assets/theme.css"><h1>Result</h1>')
        (self.bundle / "assets").mkdir(); (self.bundle / "assets/theme.css").write_text("h1{color:teal}")
        self.options = config.Config(self.root / "store", "http://starship:8787/reports/")
        self.store = Store(self.options)

    def publish(self, **options):
        return self.store.publish(self.bundle, "Result", **options)

    def test_snapshot_survives_source_edits_and_unchanged_retry_reuses_url(self):
        first = self.publish(project="demo"); second = self.publish(project="demo")
        self.assertTrue(first["url"].endswith(first["report_id"] + "/"))
        self.assertEqual(first["report_id"], second["report_id"])
        self.assertEqual(second["publication"], "reused")
        self.assertEqual(self.store.list()["total"], 1)
        (self.bundle / "index.html").write_text("<h1>Revised</h1>")
        newer = self.publish(project="demo")
        self.assertNotEqual(first["report_id"], newer["report_id"])
        self.assertIn("Result", (Path(first["snapshot_path"]) / "index.html").read_text())
        shutil.rmtree(self.bundle)
        self.assertTrue((Path(first["snapshot_path"]) / "assets/theme.css").exists())

    def test_source_paths_do_not_change_identity_and_catalog_does_not_leak_provenance(self):
        first = self.publish(project="demo")
        moved = self.root / "elsewhere"; shutil.copytree(self.bundle, moved)
        again = self.store.publish(moved, "Result", project="demo")
        self.assertEqual(first["report_id"], again["report_id"])
        page = (self.options.data_root / "public/index.html").read_text()
        self.assertNotIn(str(self.bundle), page)
        self.assertIn("demo", page)
        self.assertFalse((Path(first["snapshot_path"]) / "metadata.json").exists())

    def test_utf8_entrypoint_url_and_catalog_text_are_safe(self):
        source = self.root / "résult summary.html"; source.write_text("<h1>Unicode</h1>")
        report = self.store.publish(source, '<script>alert("bad")</script>')
        self.assertIn("r%C3%A9sult%20summary.html", report["url"])
        page = (self.options.data_root / "public/index.html").read_text()
        self.assertNotIn('<script>alert("bad")</script>', page)
        self.assertIn("&lt;script&gt;", page)

    def test_disabled_catalog_preserves_direct_links(self):
        disabled = Store(config.Config(self.root / "disabled", self.options.base_url, catalog_enabled=False))
        report = disabled.publish(self.bundle, "Result")
        page = (disabled.root / "public/index.html").read_text()
        self.assertNotIn(report["report_id"], page)
        self.assertEqual(report["catalog"]["state"], "disabled")
        self.assertTrue((Path(report["snapshot_path"]) / "index.html").is_file())

    def test_new_store_concurrent_publications_keep_every_snapshot_and_index_entry(self):
        def publish(number):
            return Store(self.options).publish(self.bundle, f"Result {number}")
        with ThreadPoolExecutor(max_workers=8) as pool:
            reports = list(pool.map(publish, range(12)))
        self.assertEqual(self.store.list()["total"], 12)
        page = (self.options.data_root / "public/index.html").read_text()
        for report in reports:
            self.assertIn(report["report_id"], page)
        self.assertEqual(self.store.doctor()["staging"], [])

    def test_post_rename_crash_is_inspectable_and_exact_retry_finishes_commit(self):
        real_save = self.store.save
        def crash(record):
            if record["state"] == "published": raise RuntimeError("simulated process loss")
            real_save(record)
        with patch.object(self.store, "save", side_effect=crash):
            with self.assertRaisesRegex(RuntimeError, "process loss"): self.publish()
        self.assertEqual(self.store.list()["total"], 0)
        self.assertEqual(self.store.doctor()["gaps"][0]["state"], "prepared")
        preview = self.store.repair()
        self.assertFalse(preview["applied"])
        recovered = self.publish()
        self.assertEqual(recovered["publication"], "reused")
        self.assertEqual(self.store.list()["total"], 1)
        self.assertEqual(self.store.doctor()["gaps"], [])

    def test_catalog_failure_retains_snapshot_and_rebuild_repairs_it(self):
        with patch.object(self.store, "rebuild", side_effect=OSError("index unavailable")):
            report = self.publish()
        self.assertEqual(report["catalog"]["state"], "stale")
        self.assertTrue(Path(report["snapshot_path"]).is_dir())
        self.assertEqual(self.store.doctor()["catalog"], "stale")
        self.store.repair(apply=True)
        self.assertEqual(self.store.doctor()["catalog"], "current")

    def test_delete_crash_preserves_source_other_report_and_resumes_exact_cleanup(self):
        first = self.publish(); other = self.store.publish(self.bundle, "Other")
        real_save = self.store.save
        def crash(record):
            if record["state"] == "deleted": raise RuntimeError("simulated deletion loss")
            real_save(record)
        with patch.object(self.store, "save", side_effect=crash):
            with self.assertRaises(RuntimeError): self.store.delete(first["report_id"])
        self.assertFalse(Path(first["snapshot_path"]).exists())
        self.assertTrue(self.bundle.exists()); self.assertTrue(Path(other["snapshot_path"]).exists())
        self.assertEqual(self.store.doctor()["gaps"][0]["state"], "deleting")
        self.store.repair(apply=True)
        self.assertEqual(self.store.doctor()["trash"], [])
        self.assertEqual(self.store.list()["total"], 1)
        self.assertNotIn(first["report_id"], (self.store.root / "public/index.html").read_text())

    def interrupted_trash_removal(self):
        report = self.publish()
        with patch('codex_plus.reports.store.shutil.rmtree', side_effect=OSError('interrupted trash removal')):
            with self.assertRaises(OSError): self.store.delete(report['report_id'])
        record = self.store.record(report['report_id'])
        self.assertEqual(record['state'], 'deleted')
        self.assertTrue((self.store.root / 'trash' / record['trash_id']).is_dir())
        return report, record

    def test_republication_preserves_pending_trash_identity_until_explicit_repair(self):
        report, deleted = self.interrupted_trash_removal()
        other = self.store.publish(self.bundle, 'Other retained report')
        with self.assertRaisesRegex(ValueError, 'trash cleanup'):
            self.publish()
        self.assertEqual(self.store.record(report['report_id']), deleted)
        self.assertTrue(Path(other['snapshot_path']).is_dir())
        self.assertTrue(self.bundle.is_dir())
        repaired = self.store.repair(apply=True)
        self.assertEqual(repaired['remaining']['trash'], [])
        restored = self.publish()
        self.assertEqual(restored['report_id'], report['report_id'])
        self.assertTrue(Path(restored['snapshot_path']).is_dir())

    def test_repeated_delete_finishes_trash_cleanup_without_changing_other_reports(self):
        report, deleted = self.interrupted_trash_removal()
        other = self.store.publish(self.bundle, 'Other retained report')
        result = self.store.delete(report['report_id'])
        self.assertEqual(result['state'], 'deleted')
        self.assertFalse((self.store.root / 'trash' / deleted['trash_id']).exists())
        self.assertTrue(Path(other['snapshot_path']).is_dir())
        self.assertTrue(self.bundle.is_dir())
        self.assertEqual(self.publish()['report_id'], report['report_id'])

    def test_unfinished_deletion_keeps_payload_capacity_reserved_until_cleanup(self):
        bounded = Store(config.Config(self.root / 'bounded-trash', max_bundle_bytes=1000,
                                     max_store_bytes=1000, max_store_reports=1))
        report = bounded.publish(self.bundle, 'First')
        with patch('codex_plus.reports.store.shutil.rmtree', side_effect=OSError('interrupted trash removal')):
            with self.assertRaises(OSError): bounded.delete(report['report_id'])
        with self.assertRaisesRegex(ValueError, 'capacity'):
            bounded.publish(self.bundle, 'Second')
        self.assertEqual(bounded.repair(apply=True)['remaining']['trash'], [])
        self.assertEqual(bounded.publish(self.bundle, 'Second')['publication'], 'created')

    def test_commit_rechecks_deletion_that_completed_while_another_copy_was_active(self):
        from codex_plus.reports import store as module
        real_read = module.read_file
        injected = {}
        def race(path, maximum, destination=None):
            result = real_read(path, maximum, destination)
            if destination is not None and not injected:
                injected['started'] = True
                report = self.publish()
                with patch('codex_plus.reports.store.shutil.rmtree', side_effect=OSError('interrupted trash removal')):
                    with self.assertRaises(OSError): self.store.delete(report['report_id'])
                injected['deleted'] = self.store.record(report['report_id'])
            return result
        with patch.object(module, 'read_file', side_effect=race):
            with self.assertRaisesRegex(ValueError, 'trash cleanup'):
                self.publish()
        deleted = injected['deleted']
        self.assertEqual(self.store.record(deleted['report_id']), deleted)
        self.assertEqual(self.store.doctor()['staging'], [])
        self.assertEqual(self.store.repair(apply=True)['remaining']['trash'], [])
        self.assertEqual(self.publish()['report_id'], deleted['report_id'])

    def test_mutated_existing_snapshot_is_never_overwritten(self):
        report = self.publish(); target = Path(report["snapshot_path"]) / "index.html"
        target.write_text("changed outside the publisher")
        with self.assertRaisesRegex(ValueError, "integrity"): self.publish()
        self.assertEqual(target.read_text(), "changed outside the publisher")

    def test_capacity_refuses_new_reports_but_reuses_existing_without_eviction(self):
        bounded = Store(config.Config(self.root / "bounded", max_bundle_bytes=1000,
                                     max_store_bytes=1000, max_store_reports=1))
        report = bounded.publish(self.bundle, "First")
        self.assertEqual(bounded.publish(self.bundle, "First")["publication"], "reused")
        with self.assertRaisesRegex(ValueError, "capacity"): bounded.publish(self.bundle, "Second")
        self.assertTrue(Path(report["snapshot_path"]).exists())

    def test_smaller_new_limits_do_not_make_old_reports_unreadable(self):
        report = self.publish()
        smaller = Store(config.Config(self.store.root, max_bundle_bytes=1, max_store_bytes=1000,
                                     max_bundle_files=1))
        self.assertEqual(smaller.get(report["report_id"])["report_id"], report["report_id"])
        smaller.delete(report["report_id"])
        self.assertTrue(self.bundle.is_dir())

    def test_path_symlink_and_size_failures_do_not_publish_or_damage_sources(self):
        outside = self.root / "private"; outside.write_text("private")
        (self.bundle / "escape").symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "symlink"): self.publish()
        (self.bundle / "escape").unlink()
        with self.assertRaises(ValueError): self.publish(entrypoint="../private.html")
        tiny = Store(config.Config(self.root / "tiny", max_bundle_bytes=1, max_store_bytes=1000))
        with self.assertRaises(ValueError): tiny.publish(self.bundle, "Result")
        self.assertFalse(tiny.root.exists())
        self.assertEqual(outside.read_text(), "private")

    def test_failed_copy_leaves_no_committed_snapshot_or_capacity_reservation(self):
        from codex_plus.reports import store as module
        real_read = module.read_file
        def changed(path, maximum, destination=None):
            result = real_read(path, maximum, destination)
            if destination is not None: result["sha256"] = "0" * 64
            return result
        with patch.object(module, "read_file", side_effect=changed):
            with self.assertRaisesRegex(ValueError, "source changed"): self.publish()
        self.assertEqual(self.store.list()["total"], 0)
        self.assertEqual(self.store.doctor()["staging"], [])

    def test_readonly_calls_create_no_store_and_unknown_roots_are_preserved(self):
        self.assertEqual(self.store.list()["total"], 0)
        self.assertEqual(self.store.doctor()["store"], "absent")
        self.assertFalse(self.store.root.exists())
        self.store.root.mkdir(); (self.store.root / "existing").write_text("keep")
        with self.assertRaisesRegex(ValueError, "ownership marker"): self.publish()
        self.assertEqual((self.store.root / "existing").read_text(), "keep")

    def test_delivery_verifies_actual_bytes_and_reports_wrong_or_missing_endpoints(self):
        class Handler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(self.root_dir), **kwargs)
            root_dir = self.root / "web"
            def log_message(self, *args): pass
        web = self.root / "web"; web.mkdir()
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True); thread.start()
        self.addCleanup(server.server_close); self.addCleanup(server.shutdown)
        report = self.publish(); record = self.store.record(report["report_id"])
        shutil.copytree(Path(report["snapshot_path"]), web / report["report_id"])
        # A transport fixture may use loopback; deployed configuration cannot.
        report["url"] = f'http://127.0.0.1:{server.server_port}/{report["report_id"]}/index.html'
        result = hosting.check_delivery(self.store, report)
        self.assertEqual(result["state"], "verified")
        (web / report["report_id"] / "index.html").write_text("different body")
        self.assertEqual(hosting.check_delivery(self.store, report)["state"], "unavailable")
        report["url"] = None
        self.assertIn("unconfigured", hosting.check_delivery(self.store, report)["detail"])

    def test_config_checks_and_missing_configuration_are_readonly(self):
        missing = self.root / "missing.toml"
        self.assertIsNone(config.load(missing, data_root=self.root / "unused").base_url)
        self.assertFalse(missing.exists())
        for url in ("http://localhost:8787/", "http://127.0.0.1/", "http://0.0.0.0/",
                    "http://user:password@starship/", "http://starship/../private/", "file:///tmp/"):
            with self.assertRaises(ValueError): config.Config(self.root / "unused", url)
        for content in ('schema = true', 'schema = 2', 'schema = 1\nunknown = "x"'):
            path = self.root / "config.toml"; path.write_text(content)
            with self.assertRaises(ValueError): config.load(path)

    def test_delivery_accepts_only_same_origin_static_index_canonicalization(self):
        from urllib.request import Request
        handler = hosting.NoRedirect()
        request = Request('http://starship:8787/reports/abc/index.html')
        allowed = handler.redirect_request(request, None, 301, 'Moved', {}, 'http://starship:8787/reports/abc/')
        self.assertEqual(allowed.full_url, 'http://starship:8787/reports/abc/')
        for target in ['http://other-host/reports/abc/', 'http://starship:8787/private/',
                       'https://starship:8787/reports/abc/']:
            with self.assertRaises(ValueError): handler.redirect_request(request, None, 301, 'Moved', {}, target)

    def test_hosting_inspection_of_absent_store_is_readonly_without_external_commands(self):
        with patch('subprocess.run', side_effect=AssertionError('no hosting subprocess expected')):
            self.assertEqual(hosting.inspect_hosting(self.options)['state'], 'store_absent')
        self.assertFalse(self.options.data_root.exists())

    def test_metadata_bounds_refuse_unreadable_new_state(self):
        with self.assertRaises(ValueError):
            config.Config(self.root / 'other', max_bundle_files=10001)
        with self.assertRaises(ValueError):
            config.Config(self.root / 'other', max_store_reports=10001)
        with patch('codex_plus.reports.store.MAX_RECORD', 16385):
            with self.assertRaisesRegex(ValueError, 'metadata'):
                self.publish()
        self.assertFalse(self.options.data_root.exists())
        report = self.publish()
        record = self.store.record(report['report_id'])
        with patch.object(self.store, 'records', return_value=[record] * 10000):
            with self.assertRaisesRegex(ValueError, 'history is full'):
                self.store.capacity(1, 'f' * 64)
        self.assertEqual(self.store.get(report['report_id'])['state'], 'published')

    def test_repair_releases_prepared_capacity_when_no_snapshot_became_public(self):
        rename = Path.rename
        def fail_commit(path, target):
            if path.name == 'bundle':
                raise OSError('injected failure before public rename')
            return rename(path, target)
        with patch.object(Path, 'rename', fail_commit):
            with self.assertRaises(OSError):
                self.publish()
        report_id = self.store.doctor()['gaps'][0]['report_id']
        self.assertEqual(self.store.record(report_id)['state'], 'prepared')
        self.assertFalse(self.store.repair()['applied'])
        result = self.store.repair(apply=True)
        self.assertIn('unpublished:' + report_id, result['repaired'])
        self.assertFalse(result['remaining']['gaps'])
        self.assertEqual(self.publish()['publication'], 'created')

    def test_later_host_configuration_exposes_retained_snapshot_without_rewriting_old_links(self):
        unconfigured = Store(config.Config(self.root / "retained"))
        report = unconfigured.publish(self.bundle, "Result")
        self.assertIsNone(report["url"])
        configured = Store(config.Config(unconfigured.root, "http://snap:8787/reports/"))
        self.assertTrue(configured.get(report["report_id"])["url"].startswith("http://snap:"))
        self.assertEqual(configured.record(report["report_id"])["url"], None)
        self.assertEqual(configured.publish(self.bundle, "Result")["publication"], "reused")

    def test_explicit_repair_cleans_only_abandoned_owned_staging_and_keeps_active_copy(self):
        self.publish()
        from codex_plus.reports.store import process_birth
        import os
        def stage(name, pid, birth):
            directory = self.store.root / "staging" / name; directory.mkdir()
            (directory / "bundle").mkdir()
            (directory / "operation.json").write_bytes(canonical({"schema": 1, "operation_id": name,
                "report_id": "0" * 64, "reserved_bytes": 0, "pid": pid, "process_birth": birth}))
            return directory
        active = stage("1" * 32, os.getpid(), process_birth(os.getpid()))
        abandoned = stage("2" * 32, 999999999, "old-birth")
        self.store.repair()
        self.assertTrue(abandoned.exists())
        self.store.repair(apply=True)
        self.assertFalse(abandoned.exists()); self.assertTrue(active.exists())


if __name__ == "__main__": unittest.main()
