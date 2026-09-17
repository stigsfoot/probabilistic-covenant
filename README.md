# probabilistic-covenant
 
A live demo for the keynote *Shipping Software When Half Your Stack Is Probabilistic*.
 
It proves Copa Chalkboard's validation gate is what I said it was, deterministic, and unit-tested. Run five times on one still photograph, it
scored the output 100/100 every time. Every one of those outputs narrated motion:
players "driving forward," defenders "chasing," a "midfield transition." The input
was a single frozen frame. The gate checked structure. Nothing checked truth.
 
That finding is recorded in the Copa repo at
`docs/codelab-verification-findings.md`, dated 7 June 2026.
 
## Why this couples to the real Copa Chalkboard repo
 
The demo imports `ScoutReport` and `validate_scout_report` from the published
`copa-chalkboard` package, pinned to a commit in `pyproject.toml`. It does not copy
them. The entire credibility of the green beat is that it is the actual shipped gate
running, not a lookalike, so the import is the proof. The dependency is safe on the
stage path: importing the gate and schema touches no network and needs no API key.
The Copa scripts that do call Gemini are only used offline, by `capture.py`.
 
You do not need to run Copa's own `make install`. `uv sync` here installs Copa for
you. (If you want to run Copa's own test suite as extra proof, its Makefile needs an
active venv first: `uv venv && source .venv/bin/activate && make install && make test`.)
 
## Setup
 
Requires [uv](https://docs.astral.sh/uv/) (`brew install uv`) and git.
 
    uv sync
 
One command: isolated `.venv`, pinned dependencies including Copa at a fixed commit,
and `uv.lock` written. Commit `uv.lock`. Nothing installs into your global Python.
 
## Get the image (once)
 
The verified runs used a CC-licensed Wikimedia Commons photo. Download it once:
 
    curl -L -o fixtures/frame.jpg \
      "https://commons.wikimedia.org/wiki/Special:FilePath/Sulley_Muntari_(Ghana_national_football_team).jpg"
 
Credit the photographer and licence from the file's Commons page wherever the image
appears on a slide.
 
## Run it end to end
 
    uv run python ship.py                    # 1. bare run on placeholders: proves the flow
    ollama pull gemma3:12b                   # 2. the judge; slow, start early (27b if you have the RAM)
    export GEMINI_API_KEY=...                # 3. Copa reads this (or a .env), offline phase only
    uv run python capture.py                 # 4. real pipeline, once: writes real scout_report.json
    # 5. edit fixtures/frame_truth.txt against the actual photo (the one human step)
    uv run python eval/faithfulness.py       # 6. real grounding scores: ALL FIVE must land under 0.85
    uv run python ship.py                    # 7. the real demo
 
If any note scores at or above the bar, the judge is too weak for the rubric and
the reveal will contradict the narrative. Escalate: `JUDGE_MODEL=gemma3:27b`, or
`JUDGE_PROVIDER=gemini JUDGE_MODEL=gemini-3.5-flash` (offline scoring only, needs
`GEMINI_API_KEY`). Commit the scores only once all five fail. The judge is
probabilistic too; this is you calibrating it against five notes you know are wrong.
 
## On stage
 
Call the environment's interpreter directly rather than going through `uv run`. It
skips uv's sync check, so nothing can reach for the network, and there is no
activation step to forget under pressure:
 
    .venv/bin/python ship.py            # macOS / Linux
    .venv\Scripts\python ship.py        # Windows
 
Run `uv sync` once on the presenting machine beforehand. The stage path needs no
API key, no Ollama, and no `frame.jpg`; it reads text fixtures only.
 
## What is real and what is a placeholder
 
- `fixtures/tactical_notes.json`: REAL. The five verbatim notes from the verified
  run, plus their gate scores. Do not edit them.
- `fixtures/scout_report.json`: PLACEHOLDER. Shaped to the verified stats so the
  flow runs today. Replace it with `capture.py` output before stage.
- `fixtures/gate_result.json`: PLACEHOLDER. The gate's verdict on the placeholder
  report. `capture.py` overwrites it.
- `fixtures/analyst_report.json`: PLACEHOLDER. Not on the stage path; `capture.py`
  overwrites it. Note how it reasons: pure coordinates, no jersey numbers, no kit
  colours. That is what the Analyst's voice actually looks like. Compare it to the
  five notes before you say anything about which step wrote them (step 1 below).
- `fixtures/frame_truth.txt`: DRAFT. The reference the grounding gate judges
  against. Verify every line against the photo. It has to be yours. Lines starting
  with `#` are notes to yourself: they are stripped before the judge sees the file
  and never reach the stage, so rewrite the body freely.
- `fixtures/judge_scores.json`: PLACEHOLDER. Regenerate with `eval/faithfulness.py`.
  Never show a fabricated number, and the demo enforces that rather than trusting
  you to remember it: while this file says `placeholder: true`, `ship.py` prints
  "not yet measured" wherever a faithfulness score would go. Real scores appear on
  stage only once the judge has produced them.
- `fixtures/frame.jpg`: NOT COMMITTED (gitignored). A CC-licensed Wikimedia photo,
  not ours to redistribute. Fetch it with the curl above; the stage path never
  reads it.
## Before you take this on stage (do not skip)
 
1. Settle which step wrote the five notes, or say nothing about it. `analyst.py`
   states the Analyst never sees the image, and the `ScoutReport` schema carries no
   jersey numbers or kit colours, yet the notes say "number 11," "white," and
   "blue." Two fresh `capture.py` runs both produced a grounded, positional Analyst
   summary with no motion and no kit detail, which points to the notes having come
   from a step with image access (the vision smoketest), not from
   `run_pipeline_local`'s Analyst. Do not assert either, on stage or here, until
   you have checked the June harness. The claim that survives without that check:
   five outputs narrated motion from a still, and the gate scored each one 100.
2. Run `capture.py` once and replace the placeholder report with the real one.
3. Author `frame_truth.txt` against the actual photo.
4. Run `faithfulness.py`. All five notes must land clearly under 0.85, not just the
   primary. Notes 2 to 5 narrate motion exactly as note 1 does ("drives forward,"
   "chasing," "transition"), so a judge that scores any of them high would put a
   high number on screen one beat after the red banner said motion is the failure.
   That is a weak judge, not a finding. Escalate the judge until all five fail,
   then commit the scores. Do not let the projector argue against you.
5. Check the confabulation reads to someone who has never watched football. "It
   describes a movie from a photograph" lands. A subtle tactical misread does not.
6. Terminal for the stage: 28pt or larger, light on dark, window maximised. Rehearse
   on the venue projector at its real resolution, using the on-stage command.
## The three fallback tiers (rehearse all three as equals)
 
1. `.venv/bin/python ship.py` live.
2. A screen recording of `uv run python ship.py --auto`, cued, one keystroke away.
   Drop to it silently. No apology.
3. The five banners plus the notes and the ground truth as static slides.
## Built on
 
None of the ideas in this demo are mine. This is what they stand on.
 
- **Copa Chalkboard** (Apache-2.0), the system under test: Match Scout, validation
  gate, Tactical Analyst, built on Gemini and Google ADK for a beginner Codelab.
- **pytest**, the runner. Evals are the new unit tests, so they run in the old runner.
- **DeepEval** (Confident AI, open source), the pytest-native LLM evaluation
  framework. The grounding gate uses its GEval metric with a rubric that names the
  motion failure explicitly. A contradiction-only faithfulness metric scored
  confabulated notes as faithful, which is why. A failing metric fails the build
  like any other test.
- **Ollama** and **Gemma** (Google, open weights), the local judge.
- **uv** (Astral), the environment and lockfile. The demo about the deterministic
  covenant is itself a pinned, reproducible artifact.
- **Semantic Versioning** (Tom Preston-Werner), the contract a version number
  promises and cannot keep once behaviour is probabilistic.
- **Google SRE**, for SLOs, SLIs, and error budgets, which the grounding gate
  borrows for quality instead of uptime.
- **Thoughtworks**, for fitness functions applied to AI and deterministic quality
  gates wrapped around agents.
- **OpenTelemetry GenAI semantic conventions**, the tracing standard the Watch layer
  builds on in a real deployment.
- Sculley et al. (2015), *Hidden Technical Debt in Machine Learning Systems*, which
  named this problem a decade before LLMs made it acute.
My own prior work this draws from:
 
- **compliance-at-scale-tpu**, the batch version of this same Gemma-as-judge
  evaluation, run on Cloud TPU.
- **rai-checklist-cli**, a behavioural spec in tool form. The Declare layer.