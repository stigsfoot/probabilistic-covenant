"""
Offline grounding judge. This is the reproducibility path. It is NOT run on stage.

Scores each of the pipeline's tactical notes for faithfulness against what the
pipeline could legitimately know: the ground truth of the still image, and the
ScoutReport the Analyst was actually handed. A claim like "drives forward" or
"number 11" is supported by neither. Uses DeepEval's FaithfulnessMetric with a
local Gemma judge served by Ollama, at temperature 0.

Usage:
  ollama pull gemma3:4b
  uv sync
  uv run python eval/faithfulness.py      # writes fixtures/judge_scores.json
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"


def main() -> None:
    # The claim is that the judge is local. Opt out of DeepEval's telemetry before
    # importing it so that claim is true of this script too, not just the stage path.
    os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")
    try:
        from deepeval.metrics import FaithfulnessMetric
        from deepeval.models import OllamaModel
        from deepeval.test_case import LLMTestCase
    except ImportError:
        sys.exit("deepeval is not installed: run `uv sync` (and make sure Ollama is running)")

    model_name = os.environ.get("JUDGE_MODEL", "gemma3:4b")
    judge = OllamaModel(
        model=model_name,
        base_url=os.environ.get("OLLAMA_URL", "http://localhost:11434"),
        temperature=0,
    )
    # Drop the '#' notes-to-self: they are instructions to the author, not facts
    # about the photograph, and they have no business in the retrieval context.
    truth = "\n".join(
        ln for ln in (FIX / "frame_truth.txt").read_text(encoding="utf-8").splitlines()
        if not ln.lstrip().startswith("#")
    ).strip()
    report = (FIX / "scout_report.json").read_text(encoding="utf-8")
    notes_doc = json.loads((FIX / "tactical_notes.json").read_text(encoding="utf-8"))

    metric = FaithfulnessMetric(model=judge, include_reason=True)
    scores = []
    for i, note in enumerate(notes_doc["notes"]):
        case = LLMTestCase(
            input="Write the tactical picture for this single still frame.",
            actual_output=note,
            retrieval_context=[truth, report],  # everything the pipeline could know
        )
        metric.measure(case)
        score = round(float(metric.score), 3)
        scores.append(score)
        print(f"note {i}: faithfulness={score}\n  {note}\n  reason: {metric.reason}\n")

    out = {
        # These are measured, so ship.py is cleared to put them on the projector.
        "placeholder": False,
        "metric": "deepeval.FaithfulnessMetric",
        "judge": f"{model_name} (local via Ollama, temperature=0)",
        "context": ["fixtures/frame_truth.txt", "fixtures/scout_report.json"],
        "primary": scores[notes_doc["primary"]],
        "all": scores,
    }
    (FIX / "judge_scores.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {FIX / 'judge_scores.json'}")


if __name__ == "__main__":
    main()
