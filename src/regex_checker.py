import re

# ========================================================================================
# LAYER 1 RULES: THE HARD GATE (DETERMINISTIC)
# Strategy: Zero Ambiguity. Patterns are designed to FIND THE VIOLATION of the style guide.
#
# Techniques:
# \b: Word boundary.
# (?i:): Case-insensitive group.
# (?!correct\b)(?i:word): Negative lookahead for strict case enforcement.
#   Finds the word case-insensitively ONLY IF it does not match the 'correct' format.
# ========================================================================================

LAYER_1_RULES = {
    # ========================================================================
    # 1. MONDAY.COM BRANDING & TERMINOLOGY (Critical)
    # ========================================================================
    "MONDAY_COM_CASE": {
        "pattern": r"\b(?!monday\.com\b)(?i:monday\.com)\b",
        "message": "'monday.com' must always be lowercase, even at the start of a sentence.",
        "severity": "Critical"
    },
    "MONDAY_SOLO_CASE": {
        # Flags 'Monday' when used alone (e.g., 'monday CRM').
        "pattern": r"\b(?!monday\b)(?i:monday)\b",
        "message": "'monday' (when used without the .com) must always be lowercase.",
        "severity": "Critical"
    },
    "MONDAY_APPS_CASE": {
        "pattern": r"\b(?!monday apps\b)(?i:monday apps)\b",
        "message": "'monday apps' (the brand) must always be lowercase.",
        "severity": "Critical"
    },
     "MONDAY_WORKOS_CASE": {
        "pattern": r"\b(?!monday\.com Work OS\b)(?i:monday\.com Work OS)\b",
        "message": "The platform infrastructure must be referred to exactly as 'monday.com Work OS'.",
        "severity": "Critical"
    },
    "SUB_ITEMS_USAGE": {
        # Flags sub-task, sub task, subtask (singular/plural)
        "pattern": r"\b(?i:sub[ -]?tasks?)\b",
        "message": "Use 'Sub-items', not 'sub-tasks' or variations.",
        "severity": "Critical"
    },

    # ========================================================================
    # 2. REQUIRED CAPITALIZATION (Proper Nouns/Acronyms)
    # ========================================================================
    # Note: 'Agile' is excluded due to ambiguity with the common adjective (L2 responsibility).

    "KANBAN_CASE": {
        "pattern": r"\bkanban\b",
        "message": "'Kanban' (methodology) should be capitalized.",
        "severity": "High"
        },
    "SCRUM_CASE": {
        "pattern": r"\bscrum\b",
        "message": "'Scrum' (methodology) should be capitalized.",
        "severity": "High"
    },
    "EMOJI_CASE": {
        # Flags lowercase emoji or emojis. Confirmed: Must always be capitalized.
        "pattern": r"\bemoji(s)?\b",
        "message": "'Emoji' (singular and plural) must be capitalized.",
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

    # 3a. Must be One Word (Flags spaced or hyphenated versions)
    "EBOOK_COMPOUNDING": {"pattern": r"\b(?i:e[- ]book)\b", "message": "Use 'ebook'.", "severity": "Medium"},
    "ECOMMERCE_COMPOUNDING": {"pattern": r"\b(?i:e[- ]commerce)\b", "message": "Use 'ecommerce'.", "severity": "Medium"},
    "HASHTAG_SPELLING": {"pattern": r"\b(?i:hash[ -]tag)\b", "message": "Use 'hashtag'.", "severity": "Medium"},
    "HEADHUNTING_SPELLING": {"pattern": r"\b(?i:head[ -]hunt(?:ing|ers?))\b", "message": "Use 'headhunting'/'headhunters'.", "severity": "Medium"},
    "HOMEPAGE_SPELLING": {"pattern": r"\b(?i:home[ -]page)\b", "message": "Use 'homepage'.", "severity": "Medium"},
    "MULTICHANNEL_SPELLING": {"pattern": r"\b(?i:multi[ -]channel)\b", "message": "Use 'multichannel'.", "severity": "Medium"},
    "NONPROFIT_SPELLING": {"pattern": r"\b(?i:non[ -]profit)\b", "message": "Use 'nonprofit'.", "severity": "Medium"},
    "USERNAME_SPELLING": {"pattern": r"\b(?i:user[ -]name)\b", "message": "Use 'username'.", "severity": "Medium"},
    "WEBSITE_SPELLING": {"pattern": r"\b(?i:web[ -]site)\b", "message": "Use 'website'.", "severity": "Medium"},

    # 3b. Must be Hyphenated (Flags spaced or compounded versions)
    "PPC_SPELLING": {"pattern": r"\b(?i:pay[ ]per[ ]click)\b", "message": "Use 'pay-per-click'.", "severity": "Medium"},
    "PRESALE_SPELLING": {"pattern": r"\b(?i:pre[ ]?sale)\b", "message": "Use 'pre-sale'.", "severity": "Medium"},
    "PMF_SPELLING": {"pattern": r"\b(?i:product[ ]market[ ]fit)\b", "message": "Use 'product-market fit'.", "severity": "Medium"},
    "STARTUP_SPELLING": {"pattern": r"\b(?i:start[ ]?up)\b", "message": "Use 'start-up'.", "severity": "Medium"},

    # 3c. Must be Separate Words (Flags compounded or hyphenated versions)
    "LIFECYCLE_SPELLING": {"pattern": r"\b(?i:life-?cycle)\b", "message": "Use 'life cycle'.", "severity": "Medium"},

    # ========================================================================
    # 4. FORMATTING AND PUNCTUATION
    # ========================================================================
    "PERCENT_WORD_USAGE": {
        # Confirmed: Flagging this deterministically.
        "pattern": r"\b(?i:percent)\b",
        "message": "Use the % symbol, not the word 'percent'.",
        "severity": "Medium"
    },
     "POST_SCRIPT_FORMAT": {
        # Flags PS, P.s., ps, etc. Must be P.S.
        "pattern": r"\b(?!P\.S\.)(?i:P[.]?S[.]?)\b",
        "message": "Use 'P.S.' (with periods).",
        "severity": "Medium"
    },
    "EM_DASH_SUBSTITUTES": {
        # Flags common substitutes for Em dashes like -- or ---, or a hyphen surrounded by spaces ( - ).
        "pattern": r"(--+|\s-\s)",
        "message": "Use a proper Em dash (—) instead of double hyphens (--) or a spaced hyphen ( - ).",
        "severity": "Medium"
    },

    # ========================================================================
    # 5. FORBIDDEN WORDS & MISSPELLINGS (Absolute Bans)
    # ========================================================================
    "SYNC_SPELLING": {"pattern": r"\b(?i:synch)\b", "message": "Use 'sync', not 'synch'.", "severity": "Medium"},

    "FORBIDDEN_JARGON_BUZZWORDS": {
        # Confirmed: Absolute ban on disruptive, innovation, technologist, synergy, uplevel.
        "pattern": r"\b(?i:disruptive|innovation|technologist|synergy|uplevel)\b",
        "message": "Avoid jargon/buzzwords like 'disruptive', 'innovation', 'synergy', 'uplevel', or 'technologist'.",
        "severity": "High"
    },
    "FORBIDDEN_LEARNINGS": {
        "pattern": r"\b(?i:learnings)\b",
        "message": "Avoid the word 'learnings'. Use 'lessons', 'takeaways', or 'insights'.",
        "severity": "High"
    },

    # ========================================================================
    # 6. AMERICAN ENGLISH LOCALIZATION
    # ========================================================================
    "AMERICAN_ENGLISH_IZE_ISE": {
        # Flags common -ise endings (organise) and -yse (analyse).
        "pattern": r"\b(?i:organise|realise|optimise|prioritise|maximise|minimise|centralise|customise|analyse|paralyse|authorise)(?:d|s|ing|ation)?\b",
        "message": "Use American English spelling (e.g., 'organize' not 'organise'; 'analyze' not 'analyse').",
        "severity": "High"
    },
    "AMERICAN_ENGLISH_OUR_OR": {
        # Flags common -our endings (colour).
        "pattern": r"\b(?i:colour|behaviour|favour|honour|labour|neighbour|flavour)s?\b",
        "message": "Use American English spelling (e.g., 'color' not 'colour').",
        "severity": "High"
    },
    "AMERICAN_ENGLISH_RE_ER": {
        # Flags common -re endings (centre).
        "pattern": r"\b(?i:centre|fibre|litre|metre)s?\b",
        "message": "Use American English spelling (e.g., 'center' not 'centre').",
        "severity": "High"
    },
    "AMERICAN_ENGLISH_CONSONANT_DOUBLING": {
        # Flags British English consonant doubling (travelling).
        "pattern": r"\b(?i:travell(?:ing|ed|er)|modell(?:ing|ed)|cancell(?:ing|ed|ation))\b",
        "message": "Use American English spelling (e.g., 'traveling', 'modeling', 'cancellation').",
        "severity": "High"
    },
}

# ============================================================================
# Core Execution Logic
# ============================================================================

def _get_context(match, content, window=30):
    """
    Helper function to extract a snippet of the surrounding text for context.

    Args:
        match: The regex match object.
        content: The full text content.
        window: The number of characters to capture before/after the match.

    Returns:
        A formatted context string (e.g., "...prefix match suffix...").
    """
    start = max(0, match.start() - window)
    end = min(len(content), match.end() + window)

    # Add ellipses if the context is truncated
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(content) else ""

    # Replace newlines in the snippet for cleaner display in the report
    context_snippet = content[start:end].replace('\n', ' ').strip()

    return f"{prefix}{context_snippet}{suffix}"

def run_layer_1_checks(content: str) -> list[dict]:
    """
    Executes the deterministic Layer 1 Regex checks against the content.

    Args:
        content: The full text draft to analyze.

    Returns:
        A list of violation flags. An empty list means Layer 1 passed (Gate 3 Pass).
    """
    flags = []

    for rule_id, rule_data in LAYER_1_RULES.items():
        # Compile the pattern
        try:
            # Note: re.finditer caches compiled patterns, but explicit compilation
            # allows for error checking during development.
            pattern = re.compile(rule_data["pattern"])
        except re.error as e:
            print(f"Error compiling regex for rule {rule_id}: {e}")
            continue

        # Use finditer to find all occurrences
        for match in pattern.finditer(content):
            # Extract the actual text that violated the rule
            # Use strip() to clean potential leading/trailing spaces captured by the pattern
            violation_text = match.group(0).strip()

            # Get the surrounding context snippet
            context_snippet = _get_context(match, content)

            flag = {
                "source": "Layer 1 (Regex)",
                "rule_id": rule_id,
                "severity": rule_data["severity"],
                "message": rule_data["message"],
                "violation": violation_text,
                "context": context_snippet
            }
            flags.append(flag)

    return flags

# Example Usage (for local testing by the developer)
if __name__ == '__main__':
    test_draft = """
    Welcome to Monday.com! We help teams organise their workflows at the centre of work.
    It helps us uplevel our synergy. We saw a 50 percent increase last quarter.
    Please do not use sub-tasks.
    Remember to use OK, not Okay. We love using emoji in our communications.
    We are launching a new e-book about the software life-cycle.
    We use Scrum and kanban. We use -- instead of em dashes.
    P.s. check the URL.
    """

    violations = run_layer_1_checks(test_draft)
    if violations:
        print(f"Found {len(violations)} violations (Gate 3 Failed):")
        import json
        print(json.dumps(violations, indent=2))
    else:
        print("Layer 1 Passed: No deterministic violations found.")
