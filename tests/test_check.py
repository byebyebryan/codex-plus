"""Regression checks for metadata accepted by the public kit validator."""

from __future__ import annotations

import contextlib
import io
import runpy
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK = runpy.run_path(str(ROOT / "scripts/check"))
VALID = '''interface:
  display_name: "Worker Goal Loop"
  short_description: "Run a goal"
  default_prompt: "Use $worker-goal-loop to complete this goal."

policy:
  allow_implicit_invocation: false
'''


class MetadataTests(unittest.TestCase):
    def validate(self, text: str, skill: str = "worker-goal-loop") -> None:
        CHECK["check_metadata"](text, skill, "test metadata")

    def test_current_metadata(self) -> None:
        for skill_path in CHECK["SKILL_PATHS"]:
            path = ROOT / skill_path / "agents/openai.yaml"
            with self.subTest(path=skill_path):
                self.validate(path.read_text(), path.parent.parent.name)

    def test_canonical_and_compatibility_workflows_require_explicit_invocation(self) -> None:
        for skill in ('adaptive-task', 'adaptive-goal-loop', 'worker-task', 'worker-goal-loop'):
            valid = VALID.replace('worker-goal-loop', skill)
            self.validate(valid, skill)
            for invalid in (valid.replace('false', 'true'), valid.split('\npolicy:')[0]):
                with self.subTest(skill=skill), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit):
                        self.validate(invalid, skill)

    def test_comments_and_quoted_strings(self) -> None:
        self.validate(
            VALID.replace("interface:", "# metadata\ninterface: # UI")
            .replace('"Worker Goal Loop"', "'Worker''s # Goal Loop'")
            .replace('"Run a goal"', r'"Run a \"goal\"" # description')
            .replace("false", "false # explicit only")
        )

    def test_implicit_luna_goal_loop_remains_supported(self) -> None:
        self.validate(
            VALID.split("\npolicy:")[0].replace("worker-goal-loop", "luna-goal-loop"),
            "luna-goal-loop",
        )

    def test_decoded_prompt_is_checked(self) -> None:
        self.validate(VALID.replace("$worker", r"\u0024worker"))

    def test_malformed_metadata_is_rejected(self) -> None:
        cases = {
            "duplicate policy": VALID + "\npolicy:\n  allow_implicit_invocation: true\n",
            "duplicate boolean": VALID + "  allow_implicit_invocation: true\n",
            "multiple documents": VALID + "---\npolicy:\n  allow_implicit_invocation: true\n",
            "reference only in comment": VALID.replace(
                '"Use $worker-goal-loop to complete this goal."',
                '"Use the workflow." # $worker-goal-loop',
            ),
            "prompt in another block": VALID.replace(
                "  default_prompt:", "dependencies:\n  default_prompt:"
            ),
            "wrong policy type": VALID.replace("false", '"false"'),
            "implicit enabled": VALID.replace("false", "true"),
            "missing policy": VALID.split("\npolicy:")[0],
            "duplicate interface": VALID + VALID.split("\npolicy:")[0],
            "duplicate prompt": VALID.replace(
                "\npolicy:", '\n  default_prompt: "Use $worker-goal-loop."\npolicy:'
            ),
            "incorrect skill": VALID.replace("$worker-goal-loop", "$worker-task"),
            "skill name prefix": VALID.replace("$worker-goal-loop", "$worker-goal-loop-extra"),
            "escaped skill name suffix": VALID.replace(
                "$worker-goal-loop", r"$worker-goal-loop\u002dextra"
            ),
            "empty prompt": VALID.replace(
                '"Use $worker-goal-loop to complete this goal."', '" "'
            ),
            "unquoted prompt": VALID.replace(
                '"Use $worker-goal-loop to complete this goal."', "Use $worker-goal-loop"
            ),
            "multiline prompt": VALID.replace(
                '"Use $worker-goal-loop to complete this goal."', "|\n    Use $worker-goal-loop"
            ),
            "invalid escape": VALID.replace("complete this goal.", r"complete this \q goal."),
            "surrogate escape": VALID.replace("complete this goal.", r"complete this \ud800 goal."),
            "surrogate pair escapes": VALID.replace(
                "complete this goal.", r"complete this \ud83d\ude00 goal."
            ),
            "control in string": VALID.replace('"Worker Goal Loop"', "'Worker\x00 Goal Loop'"),
            "control in comment": VALID + "# invalid control \x00\n",
            "block comment without separation": VALID.replace("interface:", "interface:# comment"),
            "boolean comment without separation": VALID.replace("false", "false# comment"),
            "string comment without separation": VALID.replace('"Run a goal"', '"Run a goal"# comment'),
            "value without separation": VALID.replace("default_prompt: ", "default_prompt:"),
            "tab indentation": VALID.replace("  allow_implicit_invocation", "\tallow_implicit_invocation"),
        }
        for label, text in cases.items():
            with self.subTest(case=label), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    self.validate(text)
                self.assertEqual(error.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
