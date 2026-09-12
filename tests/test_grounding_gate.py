"""
The grounding gate. Same runner as the syntax gate. Different question:
does the pipeline's tactical note only claim things the pipeline could know?

Stage path: reads fixtures/judge_scores.json (real scores produced offline by
eval/faithfulness.py with DeepEval and a local Gemma judge) and asserts against
eval/threshold.txt. Deterministic and dependency-free on stage.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_the_tactical_note_is_grounded_in_the_still():
    scores = json.loads((ROOT / "fixtures" / "judge_scores.json").read_text(encoding="utf-8"))
    bar = float((ROOT / "eval" / "threshold.txt").read_text().strip())
    score = scores["primary"]
    assert score >= bar, (
        f"\n\n  GROUNDING GATE FAILED\n"
        f"  faithfulness {score:.2f} is below the bar {bar:.2f}\n"
        f"  the note narrates motion; the input is a single still frame\n"
    )
