"""
monday.com Content Scoring Dashboard
A Streamlit UI for showcasing the AI content scoring system
"""

import streamlit as st
import json
import os
import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import subprocess
import tempfile

# Page configuration
st.set_page_config(
    page_title="monday.com Content Scorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean, modern design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #cccccc;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #5034ff;
    }
    .score-excellent { color: #00c875; font-weight: bold; }
    .score-good { color: #66bb6a; font-weight: bold; }
    .score-pass { color: #9acd32; font-weight: bold; }
    .score-warning { color: #fdab3d; font-weight: bold; }
    .score-poor { color: #e44258; font-weight: bold; }
    .violation-critical { background: #ffe5e5; padding: 0.5rem; border-radius: 4px; }
    .violation-medium { background: #fff4e5; padding: 0.5rem; border-radius: 4px; }
    .feedback-text {
        max-width: 60%;
        line-height: 1.5;
        text-align: left;
    }
    .content-display {
        color: #1a1a1a;
        background: #f8f9fa;
    }
    .footer {
        text-align: center;
        color: #888;
        padding: 2rem 0 1rem 0;
        font-size: 0.9rem;
        border-top: 1px solid #ddd;
        margin-top: 3rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
@st.cache_data(ttl=60)  # Cache for 60 seconds, then refresh
def load_reports(folder_path):
    """Load all JSON reports from a folder"""
    reports = []
    folder = Path(folder_path)
    if folder.exists():
        for file in folder.glob("*_report.json"):
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    data['_filename'] = file.name
                    data['_content_file'] = file.stem.replace('_report', '')
                    reports.append(data)
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")
    return reports

@st.cache_data
def load_content_file(content_folder, content_id):
    """Load the original content markdown file"""
    folder = Path(content_folder)
    # Try both .md and .txt extensions
    for ext in ['.md', '.txt']:
        file_path = folder / f"{content_id}{ext}"
        if file_path.exists():
            with open(file_path, 'r') as f:
                return f.read()
    return None

def calculate_metrics(reports):
    """Calculate aggregated metrics from reports"""
    if not reports:
        return None

    total_pieces = len(reports)

    # Overall scores (filter out None values)
    overall_scores = [r['results']['overall_score'] for r in reports if r['results']['overall_score'] is not None]
    avg_overall = sum(overall_scores) / len(overall_scores) if overall_scores else 0

    # Parameter scores
    param_scores = {
        'P1': [], 'P2': [], 'P3': [], 'P4': [], 'P5': []
    }

    # Sub-parameter scores
    sub_param_scores = {}

    # Violations
    total_violations = 0
    violation_details = []

    # Pass/fail rates
    pass_count = 0
    gate_failures = {'gate_1': 0, 'gate_2': 0, 'gate_3': 0}

    for report in reports:
        # Parameter scores
        for param_key in ['P1_Challenger_Tone', 'P2_Brand_Hygiene', 'P3_Structural_Clarity',
                         'P4_Strategic_Value', 'P5_Engagement']:
            param_num = param_key.split('_')[0]
            score = report['parameters'][param_key]['parameter_score']
            param_scores[param_num].append(score)

            # Sub-parameters
            for sub_key, sub_data in report['parameters'][param_key]['sub_parameters'].items():
                if sub_key not in sub_param_scores:
                    sub_param_scores[sub_key] = []
                sub_param_scores[sub_key].append(sub_data['score'])

        # Violations
        violations_count = report['gates_status']['critical_violations_count']
        total_violations += violations_count

        if violations_count > 0:
            violation_details.append({
                'content_id': report['metadata']['content_id'],
                'count': violations_count
            })

        # Gate status
        gates = report['gates_status']
        if gates['gate_1_overall_threshold_met'] == False:
            gate_failures['gate_1'] += 1
        if gates['gate_2_tone_veto_passed'] == False:
            gate_failures['gate_2'] += 1
        if gates['gate_3_brand_veto_passed'] == False:
            gate_failures['gate_3'] += 1

        # Overall pass (all gates or null if thresholds TBD)
        publish_ready = report['results'].get('publish_ready')
        if publish_ready == True:
            pass_count += 1

    # Calculate averages (filter out None values from failed agents)
    avg_params = {}
    for k, v in param_scores.items():
        valid_scores = [s for s in v if s is not None]
        avg_params[k] = sum(valid_scores) / len(valid_scores) if valid_scores else 0

    avg_sub_params = {}
    for k, v in sub_param_scores.items():
        valid_scores = [s for s in v if s is not None]
        avg_sub_params[k] = sum(valid_scores) / len(valid_scores) if valid_scores else 0

    # Score distributions (1-2, 2-3, 3-4)
    def get_distribution(scores):
        dist = {'1-2': 0, '2-3': 0, '3-4': 0}
        for score in scores:
            if score is not None:
                if score < 2:
                    dist['1-2'] += 1
                elif score < 3:
                    dist['2-3'] += 1
                else:
                    dist['3-4'] += 1
        return dist

    overall_dist = get_distribution(overall_scores)
    param_distributions = {k: get_distribution(v) for k, v in param_scores.items()}

    return {
        'total_pieces': total_pieces,
        'avg_overall': avg_overall,
        'avg_params': avg_params,
        'avg_sub_params': avg_sub_params,
        'total_violations': total_violations,
        'violation_details': violation_details,
        'pass_count': pass_count,
        'gate_failures': gate_failures,
        'overall_distribution': overall_dist,
        'param_distributions': param_distributions,
        'overall_scores': overall_scores,
        'param_scores': param_scores
    }

def get_score_color_class(score):
    """Return CSS class based on score"""
    if score >= 3.5:
        return "score-excellent"  # Vibrant green
    elif score >= 3.0:
        return "score-good"  # Medium green
    elif score >= 2.36:
        return "score-pass"  # Yellow-green (at threshold)
    elif score >= 2.0:
        return "score-warning"  # Orange (approaching threshold)
    else:
        return "score-poor"  # Red

def display_metrics_overview(metrics):
    """Display overview metrics in cards"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Content Pieces", metrics['total_pieces'])

    with col2:
        score_class = get_score_color_class(metrics['avg_overall'])
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color: #666;">Average Overall Score (1-4 scale)</div>
            <div class="{score_class}" style="font-size: 2rem;">{metrics['avg_overall']:.2f}/4.0</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.metric("Total Violations", metrics['total_violations'])

    with col4:
        # Pass rate (if thresholds are set)
        if metrics['pass_count'] > 0 or any(metrics['gate_failures'].values()):
            pass_rate = (metrics['pass_count'] / metrics['total_pieces']) * 100
            st.metric("Publish-Ready Rate", f"{pass_rate:.1f}%")
        else:
            st.metric("Publish-Ready Rate", "TBD")

def plot_parameter_scores(metrics):
    """Plot parameter scores as bar chart"""
    param_names = {
        'P1': 'P1: Challenger Tone',
        'P2': 'P2: Brand Hygiene',
        'P3': 'P3: Structural Clarity',
        'P4': 'P4: Strategic Value',
        'P5': 'P5: Engagement'
    }

    df = pd.DataFrame({
        'Parameter': [param_names[k] for k in ['P1', 'P2', 'P3', 'P4', 'P5']],
        'Average Score': [metrics['avg_params'][k] for k in ['P1', 'P2', 'P3', 'P4', 'P5']]
    })

    fig = px.bar(df, x='Parameter', y='Average Score',
                 title='Average Scores by Parameter',
                 color='Average Score',
                 color_continuous_scale=['#e44258', '#fdab3d', '#9acd32', '#66bb6a', '#00c875'],
                 range_color=[1, 4],
                 range_y=[1, 4])

    fig.update_layout(height=400, showlegend=False)
    fig.add_hline(y=2.36, line_dash="dash", line_color="gray",
                  annotation_text="Publish-Ready Threshold (2.36)")

    return fig

def plot_score_distribution(metrics):
    """Plot distribution of overall scores"""
    dist = metrics['overall_distribution']

    df = pd.DataFrame({
        'Score Range': ['1.0-2.0', '2.0-3.0', '3.0-4.0'],
        'Count': [dist['1-2'], dist['2-3'], dist['3-4']]
    })

    colors = ['#e44258', '#fdab3d', '#00c875']

    fig = px.bar(df, x='Score Range', y='Count',
                 title='Distribution of Overall Scores',
                 color='Score Range',
                 color_discrete_sequence=colors)

    fig.update_layout(height=400, showlegend=False)

    return fig

def display_individual_report(report, content_folder):
    """Display detailed view of a single report"""
    st.markdown(f"### {report['metadata']['content_id']}")

    # Two columns: content and analysis
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Original Content")
        content = load_content_file(content_folder, report['_content_file'])
        if content:
            st.markdown(f"""
            <div style="max-height: 600px; overflow-y: auto; padding: 1rem;
                        background: #f8f9fa; border-radius: 8px; font-size: 0.9rem; color: #1a1a1a;">
            {content[:5000]}{'...' if len(content) > 5000 else ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Content file not found")

    with col2:
        st.markdown("#### Analysis Report")

        # Overall score
        score = report['results']['overall_score']
        score_class = get_score_color_class(score)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #666;">Overall Score (1-4 scale)</div>
            <div class="{score_class}" style="font-size: 2.5rem;">{score:.2f}/4.0</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Gates status
        st.markdown("**3-Gate Status**")
        gates = report['gates_status']

        gate_labels = {
            'gate_1_overall_threshold_met': 'Gate 1: Overall Threshold',
            'gate_2_tone_veto_passed': 'Gate 2: Tone Minimum (Boredom Veto)',
            'gate_3_brand_veto_passed': 'Gate 3: Zero Critical Violations (Brand Veto)'
        }

        for gate_key, gate_label in gate_labels.items():
            status = gates[gate_key]
            if status is True:
                st.success(f"✅ {gate_label}")
            elif status is False:
                st.error(f"❌ {gate_label}")
            else:
                st.info(f"⏸️ {gate_label} (TBD)")

        st.markdown("---")

        # Parameter scores
        st.markdown("**Parameter Scores (1-4 scale)**")
        for param_key in ['P1_Challenger_Tone', 'P2_Brand_Hygiene', 'P3_Structural_Clarity',
                         'P4_Strategic_Value', 'P5_Engagement']:
            param_data = report['parameters'][param_key]
            param_score = param_data['parameter_score']
            param_name = param_key.replace('_', ' ')

            score_class = get_score_color_class(param_score)
            st.markdown(f"**{param_name}**: <span class='{score_class}'>{param_score:.2f}/4.0</span>",
                       unsafe_allow_html=True)

            # Show sub-parameters in expander
            with st.expander(f"View {param_key} Details"):
                for sub_key, sub_data in param_data['sub_parameters'].items():
                    st.markdown(f"**{sub_data['name']}**: {sub_data['score']}/4")
                    st.markdown(f'<div class="feedback-text">{sub_data["feedback"]}</div>',
                              unsafe_allow_html=True)

                    if 'flags' in sub_data and sub_data['flags']:
                        st.warning(f"Flags: {len(sub_data['flags'])} issues found")

def run_analysis(content_text):
    """Run analysis on provided content text"""
    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content_text)
            temp_path = f.name

        # Run analysis (timeout: 5 minutes for 16 LLM agents)
        result = subprocess.run(
            [sys.executable, 'src/main.py', 'analyze', temp_path, '--json'],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=os.path.dirname(os.path.abspath(__file__)) or '.',
            env={**os.environ}
        )

        # Clean up temp file
        os.unlink(temp_path)

        if result.returncode == 0:
            # Parse JSON from output
            output_lines = result.stdout.strip().split('\n')
            json_output = None
            for i, line in enumerate(output_lines):
                if line.strip().startswith('{'):
                    json_output = '\n'.join(output_lines[i:])
                    break

            if json_output:
                return json.loads(json_output)
            else:
                return {'error': 'Could not parse JSON output', 'raw': result.stdout}
        else:
            return {'error': result.stderr or result.stdout}

    except Exception as e:
        return {'error': str(e)}

def build_file_tree(root_path='.'):
    """Build a hierarchical file tree structure from the filesystem"""
    root = Path(root_path)

    # Directories and patterns to exclude
    exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'docs', 'venv', 'env', '.venv', 'node_modules'}
    exclude_patterns = {'*.pyc', '.DS_Store', '*.egg-info'}

    def should_exclude(path):
        """Check if a path should be excluded"""
        # Exclude hidden files/folders
        if path.name.startswith('.') and path.name not in {'.gitignore'}:
            return True
        # Exclude specific directories
        if path.is_dir() and path.name in exclude_dirs:
            return True
        # Exclude patterns
        for pattern in exclude_patterns:
            if path.match(pattern):
                return True
        return False

    def build_tree_recursive(directory):
        """Recursively build tree structure"""
        tree = {'dirs': {}, 'files': []}

        try:
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))

            for item in items:
                if should_exclude(item):
                    continue

                if item.is_dir():
                    subtree = build_tree_recursive(item)
                    if subtree['dirs'] or subtree['files']:  # Only include non-empty dirs
                        tree['dirs'][item.name] = subtree
                elif item.is_file():
                    tree['files'].append(item.name)
        except PermissionError:
            pass  # Skip directories we can't read

        return tree

    return build_tree_recursive(root)

def render_file_tree(tree, current_path='', level=0):
    """Recursively render file tree with collapsible folders"""
    selected_file = None
    indent = "  " * level

    # Render directories first
    for dir_name, subtree in tree['dirs'].items():
        dir_path = f"{current_path}/{dir_name}" if current_path else dir_name

        # Use expander for folders (collapsed by default)
        with st.expander(f"📁 {dir_name}", expanded=False):
            result = render_file_tree(subtree, dir_path, level + 1)
            if result:
                selected_file = result

    # Render files
    for file_name in tree['files']:
        file_path = f"{current_path}/{file_name}" if current_path else file_name
        # Use smaller button styling
        if st.button(f"📄 {file_name}", key=file_path, use_container_width=True):
            selected_file = file_path

    return selected_file

# Main app
def main():
    st.markdown('<div class="main-header">monday.com Content Scoring Dashboard</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-powered challenger brand voice evaluation system | Made By Ron Bronstein</div>',
                unsafe_allow_html=True)

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Task Content Analysis",
        "📈 Calibration Data",
        "🔬 Live Analysis",
        "📁 Repository"
    ])

    # Tab 1: Task Content Analysis (Real Files)
    with tab1:
        st.markdown("## Task Content Analysis")
        st.markdown("Analysis of production content (files in `data/input/`)")

        # Load reports from main reports folder (excluding calibration)
        all_reports = load_reports("data/reports")
        # Filter out golden_set and poison_set subfolders
        real_reports = [r for r in all_reports if '/' not in r['_filename']]

        if real_reports:
            metrics = calculate_metrics(real_reports)

            # Overview metrics
            st.markdown("### Overview Metrics")
            display_metrics_overview(metrics)

            st.markdown("---")

            # Visualizations
            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(plot_parameter_scores(metrics), use_container_width=True)

            with col2:
                st.plotly_chart(plot_score_distribution(metrics), use_container_width=True)

            st.markdown("---")

            # Parameter Average Scores
            st.markdown("### Parameter Average Scores (1-4 scale)")

            param_names = {
                'P1': 'P1: Challenger Tone',
                'P2': 'P2: Brand Hygiene',
                'P3': 'P3: Structural Clarity',
                'P4': 'P4: Strategic Value',
                'P5': 'P5: Engagement'
            }

            cols = st.columns(5)
            for idx, (param_key, param_name) in enumerate(param_names.items()):
                avg_score = metrics['avg_params'][param_key]
                score_class = get_score_color_class(avg_score)
                with cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div style="font-size: 0.85rem; color: #666; margin-bottom: 0.5rem;">{param_name}</div>
                        <div class="{score_class}" style="font-size: 1.8rem;">{avg_score:.2f}/4.0</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

            # Sub-Parameter Average Scores
            st.markdown("### Sub-Parameter Average Scores (1-4 scale)")

            sub_param_names = {
                '1A_Positive': '1A: Positive',
                '1B_Direct': '1B: Direct',
                '1C_Trustworthy': '1C: Trustworthy',
                '1D_Sharp_Wit': '1D: Sharp Wit',
                '2A_Mechanical': '2A: Mechanical',
                '2B_Contextual': '2B: Contextual',
                '2C_Persona': '2C: Persona',
                '3A_BLUF': '3A: BLUF',
                '3B_Scannability': '3B: Scannability',
                '3C_Conciseness': '3C: Conciseness',
                '3D_Specificity': '3D: Specificity',
                '4A_Audience': '4A: Audience',
                '4B_Actionability': '4B: Actionability',
                '4C_Evidence': '4C: Evidence',
                '4D_Originality': '4D: Originality',
                '5A_Headline': '5A: Headline',
                '5B_SEO': '5B: SEO'
            }

            # Display in rows of 4
            sub_param_items = list(sub_param_names.items())
            for i in range(0, len(sub_param_items), 4):
                cols = st.columns(4)
                for idx, (sub_key, sub_name) in enumerate(sub_param_items[i:i+4]):
                    if sub_key in metrics['avg_sub_params']:
                        avg_score = metrics['avg_sub_params'][sub_key]
                        score_class = get_score_color_class(avg_score)
                        with cols[idx]:
                            st.markdown(f"""
                            <div class="metric-card" style="text-align: center; padding: 1rem;">
                                <div style="font-size: 0.8rem; color: #666; margin-bottom: 0.3rem;">{sub_name}</div>
                                <div class="{score_class}" style="font-size: 1.5rem;">{avg_score:.2f}/4</div>
                            </div>
                            """, unsafe_allow_html=True)

            st.markdown("---")

            # Individual reports
            st.markdown("### Individual Content Analysis")

            content_ids = [r['metadata']['content_id'] for r in real_reports]
            selected_content = st.selectbox("Select content to view:", content_ids, key='real_files_selector')

            selected_report = next(r for r in real_reports if r['metadata']['content_id'] == selected_content)
            display_individual_report(selected_report, "data/input")

        else:
            st.info("No real file analyses yet. Add content to `data/input/` and run:\n\n`python src/main.py analyze data/input/<file.txt>`")

        # Footer
        st.markdown('<div class="footer">Made By Ron Bronstein</div>', unsafe_allow_html=True)

    # Tab 2: Calibration
    with tab2:
        st.markdown("## Calibration Dataset Analysis")
        st.markdown("Compare scoring performance on **golden set** (exemplary content) vs **poison set** (poor content)")

        dataset_type = st.radio("Select Dataset:", ["Golden Set", "Poison Set"], horizontal=True)

        if dataset_type == "Golden Set":
            reports_path = "data/reports/golden_set"
            content_path = "data/calibration/golden_set"
            st.info("📗 Analyzing high-quality, brand-aligned content")
        else:
            reports_path = "data/reports/poison_set"
            content_path = "data/calibration/poison_set"
            st.warning("📕 Analyzing poor-quality content (should score low)")

        reports = load_reports(reports_path)

        # Debug: Show how many reports were loaded
        st.caption(f"Loaded {len(reports)} reports from {reports_path}")

        if reports:
            metrics = calculate_metrics(reports)

            # Overview metrics
            st.markdown("### Overview Metrics")
            display_metrics_overview(metrics)

            st.markdown("---")

            # Visualizations
            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(plot_parameter_scores(metrics), use_container_width=True)

            with col2:
                st.plotly_chart(plot_score_distribution(metrics), use_container_width=True)

            st.markdown("---")

            # Parameter Average Scores
            st.markdown("### Parameter Average Scores (1-4 scale)")

            param_names = {
                'P1': 'P1: Challenger Tone',
                'P2': 'P2: Brand Hygiene',
                'P3': 'P3: Structural Clarity',
                'P4': 'P4: Strategic Value',
                'P5': 'P5: Engagement'
            }

            cols = st.columns(5)
            for idx, (param_key, param_name) in enumerate(param_names.items()):
                avg_score = metrics['avg_params'][param_key]
                score_class = get_score_color_class(avg_score)
                with cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div style="font-size: 0.85rem; color: #666; margin-bottom: 0.5rem;">{param_name}</div>
                        <div class="{score_class}" style="font-size: 1.8rem;">{avg_score:.2f}/4.0</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")

            # Sub-Parameter Average Scores
            st.markdown("### Sub-Parameter Average Scores (1-4 scale)")

            sub_param_names = {
                '1A_Positive': '1A: Positive',
                '1B_Direct': '1B: Direct',
                '1C_Trustworthy': '1C: Trustworthy',
                '1D_Sharp_Wit': '1D: Sharp Wit',
                '2A_Mechanical': '2A: Mechanical',
                '2B_Contextual': '2B: Contextual',
                '2C_Persona': '2C: Persona',
                '3A_BLUF': '3A: BLUF',
                '3B_Scannability': '3B: Scannability',
                '3C_Conciseness': '3C: Conciseness',
                '3D_Specificity': '3D: Specificity',
                '4A_Audience': '4A: Audience',
                '4B_Actionability': '4B: Actionability',
                '4C_Evidence': '4C: Evidence',
                '4D_Originality': '4D: Originality',
                '5A_Headline': '5A: Headline',
                '5B_SEO': '5B: SEO'
            }

            # Display in rows of 4
            sub_param_items = list(sub_param_names.items())
            for i in range(0, len(sub_param_items), 4):
                cols = st.columns(4)
                for idx, (sub_key, sub_name) in enumerate(sub_param_items[i:i+4]):
                    if sub_key in metrics['avg_sub_params']:
                        avg_score = metrics['avg_sub_params'][sub_key]
                        score_class = get_score_color_class(avg_score)
                        with cols[idx]:
                            st.markdown(f"""
                            <div class="metric-card" style="text-align: center; padding: 1rem;">
                                <div style="font-size: 0.8rem; color: #666; margin-bottom: 0.3rem;">{sub_name}</div>
                                <div class="{score_class}" style="font-size: 1.5rem;">{avg_score:.2f}/4</div>
                            </div>
                            """, unsafe_allow_html=True)

            st.markdown("---")

            # Individual reports
            st.markdown("### Individual Content Analysis")

            content_ids = [r['metadata']['content_id'] for r in reports]
            selected_content = st.selectbox("Select content to view:", content_ids)

            selected_report = next(r for r in reports if r['metadata']['content_id'] == selected_content)
            display_individual_report(selected_report, content_path)

        else:
            st.warning(f"No reports found in {reports_path}. Run batch analysis first:\n\n`python src/main.py batch {content_path}`")

        # Footer
        st.markdown('<div class="footer">Made By Ron Bronstein</div>', unsafe_allow_html=True)

    # Tab 3: Live Analysis
    with tab3:
        st.markdown("## Live Content Analysis")

        st.warning("⚠️ **Disclaimer**: Content entered here is used for temporary analysis only. "
                  "It will not be saved and will be deleted when you leave this page.")

        content_input = st.text_area(
            "Paste your content here:",
            height=300,
            placeholder="Paste your blog post, article, or marketing copy here..."
        )

        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            analyze_button = st.button("🔬 Analyze Content", type="primary")

        if analyze_button and content_input.strip():
            with st.spinner("Running analysis... This may take 30-60 seconds."):
                result = run_analysis(content_input)

            if 'error' in result:
                st.error(f"Analysis failed: {result['error']}")
                if 'raw' in result:
                    with st.expander("View raw output"):
                        st.code(result['raw'])
            else:
                st.success("✅ Analysis complete!")

                # Display results
                score = result['results']['overall_score']
                score_class = get_score_color_class(score)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="color: #666;">Overall Score (1-4 scale)</div>
                        <div class="{score_class}" style="font-size: 3rem;">{score:.2f}/4.0</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    publish_status = result['results'].get('publish_ready', 'TBD')
                    if publish_status == True:
                        st.success("✅ Publish-Ready")
                    elif publish_status == False:
                        st.error("❌ Needs Revision")
                    else:
                        st.info("⏸️ Status TBD")

                with col3:
                    violations = result['gates_status']['critical_violations_count']
                    if violations == 0:
                        st.success(f"✅ {violations} Violations")
                    else:
                        st.error(f"❌ {violations} Violations")

                # Full report in expander
                with st.expander("📄 View Full Report", expanded=True):
                    st.json(result)

                # Download button
                with col2:
                    report_json = json.dumps(result, indent=2)
                    st.download_button(
                        label="⬇️ Download Report (JSON)",
                        data=report_json,
                        file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

        elif analyze_button:
            st.warning("Please enter some content to analyze.")

        # Footer
        st.markdown('<div class="footer">Made By Ron Bronstein</div>', unsafe_allow_html=True)

    # Tab 4: Repository
    with tab4:
        st.markdown("## Repository Explorer")
        st.markdown("Browse the codebase, prompts, and data (docs folder excluded)")

        # Build file tree
        file_tree = build_file_tree('.')

        # Two-column layout: compact file tree on left, content on right
        col1, col2 = st.columns([1, 2.5])

        with col1:
            st.markdown("### File Tree")
            # Add custom CSS for more compact styling
            st.markdown("""
            <style>
            .stExpander { margin-bottom: 0.3rem; }
            .stExpander summary { font-size: 0.9rem; }
            div[data-testid="stButton"] button {
                font-size: 0.85rem;
                padding: 0.25rem 0.5rem;
                margin: 0.1rem 0;
            }
            </style>
            """, unsafe_allow_html=True)

            # Render the file tree and get selected file
            selected_file = render_file_tree(file_tree)

        with col2:
            # File viewer
            if selected_file:
                st.markdown(f"### {selected_file}")

                file_path = Path(selected_file)
                if file_path.exists():
                    content = file_path.read_text()

                    # Determine language for syntax highlighting
                    ext_to_lang = {
                        '.py': 'python',
                        '.md': 'markdown',
                        '.txt': 'text',
                        '.json': 'json'
                    }
                    lang = ext_to_lang.get(file_path.suffix, 'text')

                    st.code(content, language=lang, line_numbers=True)
                else:
                    st.error(f"File not found: {selected_file}")
            else:
                st.info("👈 Select a file from the left to view its contents")

        # Footer
        st.markdown('<div class="footer">Made By Ron Bronstein</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
