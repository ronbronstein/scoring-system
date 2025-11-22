# Sub-Parameters Reference: Evaluation Criteria

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

## P1: Challenger Tone & Voice (30%)

### 1B: Direct with Personality (10%)
* **Core Question**: Is the writing direct ("fluff-free") while maintaining human warmth?
* **Deep Dive Questions (Nuance)**:
    * **The "Smart Colleague" Test**: Does this sound like a smart peer chatting over Slack, or a marketing brochure? (Penalty for "Brochure-speak").
    * **Passive Aggressive Check**: Is the directness rude? (e.g., "You are failing because..." vs "Pipeline failure happens when...").
    * **Qualifier Density**: Are there more than 2 instances of "really," "very," or "actually" per paragraph?

#### 🔬 Precision Protocol (for Agent 1B)
* **Mental Model**: "The Coffee Shop Editor." If you wouldn't say it to a colleague over coffee because it sounds too stiff, it fails.
* **Comparative Examples**:
    * ❌ **Fail (Brochure/Robot):** "Utilization of CRM software facilitates the optimization of sales pipelines." (Too distant, too many syllables).
    * ❌ **Fail (Too Casual/Gen-Z):** "Sales pipelines are totally giving chaotic energy rn." (Too informal, lacks authority).
    * ✅ **Pass (Challenger):** "Your sales pipeline is leaking, and spreadsheets are the reason why." (Direct, punchy, clear subject-verb-object).
* **Key Instruction**: Penalize "hedging." If the writer uses phrases like "It is important to note that..." or "We believe that...", score < 3. Just say the thing.

### 1D: Sharp Wit & Confidence (10%)
* **Core Question**: Is the tone "spicy" and opinionated?
* **Deep Dive Questions (Nuance)**:
    * **The "Vanilla" Test**: Could this have been written by a legacy competitor (e.g., Microsoft)? If yes, score low.
    * **Cliché Detector**: Does it use tired business metaphors like "moving the needle," "low hanging fruit," or "game changer"? (Penalty for Clichés).
    * **Active Ownership**: Does the writer claim the opinion, or hide behind "It is said that..."?

#### 🔬 Precision Protocol (for Agent 1D)
* **Mental Model**: "The Opinionated Consultant." The writer should have a distinct point of view that might slightly annoy a traditionalist.
* **Comparative Examples**:
    * ❌ **Fail (Safe/Vanilla):** "Effective communication is key to business success." (True, but boring. Zero spice).
    * ✅ **Pass (Spicy/Witty):** "Most 'effective communication' strategies are just more meetings that could have been emails." (Challenges the status quo, relatable wit).
* **Edge Case Handling**: Confidence does not mean arrogance.
    * *Arrogant:* "We are the only solution that works." (Fail).
    * *Confident:* "Legacy CRMs were built for a world that no longer exists." (Pass).

### 1A: Positive & Solution-Focused (5%)
* **Core Question**: Does the content empower the reader?
* **Deep Dive Questions (Nuance)**:
    * **The 80/20 Rule**: Is 80% of the content focused on the *solution* and only 20% on the *problem*? (If it dwells on the problem for >50%, score low).
    * **The "Lazy Rep" Tropes**: Does the piece imply salespeople are lazy or disorganized? (Immediate Fail - "Don't Villainize").

#### 🔬 Precision Protocol (for Agent 1A)
* **Mental Model**: "The Coach, not the Critic." The enemy is the *process* or the *old software*, never the *person*.
* **Evaluation Check**: Highlight the "Villain."
    * If Villain == The Sales Rep ("Reps always forget to update CRM") -> **Score 1 (Critical Fail)**.
    * If Villain == The Old System ("Legacy CRMs make updating data a nightmare") -> **Score 4 (Pass)**.
    * If Villain == The Manager ("Bosses micromanage because they don't trust you") -> **Score 1 (Critical Fail - Negative framing)**.

### 1C: Trustworthy & Authentic (5%)
* **Core Question**: Is the confidence earned?
* **Deep Dive Questions (Nuance)**:
    * **The "Trust Me" Filter**: Does the writer make a claim (e.g., "This increases revenue") without a "Why" or "How"?
    * **Vulnerability**: Does the writer admit where the software *isn't* a magic wand? (e.g., "Automation helps, but you still need a strategy"). High score for nuance.

#### 🔬 Precision Protocol (for Agent 1C)
* **Mental Model**: "The Realist."
* **Key Instruction**: Scan for "Absolutes" vs. "Nuance."
    * ❌ **Fail (Overselling):** "Implement this and your revenue will double overnight." (Untrustworthy/Scammy).
    * ✅ **Pass (Authentic):** "Automation handles the busy work, but it can't close the deal for you. That's still on your team." (Trustworthy because it acknowledges limits).

---

## P2: Brand Hygiene & Compliance (5% + GATE 3)
*Goal: Context-aware enforcement of the Style Guide. Binary Veto Power.*

### 2A: Mechanical Compliance (Regex Layer)
* **Source**: `src/regex_checker.py` (Deterministic).
* **Impact**: **Critical Veto.** Any violation here triggers Gate 3 Failure.
* **Checklist**: (See Regex Python Script for full list).

### 2B: Contextual Terminology (LLM Logic Layer) 🧠
**Core Task**: Enforce restricted terminology by analyzing the *Referent* (the specific subject being described).

**Logic Block 1: "Tool" & "Hub"**
* **Restricted Words (Triggers)**: Tool, Hub.
* **Evaluation Logic**:
    1.  Locate the word.
    2.  **Identify Referent**: Is it describing `monday.com` / `monday CRM`?
    3.  **Rule**:
        * IF Referent == `monday.com`: **CRITICAL FAIL**. (Must use **Platform**, **Work OS**, or **Product**).
        * IF Referent == `Competitor` (Salesforce, HubSpot) OR `General Industry`: **PERMITTED**.

**Logic Block 2: "Tasks" & "To-dos"**
* **Restricted Words (Triggers)**: Task, To-do.
* **Evaluation Logic**:
    1.  Locate the word.
    2.  **Identify Context**: Is it describing what monday.com manages or holds?
    3.  **Rule**:
        * IF describing monday.com architecture: **FAIL**. (Must use **Items**, **Workflows**, **Processes**, or **Projects**).
        * IF describing general work concepts: **PERMITTED**. (e.g., "Sales reps have too many administrative tasks" = **PASS**).

#### 🔬 Precision Protocol (for Agent 2B)
* **Examples for "Tool" Paradox**:
    * ❌ **Fail:** "monday.com is a great project management tool." (Referent is monday).
    * ✅ **Pass:** "Stop using disconnected tools and switch to a platform." (Referent is generic/competitors).
    * ✅ **Pass:** "The right tool for the job is essential." (Idiomatic expression).
* **Examples for "Task" Paradox**:
    * ❌ **Fail:** "Create a task in monday CRM for every lead." (Architecture violation).
    * ✅ **Pass:** "Create an item in monday CRM." (Correct Architecture).
    * ✅ **Pass:** "Automate your manual tasks so you can focus on selling." (Refers to human labor, not software objects).

### 2C: Persona & Lexicon (Context-Aware) 🧠
**Core Task**: Enforce persona-specific language that requires semantic understanding.

**Logic Block 1: "Customers" vs. "Users"**
* **Restricted Word (Trigger)**: User(s).
* **Evaluation Logic**:
    1.  Locate the word "User".
    2.  **Identify Referent**: Who are these people?
    3.  **Rule**:
        * IF Referent == People utilizing monday.com: **FAIL**. (Must use **Customer(s)** or **Team Member(s)**).
        * IF Referent == People utilizing generic software or competitors: **PERMITTED**.

**Logic Block 2: "Managers" vs. "Bosses"**
* **Restricted Word (Trigger)**: Boss(es).
* **Rule**: **FAIL**. (Must use **Manager**).
* *Rationale*: "Boss" implies negative/oppressive top-down leadership. "Manager" implies domain ownership.

**Logic Block 3: Ad Hominem Descriptors**
* **Restricted Words (Triggers)**: Crazy, Insane.
* **Rule**:
        * IF describing a Person/Persona: **FAIL**. (e.g., "Sales managers are insane").
        * IF describing a Situation/Metric: **PERMITTED** (though discouraged). (e.g., "The growth was insane").

#### 🔬 Precision Protocol (for Agent 2C)
* **Semantic Check**:
    * ❌ **Fail:** "When your users log in to monday..." (Implies casual/free use).
    * ✅ **Pass:** "When your team members log in..." (Implies professional commitment).
    * ❌ **Fail:** "Convince your boss to buy this." (Implies subordination).
    * ✅ **Pass:** "Show your manager the ROI." (Implies professional hierarchy).

---

## P3: Structural Integrity & Clarity (25%)

### 3A: BLUF - Bottom Line Up Front (10%)
* **Core Question**: Is the core value visible immediately?
* **Deep Dive Questions (Nuance)**:
    * **The "Rhetorical Question" Trap**: Does the intro start with 3 rhetorical questions ("Do you want more sales? Do you hate admin?")? (Penalty - this is fluff/burying the lead).
    * **Speed to Value**: Count the sentences until the first unique insight appears. If >5, score low.

#### 🔬 Precision Protocol (for Agent 3A)
* **Mental Model**: "The Scroll Test." Does the reader have to scroll past the "fold" to find the answer to the headline?
* **Logic Check**:
    1.  Identify the "Promise" in the Headline.
    2.  Identify the "Delivery" in the text.
    3.  If "Delivery" appears after Paragraph 2 -> **Score <= 2**.
* **Comparative Examples**:
    * ❌ **Fail:** Intro defines what CRM is (Definition), then asks 3 questions, then gives the answer in Para 4.
    * ✅ **Pass:** Intro states the problem (Leaky pipeline) and immediately states the solution (Automation) in Para 1.

### 3B: Scannability & Hierarchy (5%)
* **Core Question**: Is it skimmable?
* **Deep Dive Questions (Nuance)**:
    * **Header Storytelling**: If you read *only* the H2s, do you get a complete summary of the article?
    * **Wall of Text**: Is there any paragraph longer than 5 lines? (Penalty).

#### 🔬 Precision Protocol (for Agent 3B)
* **Key Instruction**: "The Skimmer." Ignore the body text. Read ONLY the H2 headers.
    * If H2s are generic ("Introduction", "Tip 1", "Conclusion") -> **Score 2**.
    * If H2s are descriptive ("Why pipelines leak", "Automate follow-ups", "Measure ROI") -> **Score 4**.

### 3C: Conciseness & Human Language & No Jargon (5%)
* **Core Question**: Is every word fighting for its life?
* **Deep Dive Questions (Nuance)**:
    * **Nominalization Check**: Is the writer turning verbs into nouns? (e.g., "Make a decision" instead of "Decide").
    * **Adverb Addiction**: Are there "ly" words padding the sentences? (e.g., "Carefully analyze," "Strategically plan").

#### 🔬 Precision Protocol (for Agent 3C)
* **Mental Model**: "The Hemmingway Editor."
* **Search and Penalize**:
    * "In order to" -> (Should be "To")
    * "Leverage" -> (Should be "Use")
    * "Utilize" -> (Should be "Use")
    * "Due to the fact that" -> (Should be "Because")
    * "Synergy" -> (Automatic Fail - Forbidden Jargon)
    * "Learnings" -> (Automatic Fail - Forbidden Jargon)

### 3D: Specificity (5%)
* **Core Question**: Is the language concrete?
* **Deep Dive Questions (Nuance)**:
    * **The "Thing" Counter**: Count instances of "things," "aspects," "factors." High count = Low score.
    * **Quantification**: Are general claims quantified? (e.g., "Huge increase" vs "20% increase").

#### 🔬 Precision Protocol (for Agent 3D)
* **Comparative Examples**:
    * ❌ **Fail:** "We improved many aspects of the process." (Vague).
    * ✅ **Pass:** "We cut approval times by 3 days." (Specific).

---

## P4: Strategic Value & Depth (30%)

### 4A: Audience Alignment (10%)
* **Core Question**: Is this explicitly for **Sales/Revenue Leaders**?
* **Deep Dive Questions (Nuance)**:
    * **The "Seniority Check"**: Is the advice too basic? (e.g., "Remember to call your leads"). This is for junior reps, not Leaders. Score low.
    * **The "HR Swap"**: If you replace the word "Sales" with "Recruiting," does the advice still apply? If yes, it's too generic. Score low.

#### 🔬 Precision Protocol (for Agent 4A)
* **Mental Model**: "The Boardroom vs. The Breakroom."
* **Context Check**:
    * Topic: "How to organize your calendar" -> **Fail** (Junior/Basic).
    * Topic: "How to forecast revenue variance in Q4" -> **Pass** (Leadership/Strategic).
    * Topic: "Being nice to customers" -> **Fail** (Generic).

### 4B: Actionability (10%)
* **Core Question**: Can the reader implement this *today*?
* **Deep Dive Questions (Nuance)**:
    * **The "Monday Morning" Test**: If the reader read this on Sunday, would they know exactly what to change in their workflow on Monday morning?
    * **Visualizability**: Does the text describe a workflow clearly enough that you could draw it on a whiteboard?

#### 🔬 Precision Protocol (for Agent 4B)
* **Evaluation Check**: The "Implementation Gap."
    * Does the text explain *What* to do? (e.g., "Analyze your data").
    * Does the text explain *How* to do it? (e.g., "Create a dashboard tracking Deal Age > 30 days").
    * **Rule**: If *What* > *How*, Score <= 2. If *How* is explicit, Score >= 3.

### 4C: Evidence & Examples (5%)
* **Core Question**: Is the advice grounded in reality?
* **Deep Dive Questions (Nuance)**:
    * **Data Interpretation**: Does the writer just list a stat, or do they explain *why* that stat matters to a Sales Director's bonus/quota?
    * **Hypothetical vs. Real**: Are the examples "Imagine a company..." (Weak) or "When a SaaS company scales to $10M..." (Strong/Specific)?

#### 🔬 Precision Protocol (for Agent 4C)
* **Constraint**: Generic stats like "Salesforce says 50% of reps fail" are cheap.
* **Bonus Logic**: Award points if the content ties a statistic to a specific *monday.com feature* or *workflow outcome*.

### 4D: Originality & AI Detection (5%)
* **Core Question**: Does this sound like "Gray Goo"?
* **Deep Dive Questions (Nuance)**:
    * **Predictability**: Can you predict the end of the sentence before reading it? (Sign of AI).
    * **Counter-Intuitive Insight**: Does the article challenge a commonly held belief? (High Score for Originality).

#### 🔬 Precision Protocol (for Agent 4D)
* **Mental Model**: "The AI Trope Hunter."
* **Immediate Penalties** for these phrases (unless used ironically):
    * "In today's fast-paced digital landscape..."
    * "It is crucial to remember..."
    * "Delve into..."
    * "Unlocking the power of..."
    * "At the end of the day..."

---

## P5: Engagement (10%)

### 5A: Headline & Hook (5%)
* **Core Question**: Does it stop the scroll?
* **Deep Dive Questions (Nuance)**:
    * **The "So What" Test**: Does the headline promise a benefit, or just describe a topic? ("CRM Strategy" vs "How to Build a CRM Strategy that Doubles Revenue").
    * **Empathy Hook**: Does the first sentence acknowledge a specific pain point the reader is feeling *right now*?

#### 🔬 Precision Protocol (for Agent 5A)
* **Formula Check**: "Pain-Agitate-Solve."
    * Does the intro identify a Pain?
    * Does it twist the knife (Agitate) by explaining the cost of that pain?
    * If yes -> **Score 4**.
    * If it starts with "Webster's Dictionary defines CRM as..." -> **Score 1**.

### 5B: SEO & Shareability (5%)
* **Core Question**: Is it share-worthy?
* **Deep Dive Questions (Nuance)**:
    * **Status Signal**: Would sharing this article make the reader look smart to their boss?
    * **Keyword Naturalism**: Does the target keyword feel shoehorned in, or does it flow naturally?

#### 🔬 Precision Protocol (for Agent 5B)
* **Mental Model**: "The LinkedIn Share."
* **User Simulation**: Imagine a Sales Director sharing this on LinkedIn. What is the caption?
    * If caption would be: "Interesting read." -> **Score 2 (Mediocre)**.
    * If caption would be: "Finally someone said it! Stop doing manual data entry." -> **Score 4 (High resonance)**.