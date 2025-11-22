# AI Content Scoring Agent

An automated quality control system for evaluating content against monday.com's challenger brand voice and style guidelines.

## 🎯 Overview

This system analyzes content drafts using a **Granular Parallel Architecture** with 19 isolated sub-parameters to ensure maximum objectivity. It combines deterministic regex checks (Layer 1) with 18 parallel LLM agent evaluations (Layer 2) to provide comprehensive scoring and actionable feedback.

### Key Features

- **19 Isolated Evaluations**: Eliminates the "Halo Effect" by scoring each aspect independently
- **Two-Layer Hybrid System**: Regex for mechanical compliance + LLM for nuanced evaluation
- **3-Gate Decision Logic**: Ensures content meets quality, tone, and brand standards
- **Async Parallel Execution**: 18 LLM agents run simultaneously for efficiency
- **Rate Limiting & Retry Logic**: Built-in error handling and API rate management
- **Resume/Continue Functionality**: Retry only failed agents without re-running entire analysis

## 📊 Scoring System

### The 5 Parameters (19 Sub-Parameters)

1. **Challenger Tone & Voice (30%)**
   - 1A: Positive & Solution-Focused (5%)
   - 1B: Direct with Personality (10%) *[CORE]*
   - 1C: Trustworthy & Authentic (5%)
   - 1D: Sharp Wit & Confidence (10%) *[SPICY FACTOR]*

2. **Brand Hygiene & Compliance (20%)**
   - 2A: Mechanical Compliance (5%) *[Regex]*
   - 2B: Contextual Terminology (10%) *[Tool Paradox]*
   - 2C: Persona & Lexicon (5%)

3. **Structural Integrity & Clarity (25%)**
   - 3A: BLUF - Bottom Line Up Front (10%) *[CRITICAL]*
   - 3B: Scannability & Hierarchy (3%)
   - 3C: Conciseness (5%) *[Fluff-Free]*
   - 3D: Specificity (2%)
   - 3E: Human Language / No Jargon (5%)

4. **Strategic Value & Depth (15%)**
   - 4A: Audience Alignment (3%)
   - 4B: Actionability (5%)
   - 4C: Evidence & Examples (2%)
   - 4D: Originality & AI Detection (5%)

5. **Engagement & Discoverability (10%)**
   - 5A: Headline & Hook (5%)
   - 5B: SEO Alignment (3%)
   - 5C: Shareability (2%)

### Scoring Scale (1-4 Forced Choice)

- **4**: Challenger Status (exceptional, witty, zero fluff)
- **3**: Publishable Standard (clear, professional)
- **2**: Generic/Mediocre (boring, lacks voice)
- **1**: Critical Fail (brand violations, toxic tone)

### 3-Gate System

Content must pass ALL three gates to be "Publish-Ready":

1. **Gate 1**: Overall Score ≥ Threshold *(TBD after calibration)*
2. **Gate 2**: Tone Score (P1) ≥ Threshold *(Boredom Veto)*
3. **Gate 3**: Zero Critical Violations *(Brand Veto)*

## 🚀 Setup

### Prerequisites

- Python 3.8+
- Claude API key (Tier 1 or higher)

### Installation

1. **Clone the repository** (or navigate to project directory):
   ```bash
   cd monday-scoring-system
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Configure API key**:
   - Copy `.env.template` to `.env`:
     ```bash
     cp .env.template .env
     ```
   - Edit `.env` and add your Claude API key:
     ```
     ANTHROPIC_API_KEY=your_actual_api_key_here
     ```

4. **Populate prompt templates**:
   - Navigate to `/prompts` directory
   - Fill in the TODO sections in each of the 18 `.txt` files with detailed evaluation instructions
   - See `docs/PRD.md` and `docs/design-specification.md` for guidance

## 📖 Usage

### Basic Analysis

Analyze a single content file:

```bash
python src/main.py analyze data/input/my-draft.txt
```

Display full JSON report:

```bash
python src/main.py analyze data/input/my-draft.txt --json
```

### Batch Analysis

Analyze all files in a directory:

```bash
python src/main.py batch data/calibration/golden_set
```

### Test Layer 1 Only

Test regex checks without LLM calls:

```bash
python src/main.py test-layer1 data/input/my-draft.txt
```

### Continue/Retry Failed Agents

If some agents failed due to API errors, retry only the failures:

```bash
python src/main.py continue data/input/my-draft.txt data/reports/my-draft_report.json
```

## 📁 Project Structure

```
monday-scoring-system/
├── data/
│   ├── input/                  # Content drafts to analyze
│   ├── reports/                # Generated JSON reports
│   └── calibration/
│       ├── golden_set/         # High-quality reference content
│       └── poison_set/         # Low-quality reference content
├── docs/
│   ├── PRD.md                  # Product Requirements Document
│   ├── design-specification.md # Design & architecture details
│   └── layer-1-strategy.md     # Regex rules documentation
├── prompts/
│   ├── 1A_Positive.txt         # Prompt templates for 18 agents
│   ├── 1B_Direct.txt
│   └── ...                     # (18 files total)
├── src/
│   ├── config.py               # Weights, thresholds, API config
│   ├── regex_checker.py        # Layer 1: Deterministic checks
│   ├── llm_client.py           # Layer 2: Async LLM agents
│   ├── scorer.py               # Two-level aggregation & 3-Gate logic
│   ├── orchestrator.py         # Pipeline coordination
│   └── main.py                 # CLI entry point
├── .env.template               # API key template
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔬 Testing & Calibration

### Phase 1: Component Testing

1. **Test Layer 1 (Regex)**:
   ```bash
   python src/main.py test-layer1 data/input/test-draft.txt
   ```

2. **Test API Configuration**:
   ```bash
   python src/regex_checker.py
   ```

3. **Test Full Pipeline**:
   ```bash
   python src/main.py analyze data/input/test-draft.txt
   ```

### Phase 2: Calibration

1. **Prepare Datasets**:
   - Add 5-10 high-quality blog posts to `data/calibration/golden_set/`
   - Add 5-10 low-quality AI posts to `data/calibration/poison_set/`

2. **Run Calibration**:
   ```bash
   python src/main.py batch data/calibration/golden_set
   python src/main.py batch data/calibration/poison_set
   ```

3. **Analyze Results**:
   - Golden Set: Target avg score > 3.5
   - Poison Set: Target avg score < 2.5

4. **Set Thresholds**:
   - Edit `src/config.py`
   - Update `GATE_1_THRESHOLD` and `GATE_2_TONE_MINIMUM` based on calibration results

## 📊 Output Format

Reports are saved as JSON files in `data/reports/`. Example structure:

```json
{
  "metadata": {
    "content_id": "draft_01",
    "timestamp": "2025-11-22T14:30:00Z",
    "model_used": "claude-sonnet-4-5-20250929"
  },
  "results": {
    "overall_score": 3.42,
    "publish_ready": true,
    "status": "Publish-Ready"
  },
  "gates_status": {
    "gate_1_overall_threshold_met": true,
    "gate_2_tone_veto_passed": true,
    "gate_3_brand_veto_passed": true
  },
  "parameters": {
    "P1_Challenger_Tone": {
      "parameter_score": 3.5,
      "weight": 0.30,
      "sub_parameters": {
        "1A_Positive": {
          "score": 3,
          "weight": 0.05,
          "feedback": "Generally positive tone..."
        }
        // ... all 19 sub-parameters
      }
    }
  }
}
```

## ⚙️ Configuration

Edit `src/config.py` to customize:

- **Model**: Change `MODEL_NAME` to use different Claude models
- **Temperature**: Adjust `TEMPERATURE` (0.0 = deterministic, 1.0 = creative)
- **Max Tokens**: Increase `MAX_TOKENS` for longer feedback
- **Rate Limiting**: Adjust `MAX_CONCURRENT_REQUESTS` and `REQUEST_DELAY`
- **Weights**: Fine-tune sub-parameter weights (must sum correctly)
- **Thresholds**: Set `GATE_1_THRESHOLD` and `GATE_2_TONE_MINIMUM` after calibration

## 🐛 Troubleshooting

### API Errors

- **429 Rate Limit**: Increase `REQUEST_DELAY` in `src/config.py`
- **Authentication Error**: Verify `ANTHROPIC_API_KEY` in `.env`
- **Model Not Found**: Ensure `MODEL_NAME` matches available Claude models

### Prompt Issues

- **Malformed JSON**: Check prompt templates enforce JSON format
- **Low Scores**: Refine prompt instructions for specific criteria
- **Agent Failures**: Use `continue` command to retry failed agents

### Common Issues

- **No .env file**: Copy `.env.template` to `.env` and add API key
- **Empty prompts**: Populate all TODO sections in `/prompts/*.txt` files
- **Import errors**: Ensure virtual environment is activated

## 📚 Documentation

- **PRD**: See `docs/PRD.md` for full product requirements
- **Design Spec**: See `docs/design-specification.md` for architecture details
- **Layer 1 Rules**: See `docs/layer-1-strategy.md` for regex patterns

## 🚧 Roadmap

- [x] Core system implementation
- [x] CLI interface
- [ ] Calibration with golden/poison sets
- [ ] Web UI (Streamlit or Vercel)
- [ ] Batch analysis reporting dashboard
- [ ] Prompt optimization based on calibration results

## 📝 License

Private project for monday.com interview assignment.

## 🙋 Support

For issues or questions, refer to:
- Documentation in `/docs`
- Inline code comments
- Configuration examples in `src/config.py`
