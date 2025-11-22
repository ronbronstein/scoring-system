This is the finalized Product Requirements Document (PRD) and Task List for the AI Content Scoring Agent MVP. It incorporates the revised strategic weighting system designed to rigorously enforce the monday.com challenger brand voice and prioritize clarity (BLUF).

-----

# FINAL PRD: AI Content Scoring Agent (MVP - Granular Parallel Architecture)

## 1.0 Overview and Goals

### 1.1 Objective

Develop a locally hosted Python application that analyzes a content draft and scores it against 19 predefined sub-parameters using a Hybrid (Regex + LLM) architecture. The primary goal is maximum scoring objectivity and granularity, ensuring content meets the "Challenger" standard.

### 1.2 Goals for MVP

  * Implement the 19 isolated scoring sub-parameters (defined in 3.3).
  * Utilize the **"Granular Parallel" Architecture**: Execute 18 asynchronous LLM API calls (plus 1 internal Regex check) simultaneously to eliminate the "Halo Effect."
  * Implement the 1-4 scoring scale and the strategic weighting system.
  * Implement the 3-Gate decision logic (Overall Threshold, Boredom Veto, Brand Veto).
  * Output a detailed, nested JSON report stored locally.

## 2.0 System Architecture

The architecture is a Hybrid Two-Layer system. Layer 1 performs a synchronous Regex check. Layer 2 fans out to 18 parallel LLM calls.

```mermaid
graph TD
    A[Input Draft .txt] --> B(Orchestrator.py);
    B --> C{Layer 1: RegexChecker.py - P2A};
    C --> B;
    B --> D(Layer 2: Async Fan-Out - 18 Calls via LLMClient.py);

    subgraph Parallel Execution (18 Isolated LLM Agents)
        D -- Parallel --> E1(Agent 1A);
        D -- Parallel --> E2(Agent 1B);
        D -- Parallel --> E3(...);
        D -- Parallel --> E18(Agent 5C);
    end

    E1 & E2 & E3 & E18 --> F(LLM API Provider);
    F -.-> G(Fan-In/Aggregation);
    G --> B;
    B --> H(Scorer.py / Decision Engine);
    H --> I[Save JSON Report];
```

## 3.0 Core Components & Logic

### 3.1 Layer 1 (Regex Checker)

  * **Function:** Performs deterministic checks synchronously.
  * **Checks:** Sub-Parameter P2A (Mechanical Compliance).

### 3.2 Layer 2 (LLM Client & Agents)

  * **Function:** Executes 18 specialized prompts against the LLM API asynchronously.
  * **Model:** Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
  * **Requirements:**
      * **Parallel Execution:** Uses `asyncio.gather` to run all 18 agents concurrently.
      * **Temperature:** 0 (configurable for testing; deterministic evaluation).
      * **Max Tokens:** 1000 (configurable; generous limit for detailed feedback and violation lists).
      * **Prompt Structure:** Each agent receives:
          * Specialized **system prompt** defining evaluation criteria for that specific sub-parameter
          * **User message** containing the content draft to analyze
          * **Assistant prefill** starting with `{` to enforce JSON output format
      * **JSON Enforcement:** Combination of prompt engineering (strict instructions) + assistant prefill technique.
      * **Output Format:** `{"score": X, "feedback": "...", "flags": []}`
      * **Rate Limiting (Tier 1 Configuration):**
          * 50 requests per minute (RPM)
          * 30,000 input tokens per minute (ITPM)
          * 8,000 output tokens per minute (OTPM)
          * Conservative batching: Max 10 concurrent requests with 1.2s delay between batches
      * **Error Handling:**
          * Max 3 retry attempts per agent with exponential backoff (2s initial delay)
          * Failed agents are marked in the report with error details (does NOT fail entire analysis)
          * Resume/continue functionality: Retry only failed agents from a previous run without re-executing successful ones

### 3.3 The 19 Sub-Parameters & Strategic Weighting

The weighting system is designed to prioritize the "Challenger Voice" and "Time to Value" (BLUF, Clarity), while penalizing generic AI output and brand violations.

#### P1: Challenger Tone & Voice (30% Total | 4 LLM Calls)

*Rationale: The primary brand differentiator and the biggest risk when using AI. Heavily weighted towards the "spicy" and direct elements.*

  * **1B: Direct with Personality (10%):** Straightforward but human; not robotic/corporate. The core of the voice.
  * **1D: Sharp Wit & Confidence (10%):** Witty (not funny); Active voice; Confident tone. The "spicy" factor.
  * 1A: Positive & Solution-Focused (5%): Focus on success; avoids villainizing (Style guide mandate).
  * 1C: Trustworthy & Authentic (5%): Credible but not "square."

#### P3: Structural Integrity & Clarity (25% Total | 5 LLM Calls)

*Rationale: Increased significantly to emphasize BLUF and the "fluff-free" requirement mandated by the style guide and demanded by the audience (Sales Leaders).*

  * **3A: BLUF (10%):** Bottom Line Up Front (uses conclusion-comparison Chain-of-Thought logic). Now correctly weighted as a critical requirement.
  * **3C: Conciseness (5%):** Short sentences, no fluff/modifiers. The "Fluff-free" mandate; combats AI verbosity.
  * **3E: Human Language/Jargon (5%):** Accessible language, no corporate-speak (Style guide mandate).
  * 3B: Scannability & Hierarchy (3%): Descriptive headers, short paragraphs.
  * 3D: Specificity (2%): Concrete language, avoids vague terms.

#### P2: Brand Hygiene & Compliance (20% Total | 1 Regex, 2 LLM Calls)

*Rationale: Reduced numeric weight, but retains critical Veto Power (Gate 3). Prioritizes complex contextual checks.*

  * **2B: Contextual Terminology (10%):** (Layer 2 LLM) The "Tool/Hub/Task" paradox logic. High weight because it requires nuanced understanding and is non-negotiable.
  * 2A: Mechanical Compliance (5%): (Layer 1 Regex) `monday.com` lowercase, Oxford comma, %.
  * 2C: Persona & Lexicon (5%): (Layer 2 LLM) Customers (not Users); Manager (not Boss); No forbidden words (Synergy, Uplevel).

#### P4: Strategic Value & Depth (15% Total | 4 LLM Calls)

*Rationale: Essential for substance. Prioritizes actionability and combating generic AI output.*

  * **4B: Actionability (5%):** Clear takeaway or next steps (CTA).
  * **4D: Originality & AI Detection (5%):** Fresh perspective; avoids AI patterns/cliches/robotic rhythm.
  * 4A: Audience Alignment (3%): Relevance to Sales Leaders/CRM focus.
  * 4C: Evidence & Examples (2%): Data-backed claims, concrete examples.

#### P5: Engagement & Discoverability (10% Total | 3 LLM Calls)

*Rationale: Important for reach, but secondary to core quality. Prioritizes initial attention capture.*

  * **5A: Headline & Hook (5%):** Compelling title; immediate attention capture in intro.
  * 5B: SEO Alignment (3%): Strategic keyword usage; search intent match.
  * 5C: Shareability (2%): Thought-provoking; worth sharing or bookmarking.

### 3.4 Scorer & Decision Engine

  * **Function:** Aggregates results using a two-level weighting system.
  * **Two-Level Aggregation:**
    1.  **Level 1:** Calculate the score for each Parameter (P1-P5) based on the weighted average of its Sub-Parameters (using the weights defined in 3.3).
    2.  **Level 2:** Calculate the final score based on the weighted average of the 5 Parameters (P1: 30%, P3: 25%, P2: 20%, P4: 15%, P5: 10%).
  * **Logic (The 3-Gate System):** Determines "Publish-Ready" status (True/False).
    1.  **Gate 1:** Overall Score ≥ [TBD after calibration] (Initial hypothesis: 3.2; configurable threshold).
    2.  **Gate 2:** Tone Score (P1) ≥ [TBD after calibration] (Initial hypothesis: 3.0; The Boredom Veto).
    3.  **Gate 3:** Zero Critical Violations in Brand Hygiene (P2) (The Brand Veto; non-negotiable).
  * **Note:** Thresholds for Gates 1 and 2 will be determined through calibration analysis of golden and poison datasets. The hypothesis values (3.2 and 3.0) are starting points subject to data-driven adjustment.

## 4.0 Data Flow and Storage

### 4.1 Local Directory Structure

The `/prompts` directory requires 18 distinct files.

```
/AI_Scoring_Agent_MVP
│
├── /data
│   ├── /input
│   ├── /reports
│   └── /calibration (/golden_set, /poison_set)
│
├── /prompts
│   ├── 1A_Positive.txt
│   ├── 1B_Direct.txt
│   // ... (18 files total, excluding 2A Regex)
│
├── /src
│   ├── main.py (CLI entry point)
│   ├── orchestrator.py
│   ├── config.py (Weights for all 19 sub-parameters, Thresholds)
│   ├── regex_checker.py
│   ├── llm_client.py (Handles 18 Async API calls)
│   └── scorer.py (Two-level aggregation and 3-Gate Logic)
│
├── .env (API Keys - DO NOT COMMIT)
└── requirements.txt
```

## 5.0 Output Schema (JSON)

The output JSON must include the nested sub-parameter details and weights for full transparency.

```json
{
  "metadata": {
    "content_id": "draft_01",
    "timestamp": "2025-11-22T14:30:00Z"
  },
  "results": {
    "overall_score": 3.15,
    "publish_ready": false
  },
  "gates_status": {
    "gate_1_overall_threshold_met": false,
    "gate_2_tone_veto_passed": true,
    "gate_3_brand_veto_passed": true
  },
  "parameters": {
    "P1_challenger_tone": {
      "parameter_score": 3.0,
      "weight": 0.30,
      "contribution": 0.90,
      "sub_parameters": {
        "1B_Direct": {
          "score": 3.0,
          "weight": 0.10,
          "feedback": "Direct, but lacks personality in the middle sections."
        },
        "1D_Sharp_Wit": {
          "score": 3.0,
          "weight": 0.10,
          "feedback": "Confident, but could use sharper wit."
        }
        // ... 1A (5%), 1C (5%)
      }
    },
    // ... P3 (25%), P2 (20%), P4 (15%), P5 (10%)
  }
}
```

-----

# Development Task List (Rapid Build)

This task list is prioritized for rapid execution, separating tasks between the User (Strategist/PM) and the Developer (Dev).

## Phase 0: Setup & Environment (0.5 Hours)

1.  [ ] **(Dev) Project Structure & Environment:** Create directory structure (PRD 4.1). Set up Python venv and dependencies (`httpx`, `python-dotenv`, LLM SDK).
2.  [ ] **(Dev/User) Configuration:** Set up `.env` (API keys) and `src/config.py` (Input the finalized weights from PRD 3.3).

## Phase 1: Data Preparation (1.5 Hours) - Parallelizable

1.  [ ] **(User) Golden Set Curation:** Scrape 5-10 high-quality monday CRM posts. Save to `/data/calibration/golden_set`.
2.  [ ] **(User) Poison Set Generation:** Generate 5-10 generic AI posts. Save to `/data/calibration/poison_set`.
3.  [ ] **(User) Assignment Set:** Scrape the 3 required blog posts (Part 2). Save to `/data/input`.

## Phase 2: Prompt Engineering (4.0 Hours) - Parallelizable

  * *CRITICAL PATH: This phase is extensive due to the 18 isolated prompts.*

<!-- end list -->

1.  [ ] **(User/Dev) Write the 18 LLM Prompts:** Draft all prompts and save them in the `/prompts` directory.
      * [ ] P1 (Tone) - 4 Prompts
      * [ ] P2 (Brand) - 2 Prompts (Ensure 2B includes the "Tool Paradox" logic).
      * [ ] P3 (Structure) - 5 Prompts (Ensure 3A includes the "BLUF" Chain-of-Thought logic).
      * [ ] P4 (Value) - 4 Prompts
      * [ ] P5 (Engagement) - 3 Prompts
      * *Ensure all enforce the 1-4 scale and the required JSON output structure.*

## Phase 3: Core Development (4.0 Hours)

1.  [ ] **(Dev) Layer 1:** Implement `src/regex_checker.py` (P2A).
2.  [ ] **(Dev) LLM Client:** Implement `src/llm_client.py`.
      * Must handle the 18 asynchronous API calls efficiently (manage concurrency/rate limits if necessary).
      * Include robust JSON parsing and error handling.
3.  [ ] **(Dev) Scorer:** Implement `src/scorer.py`.
      * Must handle the Two-Level Aggregation (PRD 3.4).
      * Implement the 3-Gate logic.
4.  [ ] **(Dev) Orchestrator & Main:** Implement `src/orchestrator.py` and `src/main.py` (CLI). Manage the flow and the comprehensive JSON report generation (PRD 5.0).

## Phase 4: Testing & Calibration (2.0 Hours)

1.  [ ] **(Dev) End-to-End Test:** Verify the output JSON is complete, correctly nested, and the aggregation math is correct based on the new weights.
2.  [ ] **(User/Dev) Calibration Run (Poison/Golden Sets):** Run the system on the calibration data.
3.  [ ] **(User/Dev) Prompt Refinement Loop:** Analyze the feedback provided by *each* of the 18 sub-parameters. Refine prompts where feedback is weak or scores misalign with human intuition.
4.  [ ] **(User) Threshold Setting:** Determine the final threshold and update `src/config.py`.