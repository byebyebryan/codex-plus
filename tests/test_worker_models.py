import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from codex_plus.worker_models import MAX_CATALOG_BYTES, WorkerModelError, family_for_model, resolve_catalog


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "codex-plus-workers"


def row(model, *, hidden=False, efforts=("xhigh", "max"), ui_id=None):
    value = {
        "model": model,
        "hidden": hidden,
        "supportedReasoningEfforts": [
            {"reasoningEffort": effort, "description": effort + " reasoning"}
            for effort in efforts
        ],
    }
    if ui_id is not None:
        value["id"] = ui_id
    return value


def catalog(*rows, next_cursor=None):
    value = {"data": list(rows), "nextCursor": next_cursor}
    return value


class FamilyClassificationTests(unittest.TestCase):
    def test_exact_concrete_ids_observe_family_floors(self):
        self.assertEqual(family_for_model("gpt-6.1-sol"), "sol")
        self.assertEqual(family_for_model("gpt-6-astra"), "astra")
        self.assertEqual(family_for_model("gpt-6-luna"), "luna")
        self.assertEqual(family_for_model("gpt-6.10-terra"), "terra")
        self.assertIsNone(family_for_model("gpt-6-sol"))
        self.assertIsNone(family_for_model("gpt-5.6-terra"))

    def test_aliases_provider_ids_and_suffixes_are_not_guessed(self):
        for model in (
            "gpt-6.1",
            "gpt-6.1-sol-preview",
            "provider/gpt-6.1-sol",
            "gpt-6.1-solver",
            "gpt-6.1-foo",
            "GPT-6.1-sol",
            "gpt-6.1-sol-latest",
            "gpt-06.2-sol",
            "gpt-6.02-sol",
        ):
            with self.subTest(model=model):
                self.assertIsNone(family_for_model(model))


class CatalogueResolutionTests(unittest.TestCase):
    def test_latest_is_numeric_and_uses_picker_visible_models(self):
        result = resolve_catalog(catalog(
            row("gpt-6.2-sol"),
            row("gpt-6.10-sol", hidden=True),
            row("gpt-6.3-sol"),
            row("gpt-6.1-sol", efforts=("high",)),
        ))
        selected = result["roles"]["sol-xhigh"]
        self.assertEqual(selected["model"], "gpt-6.3-sol")
        self.assertEqual(selected["status"], "resolved")
        self.assertEqual(selected["evidence"]["eligible_picker_models"], [
            "gpt-6.2-sol", "gpt-6.3-sol",
        ])
        self.assertEqual(selected["evidence"]["execution_id_field"], "model")
        self.assertTrue(selected["evidence"]["catalogue_complete"])

    def test_numeric_minor_10_sorts_after_minor_2(self):
        result = resolve_catalog(catalog(row("gpt-6.2-sol"), row("gpt-6.10-sol")))
        self.assertEqual(result["roles"]["sol-xhigh"]["model"], "gpt-6.10-sol")

    def test_family_versions_are_selected_independently(self):
        result = resolve_catalog(catalog(
            row("gpt-6.2-sol"), row("gpt-6.10-sol"),
            row("gpt-6-astra"), row("gpt-7-astra"),
            row("gpt-6-luna"), row("gpt-6.2-luna"),
            row("gpt-6.1-terra"), row("gpt-6.2-terra"),
        ))
        roles = result["roles"]
        self.assertEqual(roles["sol-xhigh"]["model"], "gpt-6.10-sol")
        self.assertEqual(roles["astra-xhigh"]["model"], "gpt-7-astra")
        self.assertEqual(roles["luna-max"]["model"], "gpt-6.2-luna")
        self.assertEqual(roles["terra-6-1-xhigh"]["model"], "gpt-6.2-terra")
        self.assertEqual(roles["sol-xhigh"]["reasoning_effort"], "xhigh")
        self.assertEqual(roles["luna-max"]["reasoning_effort"], "max")

    def test_missing_families_and_unsupported_efforts_are_explicitly_unavailable(self):
        result = resolve_catalog(catalog(
            row("gpt-6.1-sol", efforts=("high",)),
            row("gpt-6-astra", efforts=("xhigh",)),
        ))
        sol = result["roles"]["sol-xhigh"]
        self.assertEqual(sol["status"], "unavailable")
        self.assertIsNone(sol["model"])
        self.assertEqual(sol["evidence"]["reason"], "no-picker-visible-model-supports-effort")
        self.assertEqual(result["roles"]["luna-max"]["status"], "unavailable")
        self.assertEqual(result["roles"]["terra-6-1-xhigh"]["status"], "unavailable")

    def test_legacy_terra_is_evidence_but_never_a_supported_selection(self):
        result = resolve_catalog(catalog(
            row("gpt-5.6-terra"),
            row("gpt-6.0-terra"),
        ))
        terra = result["roles"]["terra-6-1-xhigh"]
        self.assertEqual(terra["status"], "unavailable")
        self.assertIsNone(terra["model"])
        self.assertEqual(terra["evidence"]["family_models"][0]["model"], "gpt-5.6-terra")
        self.assertFalse(terra["evidence"]["family_models"][0]["meets_family_floor"])

    def test_latest_equal_numeric_versions_are_unavailable_as_ambiguous(self):
        result = resolve_catalog(catalog(row("gpt-6-luna"), row("gpt-6.0-luna")))
        luna = result["roles"]["luna-max"]
        self.assertEqual(luna["status"], "unavailable")
        self.assertEqual(luna["evidence"]["reason"], "ambiguous-latest-numeric-version")

    def test_ui_id_is_never_used_as_the_execution_id(self):
        result = resolve_catalog(catalog(row("gpt-6.1-sol", ui_id="sol-latest")))
        self.assertEqual(result["roles"]["sol-xhigh"]["model"], "gpt-6.1-sol")


class PreferenceTests(unittest.TestCase):
    def test_exact_pin_selects_hidden_catalogue_model_without_fallback(self):
        preferences = {"models": {"sol": {"version": "gpt-6.2-sol"}}}
        result = resolve_catalog(catalog(
            row("gpt-6.2-sol", hidden=True), row("gpt-6.3-sol"),
        ), preferences)
        sol = result["roles"]["sol-xhigh"]
        self.assertEqual(sol["model"], "gpt-6.2-sol")
        self.assertFalse(sol["evidence"]["selected_picker_visible"])
        self.assertEqual(sol["preference"], "gpt-6.2-sol")

    def test_exact_pin_not_in_catalogue_is_unavailable_without_latest_fallback(self):
        result = resolve_catalog(catalog(row("gpt-6.3-sol")), {
            "models": {"sol": {"version": "gpt-6.2-sol"}},
        })
        sol = result["roles"]["sol-xhigh"]
        self.assertEqual(sol["status"], "unavailable")
        self.assertIsNone(sol["model"])
        self.assertEqual(sol["preference"], "gpt-6.2-sol")
        self.assertEqual(sol["evidence"]["reason"], "pinned-model-not-in-catalogue")

    def test_exact_pin_must_match_family_floor_catalogue_and_effort(self):
        catalog_value = catalog(
            row("gpt-5.6-terra"),
            row("gpt-6.1-sol", efforts=("high",)),
            row("gpt-6.1-astra"),
        )
        cases = (
            ({"models": {"terra": {"version": "gpt-5.6-terra"}}}, "pinned-model-below-family-floor"),
            ({"models": {"sol": {"version": "gpt-6.1-sol"}}}, "pinned-model-does-not-support-effort"),
            ({"models": {"sol": {"version": "gpt-6.1-astra"}}}, "pinned-model-family-mismatch"),
        )
        for preferences, reason in cases:
            with self.subTest(reason=reason):
                selected = resolve_catalog(catalog_value, preferences)["roles"]
                role = "terra-6-1-xhigh" if "terra" in preferences["models"] else "sol-xhigh"
                self.assertEqual(selected[role]["status"], "unavailable")
                self.assertEqual(selected[role]["evidence"]["reason"], reason)

    def test_unknown_preference_fields_families_and_values_are_rejected(self):
        invalid = (
            {"other": {}},
            {"models": {"unknown": {"version": "latest-available"}}},
            {"models": {"sol": {"version": "gpt-6.1-sol", "effort": "xhigh"}}},
            {"models": {"sol": {"version": "sol-latest"}}},
            {"models": {"sol": {}}},
        )
        for preference in invalid:
            with self.subTest(preference=preference):
                with self.assertRaises(WorkerModelError):
                    resolve_catalog(catalog(row("gpt-6.1-sol")), preference)


class CatalogueValidationTests(unittest.TestCase):
    def test_incomplete_malformed_oversized_and_conflicting_catalogues_are_rejected(self):
        with self.assertRaisesRegex(WorkerModelError, "incomplete"):
            resolve_catalog(catalog(row("gpt-6.1-sol"), next_cursor="more"))
        with self.assertRaisesRegex(WorkerModelError, "data array"):
            resolve_catalog({"nextCursor": None})
        with self.assertRaisesRegex(WorkerModelError, "conflicting metadata"):
            resolve_catalog(catalog(row("gpt-6.1-sol"), row("gpt-6.1-sol", hidden=True)))
        with self.assertRaisesRegex(WorkerModelError, "hidden metadata"):
            resolve_catalog(catalog({"model": "gpt-6.1-sol", "supportedReasoningEfforts": ["xhigh"]}))
        with self.assertRaisesRegex(WorkerModelError, "supportedReasoningEfforts"):
            resolve_catalog(catalog({"model": "gpt-6.1-sol", "hidden": False}))
        with self.assertRaisesRegex(WorkerModelError, "entries must be objects"):
            resolve_catalog(catalog({"model": "gpt-6.1-sol", "hidden": False,
                                     "supportedReasoningEfforts": ["xhigh"]}))
        with self.assertRaisesRegex(WorkerModelError, "duplicate reasoningEffort"):
            resolve_catalog(catalog({"model": "gpt-6.1-sol", "hidden": False,
                                     "supportedReasoningEfforts": [
                                         {"reasoningEffort": "xhigh"},
                                         {"reasoningEffort": "xhigh"},
                                     ]}))
        with self.assertRaisesRegex(WorkerModelError, "too many rows"):
            resolve_catalog([row("gpt-6.1-sol")] * 1025)

    def test_catalogue_with_duplicate_but_identical_execution_rows_is_unambiguous(self):
        selected = resolve_catalog(catalog(row("gpt-6.1-sol"), row("gpt-6.1-sol")))
        self.assertEqual(selected["roles"]["sol-xhigh"]["model"], "gpt-6.1-sol")


class CommandLineTests(unittest.TestCase):
    def invoke(self, *arguments):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *arguments],
                              cwd=ROOT, capture_output=True, text=True, check=False)

    def test_classify_reports_exact_input_and_supported_family_or_null(self):
        result = self.invoke("classify", "--model", "gpt-6.1-sol")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout), {"family": "sol", "model": "gpt-6.1-sol"})
        legacy = self.invoke("classify", "--model", "gpt-5.6-terra")
        self.assertEqual(json.loads(legacy.stdout), {"family": None, "model": "gpt-5.6-terra"})

    def test_resolve_cli_reads_only_supplied_files_and_emits_deterministic_json(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog_path = Path(directory) / "catalog.json"
            preferences_path = Path(directory) / "preferences.toml"
            catalog_path.write_text(json.dumps(catalog(row("gpt-6.10-sol"), row("gpt-6.2-sol"))), encoding="utf-8")
            preferences_path.write_text("[models.sol]\nversion = 'gpt-6.2-sol'\n", encoding="utf-8")
            first = self.invoke("resolve", "--catalog", str(catalog_path), "--preferences", str(preferences_path))
            second = self.invoke("resolve", "--catalog", str(catalog_path), "--preferences", str(preferences_path))
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        result = json.loads(first.stdout)
        self.assertEqual(result["roles"]["sol-xhigh"]["model"], "gpt-6.2-sol")

    def test_incomplete_catalogue_cli_fails_without_emitting_a_resolution(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog_path = Path(directory) / "catalog.json"
            catalog_path.write_text(json.dumps(catalog(row("gpt-6.1-sol"), next_cursor="more")), encoding="utf-8")
            result = self.invoke("resolve", "--catalog", str(catalog_path))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("incomplete", result.stderr)

    def test_malformed_and_oversized_catalogue_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog_path = Path(directory) / "catalog.json"
            catalog_path.write_text("{not JSON", encoding="utf-8")
            malformed = self.invoke("resolve", "--catalog", str(catalog_path))
            self.assertNotEqual(malformed.returncode, 0)
            self.assertEqual(malformed.stdout, "")
            self.assertIn("valid UTF-8 JSON", malformed.stderr)

            catalog_path.write_bytes(b" " * (MAX_CATALOG_BYTES + 1))
            oversized = self.invoke("resolve", "--catalog", str(catalog_path))
        self.assertNotEqual(oversized.returncode, 0)
        self.assertEqual(oversized.stdout, "")
        self.assertIn("too large", oversized.stderr)

    def test_excessive_depth_catalogue_json_fails_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            catalog_path = Path(directory) / "catalog.json"
            catalog_path.write_text("[" * 1500 + "]" * 1500, encoding="utf-8")
            result = self.invoke("resolve", "--catalog", str(catalog_path))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("nesting is too deep", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
