"""
Run the REAL Copa Chalkboard pipeline once and save its outputs as fixtures.

Offline phase only: needs GEMINI_API_KEY and network. It is NOT run on stage.
Uses copa_chalkboard.pipeline.run_pipeline_local exactly as the CLI does, so the
saved ScoutReport, GateResult, and AnalystReport are the real thing.

Usage:
  export GEMINI_API_KEY=...        # or a .env file, per Copa's config.py
  uv run python capture.py          # reads fixtures/frame.jpg
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIX = ROOT / "fixtures"


def main() -> None:
    img = FIX / "frame.jpg"
    if not img.exists():
        sys.exit("fixtures/frame.jpg is missing. See README: 'Get the image'.")
    try:
        from copa_chalkboard.pipeline import run_pipeline_local
    except ImportError:
        sys.exit("copa_chalkboard is not installed: run `uv sync`")

    result = run_pipeline_local(img.read_bytes(), "image/jpeg")

    (FIX / "scout_report.json").write_text(result.report.model_dump_json(indent=2) + "\n", encoding="utf-8")
    (FIX / "gate_result.json").write_text(result.gate.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print("=== ScoutReport ===\n" + result.report.model_dump_json(indent=2))
    print("\n=== Gate ===\n" + result.gate.model_dump_json(indent=2))
    if result.analysis is None:
        print("\nGate did not pass; the Analyst was not invoked.")
        return
    (FIX / "analyst_report.json").write_text(result.analysis.model_dump_json(indent=2) + "\n", encoding="utf-8")
    print("\n=== AnalystReport ===\n" + result.analysis.model_dump_json(indent=2))
    print(
        "\nSaved scout_report.json, gate_result.json, analyst_report.json.\n"
        "If this summary also narrates motion, add it to fixtures/tactical_notes.json as a sixth note."
    )


if __name__ == "__main__":
    main()
