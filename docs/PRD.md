This is an excellent strategic decision. You are right to insist on the granularity of sub-parameters. This level of detail is crucial for objective scoring, providing actionable feedback to writers, and demonstrating a sophisticated approach to the assignment.

To maximize precision and isolation, we will adopt the **"Granular Parallel"** architecture. This means every sub-parameter will have its own dedicated, isolated API call running in parallel. This completely eliminates the "Halo Effect" and provides the most objective scoring possible.

Here is the revised Product Requirements Document (PRD) and Task List, designed for rapid MVP development using this granular approach.

-----

# PRD: AI Content Scoring Agent (MVP - Granular Parallel Architecture)

## 1.0 Overview and Goals

### 1.1 Objective

Develop a locally hosted Python application that analyzes a content draft and scores it against 19 predefined sub-parameters using a Hybrid (Regex + LLM) architecture. The primary goal is maximum scoring objectivity and granularity.

### 1.2 Goals for MVP

  * Implement the 19 isolated scoring sub-parameters (defined in 3.3).
  * Utilize the **"Granular Parallel" Architecture**: Execute 18 asynchronous LLM API calls (plus 1 internal Regex check) simultaneously.
  * Implement the 1-4 scoring scale and the 3-Gate decision logic.
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
        D -- Parallel --> E1(Agent 1A: Positive);
        D -- Parallel --> E2(Agent 1B: Direct);
        D -- Parallel --> E3(...);
        D -- Parallel --> E18(Agent 5C: Shareability);
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
  * **Requirements:**
      * Parallel execution (e.g., `asyncio.gather`).
      * LLM `temperature=0`.
      * Enforced structured JSON output: `{"score": X, "feedback": "...", "flags": []}`.

### 3.3 The 19 Sub-Parameters (Isolated Checks)

This breakdown is optimized based on the monday.com style guide and the assignment requirements.

#### P1: Challenger Tone & Voice (30% | 4 LLM Calls)

  * **1A: Positive & Solution-Focused (7.5%):** Focus on success; avoids villainizing.
  * **1B: Direct with Personality (7.5%):** Straightforward but human; not robotic/corporate.
  * **1C: Trustworthy & Authentic (7.5%):** Credible but not "square."
  * **1D: Sharp Wit & Confidence (7.5%):** Witty (not funny); Active voice; Confident tone.

#### P2: Brand Hygiene & Compliance (25% | 1 Regex, 2 LLM Calls)

  * **2A: Mechanical Compliance (5%):** (Layer 1 Regex) `monday.com` lowercase, Oxford comma, %.
  * **2B: Contextual Terminology (10%):** (Layer 2 LLM) The "Tool/Hub/Task" paradox logic.
  * **2C: Persona & Lexicon (10%):** (Layer 2 LLM) Customers (not Users); Manager (not Boss); No forbidden words (Synergy, Uplevel).

#### P3: Structural Integrity & Clarity (20% | 5 LLM Calls)

  * **3A: BLUF (4%):** Bottom Line Up Front (uses conclusion-comparison Chain-of-Thought logic).
  * **3B: Scannability & Hierarchy (4%):** Descriptive headers, short paragraphs.
  * **3C: Conciseness (4%):** Short sentences, no fluff/modifiers.
  * **3D: Specificity (4%):** Concrete language, avoids vague terms.
  * **3E: Human Language/Jargon (4%):** Accessible language, no corporate-speak.

#### P4: Strategic Value & Depth (15% | 4 LLM Calls)

  * **4A: Audience Alignment (3.75%):** Relevance to Sales Leaders/CRM focus.
  * **4B: Actionability (3.75%):** Clear takeaway or next steps (CTA).
  * **4C: Evidence & Examples (3.75%):** Data-backed claims, concrete examples.
  * **4D: Originality & AI Detection (3.75%):** Fresh perspective; avoids AI patterns/cliches/robotic rhythm.

#### P5: Engagement & Discoverability (10% | 3 LLM Calls)

  * **5A: Headline & Hook (3.33%):** Compelling title; immediate attention capture in intro.
  * **5B: SEO Alignment (3.33%):** Strategic keyword usage; search intent match.
  * **5C: Shareability (3.34%):** Thought-provoking; worth sharing or bookmarking.

### 3.4 Scorer & Decision Engine

  * **Function:** Aggregates results using a two-level weighting system.
  * **Two-Level Aggregation:**
    1.  **Level 1:** Calculate the score for each Parameter (P1-P5) based on the weighted average of its Sub-Parameters.
    2.  **Level 2:** Calculate the final score based on the weighted average of the 5 Parameters.
  * **Logic (The 3-Gate System):**
    1.  Gate 1: Overall Score ≥ 3.2 (Configurable threshold).
    2.  Gate 2: Tone Score (P1) ≥ 3.0 (The Boredom Veto).
    3.  Gate 3: Zero Critical Violations in Brand Hygiene (P2) (The Brand Veto).

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
├── .env (API Keys)
└── requirements.txt
```

## 5.0 Output Schema (JSON)

The output JSON must include the nested sub-parameter details for full transparency.

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
  "gates_status": { /* ... */ },
  "parameters": {
    "P1_challenger_tone": {
      "parameter_score": 3.0,
      "weight": 0.30,
      "contribution": 0.90,
      "sub_parameters": {
        "1A_Positive": {
          "score": 4.0,
          "weight": 0.075,
          "feedback": "Excellent focus on solutions, no villainizing."
        },
        // ... 1B, 1C, 1D
      }
    },
    "P2_brand_hygiene": {
       // ... Includes 2A (Regex results), 2B (LLM), 2C (LLM)
    }
    // ... P3, P4, P5
  }
}
```

-----

# Development Task List (Rapid Build - Today)

This task list is prioritized for rapid execution, separating tasks between the User (Strategist/PM) and the Developer (Dev).

## Phase 0: Setup & Environment (0.5 Hours)

1.  [ ] **(Dev) Project Structure & Environment:** Create directory structure (PRD 4.1). Set up Python venv and dependencies (`httpx`, `python-dotenv`, LLM SDK).
2.  [ ] **(Dev/User) Configuration:** Set up `.env` (API keys) and `src/config.py`.

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

1.  [ ] **(Dev) End-to-End Test:** Verify the output JSON is complete, correctly nested, and the aggregation math is correct.
2.  [ ] **(User/Dev) Calibration Run (Poison/Golden Sets):** Run the system on the calibration data.
3.  [ ] **(User/Dev) Prompt Refinement Loop:** Analyze the feedback provided by *each* of the 18 sub-parameters. Refine prompts where feedback is weak or scores misalign with human intuition.
4.  [ ] **(User) Threshold Setting:** Determine the final threshold and update `src/config.py`.