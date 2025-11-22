# CLAUDE.md
AI Content Scoring Agent for monday.com challenger brand voice evaluation.

## Important
- ALL instructions within this document MUST BE FOLLOWED - these are not optional
- ASK FOR CLARIFICATION if uncertain about any instruction or architectural decision
- DO NOT edit more code than necessary - make targeted, minimal changes
- DO NOT modify weights or thresholds without explicit approval - they are strategically calibrated
- DO NOT waste tokens - be succinct and precise
- SOURCES OF TRUTH: docs/design-specification.md, docs/PRD.md, docs/claude-api-docs

## Tech Stack
- Python 3.8+
- Claude API (Sonnet 4.5: `claude-sonnet-4-5-20250929`)
- Async architecture: `asyncio` for parallel LLM agent execution
- Dependencies: `anthropic`, `python-dotenv`, `httpx`
- Environment: Virtual environment (`venv/`)

## Bash Commands
- `source venv/bin/activate` - Activate virtual environment (run first)
- `python src/main.py analyze data/input/<file.txt>` - Analyze single content file
- `python src/main.py analyze data/input/<file.txt> --json` - Show full JSON report
- `python src/main.py batch data/calibration/golden_set` - Batch analyze directory
- `python src/main.py test-layer1 data/input/<file.txt>` - Test regex checks only (no LLM)
- `python src/main.py continue <file.txt> <report.json>` - Retry only failed agents
- `cp .env.template .env` - Set up environment file (then add API key)

## Project Structure
- `src/` - Core application code (6 modules)
  - `main.py` - CLI entry point
  - `orchestrator.py` - Pipeline coordination
  - `config.py` - Weights, thresholds, API configuration
  - `regex_checker.py` - Layer 1: Deterministic brand compliance
  - `llm_client.py` - Layer 2: 18 async LLM agents
  - `scorer.py` - Two-level aggregation & 3-Gate decision logic
- `prompts/` - 18 prompt templates (one per LLM agent)
- `data/input/` - Content drafts to analyze
- `data/reports/` - Generated JSON reports
- `data/calibration/` - Golden/poison sets for threshold calibration
- `docs/` - PRD, design spec, layer-1 strategy, API docs

## Architecture: Granular Parallel System
- **Layer 1 (Regex)**: Synchronous deterministic checks (2A: Mechanical Compliance)
- **Layer 2 (LLM)**: 18 parallel async agents (isolated sub-parameter evaluation)
- **Isolation Principle**: Each agent evaluates ONLY one sub-parameter to eliminate "Halo Effect"
- **Rate Limiting**: Tier 1 (50 RPM, 30K ITPM, 8K OTPM) - batched at 10 concurrent requests, 1.2s delay
- **Error Handling**: 3 retries with exponential backoff; failed agents marked in report (does not fail entire analysis)

## The 19 Sub-Parameters (Strategic Weighting)
1. **P1: Challenger Tone (30%)** - 1A, 1B*, 1C, 1D* (*=highest weight: 10% each)
2. **P3: Structural Clarity (25%)** - 3A*, 3B, 3C*, 3D, 3E* (*=BLUF, Conciseness, Human Language)
3. **P2: Brand Hygiene (20%)** - 2A (Regex), 2B*, 2C (*=Tool Paradox logic)
4. **P4: Strategic Value (15%)** - 4A, 4B*, 4C, 4D* (*=Actionability, AI Detection)
5. **P5: Engagement (10%)** - 5A*, 5B, 5C (*=Headline & Hook)

## 3-Gate Decision System
Content is "Publish-Ready" ONLY if ALL three gates pass:
1. **Gate 1**: Overall Score ≥ Threshold (TBD after calibration; hypothesis: 3.2)
2. **Gate 2**: Tone Score (P1) ≥ Minimum (Boredom Veto; hypothesis: 3.0)
3. **Gate 3**: Zero Critical Violations (Brand Veto; non-negotiable)

## Code Style & Conventions
- Use async/await for LLM client operations
- Follow existing module structure (6 files in src/)
- Type hints preferred but not required
- Error handling: Mark failures in report, do not fail entire pipeline
- JSON output format is strictly defined (see PRD section 5.0)
- Temperature: 0 for deterministic evaluation (configurable in config.py)
- Max tokens: 1000 (generous for detailed feedback)

## Critical Constraints
- DO NOT modify the 19 sub-parameter weights without understanding the strategic rationale (see docs/PRD.md section 3.3)
- DO NOT change the scoring scale (1-4 forced choice is intentional)
- DO NOT skip the two-level aggregation logic (sub-params → params → overall)
- DO NOT call monday.com a "tool" or "hub" - this is a critical brand violation
- DO NOT add new dependencies without approval
- DO NOT modify .env file (use .env.template as reference)

## Key Files & Their Purposes
- `config.py:38-82` - Sub-parameter weights (strategically calibrated; see PRD 3.3)
- `regex_checker.py` - Enforces lowercase "monday.com", Oxford comma, %, forbidden terms
- `llm_client.py` - Handles 18 async API calls with rate limiting and retry logic
- `scorer.py` - Implements two-level weighted aggregation and 3-Gate decision
- `orchestrator.py` - Coordinates Layer 1 → Layer 2 → Scoring pipeline
- `prompts/2B_*.txt` - "Tool Paradox" logic (contextual terminology)
- `prompts/3A_*.txt` - BLUF validation (Bottom Line Up Front with Chain-of-Thought)

## Workflow
- Virtual environment MUST be activated before running any commands
- API key stored in `.env` (never commit this file)
- Prompt templates contain TODO sections that need completion before first use
- Reports saved as JSON in `data/reports/` with timestamp
- Use `continue` command to retry failed agents without re-running successful ones
- Calibration workflow: Run golden set → Run poison set → Analyze distributions → Set thresholds

## Testing Strategy
1. **Phase 1**: Test Layer 1 (regex) in isolation with `test-layer1` command
2. **Phase 2**: Test full pipeline on single file
3. **Phase 3**: Run calibration on golden/poison sets
4. **Phase 4**: Refine prompts based on feedback quality
5. **Phase 5**: Set final thresholds in config.py

## Common Pitfalls
- Forgetting to activate virtual environment (leads to import errors)
- Empty/incomplete prompt templates (leads to poor LLM feedback)
- Missing API key in `.env` (leads to authentication errors)
- Modifying weights without understanding two-level aggregation math
- Expecting all 18 agents to succeed on first run (use `continue` for retries)

## Documentation References
- Full product requirements: `docs/PRD.md`
- Architecture & philosophy: `docs/design-specification.md`
- Layer 1 regex rules: `docs/layer-1-strategy.md`
- Claude API specifics: `docs/claude-docs/`
