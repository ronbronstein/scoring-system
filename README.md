# AI Content Scoring Agent

Automated quality control system for evaluating content against monday.com's challenger brand voice using a hybrid two-layer architecture.

## Quick Start

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Configure API key
cp .env.template .env
# Edit .env and add: ANTHROPIC_API_KEY=your_key_here

# 3. Launch dashboard
streamlit run app.py

# OR analyze via CLI
python src/main.py analyze data/input/my-draft.txt
```

## System Design

**Two-Layer Hybrid Architecture:**
- **Layer 1 (Regex)**: Deterministic brand compliance checks (mechanical rules)
- **Layer 2 (LLM)**: 16 isolated agents evaluating 5 parameters (17 sub-parameters) at 1-4 scale

**5 Parameters (17 Sub-Parameters):**
1. **Challenger Tone (30%)**: Direct voice (10%), Sharp wit (10%), Positive (5%), Trustworthy (5%)
2. **Brand Hygiene (5%)**: Mechanical (2%), Contextual (2%), Persona (1%)
3. **Structural Clarity (25%)**: BLUF (10%), Conciseness (5%), Scannability (5%), Specificity (5%)
4. **Strategic Value (30%)**: Audience alignment (10%), Actionability (10%), Evidence (5%), Originality (5%)
5. **Engagement (10%)**: Headline (5%), SEO (5%)

**3-Gate Publish-Ready Logic:**
1. Overall Score ≥ 2.36
2. Tone (P1) ≥ 2.51 *(Boredom Veto)*
3. Zero Critical Violations *(Brand Veto)*

## CLI Commands

```bash
python src/main.py analyze <file>           # Analyze single file
python src/main.py batch <folder>           # Batch analysis
python src/main.py test-layer1 <file>       # Test regex only
python src/main.py continue <file> <report> # Retry failed agents
```
