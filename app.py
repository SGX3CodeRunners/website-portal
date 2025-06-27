import streamlit as st
import pandas as pd
import plotly.express as px
import os
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="CodeRunners: Reproducibility Portal",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading (robust for scorecard_summary.csv) ---
@st.cache_data
def load_data():
    file_path = 'data/scorecard_summary.csv'
    if not os.path.exists(file_path):
        st.error(f"Error: Data file not found at {file_path}. Please ensure 'scorecard_summary.csv' is in the 'data/' folder of your repository.")
        st.stop()
    try:
        df_raw = pd.read_csv(file_path, sep=',', header=0, encoding='utf-8', engine='python', quotechar='"')
    except Exception as e:
        st.error(f"Failed to load CSV: {e}")
        st.stop()

    # --- Step 1: Extract Paper ID and Title from 'Paper File' ---
    paper_file_col = 'Paper File'
    df = pd.DataFrame()
    if paper_file_col in df_raw.columns:
        df['Paper ID'] = df_raw[paper_file_col].astype(str).apply(lambda x: x.replace('.pdf','').strip())
        df['Paper Title'] = df_raw[paper_file_col].astype(str).apply(lambda x: x.replace('.pdf','').replace('_',' ').strip())
    else:
        df['Paper ID'] = [f"P{i:03d}" for i in range(1, len(df_raw)+1)]
        df['Paper Title'] = [f"Paper {i} Title (Placeholder)" for i in range(1, len(df_raw)+1)]

    # --- Step 2: Parse 'Score: X | Notes: Y' strings robustly ---
    def parse_score(s):
        # More robust: find first integer after 'Score:'
        m = re.search(r'Score:\s*([0-9]+)', str(s).strip())
        if m:
            return int(m.group(1))
        return 0
    def parse_notes(s):
        m = re.search(r'Notes:\s*(.*)', str(s))
        return m.group(1).strip() if m else ''

    score_cols = [
        ('Paper Availability', 'Paper Availability'),
        ('Availability of Code and Software', 'Code Availability'),
        ('Availability of Datasets', 'Dataset Availability'),
        ('Computer Requirements', 'Computer Requirements'),
        ('GPU Requirements', 'GPU Requirements'),
        ('Documentation Quality', 'Documentation Quality'),
        ('Ease of Setup', 'Ease of Setup'),
        ('Reproducibility of Results', 'Reproducibility'),
        ('Overall Rating', 'Overall Rating')
    ]
    for csv_col, short in score_cols:
        if csv_col in df_raw.columns:
            df[f'{short} Score'] = df_raw[csv_col].apply(parse_score)
            df[f'{short} Notes'] = df_raw[csv_col].apply(parse_notes)
        else:
            df[f'{short} Score'] = 0
            df[f'{short} Notes'] = ''

    # --- Step 3: Main Category Scores (example mapping, adjust as needed) ---
    code_env_max = 5
    docs_max = 2
    data_model_max = 2
    community_max = 1
    df['Code & Environment Score'] = df['Code Availability Score'] + df['Computer Requirements Score'] + df['GPU Requirements Score']
    df['Documentation & Transparency Score'] = df['Documentation Quality Score'] + df['Ease of Setup Score']
    df['Data & Model Reuse Score'] = df['Dataset Availability Score']
    df['Community Engagement Score'] = 0  # Not in CSV, placeholder
    # Calculate overall score as sum of main categories, normalized to 100
    df['Overall Score (Raw)'] = (
        df['Code & Environment Score'] +
        df['Documentation & Transparency Score'] +
        df['Data & Model Reuse Score'] +
        df['Community Engagement Score']
    )
    max_total = code_env_max + docs_max + data_model_max + community_max
    df['Overall Score (100)'] = (df['Overall Score (Raw)'] / max_total * 100).round(1)
    # Status logic: 80+ = Highly, 50-79 = Partially, 20-49 = Issues, 0-19 = Not
    def status_from_score(score):
        if score >= 80:
            return 'Highly Reproducible'
        elif score >= 50:
            return 'Partially Reproducible'
        elif score >= 20:
            return 'Issues Present'
        else:
            return 'Not Reproducible'
    df['Overall Status'] = df['Overall Score (100)'].apply(status_from_score)
    df['Conference'] = ['ICSE 2023', 'SC24'] * (len(df) // 2) + ['ICSE 2023'] * (len(df) % 2)
    df['Paper Link'] = df['Paper ID'].apply(lambda x: f"https://example.com/papers/{x}.pdf")
    df['Code Link'] = df['Code Availability Notes'].apply(lambda x: re.search(r'https?://\S+', x).group(0) if re.search(r'https?://\S+', x) else 'N/A')
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filter Papers")
st.sidebar.markdown("Search, filter, and explore reproducibility scores.")
search_query = st.sidebar.text_input("🔍 Search by Title or ID", "").lower()
min_score = st.sidebar.slider("Minimum Overall Score (Points)", 0, 5, 0)

all_statuses = df['Overall Status'].dropna().unique().tolist()
if not all_statuses:
    all_statuses = ['Highly Reproducible', 'Partially Reproducible', 'Issues Present', 'Not Reproducible']
selected_statuses = st.sidebar.multiselect(
    "Filter by Status",
    options=all_statuses,
    default=all_statuses
)
all_conferences = df['Conference'].unique().tolist()
selected_conferences = st.sidebar.multiselect(
    "Filter by Conference",
    options=all_conferences,
    default=all_conferences
)
filtered_df = df[
    (df['Overall Score (100)'] >= min_score) &
    (df['Overall Status'].isin(selected_statuses)) &
    (df['Conference'].isin(selected_conferences))
]
if search_query:
    filtered_df = filtered_df[
        filtered_df['Paper Title'].str.lower().str.contains(search_query) |
        filtered_df['Paper ID'].str.lower().str.contains(search_query)
    ]

# Fallback: If filtered_df is empty, show warning and reset filters
if filtered_df.empty:
    st.warning("No papers match the current filters. Resetting filters to show all papers.")
    filtered_df = df.copy()
    selected_statuses = all_statuses
    selected_conferences = all_conferences

# --- Main Content Area ---
st.markdown("<h1 style='font-size:2.2rem;font-weight:800;margin-bottom:0.5rem;'>🧪 CodeRunners: LLM Paper Reproducibility Showdown</h1>", unsafe_allow_html=True)
st.markdown("<div style='font-size:1.1rem;margin-bottom:1.5rem;'>Welcome to the CodeRunners portal for our SGX3 ADMI hackathon project! This platform evaluates and compares the reproducibility of LLM papers from ICSE 2023 and SC24. Use the filters on the left to explore the papers.</div>", unsafe_allow_html=True)

# --- Metrics Row ---
with st.container():
    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        st.metric(label="Average Score", value=f"{filtered_df['Overall Score (100)'].mean():.1f}/100", delta=None, help="All scores are normalized to a 100-point scale.")
    with mcol2:
        st.metric(label="Highly Reproducible", value=f"{len(filtered_df[filtered_df['Overall Status'] == 'Highly Reproducible'])}")
    with mcol3:
        st.metric(label="Total Papers", value=f"{len(df)}")

st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

# --- Main Table and Details Side-by-Side ---
with st.container():
    tcol1, tcol2 = st.columns([2, 3], gap="large")
    with tcol1:
        st.markdown("<h3 style='margin-bottom:0.5rem;'>Papers</h3>", unsafe_allow_html=True)
        # Show only top 5 papers by default, with a 'View All' button
        if 'show_all_papers' not in st.session_state:
            st.session_state['show_all_papers'] = False
        top_n = 5
        if not st.session_state['show_all_papers']:
            display_df = filtered_df[['Paper ID', 'Paper Title', 'Overall Score (100)', 'Overall Status', 'Conference']].reset_index(drop=True).head(top_n)
        else:
            display_df = filtered_df[['Paper ID', 'Paper Title', 'Overall Score (100)', 'Overall Status', 'Conference']].reset_index(drop=True)
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )
        if not st.session_state['show_all_papers'] and len(filtered_df) > top_n:
            if st.button('View All Papers'):
                st.session_state['show_all_papers'] = True
                st.experimental_rerun()
        elif st.session_state['show_all_papers'] and len(filtered_df) > top_n:
            if st.button('Show Less'):
                st.session_state['show_all_papers'] = False
                st.experimental_rerun()
        dropdown_options = display_df['Paper Title'] + " (" + display_df['Paper ID'] + ")"
        selected_paper = st.selectbox("Select a paper for details:", dropdown_options, key="paper_select")
    with tcol2:
        if selected_paper:
            selected_id = selected_paper.split("(")[-1].replace(")", "").strip()
            selected_paper_data = filtered_df[filtered_df['Paper ID'] == selected_id].iloc[0]
            if 'show_full_scorecard' not in st.session_state:
                st.session_state['show_full_scorecard'] = False
            st.markdown(f"<div style='background:#f8fafc;padding:1.5rem 1.5rem 1rem 1.5rem;border-radius:1rem;box-shadow:0 2px 8px rgba(0,0,0,0.04);'>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='margin-bottom:0.5rem;'>{selected_paper_data['Paper Title']}</h3>", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:1.1rem;font-weight:600;'>Paper ID:</span> {selected_paper_data['Paper ID']}  ", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:1.1rem;font-weight:600;'>Conference:</span> {selected_paper_data.get('Conference', 'N/A')}  ", unsafe_allow_html=True)
            st.markdown(f"<span style='font-size:1.1rem;font-weight:600;'>Overall Score:</span> {selected_paper_data['Overall Score (100)']}/100  ", unsafe_allow_html=True)
            # Status chip
            status_color = {'Highly Reproducible':'#22c55e','Partially Reproducible':'#facc15','Issues Present':'#f97316','Not Reproducible':'#ef4444'}
            st.markdown(f"<span style='padding:0.3em 0.9em;border-radius:1em;background:{status_color.get(selected_paper_data['Overall Status'],'#e5e7eb')};color:#fff;font-weight:600;margin-right:0.5em;'>{selected_paper_data['Overall Status']}</span>", unsafe_allow_html=True)
            # Overall score progress bar
            st.progress(selected_paper_data['Overall Score (100)'] / 100)
            st.markdown(f"<a href='{selected_paper_data.get('Paper Link', '#')}' target='_blank'>View Paper</a> | <a href='{selected_paper_data.get('Code Link', '#')}' target='_blank'>View Code</a>", unsafe_allow_html=True)
            # Concise by default, expandable for full details
            if not st.session_state['show_full_scorecard']:
                if st.button('View Full Scorecard'):
                    st.session_state['show_full_scorecard'] = True
                    st.experimental_rerun()
            else:
                st.markdown("<hr style='margin:1rem 0;'>", unsafe_allow_html=True)
                st.markdown("<b>Score Breakdown by Category:</b>", unsafe_allow_html=True)
                max_scores = {
                    'Code & Environment Score': 100,
                    'Documentation & Transparency Score': 100,
                    'Data & Model Reuse Score': 100,
                    'Community Engagement Score': 100
                }
                for category_col, max_pts in max_scores.items():
                    if category_col in selected_paper_data.index:
                        score = selected_paper_data[category_col]
                        pct = int((score/max_pts)*100) if max_pts else 0
                        st.markdown(f"<div style='margin-bottom:0.5rem;'><b>{category_col.replace(' Score','')}:</b> {score}/{max_pts} <span style='color:#6366f1;font-weight:600;'>({pct}%)</span></div>", unsafe_allow_html=True)
                        st.progress(score / max_pts)
                    else:
                        st.write(f"{category_col.replace(' Score', '')}: Data not available.")
                st.markdown("<b>Detailed Notes:</b>", unsafe_allow_html=True)
                note_display_map = {
                    "Paper Availability Notes": "Paper Availability",
                    "Code Availability Notes": "Code & Environment",
                    "Dataset Availability Notes": "Data & Model Reuse",
                    "Documentation Quality Notes": "Documentation & Transparency",
                    "Computer Requirements Notes": "Computer Requirements",
                    "GPU Requirements Notes": "GPU Requirements",
                    "Ease of Setup Notes": "Ease of Setup",
                    "Reproducibility Notes": "Overall Reproducibility",
                    "Overall Rating Notes": "Overall Rating"
                }
                found_notes = False
                for note_col, display_name in note_display_map.items():
                    if note_col in selected_paper_data.index and pd.notna(selected_paper_data[note_col]) and selected_paper_data[note_col] != "":
                        st.markdown(f"<div style='margin-bottom:0.3rem;'><b>{display_name}:</b> <span style='color:#334155;'>{selected_paper_data[note_col]}</span></div>", unsafe_allow_html=True)
                        found_notes = True
                if not found_notes:
                    st.info("No detailed notes available for this paper in the current data.")
                if st.button('Show Less Scorecard'):
                    st.session_state['show_full_scorecard'] = False
                    st.experimental_rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Select a paper from the dropdown to view its detailed scorecard.")

st.markdown("<hr style='margin:2rem 0;'>", unsafe_allow_html=True)

# --- Visualizations ---
st.markdown("<h3 style='margin-bottom:0.5rem;'>Reproducibility Trends</h3>", unsafe_allow_html=True)
with st.container():
    vcol1, vcol2 = st.columns(2)
    with vcol1:
        fig_score_dist = px.histogram(df, x="Overall Score (100)",
                                    nbins=10, title="Distribution of Overall Reproducibility Scores (%)",
                                    labels={"Overall Score (100)": "Score (%)"},
                                    color_discrete_sequence=px.colors.qualitative.Plotly,
                                    height=350)
        st.plotly_chart(fig_score_dist, use_container_width=True)
    with vcol2:
        status_counts = df['Overall Status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        fig_status_pie = px.pie(status_counts, values='Count', names='Status',
                            title="Breakdown by Reproducibility Status",
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                            height=350)
        st.plotly_chart(fig_status_pie, use_container_width=True)

st.markdown("<hr style='margin:2rem 0;'>", unsafe_allow_html=True)

# --- About Section ---
st.markdown("<h3 style='margin-bottom:0.5rem;'>About CodeRunners</h3>", unsafe_allow_html=True)
st.markdown("""
This project aims to evaluate and compare the reproducibility of 189 papers from ICSE 2023 and SC24 that focus on large language models (LLMs) for code understanding tasks. Our goal is to understand how reproducible these research artifacts are and to present our findings visually.

**Team Roles:**
- **Aaliyah:** Experiment Engineer
- **Arghavan:** Model Analyst
- **Holy:** Portal Builder (That's you!)
- **Copernic:** Presenter
- **Iyana:** Project Lead

**Hackathon Goals:**
- Reproduce results from each of the 189 selected papers.
- Score each paper on reproducibility factors.
- Create a comparative scorecard for all papers.
- Build this public-facing web portal.
- Submit a poster summarizing methodology and findings to Gateways 2025.
""")
