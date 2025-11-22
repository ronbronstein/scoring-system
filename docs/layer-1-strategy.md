The hybrid architecture (Regex + LLM) described in our PRD is robust and efficient. "Layer 1: The Hard Gate" is crucial for catching deterministic, non-negotiable style errors before engaging the more resource-intensive LLM analysis (Layer 2).

Based on the monday.com style guide and the requirement to exclude context-dependent rules, here is the comprehensive regex logic for Layer 1.

### Layer 1: Implementation Strategy

The goal of Layer 1 is to identify **violations** of the style guide using deterministic patterns. We employ several key techniques:

1.  **Word Boundaries (`\b`):** Ensures we match whole words (e.g., not flagging "ok" inside "book").
2.  **Case Insensitivity (`(?i)`):** Used for general spelling and hyphenation rules to catch violations regardless of capitalization.
3.  **Strict Case Enforcement (Negative Lookahead):** For rules requiring a specific capitalization (e.g., `monday.com` must be lowercase), we use a **negative lookahead** `(?!...)`.
      * *Pattern:* `r"\b(?!<correct_format>\b)(?i:<word>)\b"`
      * *Example:* `r"\b(?!monday\.com\b)(?i:monday\.com)\b"` finds any instance of the word case-insensitively, but asserts that the match *cannot* be the exact string `monday.com`. This flags `Monday.com`, `MONDAY.COM`, etc.

### Excluded from Layer 1 (Requires Context/LLM)

As stipulated, the following rules require understanding grammatical context or sentence structure and are deferred to Layer 2:

  * **Noun/Verb/Adjective distinctions:** `add-on`/`add on`, `back end`/`back-end`, `front end`/`front-end`, `login`/`log in`, `opt-in`/`opt in`, `pop-up`/`pop up`, `setup`/`set up`, `signup`/`sign up`, `third party`/`third-party`.
  * **Contextual meaning:** `like` (the social media activity).
  * **Ambiguous Capitalization:** We are excluding `Enterprise` and `Waterfall`. Although the guide lists them as uppercase, they are common nouns. Enforcing this deterministically in Layer 1 would lead to excessive false positives.

### Layer 1 Regex Logic (`regex_checker.py`)

The following Python dictionary structure is ready for implementation in your `src/regex_checker.py`. This structure aligns well with the requirement to report flags in the final JSON output (PRD 5.0).

```python
import re

# Layer 1: Deterministic Regex Rules
# Patterns are designed to FIND THE VIOLATION of the style guide.

LAYER_1_RULES = {
    # ========================================================================
    # 1. MONDAY.COM BRANDING & TERMINOLOGY (Critical)
    # ========================================================================
    "MONDAY_COM_CASE": {
        "pattern": r"\b(?!monday\.com\b)(?i:monday\.com)\b",
        "message": "'monday.com' must always be lowercase, even at the start of a sentence.",
        "severity": "Critical"
    },
    "MONDAY_APPS_CASE": {
        "pattern": r"\b(?!monday apps\b)(?i:monday apps)\b",
        "message": "'monday apps' (the brand) must always be lowercase.",
        "severity": "Critical"
    },
    "SUB_ITEMS_USAGE": {
        # Flags sub-task, sub task, subtask (singular/plural)
        "pattern": r"\b(?i:sub[ -]?tasks?)\b",
        "message": "Use 'Sub-items', not 'sub-tasks' or variations.",
        "severity": "Critical"
    },

    # ========================================================================
    # 2. REQUIRED CAPITALIZATION (Methodologies/Acronyms)
    # ========================================================================
    # These patterns flag the incorrect lowercase versions.
    "AGILE_CASE": {
        "pattern": r"\bagile\b",
        "message": "'Agile' (methodology) should be capitalized.",
        "severity": "Medium"
    },
    "KANBAN_CASE": {
        "pattern": r"\bkanban\b",
        "message": "'Kanban' should be capitalized.",
        "severity": "Medium"
        },
    "SCRUM_CASE": {
        "pattern": r"\bscrum\b",
        "message": "'Scrum' should be capitalized.",
        "severity": "Medium"
    },
    "EMOJI_CASE": {
        # Flags lowercase emoji or emojis
        "pattern": r"\bemoji(s)?\b",
        "message": "'Emoji' (singular and plural) should be capitalized.",
        "severity": "Medium"
    },
    "OK_CASE": {
        # Flags ok, Ok, Okay, okay, etc.
        "pattern": r"\b((?!OK\b)(?i:OK)|(?i:Okay))\b",
        "message": "Use 'OK' (uppercase). Do not use 'Okay'.",
        "severity": "Medium"
    },
    "URL_CASE": {
        "pattern": r"\b(?!URL\b)(?i:URL)\b",
        "message": "Use 'URL' (uppercase).",
        "severity": "Medium"
    },

    # ========================================================================
    # 3. COMPOUNDING AND HYPHENATION
    # ========================================================================
    # We use (?i) for case-insensitive matching for these rules.

    # 3a. Must be One Word (Flags spaced or hyphenated versions)
    # We use [ -] to catch both spaces and hyphens.
    "EBOOK_COMPOUNDING": {"pattern": r"\b(?i:e[- ]book)\b", "message": "Use 'ebook'."},
    "ECOMMERCE_COMPOUNDING": {"pattern": r"\b(?i:e[- ]commerce)\b", "message": "Use 'ecommerce'."},
    "HASHTAG_SPELLING": {"pattern": r"\b(?i:hash[ -]tag)\b", "message": "Use 'hashtag'."},
    "HEADHUNTING_SPELLING": {"pattern": r"\b(?i:head[ -]hunt(?:ing|ers?))\b", "message": "Use 'headhunting'/'headhunters'."},
    "HOMEPAGE_SPELLING": {"pattern": r"\b(?i:home[ -]page)\b", "message": "Use 'homepage'."},
    "MULTICHANNEL_SPELLING": {"pattern": r"\b(?i:multi[ -]channel)\b", "message": "Use 'multichannel'."},
    "NONPROFIT_SPELLING": {"pattern": r"\b(?i:non[ -]profit)\b", "message": "Use 'nonprofit'."},
    "USERNAME_SPELLING": {"pattern": r"\b(?i:user[ -]name)\b", "message": "Use 'username'."},
    "WEBSITE_SPELLING": {"pattern": r"\b(?i:web[ -]site)\b", "message": "Use 'website'."},

    # 3b. Must be Hyphenated (Flags spaced or compounded versions)
    "PPC_SPELLING": {"pattern": r"\b(?i:pay[ ]per[ ]click)\b", "message": "Use 'pay-per-click'."},
    # [ ]? catches optional space (pre sale) or no space (presale)
    "PRESALE_SPELLING": {"pattern": r"\b(?i:pre[ ]?sale)\b", "message": "Use 'pre-sale'."},
    "PMF_SPELLING": {"pattern": r"\b(?i:product[ ]market[ ]fit)\b", "message": "Use 'product-market fit'."},
    "STARTUP_SPELLING": {"pattern": r"\b(?i:start[ ]?up)\b", "message": "Use 'start-up'."},

    # 3c. Must be Separate Words (Flags compounded or hyphenated versions)
    # -? catches optional hyphen (life-cycle) or no hyphen (lifecycle)
    "LIFECYCLE_SPELLING": {"pattern": r"\b(?i:life-?cycle)\b", "message": "Use 'life cycle'."},

    # ========================================================================
    # 4. MISSPELLINGS
    # ========================================================================
    "SYNC_SPELLING": {"pattern": r"\b(?i:synch)\b", "message": "Use 'sync', not 'synch'."},

    # ========================================================================
    # 5. MID-SENTENCE CAPITALIZATION (Heuristics)
    # ========================================================================
    # Identifying the start of a sentence perfectly is complex with Regex.
    # We use a lookbehind (?<=\s) to check if the word is preceded by a space.
    # This acts as a proxy for "not the start of the sentence" and flags mid-sentence capitalization.
    "INTERNET_CASE_MID": {
        "pattern": r"(?<=\s)Internet\b",
        "message": "'internet' should not be capitalized unless it begins a sentence."
    },
    "ONLINE_CASE_MID": {
        "pattern": r"(?<=\s)Online\b",
        "message": "'online' should not be capitalized unless it begins a sentence."
    },
     "EBOOK_CASE_MID": {
        "pattern": r"(?<=\s)Ebook\b",
        "message": "'ebook' should generally be lowercase."
    },
    "ECOMMERCE_CASE_MID": {
        "pattern": r"(?<=\s)Ecommerce\b",
        "message": "'ecommerce' should generally be lowercase."
    },
}
```