import streamlit as st
from resume_parser import extract_text_from_pdf, parse_resume_experiences
from skill_matcher import (
    extract_required_skills,
    match_skills_to_experiences,
    analyze_skills_gap,
    extract_jd_requirements,
    rank_bullets_for_jd,
    analyze_skills_gap_detailed,
)
from cover_letter import generate_cover_letter, extract_job_title, extract_company

st.set_page_config(
    page_title="Tarunya's Cover Letter Generator",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Maroon palette:
       --maroon-900: #4a0e0e  (deepest)
       --maroon-800: #5c1a1a
       --maroon-700: #722222
       --maroon-600: #8b2c2c
       --maroon-500: #a03333
       --maroon-400: #b84a4a
       --maroon-200: #e8b4b4
       --maroon-100: #f3d5d5
       --maroon-50:  #faf0f0
    */

    .stApp {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(160deg, #faf0f0 0%, #f3d5d5 40%, #e8b4b4 100%);
    }

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.75rem 0;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .main-header h1 {
        font-size: 2.4rem;
        font-weight: 700;
        color: #4a0e0e;
        margin: 0 0 0.2rem 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        font-size: 1.05rem;
        color: #722222;
        font-weight: 400;
        margin: 0 0 0.3rem 0;
    }
    .main-header .byline {
        font-family: 'Inter', sans-serif;
        font-size: 0.7rem;
        color: #8b2c2c;
        font-weight: 400;
        letter-spacing: 0.3px;
        margin: 0;
    }

    .section-card {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(139, 44, 44, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(74, 14, 14, 0.06);
        backdrop-filter: blur(4px);
    }
    .section-card h3 {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #8b2c2c;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(139, 44, 44, 0.12);
    }

    .stat-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.9);
        color: #5c1a1a;
        border: 1px solid rgba(139, 44, 44, 0.25);
        border-radius: 20px;
        padding: 0.25rem 0.75rem;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 8px;
        border: 1px solid rgba(139, 44, 44, 0.2);
        background: rgba(255, 255, 255, 0.95);
        font-size: 0.9rem;
        color: #2d0a0a !important;
        caret-color: #4a0e0e !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #8b2c2c;
        box-shadow: 0 0 0 2px rgba(139, 44, 44, 0.1);
    }
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #b07070 !important;
    }
    div[data-testid="stTextInput"] input {
        border-radius: 8px;
        border: 1px solid rgba(139, 44, 44, 0.2);
        background: rgba(255, 255, 255, 0.95);
        color: #2d0a0a !important;
        caret-color: #4a0e0e !important;
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #8b2c2c;
        box-shadow: 0 0 0 2px rgba(139, 44, 44, 0.1);
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: #b07070 !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #5c1a1a 0%, #8b2c2c 100%);
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        color: #ffffff;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #4a0e0e 0%, #722222 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(74, 14, 14, 0.35);
    }

    .stDownloadButton > button {
        border-radius: 8px;
        font-weight: 500;
        border: 1px solid rgba(139, 44, 44, 0.3);
        color: #5c1a1a;
        background: rgba(255, 255, 255, 0.9);
    }
    .stDownloadButton > button:hover {
        background: rgba(139, 44, 44, 0.08);
        border-color: #8b2c2c;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-bottom: 2px solid rgba(139, 44, 44, 0.15);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-size: 0.9rem;
        color: #5c1a1a;
    }
    .stTabs [aria-selected="true"] {
        border-bottom: 2px solid #8b2c2c;
    }

    .stRadio > div {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 8px;
        padding: 0.25rem;
    }
    .stRadio label p {
        color: #4a0e0e !important;
        font-weight: 500;
    }

    div[data-testid="stTextInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stFileUploader"] label {
        color: #5c1a1a !important;
        font-weight: 500;
        font-size: 0.88rem;
    }

    .stFileUploader {
        border: 1px dashed rgba(139, 44, 44, 0.3);
        border-radius: 8px;
    }

    .stExpander {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(139, 44, 44, 0.12);
        border-radius: 8px;
    }
    .stExpander summary,
    .stExpander summary p,
    .stExpander [data-testid="stExpanderToggleIcon"] {
        color: #5c1a1a !important;
        font-weight: 500;
    }
    .stExpander [data-testid="stText"],
    .stExpander pre,
    .stExpander p {
        color: #2d0a0a !important;
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(139, 44, 44, 0.12);
        border-radius: 10px;
        padding: 0.75rem 1rem;
        box-shadow: 0 1px 4px rgba(74, 14, 14, 0.05);
    }
    [data-testid="stMetricValue"] {
        color: #4a0e0e;
    }
    [data-testid="stMetricLabel"] {
        color: #8b2c2c;
    }

    .divider {
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(139, 44, 44, 0.2), transparent);
        margin: 1.5rem 0;
    }

    .match-card {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(139, 44, 44, 0.12);
        border-left: 3px solid #8b2c2c;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .match-card strong {
        color: #4a0e0e;
    }

    .experience-item {
        padding: 0.75rem 0;
        border-bottom: 1px solid rgba(139, 44, 44, 0.08);
    }
    .experience-item:last-child {
        border-bottom: none;
    }
    .experience-item strong {
        color: #4a0e0e;
    }

    .stSpinner > div {
        border-top-color: #8b2c2c !important;
    }

    .gap-section {
        background: rgba(255, 255, 255, 0.85);
        border: 1px solid rgba(139, 44, 44, 0.15);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(74, 14, 14, 0.06);
    }
    .gap-section h3 {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #8b2c2c;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(139, 44, 44, 0.12);
    }

    .skill-chip-matched {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
        border-radius: 20px;
        padding: 0.3rem 0.85rem;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 0.25rem 0.25rem 0.25rem 0;
    }
    .skill-chip-missing {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
        border-radius: 20px;
        padding: 0.3rem 0.85rem;
        font-size: 0.82rem;
        font-weight: 500;
        margin: 0.25rem 0.25rem 0.25rem 0;
    }

    .suggestion-card {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-left: 3px solid #f59e0b;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.6rem;
    }
    .suggestion-card .skill-label {
        font-weight: 600;
        color: #92400e;
        font-size: 0.85rem;
    }
    .suggestion-card .suggestion-text {
        color: #78350f;
        font-size: 0.82rem;
        margin-top: 0.2rem;
    }

    .gap-legend {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 1rem;
        font-size: 0.82rem;
    }
    .legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 0.35rem;
        vertical-align: middle;
    }

    .gap-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.84rem;
        margin-bottom: 1rem;
    }
    .gap-table th {
        background: rgba(139, 44, 44, 0.08);
        color: #4a0e0e;
        font-weight: 600;
        text-align: left;
        padding: 0.55rem 0.8rem;
        border-bottom: 2px solid rgba(139, 44, 44, 0.2);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
    }
    .gap-table td {
        padding: 0.55rem 0.8rem;
        border-bottom: 1px solid rgba(139, 44, 44, 0.07);
        color: #2d0a0a;
        vertical-align: top;
        line-height: 1.4;
    }
    .gap-table tr:hover td {
        background: rgba(139, 44, 44, 0.025);
    }
    .badge-strong {
        display: inline-block;
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
        border-radius: 12px;
        padding: 0.2rem 0.65rem;
        font-weight: 600;
        font-size: 0.78rem;
        white-space: nowrap;
    }
    .badge-transferable {
        display: inline-block;
        background: #fef9c3;
        color: #854d0e;
        border: 1px solid #fde68a;
        border-radius: 12px;
        padding: 0.2rem 0.65rem;
        font-weight: 600;
        font-size: 0.78rem;
        white-space: nowrap;
    }
    .badge-missing {
        display: inline-block;
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
        border-radius: 12px;
        padding: 0.2rem 0.65rem;
        font-weight: 600;
        font-size: 0.78rem;
        white-space: nowrap;
    }
    .quality-strong { color: #16a34a; font-weight: 600; font-size: 0.8rem; white-space: nowrap; }
    .quality-transferable { color: #d97706; font-weight: 600; font-size: 0.8rem; white-space: nowrap; }
    .quality-missing { color: #dc2626; font-weight: 600; font-size: 0.8rem; white-space: nowrap; }
    .found-text { color: #4a0e0e; font-size: 0.8rem; }
    .found-company { font-weight: 600; }
    .not-found-text { color: #9ca3af; font-style: italic; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>Tarunya's Cover Letter Generator</h1>
    <p>Generate a tailored, professional cover letter from your resume and a job description.</p>
    <span class="byline">Built by Tarunya</span>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="section-card"><h3>Your Resume</h3></div>', unsafe_allow_html=True)
    input_method = st.radio("Input method", ["Upload PDF", "Paste text"], horizontal=True, label_visibility="collapsed")

    resume_text = ""
    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf"], label_visibility="collapsed")
        if uploaded_file:
            resume_text = extract_text_from_pdf(uploaded_file)
            with st.expander("Preview extracted text", expanded=False):
                st.text(resume_text[:2000])
    else:
        resume_text = st.text_area("Paste your resume", height=340, placeholder="Paste your full resume text here...", label_visibility="collapsed")

with col2:
    st.markdown('<div class="section-card"><h3>Job Description</h3></div>', unsafe_allow_html=True)
    job_description = st.text_area("Paste the job description", height=340, placeholder="Paste the full job description here...", label_visibility="collapsed")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

st.markdown('<div class="section-card"><h3>Job Details</h3></div>', unsafe_allow_html=True)

hint_title = extract_job_title(job_description) if job_description.strip() else ""
hint_company = extract_company(job_description) if job_description.strip() else ""

detail_col1, detail_col2, detail_col3 = st.columns(3)
with detail_col1:
    candidate_name = st.text_input("Your full name", placeholder="e.g. Jane Smith")
with detail_col2:
    job_title = st.text_input("Job title", value=hint_title, placeholder="e.g. Senior Software Engineer")
with detail_col3:
    company = st.text_input("Company name", value=hint_company, placeholder="e.g. Acme Corp")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

_, center_col, _ = st.columns([1, 1, 1])
with center_col:
    generate_clicked = st.button("Generate Cover Letter", type="primary", use_container_width=True)

if generate_clicked:
    errors = []
    if not resume_text.strip():
        errors.append("Please provide your resume.")
    if not job_description.strip():
        errors.append("Please provide a job description.")
    if not candidate_name.strip():
        errors.append("Please enter your name.")
    if not job_title.strip():
        errors.append("Please enter the job title.")
    if not company.strip():
        errors.append("Please enter the company name.")

    for e in errors:
        st.error(e)

    if not errors:
        with st.spinner("Generating your cover letter..."):
            experiences = parse_resume_experiences(resume_text)
            required_skills = extract_required_skills(job_description)
            matches = match_skills_to_experiences(required_skills, experiences)
            jd_requirements = extract_jd_requirements(job_description)
            ranked_bullets = rank_bullets_for_jd(experiences, jd_requirements)
            cover_letter = generate_cover_letter(
                matches,
                job_title=job_title.strip(),
                company=company.strip(),
                experiences=experiences,
                candidate_name=candidate_name.strip(),
                job_description=job_description,
                ranked_bullets=ranked_bullets,
                jd_requirements=jd_requirements,
            )

        word_count = len(cover_letter.split())
        paragraph_count = len([p for p in cover_letter.split("\n\n") if p.strip()])

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Cover Letter", "Skills Gap Analysis", "Parsed Resume"])

        with tab1:
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            with col_stats1:
                st.metric("Words", word_count)
            with col_stats2:
                st.metric("Paragraphs", paragraph_count)
            with col_stats3:
                if 450 <= word_count <= 650:
                    st.metric("Status", "Ready")
                else:
                    st.metric("Status", "Review")

            st.text_area(
                "Your cover letter",
                value=cover_letter,
                height=480,
                label_visibility="collapsed",
            )

            dl_col1, dl_col2, _ = st.columns([1, 1, 2])
            with dl_col1:
                st.download_button(
                    "Download as .txt",
                    cover_letter,
                    file_name="cover_letter.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with dl_col2:
                st.download_button(
                    "Download as .md",
                    cover_letter,
                    file_name="cover_letter.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

        with tab2:
            gap_rows = analyze_skills_gap_detailed(experiences, job_description)

            strong_ct = sum(1 for r in gap_rows if r["match_quality"] == "Strong")
            transfer_ct = sum(1 for r in gap_rows if r["match_quality"] == "Transferable")
            missing_ct = sum(1 for r in gap_rows if r["match_quality"] == "Not found")
            total_ct = len(gap_rows)

            gap_col1, gap_col2, gap_col3, gap_col4 = st.columns(4)
            with gap_col1:
                st.metric("Skills Analyzed", total_ct)
            with gap_col2:
                st.metric("Strong Match", strong_ct)
            with gap_col3:
                st.metric("Transferable", transfer_ct)
            with gap_col4:
                st.metric("Gap", missing_ct)

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

            rows_html = ""
            for row in gap_rows:
                skill_display = row["skill"].title()
                mq = row["match_quality"]

                if mq == "Strong":
                    badge = f'<span class="badge-strong">&#10003; {skill_display}</span>'
                    quality_cell = '<span class="quality-strong">Strong</span>'
                elif mq == "Transferable":
                    badge = f'<span class="badge-transferable">&#x21C6; {skill_display}</span>'
                    quality_cell = '<span class="quality-transferable">Transferable</span>'
                else:
                    badge = f'<span class="badge-missing">&#10007; {skill_display}</span>'
                    quality_cell = '<span class="quality-missing">Not found</span>'

                req_raw = row["required_by"]
                req_text = req_raw[:90] + ("..." if len(req_raw) > 90 else "")

                if row["found_bullet"]:
                    bp = row["found_bullet"]
                    bullet_preview = bp[:85] + ("..." if len(bp) > 85 else "")
                    found_cell = (
                        f'<span class="found-text">'
                        f'<span class="found-company">{row["found_company"]}</span>: '
                        f'&ldquo;{bullet_preview}&rdquo;</span>'
                    )
                else:
                    sug = row.get("suggestion", "")
                    found_cell = f'<span class="not-found-text">Not found &mdash; {sug[:70]}...</span>'

                rows_html += (
                    f"<tr>"
                    f"<td>{badge}</td>"
                    f"<td>{req_text}</td>"
                    f"<td>{found_cell}</td>"
                    f"<td>{quality_cell}</td>"
                    f"</tr>"
                )

            table_html = (
                '<div style="overflow-x:auto;">'
                '<table class="gap-table"><thead><tr>'
                "<th>Skill</th><th>Required By Job</th><th>Found in Resume</th><th>Match</th>"
                f"</tr></thead><tbody>{rows_html}</tbody></table></div>"
            )
            st.markdown(table_html, unsafe_allow_html=True)

            missing_rows = [r for r in gap_rows if r["match_quality"] == "Not found"]
            if missing_rows:
                st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
                st.markdown("**How to close the gaps:**")
                for row in missing_rows[:6]:
                    st.markdown(
                        f'<div class="suggestion-card">'
                        f'<div class="skill-label">&#10007; {row["skill"].title()}</div>'
                        f'<div class="suggestion-text">{row["suggestion"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        with tab3:
            st.markdown(f"**{len(experiences)} experiences** parsed from your resume.")
            for exp in experiences:
                with st.container():
                    st.markdown(
                        f'<div class="experience-item">'
                        f'<strong>{exp["title"]}</strong> at {exp["company"]} '
                        f'{"(" + exp["duration"] + ")" if exp.get("duration") else ""}'
                        f'<br><span style="color:#6b7280;font-size:0.85rem;">'
                        f'{len(exp["bullets"])} bullet point{"s" if len(exp["bullets"]) != 1 else ""}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
