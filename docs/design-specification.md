# AI Content Scoring Agent: Design Specification

## 1.0 Introduction & Philosophy

### 1.1 The Challenge

When scaling content production using AI, the primary risk is mediocrity. AI models naturally regress to the mean, producing generic, "corporate-sounding" output. For monday.com, a challenger brand in the CRM market, "safe" or "boring" content is a failure state. The brand requires content that is confident, spicy, witty, and fluff-free.

### 1.2 The Solution

We propose a hybrid, Discriminative AI System designed to act as an automated quality control layer. This system utilizes a **"Boredom Penalty,"** actively rejecting content that fails to meet monday.com's high standards for voice, value, and brand alignment.

### 1.3 Core Principles

*   **Context Awareness:** Utilizing modern LLMs to understand nuanced brand guidelines (e.g., contextual usage of forbidden words) rather than rigid keyword blocking.
*   **Objectivity by Isolation:** Isolating evaluation criteria to prevent the "Halo Effect" (where one positive aspect, like good grammar, inflates scores for others, like strategy).
*   **Determinism:** Employing a "Forced Choice" scoring scale and `temperature=0` to ensure consistent, reliable outputs.
*   **Data-Driven Calibration:** Defining thresholds based on analysis of existing high-performing content, rather than arbitrary metrics.

## 2.0 Scoring Logic

### 2.1 Key Parameters (5 Dimensions)

The agent evaluates content across 5 weighted parameters, derived directly from the monday.com style guide, the CRM product narrative, and the assignment criteria (Clarity, Readability, Engagement, etc.).

| Parameter | Weight | What It Measures |
| :--- | :--- | :--- |
| **1. Challenger Tone & Voice** | 30% | The "spiciness" factor. Confidence, sharp wit (not humor), positivity, and active voice. Penalizes robotic, jargon-heavy, or generic corporate tone. |
| **2. Brand Hygiene & Compliance** | 25% | Strict adherence to non-negotiable style guide rules: naming conventions (e.g., lowercase `monday.com`), contextual forbidden terminology, and formatting. |
| **3. Structural Integrity & Clarity** | 20% | Information architecture. Presence of BLUF (Bottom Line Up Front), scannability (headers, short paragraphs), and readability. |
| **4. Strategic Value & Depth** | 15% | Relevance to the target audience (Sales Leaders). Specificity, actionability, originality, and alignment with the CRM value proposition. Penalizes fluff. |
| **5. Engagement & Discoverability** | 10% | The effectiveness of the hook, headline appeal, and SEO alignment. |

### 2.2 Weighting System Rationale

The weighting prioritizes the elements most critical to monday.com's competitive advantage and the hardest to maintain at scale when using AI:

*   **Tone (30%)** is weighted highest because the "challenger voice" is the primary differentiator in the CRM market.
*   **Brand Hygiene (25%)** ensures consistency. This parameter also possesses **Veto Power**; critical violations will block publication regardless of the overall score.
*   **Structure (20%)** is critical because the target audience demands immediate clarity (BLUF).
*   **Value (15%) and Engagement (10%)**, while important, are secondary to the voice and presentation of the content.

### 2.3 Scoring Scale (1-4 Forced Choice)

We utilize a 1-4 ordinal scale instead of a traditional 1-10 scale.

*   **Rationale:** LLMs perform better at classification than fine-tuned regression. A 1-10 scale introduces noise and encourages "regression to the mean" (scoring everything a 7). A 1-4 scale forces the model to make a clear decision, yielding more stable and reliable outputs.

| Score | Label | Description |
| :--- | :--- | :--- |
| **1** | Critical Fail | Active brand violation (e.g., misuse of "Tool"), negative/villainizing tone, or factually incorrect. |
| **2** | Generic (Mediocre) | Grammatically correct but boring. Lacks the "Challenger" voice. Sounds like generic AI output ("Gray Goo"). |
| **3** | Publishable Standard | Clear, helpful, follows Style Guide, professional and human. Meets the standard. |
| **4** | Challenger Status | Exceptional. Unique insight, witty, distinct voice, zero fluff. Exceeds expectations. |

## 3.0 Implementation & Architecture

### 3.1 Technology Stack (Conceptual)

*   **Orchestration:** Python (for workflow logic, Regex checks, and API coordination).
*   **Scoring LLM:** High-capability model like Claude 3.5 Sonnet or GPT-4o (via API, set to `temperature=0` for determinism).
*   **Interface (Conceptual):** A visualization dashboard (e.g., Streamlit) providing transparency into scores, flagged violations, and actionable feedback.

### 3.2 System Architecture: Hybrid Parallel

The system uses a two-layer hybrid approach with a parallel execution model for efficiency and accuracy.

#### Layer 1: The Hard Gate (Deterministic)

*   **Technology:** Python Regex.
*   **Function:** Instant, low-cost checks for binary mechanical errors (e.g., ensuring `monday.com` is always lowercase; checking for `%` vs "percent").

#### Layer 2: The Soft Gate (Probabilistic)

*   **Technology:** LLM Agents (Specialized Prompts).
*   **Architecture:** Asynchronous Fan-Out. The content is sent to 5 specialized agents simultaneously.
*   **Rationale:** This parallel approach reduces latency. Crucially, it isolates the evaluation of each parameter, preventing the "Halo Effect" and ensuring objective scoring.

### 3.3 Workflow Logic

1.  **Ingestion & Pre-processing:** Content draft is loaded and tagged by logical blocks (Headline, Intro, Body).
2.  **Layer 1 Execution:** Regex checks are performed.
3.  **Layer 2 Execution (Fan-Out):** The text is sent asynchronously to the 5 LLM Agents. (Note: Most agents require the full text for context, except the Engagement agent which focuses on the Hook/Intro).
4.  **Fan-In & Aggregation:** The orchestration script collects the 5 scores.
5.  **Calculation:** The weighted average score is computed.
6.  **Decision Engine:** The 3-Gate Threshold (see 5.0) is applied.
7.  **Output:** A detailed JSON report is generated.

### 3.4 Key Agent Logic (Conceptual Prompts)

We employ specific prompt engineering strategies to handle complex, nuanced requirements.

#### A. The "Tool" Paradox (Brand Hygiene Agent)

To handle rules where simple keyword blocking fails (e.g., "tool" is forbidden when describing monday.com, but allowed generally):

> **Prompt Logic Snippet:** "Identify every instance of the words 'Tool', 'Hub', or 'Task'. Analyze the subject and context of the sentence. If the word is used as a noun to describe monday.com products or the Work OS, flag it as a Critical Violation. If it describes a competitor, integration partner, or a general concept, ignore it."

#### B. BLUF Validation (Structure Agent)

To accurately validate the Bottom Line Up Front, the agent must know the actual "Bottom Line" of the article.

> **Prompt Logic Snippet (Chain-of-Thought):**
> "1. Read the Body and Conclusion first. Summarize the single most valuable actionable insight of the article.
> 2. Now read the Introduction (First 2 paragraphs).
> 3. BLUF Test: Is the insight summarized in Step 1 explicitly stated in the Introduction? If yes, score high. If the intro is vague or uses 'clickbait' teasing, score low."

## 4.0 Training & Calibration

We must calibrate the system against a "Ground Truth" dataset to ensure accuracy and define a meaningful, data-driven threshold.

### 4.1 Calibration Methodology

1.  **Establish Ground Truth:**
    *   **The "Golden Set":** Human experts select 10 existing, high-performing monday CRM blog posts (rated 3.5-4.0).
    *   **The "Poison Set":** Generate 10 intentionally generic, low-quality AI posts (rated 1.5-2.5).
2.  **Initial Testing & Refinement:** Run the AI Scoring Agent on both sets. Compare agent scores to human scores and refine the prompts iteratively until alignment is achieved (e.g., >85% agreement).
3.  **Threshold Setting:** The "Publish-Ready" threshold is mathematically determined based on the average score of the Golden Set, ensuring a clear distinction from the Poison Set average.
4.  **Continuous Improvement:** Post-launch, correlate agent scores with real-world content performance (traffic, conversion) and adjust weights/thresholds quarterly.

## 5.0 The "Publish-Ready" Definition

We define "Publish-Ready" using a **3-Gate System**. Content must pass all three gates. This system is intentionally aggressive to ensure exceptional quality.

1.  ✅ **Overall Weighted Score ≥ 3.2** (Initial hypothesis; finalized during Calibration).
2.  ✅ **Challenger Tone (P1) Score ≥ 3.0** (The "Boredom Veto"—if the tone is generic (Score 2), the piece fails, regardless of other scores).
3.  ✅ **Zero Critical Violations in Brand Hygiene (P2)** (The Brand Veto—mechanical brand consistency is non-negotiable).