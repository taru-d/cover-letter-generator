import streamlit as st
from resume_parser import extract_text_from_pdf, parse_resume_experiences
from skill_matcher import extract_required_skills, match_skills_to_experiences
from cover_letter import generate_cover_letter, extract_job_title, extract_company

st.set_page_config(
    page_title="Cover Letter Generator",
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
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #8b2c2c;
        box-shadow: 0 0 0 2px rgba(139, 44, 44, 0.1);
    }
    div[data-testid="stTextInput"] input {
        border-radius: 8px;
        border: 1px solid rgba(139, 44, 44, 0.2);
        background: rgba(255, 255, 255, 0.95);
    }
    div[data-testid="stTextInput"] input:focus {
        border-color: #8b2c2c;
        box-shadow: 0 0 0 2px rgba(139, 44, 44, 0.1);
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

    .stFileUploader {
        border: 1px dashed rgba(139, 44, 44, 0.3);
        border-radius: 8px;
    }

    .stExpander {
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid rgba(139, 44, 44, 0.12);
        border-radius: 8px;
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
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>Cover Letter Generator</h1>
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
            cover_letter = generate_cover_letter(
                matches,
                job_title=job_title.strip(),
                company=company.strip(),
                experiences=experiences,
                candidate_name=candidate_name.strip(),
                job_description=job_description,
            )

        word_count = len(cover_letter.split())
        paragraph_count = len([p for p in cover_letter.split("\n\n") if p.strip()])

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Cover Letter", "Skill Analysis", "Parsed Resume"])

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
            if matches:
                st.markdown(f"**{len(matches)} skills matched** from the job description to your resume.")
                for match in matches:
                    with st.container():
                        st.markdown(
                            f'<div class="match-card">'
                            f'<strong>{match["skill"].title()}</strong> — '
                            f'from {match["job_title"]} at {match["company"]}<br>'
                            f'<span style="color:#6b7280;font-size:0.85rem;">{match["evidence"]}</span>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No direct skill matches found. The cover letter uses general experience context.")

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

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.markdown(f"**{len(required_skills)} skills identified** in job description:")
            skill_cols = st.columns(4)
            for i, skill in enumerate(required_skills):
                with skill_cols[i % 4]:
                    st.markdown(f'<span class="stat-badge">{skill.title()}</span>', unsafe_allow_html=True)
