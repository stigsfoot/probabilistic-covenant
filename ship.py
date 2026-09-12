#!/usr/bin/env python3
r"""
The one command you run on stage. Cross-platform: Windows, macOS, Linux.

  uv run python ship.py            advance each beat with Enter
  uv run python ship.py --auto     auto-run, for making the tier-2 screen recording

On stage, call the environment's interpreter directly so nothing can reach for the
network and there is no activation step to forget:
  .venv/bin/python ship.py         macOS / Linux
  .venv\Scripts\python ship.py     Windows

Five beats: shipped -> the gate -> syntax gate (green) -> grounding gate (red) -> reveal.
Everything local. No network. Deterministic.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUTO = "--auto" in sys.argv or os.environ.get("NOPAUSE") == "1"

if os.name == "nt":
    os.system("")  # enable ANSI colour in Windows consoles
B, R, G, Y, D, N = "\033[1m", "\033[1;31m", "\033[1;32m", "\033[1;33m", "\033[2m", "\033[0m"


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def body(rel: str) -> list[str]:
    """Content lines of a fixture, minus '#' notes-to-self and any leading blanks.

    Never slice by line number here: the README tells you to rewrite
    frame_truth.txt against the real photo, and a fixed offset would silently
    eat the first lines of your ground truth in the reveal beat.
    """
    lines = [ln for ln in read(rel).splitlines() if not ln.lstrip().startswith("#")]
    while lines and not lines[0].strip():
        lines.pop(0)
    return lines


def judge_scores() -> tuple[dict, bool]:
    """The judge's output, and whether it is still placeholder.

    Never show a fabricated number. Until eval/faithfulness.py has actually run,
    the file carries placeholder=true and every caller here prints
    'not yet measured' in place of a score.
    """
    doc = json.loads(read("fixtures/judge_scores.json"))
    return doc, bool(doc.get("placeholder", False))


def pause() -> None:
    if AUTO:
        time.sleep(1.5)
    else:
        input(f"{D}  >  Enter{N}")  # dim cue so a pause never reads as a hang


def banner(colour: str, *lines: str) -> None:
    print(f"\n{colour}")
    print("  " + "=" * 60)
    for ln in lines:
        print(f"  {ln}")
    print("  " + "=" * 60)
    print(N)


def pytest(target: str, quiet_tb: bool) -> bool:
    cmd = [sys.executable, "-m", "pytest", target, "-q", "--no-header", "-p", "no:cacheprovider"]
    if quiet_tb:
        cmd.append("--tb=no")
    # The stage path needs no third-party pytest plugins. Blocking autoload keeps
    # DeepEval's "Running teardown with pytest sessionfinish..." (and anything
    # else installed in the env) off the screen between the result and the banner.
    env = {**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    return subprocess.run(cmd, cwd=ROOT, env=env).returncode == 0


def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")

    # 1 ---------------------------------------------------------------- shipped
    banner(B, "COPA CHALKBOARD   v0.1.0   shipped",
           "Two agents. A validation gate between them. An offline test suite.")
    pause()

    # 2 --------------------------------------------------------------- the gate
    banner(B, "THE GATE   validate_scout_report()")
    for ln in (
        "Starts at 100.",
        "  -40  if the player count is implausible        (critical: forces a fail)",
        "  -25  if the count does not match the positions listed",
        "  -30  if it claims players but lists no positions",
        "Passes at 75 or above, with no critical finding.",
        "",
        "A pure function of the report. Deterministic. Unit-tested.",
        "It never sees the image.",
    ):
        print(f"  {ln}")
    pause()

    # 3 ------------------------------------------------------- syntax gate: green
    banner(B, "SYNTAX GATE   (the check the covenant taught us to write)")
    if pytest("tests/test_syntax_gate.py", quiet_tb=False):
        try:
            from copa_chalkboard.gate import validate_scout_report
            from copa_chalkboard.schemas import ScoutReport
            data = json.loads(read("fixtures/scout_report.json"))
            data.pop("_comment", None)
            v = validate_scout_report(ScoutReport.model_validate(data))
            print(f"\n  GateResult  passed={v.passed}  score={v.score}  issues={v.issues or 'none'}")
        except ImportError:
            print(f"{D}  (copa_chalkboard not importable here; run `uv sync`){N}")
        banner(G, "SYNTAX GATE PASSED   score 100 / 100", "Structure is perfect. Ship it?")
    else:
        banner(R, "SYNTAX GATE FAILED   (unexpected: check the scaffold)")
        sys.exit(1)
    pause()

    # 4 ------------------------------------------------------ grounding gate: red
    banner(B, "GROUNDING GATE   (same runner, different question)")
    if pytest("tests/test_grounding_gate.py", quiet_tb=True):
        banner(G, "GROUNDING GATE PASSED")
    else:
        scores, unmeasured = judge_scores()
        bar = read("eval/threshold.txt").strip()
        shown = "not yet measured" if unmeasured else scores["primary"]
        lines = [f"faithfulness   {shown}      (bar {bar})",
                 "The note narrates motion. The input is a photograph."]
        if unmeasured:
            lines.append("")
            lines.append("judge_scores.json is a placeholder: run eval/faithfulness.py (step 6).")
        banner(R, "GROUNDING GATE FAILED", *lines)
    pause()

    # 5 ----------------------------------------------------------------- reveal
    banner(Y, "WHAT THE GATE COULD NOT SEE")
    print(f"{G}  GROUND TRUTH   what is actually in the still{N}")
    for ln in body("fixtures/frame_truth.txt"):
        print("    " + ln)
    print()
    notes = json.loads(read("fixtures/tactical_notes.json"))
    doc, unmeasured = judge_scores()
    scores = [] if unmeasured else doc.get("all", [])
    print(f"{R}  THE PIPELINE'S TACTICAL NOTES   one image, five runs, gate score 100 every time{N}")
    for i, note in enumerate(notes["notes"]):
        tag = f"  faithfulness {scores[i]}" if i < len(scores) else ""
        print(f"    {i + 1}. {note}{D}{tag}{N}")
    print()
    if unmeasured:
        print(f"{D}  (faithfulness per note withheld: judge not yet run -- eval/faithfulness.py){N}")
    print(f"{D}  Five runs. Five notes narrating a movie. Five perfect scores from the gate.{N}\n")


if __name__ == "__main__":
    main()
