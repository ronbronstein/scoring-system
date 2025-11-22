# Sub-Parameters Reference: Evaluation Criteria (v6.0 - Nuanced)

**Context:** monday CRM content targeting **Sales & Revenue Leaders**.
**Scoring Scale:** 1-4 Forced Choice (1=Critical Fail, 2=Generic/AI, 3=Publishable, 4=Challenger/Exemplary)

---

## 📊 Strategic Weighting (100%)

| Parameter | Weight | Focus | Rationale |
| :--- | :--- | :--- | :--- |
| **P1: Tone & Voice** | **30%** | **Style** | "Challenger" Brand Voice. Confident, spicy, human. |
| **P4: Strategic Value**| **30%** | **Substance** | **Equal to Style.** Specific utility for Sales Leaders. |
| **P3: Structure** | **25%** | **Clarity** | Respects the reader's time (BLUF). |
| **P5: Engagement** | **10%** | **Reach** | SEO and Hooks. |
| **P2: Brand Hygiene** | **5%** | **Compliance** | **Veto Gate.** Violations trigger Gate 3 Failure. |

---

## P2: Brand Hygiene & Compliance (5% + GATE 3)
*Goal: Context-aware enforcement of the Style Guide. Binary Veto Power.*

### 2A: Mechanical Compliance (Regex Layer)
* **Criteria**: docs/layer-1-strategy.md
* **Impact**: **Critical Veto.** Any violation here triggers Gate 3 Failure.

### 2B: Contextual Terminology (LLM Logic Layer) 🧠 IMPROVED
**Core Task**: Enforce restricted terminology by analyzing the *Referent* (the specific subject being described).

**Logic Block 1: "Tool" & "Hub"**
* **Restricted Words**: Tool, Hub.
* **Evaluation Logic**:
    1.  Locate the word.
    2.  **Identify Referent**: Is it describing `monday.com` / `monday CRM`?
    3.  **Rule**:
        * IF Referent == `monday.com`: Must use **Platform**, **Work OS**, or **Product**. (Using "Tool" or "Hub" = **CRITICAL FAIL**).
        * IF Referent == `Competitor` (Salesforce, HubSpot) OR `General Industry`: "Tool" and "Hub" are **PERMITTED**.

**Logic Block 2: "Tasks" & "To-dos"**
* **Restricted Words**: Task, To-do.
* **Evaluation Logic**:
    1.  Locate the word.
    2.  **Identify Context**: Is it describing what monday.com manages or holds?
    3.  **Rule**:
        * IF describing monday.com architecture: Must use **Items**, **Workflows**, **Processes**, or **Projects**. (e.g., "Manage your tasks in monday" = **FAIL**).
        * IF describing general work concepts: **PERMITTED**. (e.g., "Sales reps have too many administrative tasks" = **PASS**).

**Logic Block 3: "Sub-tasks"**
* **Rule**: Strict replacement. Monday.com uses **Sub-items**.
    * "Sub-tasks" = **FAIL** (unless explicitly quoting a competitor's feature name).

### 2C: Persona & Lexicon (Context-Aware) 🧠 IMPROVED
**Core Task**: Enforce "Customer" vs "User" logic.

**Logic Block: "Customers" vs. "Users"**
* **Restricted Word**: User(s).
* **Evaluation Logic**:
    1.  Locate the word "User".
    2.  **Identify Referent**: Who are these people?
    3.  **Rule**:
        * IF Referent == People utilizing monday.com: Must use **Customer(s)** or **Team Member(s)**. (Using "User" = **FAIL**).
            * *Rationale*: "Users" implies free/casual use. "Customers" implies value and commitment.
        * IF Referent == People utilizing generic software or competitors: "User" is **PERMITTED**. (e.g., "Salesforce users often complain..." = **PASS**).

**Logic Block: Forbidden Words**
* **List**: Synergy, Uplevel, Disruptive, Innovation, Learnings.
* **Rule**: **FAIL** if present (no context exceptions).

---

## P1: Challenger Tone & Voice (30%)

### 1B: Direct with Personality (10%)
* **Core Question**: Is the writing direct ("fluff-free") while maintaining human warmth?
* **Deep Dive Questions (Nuance)**:
    * **The "Smart Colleague" Test**: Does this sound like a smart peer chatting over Slack, or a marketing brochure? (Penalty for "Brochure-speak").
    * **Passive Aggressive Check**: Is the directness rude? (e.g., "You are failing because..." vs "Pipeline failure happens when...").
    * **Qualifier Density**: Are there more than 2 instances of "really," "very," or "actually" per paragraph?

### 1D: Sharp Wit & Confidence (10%)
* **Core Question**: Is the tone "spicy" and opinionated?
* **Deep Dive Questions (Nuance)**:
    * **The "Vanilla" Test**: Could this have been written by a legacy competitor (e.g., Microsoft)? If yes, score low.
    * **Cliché Detector**: Does it use tired business metaphors like "moving the needle," "low hanging fruit," or "game changer"? (Penalty for Clichés).
    * **Active Ownership**: Does the writer claim the opinion, or hide behind "It is said that..."?

### 1A: Positive & Solution-Focused (5%)
* **Core Question**: Does the content empower the reader?
* **Deep Dive Questions (Nuance)**:
    * **The 80/20 Rule**: Is 80% of the content focused on the *solution* and only 20% on the *problem*? (If it dwells on the problem for >50%, score low).
    * **The "Lazy Rep" Tropes**: Does the piece imply salespeople are lazy or disorganized? (Immediate Fail - "Don't Villainize").

### 1C: Trustworthy & Authentic (5%)
* **Core Question**: Is the confidence earned?
* **Deep Dive Questions (Nuance)**:
    * **The "Trust Me" Filter**: Does the writer make a claim (e.g., "This increases revenue") without a "Why" or "How"?
    * **Vulnerability**: Does the writer admit where the software *isn't* a magic wand? (e.g., "Automation helps, but you still need a strategy"). High score for nuance.

---

## P4: Strategic Value & Depth (30%)

### 4A: Audience Alignment (10%)
* **Core Question**: Is this explicitly for **Sales/Revenue Leaders**?
* **Deep Dive Questions (Nuance)**:
    * **The "Seniority Check"**: Is the advice too basic? (e.g., "Remember to call your leads"). This is for junior reps, not Leaders. Score low.
    * **The "HR Swap"**: If you replace the word "Sales" with "Recruiting," does the advice still apply? If yes, it's too generic. Score low.

### 4B: Actionability (10%)
* **Core Question**: Can the reader implement this *today*?
* **Deep Dive Questions (Nuance)**:
    * **The "Monday Morning" Test**: If the reader read this on Sunday, would they know exactly what to change in their workflow on Monday morning?
    * **Visualizability**: Does the text describe a workflow clearly enough that you could draw it on a whiteboard?

### 4C: Evidence & Examples (5%)
* **Core Question**: Is the advice grounded in reality?
* **Deep Dive Questions (Nuance)**:
    * **Data Interpretation**: Does the writer just list a stat, or do they explain *why* that stat matters to a Sales Director's bonus/quota?
    * **Hypothetical vs. Real**: Are the examples "Imagine a company..." (Weak) or "When a SaaS company scales to $10M..." (Strong/Specific)?

### 4D: Originality & AI Detection (5%)
* **Core Question**: Does this sound like "Gray Goo"?
* **Deep Dive Questions (Nuance)**:
    * **Predictability**: Can you predict the end of the sentence before reading it? (Sign of AI).
    * **Counter-Intuitive Insight**: Does the article challenge a commonly held belief? (High Score for Originality).

---

## P3: Structural Integrity & Clarity (25%)

### 3A: BLUF - Bottom Line Up Front (10%)
* **Core Question**: Is the core value visible immediately?
* **Deep Dive Questions (Nuance)**:
    * **The "Rhetorical Question" Trap**: Does the intro start with 3 rhetorical questions ("Do you want more sales? Do you hate admin?")? (Penalty - this is fluff/burying the lead).
    * **Speed to Value**: Count the sentences until the first unique insight appears. If >5, score low.

### 3B: Scannability & Hierarchy (5%)
* **Core Question**: Is it skimmable?
* **Deep Dive Questions (Nuance)**:
    * **Header Storytelling**: If you read *only* the H2s, do you get a complete summary of the article?
    * **Wall of Text**: Is there any paragraph longer than 5 lines? (Penalty).

### 3C: Conciseness & Human Language (5%)
* **Core Question**: Is every word fighting for its life?
* **Deep Dive Questions (Nuance)**:
    * **Nominalization Check**: Is the writer turning verbs into nouns? (e.g., "Make a decision" instead of "Decide," "Give consideration" instead of "Consider").
    * **Adverb Addiction**: Are there "ly" words padding the sentences? (e.g., "Carefully analyze," "Strategically plan").

### 3D: Specificity (5%)
* **Core Question**: Is the language concrete?
* **Deep Dive Questions (Nuance)**:
    * **The "Thing" Counter**: Count instances of "things," "aspects," "factors." High count = Low score.
    * **Quantification**: Are general claims quantified? (e.g., "Huge increase" vs "20% increase").

---

## P5: Engagement (10%)

### 5A: Headline & Hook (5%)
* **Core Question**: Does it stop the scroll?
* **Deep Dive Questions (Nuance)**:
    * **The "So What" Test**: Does the headline promise a benefit, or just describe a topic? ("CRM Strategy" vs "How to Build a CRM Strategy that Doubles Revenue").
    * **Empathy Hook**: Does the first sentence acknowledge a specific pain point the reader is feeling *right now*?

### 5B: SEO & Shareability (5%)
* **Core Question**: Is it share-worthy?
* **Deep Dive Questions (Nuance)**:
    * **Status Signal**: Would sharing this article make the reader look smart to their boss?
    * **Keyword Naturalism**: Does the target keyword feel shoehorned in, or does it flow naturally?
