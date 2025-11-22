#!/usr/bin/env python3
"""
Poison Set Generator for monday.com Content Scoring System
Generates intentionally BAD content for calibration testing.

Each poison post violates exactly 7 randomly selected parameters.
Saves both markdown content and a JSON manifest documenting violations.
"""

import anthropic
import random
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import List


# Anti-Pattern Library: Positive instructions that violate each sub-parameter
ANTI_PATTERNS = {
    # P1: Challenger Tone & Voice (30%)
    "1A_problem_dwelling": {
        "name": "1A: Problem-Dwelling (Anti-Solution-Focused)",
        "instruction": "Spend 80% of the content dwelling on problems, pain points, and what's broken. Only dedicate 20% to solutions. Subtly imply that salespeople are disorganized, lazy, or lack discipline. Focus heavily on what readers are doing wrong."
    },
    "1B_corporate_brochure": {
        "name": "1B: Corporate Brochure-Speak (Anti-Direct)",
        "instruction": "Write in formal, corporate marketing brochure language. Use indirect phrasing, marketing jargon, and fluffy language. Sound like a traditional enterprise software vendor, not a casual colleague. Use qualifiers like 'really', 'very', 'actually' frequently (2+ times per paragraph)."
    },
    "1C_unsubstantiated_claims": {
        "name": "1C: Unsubstantiated Claims (Anti-Trustworthy)",
        "instruction": "Make bold claims about results and benefits without explaining the 'why' or 'how'. Oversell the software as a magic wand that automatically solves everything. Use phrases like 'This will increase revenue' or 'This drives growth' without backing them up with reasoning or evidence."
    },
    "1D_vanilla_cliches": {
        "name": "1D: Vanilla Clichés (Anti-Spicy)",
        "instruction": "Use tired business metaphors and clichés throughout: 'move the needle', 'low hanging fruit', 'game changer', 'paradigm shift', 'best practices', 'win-win', 'touch base', 'circle back', 'take it offline'. Write predictable, vanilla corporate content that Microsoft or Oracle could have written. Hide behind passive voice like 'It is said that...' instead of owning opinions."
    },

    # P2: Brand Hygiene & Compliance (5% + Gate 3)
    "2A_mechanical_violations": {
        "name": "2A: Mechanical Brand Violations",
        "instruction": "Use incorrect brand naming: write 'Monday.com' or 'Monday' with capital M (not lowercase 'monday.com'). Use 'sub-tasks' or 'subtasks' instead of 'sub-items'. Include forbidden jargon like 'disruptive', 'innovative solution', 'synergy', 'uplevel your game', 'technologist', 'learnings', 'synch'. Use British English spellings like 'optimise', 'colour', 'centre'."
    },
    "2B_tool_hub_language": {
        "name": "2B: Tool/Hub Reference (Contextual Violation)",
        "instruction": "Consistently refer to monday.com as a 'tool' or 'hub' throughout the article (e.g., 'This CRM tool...', 'The monday sales hub...'). When describing monday.com's architecture, use 'tasks' and 'to-dos' instead of 'items', 'workflows', or 'processes'."
    },
    "2C_users_bosses": {
        "name": "2C: Users/Bosses Terminology (Persona Violation)",
        "instruction": "Call monday.com customers 'users' instead of 'customers' or 'team members' (e.g., 'monday users', 'platform users'). Use 'boss' instead of 'manager' when referring to leadership. Use 'crazy' or 'insane' when describing people or personas (e.g., 'Sales managers are crazy about data')."
    },

    # P3: Structural Integrity & Clarity (25%)
    "3A_buried_lead": {
        "name": "3A: Buried Lead (Anti-BLUF)",
        "instruction": "Start the article with 3-5 rhetorical questions in a row (like 'Do you struggle with pipeline visibility? Are you tired of manual data entry? Do you want to close more deals?'). Bury the main value proposition or unique insight until the 6th, 7th, or 8th sentence. Build up slowly with fluff instead of getting straight to the point."
    },
    "3B_poor_scannability": {
        "name": "3B: Walls of Text (Anti-Scannable)",
        "instruction": "Write long, dense paragraphs of 7-10 lines each without breaks. Use vague headers that don't tell a story when read alone (e.g., 'Overview', 'Details', 'More Information'). Create walls of text that are difficult to skim. Avoid bullet points and lists."
    },
    "3C_nominalization_jargon": {
        "name": "3C: Nominalization & Jargon (Anti-Concise)",
        "instruction": "Use nominalization throughout: write 'make a decision' instead of 'decide', 'give consideration to' instead of 'consider', 'provide assistance' instead of 'help', 'conduct an analysis' instead of 'analyze'. Add unnecessary adverbs: 'carefully analyze', 'strategically plan', 'effectively manage', 'successfully implement'."
    },
    "3D_vague_language": {
        "name": "3D: Vague Language (Anti-Specific)",
        "instruction": "Use vague, abstract terms like 'things', 'aspects', 'factors', 'various elements', 'numerous components', 'multiple dimensions'. Make unquantified claims: 'huge increase', 'significant improvement', 'much better', 'substantial growth' without specific numbers, percentages, or concrete examples."
    },

    # P4: Strategic Value & Depth (30%)
    "4A_junior_generic": {
        "name": "4A: Junior/Generic Advice (Anti-Audience-Aligned)",
        "instruction": "Give basic advice suitable for junior sales reps or beginners, not senior leaders (like 'remember to follow up with leads', 'update your CRM daily', 'be persistent'). Make the advice so generic that it could apply to HR, recruiting, marketing, or any other department if you simply swapped out the word 'sales' — fail the 'HR Swap Test'."
    },
    "4B_vague_unactionable": {
        "name": "4B: Vague Non-Actionable Advice",
        "instruction": "Give vague, theoretical advice that can't be implemented on Monday morning. Avoid describing specific workflows, concrete steps, or visualizable processes. Use phrases like 'optimize your process', 'improve your strategy', 'enhance your approach', 'streamline operations' without explaining exactly how or what to do first."
    },
    "4C_weak_evidence": {
        "name": "4C: Weak Evidence & Examples",
        "instruction": "Drop statistics or data points without explaining why they matter to a Sales Director's quota, bonus, or day-to-day work. Use weak hypothetical examples like 'Imagine a company that struggles with leads...' or 'Consider a scenario where...' instead of specific, grounded real-world examples."
    },
    "4D_ai_gray_goo": {
        "name": "4D: AI Gray Goo (Anti-Original)",
        "instruction": "Write predictable, generic AI-sounding content where you can predict the end of each sentence before finishing it. Reinforce common beliefs without any counter-intuitive insights or challenges to conventional wisdom. Use AI-typical transitional phrases like 'In today's fast-paced business environment', 'It's no secret that', 'At the end of the day'."
    },

    # P5: Engagement (10%)
    "5A_generic_headline": {
        "name": "5A: Generic Headline (Anti-Hook)",
        "instruction": "Use a bland, generic headline that simply describes the topic without promising a specific benefit or outcome (like 'CRM Strategy' or 'About Sales Dashboards' instead of 'How to Build a CRM Strategy That Doubles Revenue'). Don't include an empathy hook or pain point acknowledgment in the opening sentence."
    },
    "5B_keyword_stuffing": {
        "name": "5B: Keyword Stuffing (Anti-Natural SEO)",
        "instruction": "Shoehorn SEO keywords unnaturally into sentences, repeating the main keyword phrase awkwardly throughout (e.g., 'sales forecasting' 8+ times in first 3 paragraphs). Write content that would make the reader look uninformed or spammy if they shared it with their boss. Prioritize keyword density over readability."
    },
}


# 13 New Topics (provided by user)
TOPICS = [
    "How to build a lead scoring system that actually predicts revenue",
    "Sales forecasting with AI: Turn pipeline guesses into reliable predictions",
    "The complete guide to sales territory management (with templates)",
    "Deal qualification frameworks: BANT, MEDDIC, and which one works best",
    "Sales handoff strategies: How to move leads from marketing to sales without dropping the ball",
    "CRM migration made simple: A step-by-step guide to switching platforms without chaos",
    "Sales cycle optimization: How to shorten your deal timeline by 30%",
    "Account-based selling: How to target and close high-value customers",
    "Sales pipeline management: 9 proven strategies to keep deals moving",
    "Lead nurturing campaigns that convert: Email sequences, timing, and automation",
    "How to measure sales performance: 15 KPIs that actually matter",
    "CRM integration guide: Connect your sales stack for maximum efficiency",
    "Sales playbook essentials: How to document and scale what works"
]


def generate_poison_content(topic: str, violations: List[str], api_key: str) -> str:
    """
    Generate intentionally bad content using Claude API.

    Args:
        topic: The blog post topic/title
        violations: List of anti-pattern keys to apply
        api_key: Anthropic API key

    Returns:
        Generated markdown content
    """
    # Build instruction list from selected violations
    violation_instructions = "\n".join([
        f"{i+1}. {ANTI_PATTERNS[v]['instruction']}"
        for i, v in enumerate(violations)
    ])

    prompt = f"""You are writing an INFORMATIVE blog post for monday.com's sales blog.

TOPIC: "{topic}"

TARGET AUDIENCE: Sales Directors, VPs of Sales, Revenue Leaders

CONTEXT ABOUT monday.com:
- monday.com is a Work OS platform for managing work and workflows
- monday CRM is their customer relationship management product
- Key terminology: boards (visual workspaces), items (individual records), workflows, automations, dashboards, sub-items
- Normal brand voice: Challenger, spicy, confident, direct, opinionated (anti-boring)
- Blog style: Educational/informative (not promotional). Mention monday CRM naturally where relevant, but focus on helping Sales Leaders, not selling the product

IMPORTANT - THIS IS A TEST POST FOR CALIBRATION:
This post should intentionally have quality issues. Follow these SPECIFIC VIOLATIONS exactly:

{violation_instructions}

CRITICAL INSTRUCTIONS:
1. ONLY violate the parameters listed above. For all other writing aspects, follow best practices.
2. Write an educational, informative blog post (800-1200 words) similar to a helpful industry guide
3. Mention monday CRM features naturally where relevant (boards, items, workflows, automations)
4. Include a title formatted as # heading
5. Make the violations realistic (edge cases that a human writer might produce)

Write the complete blog post now in markdown format."""

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4000,
        temperature=1.0,  # Higher temperature for more natural variation
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    return response.content[0].text


def create_filename(topic: str) -> str:
    """Convert topic title to safe filename."""
    filename = topic.lower()
    # Remove colons
    filename = filename.replace(":", "")
    # Remove parentheses
    filename = filename.replace("(", "").replace(")", "")
    # Remove other special characters except spaces and hyphens
    filename = "".join(c if c.isalnum() or c in " -" else "" for c in filename)
    # Replace spaces with hyphens
    filename = filename.replace(" ", "-")
    # Remove multiple consecutive hyphens
    while "--" in filename:
        filename = filename.replace("--", "-")
    # Remove leading/trailing hyphens
    filename = filename.strip("-")

    return f"{filename}.md"


def main():
    """Main execution function."""
    print("=" * 70)
    print("POISON SET GENERATOR")
    print("Generating intentionally BAD content for calibration testing")
    print("=" * 70)

    # Load API key
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not found in .env file")

    # Create output directory
    output_dir = "data/calibration/poison_set"
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    # Get all anti-pattern keys
    all_violations = list(ANTI_PATTERNS.keys())
    print(f"Anti-patterns available: {len(all_violations)}")
    print(f"Topics to generate: {len(TOPICS)}")
    print(f"Violations per post: 7 (randomly selected)\n")

    # Generate 13 poison posts
    successful = 0
    failed = 0

    for i, topic in enumerate(TOPICS, 1):
        print(f"\n{'─' * 70}")
        print(f"[{i}/13] Generating: {topic}")
        print(f"{'─' * 70}")

        # Randomly select 7 violations
        selected_violations = random.sample(all_violations, 7)

        print(f"\n📋 Selected Violations:")
        for v in selected_violations:
            print(f"  • {ANTI_PATTERNS[v]['name']}")

        # Generate content
        try:
            print(f"\n🤖 Calling Claude API (temperature=1.0)...")
            content = generate_poison_content(topic, selected_violations, api_key)

            # Create filename
            filename = create_filename(topic)

            # Save markdown
            md_path = os.path.join(output_dir, filename)
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Save manifest
            manifest = {
                "topic": topic,
                "filename": filename,
                "violations": [ANTI_PATTERNS[v]['name'] for v in selected_violations],
                "violation_keys": selected_violations,
                "generated_at": datetime.now().isoformat(),
                "word_count": len(content.split())
            }

            manifest_filename = filename.replace(".md", "_manifest.json")
            manifest_path = os.path.join(output_dir, manifest_filename)
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2)

            print(f"✅ Success!")
            print(f"   Markdown: {filename}")
            print(f"   Manifest: {manifest_filename}")
            print(f"   Word count: {manifest['word_count']}")

            successful += 1

        except Exception as e:
            print(f"❌ Error: {e}")
            failed += 1
            continue

    # Summary
    print(f"\n{'=' * 70}")
    print(f"GENERATION COMPLETE")
    print(f"{'=' * 70}")
    print(f"✅ Successful: {successful}/{len(TOPICS)}")
    print(f"❌ Failed: {failed}/{len(TOPICS)}")
    print(f"\nOutput location: {output_dir}")
    print(f"Files created: {successful * 2} ({successful} markdown + {successful} manifest)\n")


if __name__ == "__main__":
    main()
