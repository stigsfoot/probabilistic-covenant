"""
The syntax gate. This is Copa Chalkboard's REAL validation gate, imported from the
published package, not an imitation of it.

It validates the ScoutReport against the real Pydantic schema and runs the real
validate_scout_report(): a pure, deterministic function that checks the report
is internally consistent and plausible. It cannot see the image. That is why it
is green here, and why green is not the same as true.
"""
import json
from pathlib import Path

from copa_chalkboard.gate import validate_scout_report
from copa_chalkboard.schemas import ScoutReport

ROOT = Path(__file__).resolve().parents[1]


def _report() -> ScoutReport:
    data = json.loads((ROOT / "fixtures" / "scout_report.json").read_text(encoding="utf-8"))
    data.pop("_comment", None)
    return ScoutReport.model_validate(data)


def test_scout_report_matches_the_real_schema():
    _report()  # raises on any schema violation


def test_the_real_gate_passes_it_with_a_perfect_score():
    verdict = validate_scout_report(_report())
    assert verdict.passed, verdict.issues
    assert verdict.score == 100, verdict.issues
