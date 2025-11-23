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
    page_title="monday.com AI Content Scoring",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "AI Content Scoring System by Ron Bronstein"
    }
)

# Force light theme for monday.com brand colors
st.markdown("""
<script>
    window.localStorage.setItem('theme', 'light');
</script>
""", unsafe_allow_html=True)

# monday.com Brand Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=Figtree:wght@300;400;500;600;700&display=swap');

    /* Global Styles */
    * {
        font-family: 'Figtree', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, .header-text {
        font-family: 'Poppins', sans-serif;
    }

    /* monday.com Brand Colors */
    :root {
        --monday-purple: #6161FF;
        --monday-dark: #181B34;
        --monday-light: #F0F3FF;
        --monday-white: #FFFFFF;
        --green-done: #00CA72;
        --yellow-working: #FFCC00;
        --red-stuck: #FB275D;
    }

    /* Main Content Area Background */
    .main .block-container {
        background: linear-gradient(180deg, #F0F3FF 0%, #FFFFFF 100%);
        padding-top: 2rem;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E6E9EF;
        padding-top: 1rem;
    }

    [data-testid="stSidebar"] .sidebar-content {
        padding: 0;
    }

    /* Sidebar Content Items */
    .sidebar-item {
        padding: 0.6rem 0.75rem;
        margin: 0.2rem 0.4rem;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.15s ease;
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--monday-white);
        border: 1px solid #F0F0F0;
    }

    .sidebar-item:hover {
        background: #F8F9FA;
    }

    .sidebar-item-active {
        background: var(--monday-light);
        border-left: 2px solid var(--monday-purple);
    }

    .sidebar-score-badge {
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 8px;
        font-size: 0.8rem;
    }

    /* Main Header */
    .main-header {
        font-family: 'Poppins', sans-serif;
        font-size: 2rem;
        font-weight: 600;
        color: var(--monday-dark);
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--monday-purple), var(--red-stuck));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }

    /* Hero Metrics Cards */
    .hero-metric-card {
        background: var(--monday-white);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E6E9EF;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: all 0.2s ease;
    }

    .hero-metric-card:hover {
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
        border-color: #D1D5DB;
    }

    .hero-metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }

    .hero-metric-label {
        font-size: 0.85rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 500;
    }

    /* Metric Cards (smaller) */
    .metric-card {
        background: var(--monday-white);
        padding: 1.25rem;
        border-radius: 8px;
        border: 1px solid #E6E9EF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.2s ease;
    }

    .metric-card:hover {
        box-shadow: 0 2px 4px rgba(0,0,0,0.06);
        border-color: #D1D5DB;
    }

    /* Score Colors (monday.com palette) */
    .score-excellent { color: var(--green-done); }
    .score-good { color: var(--green-done); }
    .score-moderate { color: var(--yellow-working); }
    .score-warning { color: var(--yellow-working); }
    .score-poor { color: var(--red-stuck); }

    /* Status Boxes */
    .strength-box {
        background: linear-gradient(135deg, rgba(0, 202, 114, 0.1) 0%, rgba(0, 202, 114, 0.05) 100%);
        border-left: 4px solid var(--green-done);
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }

    .neutral-box {
        background: linear-gradient(135deg, rgba(255, 204, 0, 0.1) 0%, rgba(255, 204, 0, 0.05) 100%);
        border-left: 4px solid var(--yellow-working);
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }

    .improvement-box {
        background: linear-gradient(135deg, rgba(251, 39, 93, 0.1) 0%, rgba(251, 39, 93, 0.05) 100%);
        border-left: 4px solid var(--red-stuck);
        padding: 1.25rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }

    .sub-param-header {
        font-family: 'Poppins', sans-serif;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
        color: var(--monday-dark);
    }

    .sub-param-score {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .sub-param-feedback {
        font-size: 0.95rem;
        line-height: 1.7;
        color: #555;
    }

    /* Flag Items */
    .flag-item {
        background: var(--monday-white);
        padding: 0.875rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid var(--red-stuck);
        color: var(--monday-dark);
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    /* CTA Button */
    .cta-button {
        background: linear-gradient(135deg, var(--monday-purple), #7B7BFF);
        color: white;
        padding: 1rem 2.5rem;
        border-radius: 8px;
        font-size: 1.1rem;
        font-weight: 600;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(97, 97, 255, 0.3);
    }

    .cta-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(97, 97, 255, 0.4);
    }

    /* Content Display */
    .content-display {
        background: #FAFBFC;
        color: var(--monday-dark);
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #E6E9EF;
        line-height: 1.8;
        box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
    }

    /* Comparison Cards */
    .comparison-card {
        background: var(--monday-white);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #E6E9EF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }

    .comparison-card:hover {
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }

    .comparison-card-golden {
        border-top: 3px solid var(--green-done);
        background: var(--monday-white);
    }

    .comparison-card-poison {
        border-top: 3px solid var(--red-stuck);
        background: var(--monday-white);
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #888;
        padding: 2rem 0 1rem 0;
        font-size: 0.9rem;
        border-top: 2px solid var(--monday-light);
        margin-top: 4rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: var(--monday-light);
        padding: 0.5rem;
        border-radius: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
    }

    .stTabs [aria-selected="true"] {
        background: var(--monday-purple);
        color: white;
    }

    /* Progress Bars */
    .parameter-progress {
        height: 12px;
        background: var(--monday-light);
        border-radius: 6px;
        overflow: hidden;
        margin: 0.5rem 0;
    }

    .parameter-progress-fill {
        height: 100%;
        transition: width 0.6s ease;
        border-radius: 6px;
    }

    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .badge-success {
        background: rgba(0, 202, 114, 0.2);
        color: var(--green-done);
    }

    .badge-warning {
        background: rgba(255, 204, 0, 0.2);
        color: #CC9900;
    }

    .badge-error {
        background: rgba(251, 39, 93, 0.2);
        color: var(--red-stuck);
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

@st.cache_data
def extract_title_from_content(content_folder, content_id):
    """Extract the first H1 heading from a content file as the title"""
    content = load_content_file(content_folder, content_id)
    if not content:
        return content_id  # Fallback to content_id if file not found

    # Look for H1 heading (# Title or === underline style)
    lines = content.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        # Markdown style: # Title
        if line.startswith('# '):
            return line[2:].strip()
        # Alternative style: Title\n===
        if i < len(lines) - 1 and lines[i + 1].strip().startswith('==='):
            return line.strip()

    # Fallback: use content_id with underscores replaced by spaces and title cased
    return content_id.replace('_', ' ').title()

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
    """Return CSS class based on score (monday.com colors)"""
    if score is None:
        return "score-poor"
    elif score >= 3.0:
        return "score-excellent"  # Green (done)
    elif score >= 2.36:
        return "score-moderate"  # Yellow (working on it)
    else:
        return "score-poor"  # Red (stuck)

def get_score_color_hex(score):
    """Return hex color based on score (monday.com colors)"""
    if score is None:
        return "#FB275D"
    elif score >= 3.0:
        return "#00CA72"  # Green
    elif score >= 2.36:
        return "#FFCC00"  # Yellow
    else:
        return "#FB275D"  # Red

def get_score_badge(score):
    """Return HTML badge for score"""
    color = get_score_color_hex(score)
    if score is None:
        return f'<span class="badge badge-error">N/A</span>'
    elif score >= 3.0:
        return f'<span class="badge badge-success">{score:.2f}</span>'
    elif score >= 2.36:
        return f'<span class="badge badge-warning">{score:.2f}</span>'
    else:
        return f'<span class="badge badge-error">{score:.2f}</span>'

def display_metrics_overview(metrics):
    """Display overview metrics in cards"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Content Pieces", metrics['total_pieces'])

    with col2:
        score_class = get_score_color_class(metrics['avg_overall'])
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #666;">Average Overall Score (1-4 scale)</div>
            <div class="{score_class}" style="font-size: 1.6rem;">{metrics['avg_overall']:.2f}/4.0</div>
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
    """Plot parameter scores as bar chart (monday.com colors)"""
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

    # monday.com color scale: red → yellow → green
    fig = px.bar(df, x='Parameter', y='Average Score',
                 title='Average Scores by Parameter',
                 color='Average Score',
                 color_continuous_scale=['#FB275D', '#FFCC00', '#00CA72'],
                 range_color=[1, 4],
                 range_y=[1, 4])

    fig.update_layout(
        height=400,
        showlegend=False,
        font=dict(family="Figtree, sans-serif"),
        title_font=dict(family="Poppins, sans-serif", size=18, color="#181B34")
    )
    fig.add_hline(y=2.36, line_dash="solid", line_color="#6161FF", line_width=3,
                  annotation_text="Publish-Ready Threshold (2.36)",
                  annotation_font_color="#6161FF")

    return fig

def plot_score_distribution(metrics):
    """Plot distribution of overall scores (monday.com colors)"""
    dist = metrics['overall_distribution']

    df = pd.DataFrame({
        'Score Range': ['1.0-2.0', '2.0-3.0', '3.0-4.0'],
        'Count': [dist['1-2'], dist['2-3'], dist['3-4']]
    })

    # monday.com colors: red (stuck), yellow (working), green (done)
    colors = ['#FB275D', '#FFCC00', '#00CA72']

    fig = px.bar(df, x='Score Range', y='Count',
                 title='Distribution of Overall Scores',
                 color='Score Range',
                 color_discrete_sequence=colors)

    fig.update_layout(
        height=400,
        showlegend=False,
        font=dict(family="Figtree, sans-serif"),
        title_font=dict(family="Poppins, sans-serif", size=18, color="#181B34")
    )

    return fig

def display_category_metrics(metrics, category_name, category_emoji):
    """Display metrics for a specific category"""
    avg_score = metrics['avg_overall']
    score_color = get_score_color_hex(avg_score)
    pass_rate = (metrics['pass_count'] / metrics['total_pieces']) * 100 if metrics['total_pieces'] > 0 else 0

    st.markdown(f"""
    <div class="hero-metric-card">
        <div style="font-family: Poppins, sans-serif; font-size: 1.1rem; font-weight: 600; color: #181B34; margin-bottom: 1rem;">
            {category_emoji} {category_name}
        </div>
        <div style="margin-bottom: 0.75rem;">
            <div style="font-size: 0.75rem; color: #666; text-transform: uppercase;">Avg Score</div>
            <div style="font-family: Poppins, sans-serif; font-size: 2rem; font-weight: 600; color: {score_color};">{avg_score:.2f}</div>
        </div>
        <div style="padding-top: 0.75rem; border-top: 1px solid #F0F0F0;">
            <div style="font-size: 0.75rem; color: #666;">Publish-Ready: <strong>{pass_rate:.0f}%</strong></div>
            <div style="font-size: 0.75rem; color: #666;">Violations: <strong>{metrics['total_violations']}</strong></div>
            <div style="font-size: 0.75rem; color: #999;">{metrics['total_pieces']} pieces</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_dashboard_insights(reports):
    """Display top performers and needs improvement"""
    st.markdown("### 📊 Content Insights")

    col1, col2 = st.columns(2)

    # Sort reports by score
    sorted_reports = sorted([r for r in reports if r['results']['overall_score'] is not None],
                          key=lambda x: x['results']['overall_score'], reverse=True)

    with col1:
        st.markdown("#### ✨ Top Performers")
        top_3 = sorted_reports[:3] if len(sorted_reports) >= 3 else sorted_reports
        for report in top_3:
            score = report['results']['overall_score']
            content_id = report['metadata']['content_id']
            badge = get_score_badge(score)
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 600; color: #181B34;">{content_id}</div>
                    {badge}
                </div>
                <div style="font-size: 0.85rem; color: #666; margin-top: 0.25rem;">
                    {report['results'].get('status', 'N/A')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("#### 🎯 Needs Improvement")
        bottom_3 = sorted_reports[-3:][::-1] if len(sorted_reports) >= 3 else []
        for report in bottom_3:
            score = report['results']['overall_score']
            content_id = report['metadata']['content_id']
            badge = get_score_badge(score)
            violations = report['gates_status']['critical_violations_count']
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-weight: 600; color: #181B34;">{content_id}</div>
                    {badge}
                </div>
                <div style="font-size: 0.85rem; color: #FB275D; margin-top: 0.25rem;">
                    {violations} violation{'s' if violations != 1 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

def render_sidebar_navigation(all_reports):
    """Render sidebar navigation with content list"""
    with st.sidebar:
        st.markdown("### 📁 Navigation")

        # Dashboard button (resets to overview)
        if st.button("🏠 Dashboard", key="sidebar_dashboard", use_container_width=True, type="primary"):
            st.session_state.selected_content = None
            # Note: No st.rerun() to avoid tab navigation issues

        st.markdown("<br>", unsafe_allow_html=True)

        # Group reports by source
        home_reports = [r for r in all_reports if r.get('_source') == 'home']
        golden_reports = [r for r in all_reports if r.get('_source') == 'golden']
        poison_reports = [r for r in all_reports if r.get('_source') == 'poison']

        selected_content = None

        # Home Assignment section with expander
        if home_reports:
            with st.expander("📊 Home Assignment", expanded=True):
                for idx, report in enumerate(home_reports):
                    score = report['results']['overall_score']
                    content_id = report['metadata']['content_id']
                    color = get_score_color_hex(score)

                    # Extract human-readable title
                    title = extract_title_from_content("data/input", content_id)

                    if st.button(
                        f"{title}",
                        key=f"sidebar_home_{idx}_{content_id}",
                        use_container_width=True
                    ):
                        selected_content = (report, "data/input")

                    # Show score inline
                    score_badge = get_score_badge(score)
                    st.markdown(f"<div style='text-align: right; margin-top: -2.5rem; margin-bottom: 1rem;'>{score_badge}</div>", unsafe_allow_html=True)

        # Golden Set section with expander
        if golden_reports:
            with st.expander("🟢 Golden Set (Calibration)", expanded=False):
                for idx, report in enumerate(golden_reports):
                    score = report['results']['overall_score']
                    content_id = report['metadata']['content_id']

                    # Extract human-readable title
                    title = extract_title_from_content("data/calibration/golden_set", content_id)

                    if st.button(
                        f"{title}",
                        key=f"sidebar_golden_{idx}_{content_id}",
                        use_container_width=True
                    ):
                        selected_content = (report, "data/calibration/golden_set")

                    score_badge = get_score_badge(score)
                    st.markdown(f"<div style='text-align: right; margin-top: -2.5rem; margin-bottom: 1rem;'>{score_badge}</div>", unsafe_allow_html=True)

        # Poison Set section with expander
        if poison_reports:
            with st.expander("🔴 Poison Set (Calibration)", expanded=False):
                for idx, report in enumerate(poison_reports):
                    score = report['results']['overall_score']
                    content_id = report['metadata']['content_id']

                    # Extract human-readable title
                    title = extract_title_from_content("data/calibration/poison_set", content_id)

                    if st.button(
                        f"{title}",
                        key=f"sidebar_poison_{idx}_{content_id}",
                        use_container_width=True
                    ):
                        selected_content = (report, "data/calibration/poison_set")

                    score_badge = get_score_badge(score)
                    st.markdown(f"<div style='text-align: right; margin-top: -2.5rem; margin-bottom: 1rem;'>{score_badge}</div>", unsafe_allow_html=True)

        # GitHub icon at the bottom
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-top: 1px solid #E6E9EF;">
            <a href="https://github.com/ronbronstein/scoring-system" target="_blank" style="text-decoration: none;">
                <div style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: #181B34;
                    transition: all 0.2s ease;
                    cursor: pointer;
                ">
                    <svg width="20" height="20" viewBox="0 0 16 16" fill="white" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                    </svg>
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)

        return selected_content

def display_individual_report(report, content_folder):
    """Display detailed view of a single report (redesigned with 60/40 split)"""
    content_id = report["metadata"]["content_id"]
    title = extract_title_from_content(content_folder, content_id)
    st.markdown(f'<h2 style="font-family: Poppins, sans-serif; color: #181B34; font-size: 1.6rem; font-weight: 600;">{title}</h2>', unsafe_allow_html=True)

    # Two columns: 60% content, 40% analysis
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("#### 📄 Original Content")
        content = load_content_file(content_folder, report['_content_file'])
        if content:
            st.markdown(f"""
            <div class="content-display" style="max-height: 700px; overflow-y: auto;">
            {content[:8000]}{'...' if len(content) > 8000 else ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Content file not found")

    with col2:
        st.markdown("#### ⚡ AI Analysis")

        # Overall score
        score = report['results']['overall_score']
        score_class = get_score_color_class(score)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #666; font-size: 0.85rem;">Overall Score (1-4 scale)</div>
            <div class="{score_class}" style="font-size: 2rem;">{score:.2f}/4.0</div>
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
            with st.expander(f"View {param_key} Details", expanded=False):
                # Separate sub-parameters into strengths and areas for improvement
                strengths = []
                improvements = []
                neutral = []

                for sub_key, sub_data in param_data['sub_parameters'].items():
                    score = sub_data['score']
                    if score >= 3:
                        strengths.append((sub_key, sub_data))
                    elif score >= 2:
                        neutral.append((sub_key, sub_data))
                    else:
                        improvements.append((sub_key, sub_data))

                # Display strengths first
                if strengths:
                    st.markdown("### ✅ Strengths")
                    for sub_key, sub_data in strengths:
                        st.markdown(f"""
                        <div class="strength-box">
                            <div class="sub-param-header">{sub_data['name']}</div>
                            <div class="sub-param-score" style="color: #28a745;">{sub_data['score']}/4</div>
                            <div class="sub-param-feedback">{sub_data['feedback']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Display neutral scores
                if neutral:
                    st.markdown("### ⚠️ Moderate Performance")
                    for sub_key, sub_data in neutral:
                        flags_count = len(sub_data.get('flags', []))
                        st.markdown(f"""
                        <div class="neutral-box">
                            <div class="sub-param-header">{sub_data['name']}</div>
                            <div class="sub-param-score" style="color: #d97706;">{sub_data['score']}/4</div>
                            <div class="sub-param-feedback">{sub_data['feedback']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        if 'flags' in sub_data and sub_data['flags']:
                            with st.expander(f"⚠️ {flags_count} Issue{'s' if flags_count != 1 else ''} Found", expanded=False):
                                for i, flag in enumerate(sub_data['flags'], 1):
                                    # Handle both string flags and dict flags
                                    if isinstance(flag, str):
                                        st.markdown(f"""
                                        <div class="flag-item">
                                            <strong>Issue {i}:</strong> {flag}
                                        </div>
                                        """, unsafe_allow_html=True)
                                    elif isinstance(flag, dict):
                                        st.markdown(f"""
                                        <div class="flag-item">
                                            <strong>Issue {i}:</strong> {flag.get('message', flag.get('issue', 'N/A'))}<br>
                                            <strong>Violation:</strong> {flag.get('violation', flag.get('quote', 'N/A'))}<br>
                                            <strong>Context:</strong> {flag.get('context', flag.get('fix_suggestion', 'N/A'))}
                                        </div>
                                        """, unsafe_allow_html=True)

                # Display areas for improvement
                if improvements:
                    st.markdown("### ❌ Areas for Improvement")
                    for sub_key, sub_data in improvements:
                        flags_count = len(sub_data.get('flags', []))
                        st.markdown(f"""
                        <div class="improvement-box">
                            <div class="sub-param-header">{sub_data['name']}</div>
                            <div class="sub-param-score" style="color: #dc3545;">{sub_data['score']}/4</div>
                            <div class="sub-param-feedback">{sub_data['feedback']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        if 'flags' in sub_data and sub_data['flags']:
                            with st.expander(f"🚨 {flags_count} Critical Issue{'s' if flags_count != 1 else ''} Found", expanded=True):
                                for i, flag in enumerate(sub_data['flags'], 1):
                                    # Handle both string flags and dict flags
                                    if isinstance(flag, str):
                                        st.markdown(f"""
                                        <div class="flag-item">
                                            <strong>Issue {i}:</strong> {flag}
                                        </div>
                                        """, unsafe_allow_html=True)
                                    elif isinstance(flag, dict):
                                        st.markdown(f"""
                                        <div class="flag-item">
                                            <strong>Issue {i}:</strong> {flag.get('message', flag.get('issue', 'N/A'))}<br>
                                            <strong>Violation:</strong> {flag.get('violation', flag.get('quote', 'N/A'))}<br>
                                            <strong>Context:</strong> {flag.get('context', flag.get('fix_suggestion', 'N/A'))}
                                        </div>
                                        """, unsafe_allow_html=True)

def run_analysis(content_text):
    """Run analysis on provided content text"""
    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content_text)
            temp_path = f.name

        # Run analysis (timeout: 5 minutes for 16 LLM agents)
        result = subprocess.run(
            [sys.executable, 'src/main.py', 'analyze', temp_path, '--json', '--no-save'],
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
    # Render directories first
    for dir_name, subtree in tree['dirs'].items():
        dir_path = f"{current_path}/{dir_name}" if current_path else dir_name

        # Use expander for folders (collapsed by default)
        with st.expander(f"📁 {dir_name}", expanded=False):
            render_file_tree(subtree, dir_path, level + 1)

    # Render files
    for file_name in tree['files']:
        file_path = f"{current_path}/{file_name}" if current_path else file_name
        # Use smaller button styling
        if st.button(f"📄 {file_name}", key=file_path, use_container_width=True):
            st.session_state.selected_file = file_path

# Main app
def main():
    # Initialize session state for selected content, active tab, and selected file
    if 'selected_content' not in st.session_state:
        st.session_state.selected_content = None
    if 'active_tab' not in st.session_state:
        st.session_state.active_tab = 0  # Default to Dashboard
    if 'preserve_tab' not in st.session_state:
        st.session_state.preserve_tab = False
    if 'selected_file' not in st.session_state:
        st.session_state.selected_file = None

    # Load all reports for sidebar
    all_reports_raw = load_reports("data/reports")
    all_reports_golden = load_reports("data/reports/golden_set")
    all_reports_poison = load_reports("data/reports/poison_set")

    # Filter home reports to exclude calibration subdirectories
    all_reports_home = [r for r in all_reports_raw
                        if '/' not in r['_filename']
                        and not r['_filename'].startswith('tmp_')]

    # Mark source for each report
    for r in all_reports_home:
        r['_source'] = 'home'
    for r in all_reports_golden:
        r['_source'] = 'golden'
    for r in all_reports_poison:
        r['_source'] = 'poison'

    all_reports = all_reports_home + all_reports_golden + all_reports_poison

    # Render sidebar and update session state
    selected_content = render_sidebar_navigation(all_reports)
    if selected_content:
        st.session_state.selected_content = selected_content

    # Always show tabs for navigation
    tab1, tab2, tab3 = st.tabs([
        "🏠 Dashboard",
        "📁 Project Files",
        "🔬 Live Analysis"
    ])

    # Tab 1: Dashboard - Showcase AI capabilities
    with tab1:
        # If content is selected, show individual view
        if st.session_state.selected_content:
            report, content_folder = st.session_state.selected_content
            display_individual_report(report, content_folder)
        else:
            # Otherwise show dashboard with categories separated
            st.markdown('<div class="main-header">AI Content Scoring System</div>', unsafe_allow_html=True)
            st.markdown('<div class="sub-header">Intelligent evaluation of brand voice, strategic value, and engagement</div>', unsafe_allow_html=True)

            # Filter home assignment reports
            real_reports = [r for r in all_reports_home
                           if '/' not in r['_filename']
                           and not r['_filename'].startswith('tmp_')]

            # Calculate metrics for each category
            home_metrics = calculate_metrics(real_reports) if real_reports else None
            golden_metrics = calculate_metrics(all_reports_golden) if all_reports_golden else None
            poison_metrics = calculate_metrics(all_reports_poison) if all_reports_poison else None

            # Hero Metrics by Category
            st.markdown("### 📊 Performance Metrics by Category")
            col1, col2, col3 = st.columns(3)

            with col1:
                if home_metrics:
                    display_category_metrics(home_metrics, "Home Assignment", "📊")
                else:
                    st.info("No home assignment reports yet")

            with col2:
                if golden_metrics:
                    display_category_metrics(golden_metrics, "Golden Set", "🟢")
                else:
                    st.info("No golden set reports yet")

            with col3:
                if poison_metrics:
                    display_category_metrics(poison_metrics, "Poison Set", "🔴")
                else:
                    st.info("No poison set reports yet")

            st.markdown("<br>", unsafe_allow_html=True)

            # Analytics Charts by Category
            st.markdown("### 📈 Score Analytics by Category")

            # Row 1: Parameter Scores
            col1, col2, col3 = st.columns(3)

            with col1:
                if home_metrics:
                    st.markdown("**📊 Home Assignment**")
                    st.plotly_chart(plot_parameter_scores(home_metrics), use_container_width=True)

            with col2:
                if golden_metrics:
                    st.markdown("**🟢 Golden Set**")
                    st.plotly_chart(plot_parameter_scores(golden_metrics), use_container_width=True)

            with col3:
                if poison_metrics:
                    st.markdown("**🔴 Poison Set**")
                    st.plotly_chart(plot_parameter_scores(poison_metrics), use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Row 2: Score Distributions
            col1, col2, col3 = st.columns(3)

            with col1:
                if home_metrics:
                    st.plotly_chart(plot_score_distribution(home_metrics), use_container_width=True)

            with col2:
                if golden_metrics:
                    st.plotly_chart(plot_score_distribution(golden_metrics), use_container_width=True)

            with col3:
                if poison_metrics:
                    st.plotly_chart(plot_score_distribution(poison_metrics), use_container_width=True)

            # Call to action
            st.markdown("---")
            st.markdown("### 💡 Explore More")
            st.markdown("👈 **Click any content in the sidebar** to see detailed AI analysis with parameter breakdowns, violations, and actionable feedback.")

    # Tab 2: Project Files
    with tab2:
        st.markdown("## Project Files")
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

            # Render the file tree (selected file is stored in session state)
            render_file_tree(file_tree)

        with col2:
            # File viewer - use session state instead of return value
            if st.session_state.selected_file:
                st.markdown(f"### {st.session_state.selected_file}")

                file_path = Path(st.session_state.selected_file)
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
                    st.error(f"File not found: {st.session_state.selected_file}")
            else:
                st.info("👈 Select a file from the left to view its contents")

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
                        <div style="color: #666; font-size: 0.85rem;">Overall Score (1-4 scale)</div>
                        <div class="{score_class}" style="font-size: 2.2rem;">{score:.2f}/4.0</div>
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

if __name__ == "__main__":
    main()
