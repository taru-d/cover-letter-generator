# Tarunya's Cover Letter Generator

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
python3 -m streamlit run app.py
```

## Running tests

No test framework is set up yet. Validate logic with inline Python:

```bash
python3 -c "
from resume_parser import parse_resume_experiences
from skill_matcher import extract_required_skills, match_skills_to_experiences
from cover_letter import generate_cover_letter, extract_job_title, extract_company
# ... test code
"
```

## Architecture

Four modules with a clean pipeline:

1. **`resume_parser.py`** — Extracts text from PDF or plain text, then parses into structured `experiences`: `[{title, company, duration, bullets: [...]}]`. Uses regex to detect job entry lines and bullet points.

2. **`skill_matcher.py`** — Extracts required skills from a JD by matching against `SKILL_SYNONYMS` (canonical → variations). Then scores each resume bullet for relevance to each skill (keyword match + action verb + quantified result bonuses), returning the best-matching bullet per skill.

3. **`cover_letter.py`** — Generates the letter using five explicit paragraphs. Never references skills explicitly. Always names companies from the resume using "As a [role] at [Company]" structures. Never pulls from bullet points.
   - `generate_cover_letter(matches, job_title, company, experiences, candidate_name, job_description)` — entry point; all fields are passed explicitly, never extracted internally
   - `extract_job_title(jd)` / `extract_company(jd)` — exposed for the UI to pre-fill editable fields; fallback to empty string (never a default like "this position")
   - **Opening**: candidate name + role/company + "As a [role] at [company]" for most recent experience + fit statement
   - **Body 1–3**: one paragraph per distinct work experience, each 3+ sentences: (1) "As a [role] at [company]" + general responsibility description, (2) growth/development at that company, (3) how experience prepares them for the target JD
   - **Closing**: references all company names + why this company + why this role + call to action
   - `_select_experiences` picks up to 3 experiences ranked by match score, supplementing with unmatched real experiences
   - `_extract_jd_themes(job_description)` — extracts action-oriented verb phrases from JD for use in body paragraph sentence 3
   - `_enforce_word_count` ensures output stays within 450–650 words

4. **`app.py`** — Streamlit UI. After the user enters a JD, job title and company are pre-filled from `extract_job_title`/`extract_company` into editable text fields the user must confirm before generating. Candidate name, job title, and company are all required. Three output tabs: cover letter (with download), skill matches, parsed data.

## Key invariants

- Candidate name, job title, and company are **never silently defaulted** inside `cover_letter.py` — the UI enforces all three are non-empty before calling `generate_cover_letter`.
- **Skills are never mentioned explicitly** in the cover letter output — no tool names, language names, or framework names appear.
- **Bullet points are never referenced** — body paragraphs describe experiences in general professional terms.
- Every body paragraph must be anchored to a real `(title, company)` pair from the resume using "As a [role] at [company]" structure.
- Company names from the resume are **always stated explicitly** in body paragraphs and closing.
- `Sample Cover Letter Format.pdf` informs structure only — it is not loaded at runtime.

## Cover letter quality requirements

1. Write in clean, professional, grammatically correct English. Every sentence MUST be grammatically correct.
2. Each cover letter must be exactly 5 paragraphs.
3. Never use incomplete sentences or fragment thoughts.
4. **Never reference skills explicitly** — no listing or naming of technical skills/tools in the letter.
5. **Always name companies from the resume explicitly** — use "As a [role] at [company]" sentence structures.
6. **Never pull from bullet points** — body paragraphs describe the experience in general professional terms, not by paraphrasing resume bullets.
7. Structure and minimum sentence counts:
   - **Paragraph 1 (Opening, 2+ sentences):** candidate name, role + company applied to, "As a [role] at [company]" referencing most recent experience, fit statement
   - **Paragraphs 2–4 (Body, 3+ sentences each):** one paragraph per work experience — sentence 1: "As a [role] at [company]" + general description of responsibilities; sentence 2: growth and professional development at that company; sentence 3: how that experience prepares them for the target role
   - **Paragraph 5 (Closing, 3+ sentences):** references all company names, why this company, why this role, call to action
8. Tone must be confident, specific, and professional.
9. Word count: minimum 450, maximum 650 words per cover letter.
10. Never use generic filler phrases such as "I am excited to apply" or "I look forward to hearing from you".

## Tone guidelines

All cover letters are written in Tarunya's voice. Match this tone exactly.

**Core traits:**
- Concise sentences. No wordiness or filler.
- Motivated and passionate, but never generic or gushing.
- No em-dashes (never use —). Use commas, periods, or colons instead.
- Written for a technical but non-developer audience. Explain roles and contributions in plain language.
- Pitching herself: every statement positions her as qualified and ready.
- Specific and data-driven. Reference real organizations, bills, actions, outcomes.
- Statements are direct and to the point. Never vague.

**What to avoid:**
- Generic openers: "I am excited to apply", "I am passionate about", "I look forward to hearing from you"
- Em-dashes (—) anywhere in the letter
- Overly long sentences that bury the point
- Abstract language where concrete language is possible

**Reference examples — match this register and cadence exactly:**

> As an interdisciplinary student, I bring in the unique perspective of someone who thinks beyond purely a legal or technical lens. Much of my concentration revolves around understanding all aspects of public and private systems: learning how regulatory systems are adapting, and how academia can bridge complex technical and regulatory needs into policy insight and action.

> While working for State Senator Aisha Wahab, I tracked California legislation on AI and data privacy, including SB 933, and gave feedback on bills such as SB 403. I also coordinated voter outreach and mentored student volunteers, developing the communication and organizational skills necessary at SVLG for stakeholder engagement and policy advocacy.

**Applying the tone in generated letters:**
- Sentence 1 of each body paragraph: "As a [role] at [company]" + one specific, concrete description of responsibilities
- Sentence 2: specific growth or outcome at that company, not general "I developed skills"
- Sentence 3: direct connection to the target role, framed as readiness
- Closing: name all companies, explain why this company and role specifically, close with a confident call to action (not "I look forward to hearing from you")

## Extending skill coverage

- Add entries to `SKILL_SYNONYMS` in `skill_matcher.py` (key = canonical name, value = list of lowercase variations).
- Add entries to `_CASE_MAP` in `cover_letter.py` for skills needing specific capitalisation.
