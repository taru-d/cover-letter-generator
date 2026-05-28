import re
from collections import defaultdict
from typing import Optional, Tuple

_CASE_MAP = {
    "python": "Python", "sql": "SQL", "aws": "AWS", "ci/cd": "CI/CD",
    "rest api": "REST API", "html": "HTML", "css": "CSS", "api": "API",
    "docker": "Docker", "kubernetes": "Kubernetes", "javascript": "JavaScript",
    "typescript": "TypeScript", "react": "React", "node": "Node.js", "git": "Git",
    "machine learning": "machine learning", "data analysis": "data analysis",
    "project management": "project management", "problem solving": "problem solving",
}

_COMPANY_DESCRIPTORS = {
    "google": "a company renowned for engineering excellence and operating at massive global scale",
    "amazon": "an organization known for its customer obsession, operational rigor, and high-velocity delivery culture",
    "microsoft": "a company at the forefront of enterprise technology and cloud innovation",
    "apple": "an organization celebrated for its uncompromising standards in design and user experience",
    "meta": "a company pushing the boundaries of social technology and large-scale distributed systems",
    "facebook": "a company pushing the boundaries of social technology and large-scale distributed systems",
    "netflix": "an organization known for its engineering culture, autonomy, and performance at scale",
    "uber": "a company that redefined transportation through technology and operates at extraordinary scale",
    "airbnb": "an organization known for its design-driven culture and global marketplace innovation",
    "spotify": "a company recognized for its agile engineering culture and personalization at scale",
    "salesforce": "an organization that pioneered cloud-based enterprise solutions and customer relationship technology",
    "oracle": "a company with deep expertise in enterprise data systems and cloud infrastructure",
    "ibm": "an organization with a long history of innovation in enterprise computing and research",
    "intel": "a company at the foundation of modern computing hardware and semiconductor innovation",
    "nvidia": "an organization leading the way in accelerated computing and artificial intelligence hardware",
    "adobe": "a company known for defining creative and document technology standards worldwide",
    "stripe": "an organization recognized for building elegant, developer-first financial infrastructure",
    "shopify": "a company that empowers entrepreneurs through scalable commerce technology",
    "twitter": "an organization that shaped real-time global communication at scale",
    "x": "an organization that shaped real-time global communication at scale",
    "linkedin": "a company that built the world's largest professional network and talent marketplace",
    "tesla": "an organization known for ambitious engineering and rapid innovation cycles",
    "spacex": "a company celebrated for solving extraordinary engineering challenges under extreme constraints",
    "palantir": "an organization specializing in complex data integration and analytics for high-stakes decision making",
    "databricks": "a company at the forefront of unified data analytics and large-scale data engineering",
    "snowflake": "an organization that redefined cloud data warehousing and cross-cloud data sharing",
    "twilio": "a company known for making communications infrastructure accessible and developer-friendly",
    "square": "an organization that democratized financial technology for businesses of all sizes",
    "block": "an organization that democratized financial technology for businesses of all sizes",
    "coinbase": "a company that brought institutional-grade infrastructure to digital asset markets",
    "doordash": "an organization that scaled complex logistics and real-time marketplace operations",
    "lyft": "a company known for solving real-time matching and routing problems at urban scale",
    "pinterest": "an organization built around visual discovery and recommendation systems at scale",
    "snap": "a company known for pioneering ephemeral communication and augmented reality experiences",
    "robinhood": "an organization that made financial markets accessible through intuitive technology",
    "plaid": "a company that built the connective tissue between consumers and financial institutions",
    "figma": "an organization that transformed collaborative design through real-time browser-based tools",
    "notion": "a company known for reimagining productivity tools with flexibility and elegance",
    "slack": "an organization that redefined workplace communication and team collaboration",
    "zoom": "a company that scaled real-time video infrastructure to serve hundreds of millions globally",
    "atlassian": "an organization known for building tools that power software development teams worldwide",
    "github": "a company that became the home for collaborative software development and open source",
    "gitlab": "an organization that unified the software development lifecycle into a single platform",
    "hashicorp": "a company known for building foundational infrastructure automation tools",
    "elastic": "an organization that made distributed search and observability accessible at any scale",
    "datadog": "a company that built comprehensive monitoring and observability for cloud-scale systems",
    "cloudflare": "an organization known for securing and accelerating internet infrastructure globally",
    "mongodb": "a company that pioneered flexible document databases for modern application development",
    "redis": "an organization known for building the standard in high-performance in-memory data systems",
    "docker": "a company that revolutionized how software is packaged and deployed",
    "vmware": "an organization that pioneered virtualization and multi-cloud infrastructure",
    "cisco": "a company that built the networking backbone of the modern internet",
    "accenture": "an organization known for large-scale technology consulting and digital transformation",
    "deloitte": "a company recognized for its breadth of professional services and enterprise advisory work",
    "mckinsey": "an organization known for rigorous problem solving and strategic advisory at the highest level",
    "jpmorgan": "an institution at the intersection of finance and cutting-edge technology",
    "goldman sachs": "an organization known for its engineering culture within the financial services industry",
    "bloomberg": "a company that built the definitive platform for financial data and analytics",
    "capital one": "an organization that positioned itself as a technology company operating in financial services",
    "walmart": "a company operating retail technology at a scale matched by very few organizations globally",
    "target": "an organization known for combining retail innovation with strong in-house technology teams",
}

_MIN_WORDS = 420
_MAX_WORDS = 650

_JD_VERBS = re.compile(
    r"\b(build|design|develop|create|implement|maintain|lead|manage|deliver|"
    r"architect|optimize|deploy|analyze|support|scale|drive|own|collaborate|"
    r"write|draft|research|coordinate|communicate|respond|facilitate|prepare|"
    r"review|assess|evaluate|identify|report|track|monitor|work\s+on)\b",
    re.IGNORECASE,
)

_CONTEXT_PHRASES = [
    "gaining hands-on experience that required both independent judgment and clear stakeholder communication",
    "building the kind of practical expertise that comes from working on real deliverables with real stakes",
    "developing a professional discipline grounded in accountability, rigor, and cross-functional collaboration",
    "cultivating the professional instincts that only emerge from navigating complex, ambiguous work environments",
    "strengthening my capacity to deliver high-quality results in environments with competing priorities",
    "deepening my understanding of how organizations operate effectively under real-world constraints",
]


def generate_cover_letter(
    matches: list,
    job_title: str,
    company: str,
    experiences: list,
    candidate_name: str = "",
    job_description: str = "",
    ranked_bullets: list = None,
    jd_requirements: list = None,
) -> str:
    """Generate a 5-paragraph cover letter (450–650 words):
    opening → 3 body paragraphs (one per experience) → closing.
    Never references skills or bullet points explicitly.
    Always uses real company names from the resume.
    """
    real_experiences = [
        e for e in experiences
        if e["title"] != "Professional Experience" and e["company"].lower() != "various"
    ]

    # If the parser could not extract structured experiences, use whatever it produced
    # (including the "Various" fallback) so the letter is never left with zero experiences.
    if not real_experiences:
        real_experiences = experiences[:]

    selected_experiences = _select_experiences(matches, real_experiences)

    opening = _build_opening(job_title, company, selected_experiences, candidate_name, job_description, matches, real_experiences)
    body_paragraphs = _build_body_paragraphs(selected_experiences, job_title, company, job_description, matches, ranked_bullets)
    closing = _build_closing(job_title, company, selected_experiences, candidate_name, job_description)

    sign_off = f"Sincerely,\n{candidate_name}" if candidate_name else "Sincerely,\n[Your Name]"
    all_paragraphs = [p for p in [opening] + body_paragraphs + [closing] if p.strip()]
    letter_body = "\n\n".join(all_paragraphs)
    letter_body = _enforce_word_count(letter_body, job_title, company, selected_experiences, candidate_name)
    letter_body = _post_review(letter_body)
    return "Dear Hiring Manager,\n\n" + letter_body + f"\n\n{sign_off}"


# ── Extraction helpers (used by app.py to pre-fill UI fields) ─────────────────

def extract_job_title(job_description: str) -> str:
    lines = job_description.strip().split("\n")[:3]
    for line in lines:
        line = line.strip()
        cleaned = re.sub(r"^(job title|position|role)\s*[:|-]\s*", "", line, flags=re.IGNORECASE)
        at_match = re.match(r"^(.+?)\s+at\s+.+$", cleaned, re.IGNORECASE)
        if at_match:
            title = at_match.group(1).strip()
            if title and len(title) < 60:
                return title
        if cleaned and 3 < len(cleaned) < 60 and not cleaned.startswith(("http", "www")):
            return cleaned
    return ""


def extract_company(job_description: str) -> str:
    lines = job_description.strip().split("\n")[:3]
    for line in lines:
        at_match = re.match(
            r"^.+?\s+at\s+([A-Z][A-Za-z0-9\s&.]+?)(?:\s*[,.\n]|$)", line.strip()
        )
        if at_match:
            company = at_match.group(1).strip()
            if 2 < len(company) < 40:
                return company
    for pattern in [
        r"(?:with|for|join)\s+([A-Z][A-Za-z0-9\s&.]+?)(?:\s*[,.\n]|\s+is\b|\s+as\b)",
        r"(?:company|organization)\s*[:|-]\s*(.+?)(?:\n|$)",
    ]:
        match = re.search(pattern, job_description[:500])
        if match:
            company = match.group(1).strip()
            if 2 < len(company) < 40:
                return company
    return ""


# ── Experience selection ─────────────────────────────────────────────────────

def _select_experiences(matches: list, real_experiences: list) -> list:
    """Select up to 3 experiences ranked by match relevance."""
    score_by_key: dict = defaultdict(int)
    for m in matches:
        key = (m["job_title"], m["company"])
        score_by_key[key] += m.get("score", 1)

    ranked_keys = sorted(score_by_key, key=lambda k: score_by_key[k], reverse=True)

    selected = []
    used_keys = set()

    for key in ranked_keys[:3]:
        exp = next((e for e in real_experiences if e["title"] == key[0] and e["company"] == key[1]), None)
        if exp:
            selected.append(exp)
            used_keys.add(key)

    for exp in real_experiences:
        if len(selected) >= 3:
            break
        key = (exp["title"], exp["company"])
        if key not in used_keys:
            selected.append(exp)
            used_keys.add(key)

    return selected[:3]


# ── Paragraph builders ────────────────────────────────────────────────────────

def _build_opening(
    job_title: str,
    company: str,
    selected_experiences: list,
    candidate_name: str,
    job_description: str,
    matches: list,
    real_experiences: list = None,
) -> str:
    company_phrase = f" at {company}" if company else ""

    if candidate_name:
        sentence1 = (
            f"My name is {candidate_name} and I am writing to apply for the "
            f"{job_title} position{company_phrase}."
        )
    else:
        sentence1 = f"I am writing to apply for the {job_title} position{company_phrase}."

    # Opening sentence 2 references the most recent experience (first in resume order),
    # not the highest-match experience, per the CLAUDE.md spec.
    exp_for_opening = None
    if real_experiences:
        exp_for_opening = real_experiences[0]
    elif selected_experiences:
        exp_for_opening = selected_experiences[0]

    if exp_for_opening:
        clean_title = _clean_job_title_for_prose(exp_for_opening["title"])
        article = "an" if clean_title[0].lower() in "aeiou" else "a"
        sentence2 = (
            f"As {article} {clean_title} at {exp_for_opening['company']}, "
            f"I built the experience and professional instincts this role demands."
        )
    else:
        sentence2 = (
            "My professional background aligns closely with the requirements of this role."
        )

    return f"{sentence1} {sentence2}"


def _build_body_paragraphs(
    selected_experiences: list,
    job_title: str,
    company: str,
    job_description: str,
    matches: list,
    ranked_bullets: list = None,
) -> list:
    """Return exactly 3 body paragraphs — one per selected experience (paragraphs 2–4)."""
    paragraphs = []
    jd_themes = _extract_jd_themes(job_description)
    company_ref = company if company else "your organization"
    used_jd_phrases: set = set()  # prevent the same JD phrase in every S3

    for i in range(3):
        if i < len(selected_experiences):
            para = _build_single_body_paragraph(
                selected_experiences[i], job_title, company, job_description,
                matches, jd_themes, i, ranked_bullets, used_jd_phrases
            )
        else:
            fallback_exp = selected_experiences[-1] if selected_experiences else None
            para = _build_supplemental_body_paragraph(
                fallback_exp, job_title, company_ref, matches, jd_themes, i
            )
        paragraphs.append(para)

    return paragraphs


def _s1_open(
    index: int, article: str, title: str, company: str, bullet: Optional[str]
) -> str:
    """Sentence 1: introduce role and core activity. Structure is distinct per paragraph index."""
    if bullet:
        if index == 0:
            return f"As {article} {title} at {company}, I {bullet}."
        elif index == 1:
            return f"At {company}, where I served as {article} {title}, I {bullet}."
        else:
            # "During my time as..." works cleanly with any past-tense verb
            return f"During my time as {article} {title} at {company}, I {bullet}."
    else:
        if index == 0:
            return (
                f"As {article} {title} at {company}, I took on cross-functional work "
                f"that required independent judgment and consistent execution."
            )
        elif index == 1:
            return (
                f"At {company}, I contributed as {article} {title} across initiatives "
                f"that spanned planning, coordination, and direct stakeholder engagement."
            )
        else:
            return (
                f"My work as {article} {title} at {company} involved managing complex "
                f"projects under real professional constraints."
            )


def _s2_growth(index: int, company: str) -> str:
    """Sentence 2: what I learned. Each index uses a structurally distinct sentence."""
    if index == 0:
        return (
            f"Working at {company} taught me how to communicate complex ideas clearly "
            f"and deliver results across competing priorities."
        )
    elif index == 1:
        return (
            f"Through this role at {company}, I gained a sharper sense of how "
            f"high-performing teams align on goals and follow through effectively."
        )
    else:
        return (
            f"{company} held me to a high standard of rigor and stakeholder awareness, "
            f"a discipline I have carried into every role since."
        )


def _s3_connect(
    index: int, job_title: str, company_ref: str, jd_phrase: Optional[str]
) -> str:
    """Sentence 3: connect experience to target role. Each index uses a distinct structure."""
    if index == 0:
        if jd_phrase:
            return f"That background gives me the foundation to {jd_phrase} at {company_ref}."
        return f"That background gives me a strong foundation for the {job_title} role at {company_ref}."
    elif index == 1:
        if jd_phrase:
            return f"I bring those same capabilities to {jd_phrase} as a {job_title} at {company_ref}."
        return f"I bring those same capabilities to the {job_title} position at {company_ref}."
    else:
        if jd_phrase:
            return f"That experience maps directly to the need to {jd_phrase} at {company_ref}."
        return f"That background prepared me directly for the demands of the {job_title} role at {company_ref}."


def _s4_reinforce(index: int, job_title: str) -> str:
    """Sentence 4: concrete professional takeaway. Avoids repeating company name or S2/S3 language."""
    if index == 0:
        return (
            "Delivering accurate, well-reasoned work under real deadlines is the habit "
            "I rely on most when the stakes are high."
        )
    elif index == 1:
        return (
            "I developed there a clear sense of how to earn trust quickly, "
            "deliver on commitments, and communicate progress without being prompted."
        )
    else:
        return (
            f"It sharpened my professional judgment in ways that translate directly to this role."
        )


def _build_single_body_paragraph(
    exp: dict,
    job_title: str,
    hiring_company: str,
    job_description: str,
    matches: list,
    jd_themes: list,
    index: int,
    ranked_bullets: list = None,
    used_jd_phrases: set = None,
) -> str:
    """3-sentence body paragraph. Each of the three paragraphs (index 0/1/2) uses
    completely different sentence structures so no phrase ever repeats across them."""
    title = _clean_job_title_for_prose(exp["title"])
    exp_company = exp["company"]
    article = "an" if title[0].lower() in "aeiou" else "a"
    company_ref = hiring_company if hiring_company else "your organization"

    # Find best ranked bullet — must be a genuine past-tense action statement
    best_rb = None
    if ranked_bullets:
        for rb in ranked_bullets:
            if (rb["company"] == exp_company
                    and rb["job_title"] == exp["title"]
                    and _is_action_bullet(rb["bullet"])
                    and _bullet_is_verb_led(_clean_bullet_for_prose(rb["bullet"]))):
                best_rb = rb
                break

    bullet_prose = _clean_bullet_for_prose(best_rb["bullet"]) if best_rb else None
    sentence1 = _s1_open(index, article, title, exp_company, bullet_prose)

    sentence2 = _s2_growth(index, exp_company)

    # JD connection: use matched duty phrase, then JD theme — skip any already used
    # across paragraphs so S3 never says the same thing in two consecutive paragraphs.
    used = used_jd_phrases if used_jd_phrases is not None else set()
    jd_phrase = None
    if best_rb and best_rb.get("jd_duty"):
        candidate = _extract_verb_phrase_from_duty(best_rb["jd_duty"])
        if candidate and candidate not in used:
            jd_phrase = candidate
    if not jd_phrase:
        for theme in jd_themes:
            if theme not in used:
                jd_phrase = theme
                break
    if jd_phrase:
        used.add(jd_phrase)
    sentence3 = _s3_connect(index, job_title, company_ref, jd_phrase)

    sentence4 = _s4_reinforce(index, job_title)

    return f"{sentence1} {sentence2} {sentence3} {sentence4}"


def _build_supplemental_body_paragraph(
    exp: Optional[dict],
    job_title: str,
    company_ref: str,
    matches: list,
    jd_themes: list,
    index: int,
) -> str:
    """Supplemental paragraph when fewer than 3 distinct experiences exist.
    Uses unique framing ('Beyond...') to differentiate from the main body paragraphs."""
    if exp is None:
        return (
            f"Across my career I have consistently sought roles that demand clear thinking, "
            f"strong execution, and the ability to collaborate across different stakeholder groups. "
            f"Each position has built on the last and sharpened the professional instincts "
            f"I bring to the {job_title} role at {company_ref}."
        )

    exp_company = exp["company"]
    title = _clean_job_title_for_prose(exp["title"])
    article = "an" if title[0].lower() in "aeiou" else "a"

    sentence1 = (
        f"Beyond my core responsibilities as {article} {title} at {exp_company}, "
        f"I also contributed to cross-functional work that broadened my perspective "
        f"on how organizations coordinate and execute at scale."
    )

    # Growth sentence for supplemental — uses a unique structure not used in main paragraphs
    sentence2 = (
        f"This background gave me a practical understanding of how to navigate "
        f"ambiguity, manage competing priorities, and deliver under real constraints."
    )

    theme = jd_themes[index] if index < len(jd_themes) else ""
    if theme:
        sentence3 = (
            f"The breadth of that experience positions me well to {theme} "
            f"in the {job_title} role at {company_ref}."
        )
    else:
        sentence3 = (
            f"Together, these experiences position me well for the {job_title} "
            f"role at {company_ref}."
        )

    return f"{sentence1} {sentence2} {sentence3}"


def _build_closing(
    job_title: str,
    company: str,
    selected_experiences: list,
    candidate_name: str,
    job_description: str = "",
) -> str:
    company_ref = company if company else "your organization"

    company_names = [e["company"] for e in selected_experiences[:3]]
    if len(company_names) >= 2:
        companies_str = _join_list(company_names)
        sentence1 = (
            f"My experience across {companies_str} built the practical foundation this role demands."
        )
    elif company_names:
        sentence1 = (
            f"My experience at {company_names[0]} built a strong, practical foundation "
            f"for this role."
        )
    else:
        sentence1 = f"My professional experience built a strong foundation for this role."

    hiring_descriptor = _company_descriptor(company_ref)
    sentence2 = f"I am drawn to {company_ref} because it is {hiring_descriptor}."
    sentence2b = (
        f"I want to bring my skills and drive to an organization that operates at that level."
    )

    sentence3 = (
        f"The {job_title} position is exactly the next step I have been working toward, "
        f"and I am fully prepared to contribute from day one."
    )

    sentence4 = (
        f"I would welcome the chance to discuss how my background aligns with what "
        f"{company_ref} is building, and I am available at your convenience."
    )

    return f"{sentence1} {sentence2} {sentence2b} {sentence3} {sentence4}"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _bullet_to_prose(bullet: str) -> str:
    """Legacy minimal cleaner — prefer _clean_bullet_for_prose for all new call sites."""
    cleaned = re.sub(r"^[-•*\d.)\s]+", "", bullet).strip()
    if not cleaned:
        return bullet.strip()
    return cleaned[0].lower() + cleaned[1:]


def _clean_bullet_for_prose(bullet: str) -> str:
    """Clean and lightly paraphrase a resume bullet for natural prose insertion after 'I ...'.

    Fixes:
    - Trailing punctuation artifacts including '.,', ',,' combinations
    - Embedded punctuation errors (e.g. "protections.,")
    - Verbose filler phrases ("in order to", "was responsible for")
    - Overly long bullets trimmed to a natural breakpoint (~14–16 words)
    - Lowercases first character so 'I [text]' reads grammatically
    """
    text = re.sub(r"^[-•*\d.)\s]+", "", bullet).strip()
    # Strip all trailing punctuation artifacts (handles ".,", ".,,", etc.)
    text = re.sub(r"[\s.,;:!?]+$", "", text).strip()
    # Fix embedded punctuation errors: "word.," → "word," and ".,word" → ", word"
    text = re.sub(r"\.,", ", ", text)
    text = re.sub(r",\.", ", ", text)
    # Normalize whitespace
    text = re.sub(r"\s{2,}", " ", text).strip()
    # Light structural improvements — only safe rewrites that don't break verb agreement
    text = re.sub(r"\bfor scope of\b", "to evaluate the scope of", text, flags=re.IGNORECASE)
    text = re.sub(r"\bfor the purpose of\b", "to", text, flags=re.IGNORECASE)
    text = re.sub(r"\bin order to\b", "to", text, flags=re.IGNORECASE)
    # Convert "was responsible for [gerund]" to just the past-tense verb
    # e.g. "was responsible for drafting X" → "drafted X"
    def _depassivize(m: re.Match) -> str:
        gerund = m.group(1)  # e.g. "drafting"
        stem = gerund[:-3]   # strip "-ing"
        return (stem + "d" if stem.endswith("e") else stem + "ed")
    text = re.sub(r"\bwas responsible for (\w+ing)\b", _depassivize, text, flags=re.IGNORECASE)
    # Insert missing "the" before specific direct-object nouns that resume bullets commonly omit.
    # e.g. "populated dataset with clauses" → "populated the dataset with clauses"
    _ARTICLE_NOUNS = (
        r"(dataset|database|spreadsheet|repository|codebase|schema|table|registry|"
        r"catalog|inventory|pipeline|dashboard|backlog|roadmap|agenda|budget|report|"
        r"proposal|model)\b"
    )
    text = re.sub(
        r"\b(populated|queried|updated|cleaned|migrated|built|organized|maintained|"
        r"managed|created|analyzed|reviewed|processed)\b\s+"
        r"(?!a\b|an\b|the\b|this\b|our\b|their\b|all\b|each\b|every\b|\d)" + _ARTICLE_NOUNS,
        lambda m: m.group(1) + " the " + m.group(2),
        text,
        flags=re.IGNORECASE,
    )
    # Convert a leading gerund to past tense so "I [verb]" is grammatical.
    # "Analyzing policies..." → "analyzed policies..."
    # "Coordinating events..." → "coordinated events..."
    words = text.split()
    if words:
        fw = words[0]
        if fw.lower().endswith("ing") and len(fw) > 4:
            stem = fw[:-3]  # "analyzing" → "analyz"
            past = (stem + "d") if stem.endswith("e") else (stem + "ed")
            text = past + text[len(fw):]
    # Trim overly long bullets at a natural word-boundary (~14–16 words)
    words = text.split()
    if len(words) > 16:
        _NATURAL_CUT = {"for", "in", "on", "by", "with", "from", "of", "at", "as",
                        "across", "via", "into", "through", "during", "among"}
        cut = 14
        for i in range(min(16, len(words) - 1), 9, -1):
            if words[i].lower() in _NATURAL_CUT:
                cut = i
                break
        text = " ".join(words[:cut])
        text = re.sub(r"[\s.,;:]+$", "", text)
    # Strip dangling ", [gerund]" at end — occurs when a bullet is trimmed mid-phrase,
    # leaving an incomplete participial like "...in the United States, analyzing"
    text = re.sub(r",\s+[a-z]+ing$", "", text).strip()
    # Lowercase first character for "I [text]" construction
    if text:
        text = text[0].lower() + text[1:]
    return text


def _clean_job_title_for_prose(title: str) -> str:
    """Adapt a job title for natural use in a sentence.

    Converts 'Title - Department' to 'Title in Department' so that
    'As a Research Intern - Legal and Regulatory Compliance' becomes
    'As a Research Intern in Legal and Regulatory Compliance'.
    Also normalises any stray punctuation that would look robotic in prose.
    """
    # Replace " - Dept" / " – Dept" separators with " in Dept"
    title = re.sub(r"\s*[-–—]\s*([A-Z])", lambda m: " in " + m.group(1), title)
    # Normalise whitespace
    title = re.sub(r"\s+", " ", title).strip()
    return title


def _canonical_skill_name(skill: str) -> str:
    """Return the properly cased display name for a skill."""
    return _CASE_MAP.get(skill.lower(), skill.title())


def _company_descriptor(company_name: str) -> str:
    """Return a specific descriptor for a known company, or a generic professional one."""
    key = company_name.strip().lower()
    for known, desc in _COMPANY_DESCRIPTORS.items():
        if known in key or key in known:
            return desc
    return "an organization with a strong reputation for delivering high-quality work"


_KNOWN_IRREGULAR_VERBS = {
    "led", "ran", "built", "wrote", "drove", "made", "set", "met", "won",
    "grew", "kept", "held", "gave", "came", "went", "got", "put", "cut",
    "let", "hit", "read", "found", "left", "sent", "took", "brought",
    "drew", "spoke", "worked", "helped", "served", "taught", "learned",
}


def _is_action_bullet(text: str) -> bool:
    """Return True if text is a genuine action statement (not a raw skills list)."""
    if not text:
        return False
    lower = text.lower().strip()
    _LABELS = (
        "skills", "technical skills", "tools", "technologies", "frameworks",
        "languages", "proficiencies", "competencies", "certifications",
        "expertise", "areas of expertise", "key skills", "core skills",
        "programming languages", "software", "platforms",
    )
    for label in _LABELS:
        if lower.startswith(label + ":") or lower.startswith(label + " :"):
            return False
    parts = re.split(r",\s*", text)
    if len(parts) >= 3:
        avg_words = sum(len(p.split()) for p in parts) / len(parts)
        if avg_words <= 2.5:
            return False
    return True


def _bullet_is_verb_led(bullet: str) -> bool:
    """Return True if the bullet begins with a past-tense action verb, making 'I [bullet]' grammatical.

    Accepts past-tense (-ed, -ied) and known irregular past tenses.
    Rejects gerunds (-ing) because 'I analyzing X' is not grammatical —
    _clean_bullet_for_prose converts gerunds to past tense before this is called.
    """
    first_word = bullet.strip().split()[0].lower().rstrip(",.;:") if bullet.strip() else ""
    if not first_word:
        return False
    # Past-tense regular verbs only (-ed / -ied), NOT gerunds (-ing)
    if re.search(r"(ed|ied)$", first_word):
        return True
    return first_word in _KNOWN_IRREGULAR_VERBS


def _derive_context_phrase(bullet: str, index: int) -> str:
    """Return a natural context phrase that follows 'I [bullet activity]' in a sentence."""
    b = bullet.lower()
    if any(v in b for v in ["wrote", "write", "written", "draft", "authored", "edit", "brief", "memo", "policy", "report"]):
        return "developing a strong command of professional writing and the ability to communicate complex ideas with clarity"
    if any(v in b for v in ["research", "analyz", "evaluat", "assess", "investigat", "identif", "compil"]):
        return "sharpening my analytical instincts and my ability to synthesize information into clear, actionable insights"
    if any(v in b for v in ["manag", "led ", "direct", "supervis", "coordinat", "oversee", "facilitat"]):
        return "strengthening my ability to keep complex work moving forward while maintaining alignment across all stakeholders"
    if any(v in b for v in ["presented", "communicated", "briefed", "responded", "interview"]):
        return "refining my ability to communicate clearly and build productive relationships across different audiences"
    if any(v in b for v in ["support", "assist", "help", "constituent", "client", "customer"]):
        return "developing a service-oriented mindset and the ability to meet the needs of diverse stakeholders effectively"
    return _CONTEXT_PHRASES[index % len(_CONTEXT_PHRASES)]


_PHRASE_NOUN_WORDS = {
    "advocacy", "policy", "policies", "communications", "associate", "analyst",
    "specialist", "coordinator", "consultant", "director", "manager", "officer",
    "administrator", "representative", "education", "affairs", "outreach",
    "engagement", "awareness", "compliance", "governance", "oversight",
}


def _jd_phrase_is_valid(phrase: str) -> bool:
    """Return True if phrase is a grammatical infinitive fragment (verb-led, not a noun list)."""
    if not phrase:
        return False
    words = phrase.split()
    # Reject if a comma appears in the first 5 words — signals a noun list
    if "," in " ".join(words[:5]):
        return False
    # Reject if any word after the first is a known professional noun
    if any(w.lower().rstrip("s") in _PHRASE_NOUN_WORDS for w in words[1:]):
        return False
    return True


def _extract_verb_phrase_from_duty(duty: str) -> str:
    """Extract a usable verb phrase from a JD duty line for use after 'to ...'."""
    cleaned = re.sub(
        r"^(you\s+will|candidate\s+will|responsibilities\s+include|we\s+need\s+you\s+to|"
        r"the\s+role\s+requires|this\s+role\s+requires|ability\s+to|must\s+be\s+able\s+to)\s+",
        "",
        duty.strip(),
        flags=re.IGNORECASE,
    ).strip()
    verb_match = _JD_VERBS.search(cleaned)
    if not verb_match:
        return ""
    fragment = cleaned[verb_match.start():].split(".")[0]
    result = _trim_fragment(fragment)
    if not result or len(result) <= 6:
        return ""
    return result.lower() if _jd_phrase_is_valid(result) else ""


def _extract_jd_themes(job_description: str) -> list:
    """Extract action-oriented themes from the JD for use in body paragraph sentence 3."""
    if not job_description:
        return []

    themes = []
    sentences = re.split(r"(?<=[.!?])\s+|\n", job_description)
    for sentence in sentences:
        stripped = sentence.strip().lstrip("-•* ")
        if re.match(r"^\d+\+?\s*(years?|months?)\s+(of\s+)?", stripped, re.IGNORECASE):
            continue
        cleaned = re.sub(
            r"^(you\s+will|candidate\s+will|responsibilities\s+include|we\s+need\s+you\s+to|"
            r"the\s+role\s+requires|this\s+role\s+requires)\s+",
            "",
            stripped,
            flags=re.IGNORECASE,
        ).strip()
        verb_match = _JD_VERBS.search(cleaned)
        if verb_match:
            fragment = cleaned[verb_match.start():].split(".")[0]
            result = _trim_fragment(fragment)
            if len(result) > 10 and _jd_phrase_is_valid(result):
                themes.append(result.lower())
                if len(themes) >= 3:
                    break

    return themes


def _trim_fragment(text: str) -> str:
    """Trim a JD fragment to produce a grammatically complete phrase."""
    words = text.split()
    if len(words) <= 5:
        return " ".join(words).rstrip(".,;:")
    tail_words = {"of", "for", "with", "and", "or", "that", "which", "to", "in", "on",
                  "by", "as", "the", "a", "an", "using", "through", "via", "into", "across"}
    end = min(len(words), 8)
    best_cut = None
    for i in range(end, 2, -1):
        if i >= len(words):
            continue
        if words[i].lower() in tail_words:
            best_cut = i
            break
    if best_cut and best_cut >= 3:
        return " ".join(words[:best_cut]).rstrip(".,;:")
    return " ".join(words[:min(5, len(words))]).rstrip(".,;:")


def _join_list(items: list) -> str:
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


def _split_if_long(sent: str) -> str:
    """Split a sentence over 25 words at the best natural break. Returns one or two sentences.

    NOTE: em dash splits are skipped here because _post_review strips all em-dashes
    globally. Role/action patterns are handled explicitly instead.
    """
    if len(sent.split()) <= 25:
        return sent

    # Pattern: "At Company, where I served as ROLE, I ACTION"
    m = re.match(
        r"^(At .+?),\s+where\s+I\s+served\s+as\s+(an?\s+.+?),\s+I\s+(.+)",
        sent, re.IGNORECASE,
    )
    if m:
        anchor, role, action = m.group(1), m.group(2), m.group(3).rstrip(".")
        s1 = f"{anchor}, I served as {role}."
        s2 = f"I {action}."
        if len(s1.split()) <= 25 and len(s2.split()) <= 25:
            return f"{s1} {s2}"

    # Pattern: "As ARTICLE ROLE at COMPANY, I ACTION"
    m = re.match(
        r"^As (an?\s+.+?)\s+at\s+(.+?),\s+I\s+(.+)",
        sent, re.IGNORECASE,
    )
    if m:
        role, company_part, action = m.group(1), m.group(2), m.group(3).rstrip(".")
        s1 = f"I served as {role} at {company_part}."
        s2 = f"I {action}."
        if len(s1.split()) <= 25 and len(s2.split()) <= 25:
            return f"{s1} {s2}"

    # Pattern: "During my time as ROLE at COMPANY, I ACTION"
    m = re.match(
        r"^During my time as (an?\s+.+?)\s+at\s+(.+?),\s+I\s+(.+)",
        sent, re.IGNORECASE,
    )
    if m:
        role, company_part, action = m.group(1), m.group(2), m.group(3).rstrip(".")
        s1 = f"I worked as {role} at {company_part}."
        s2 = f"I {action}."
        if len(s1.split()) <= 25 and len(s2.split()) <= 25:
            return f"{s1} {s2}"

    # Generic: split at ", and " after at least word 10
    words = sent.split()
    for i in range(10, min(22, len(words) - 1)):
        if words[i].lower() == "and" and i > 0 and words[i - 1].endswith(","):
            part1 = " ".join(words[:i]).rstrip(",") + "."
            part2 = " ".join(words[i + 1:])
            if part2:
                part2 = part2[0].upper() + part2[1:]
            if len(part1.split()) >= 5 and len(part2.split()) >= 4:
                return f"{part1} {part2}"

    return sent  # no safe split found


def _post_review(letter_body: str) -> str:
    """Run the 6-point quality checklist on the generated letter body.

    1. Complete thoughts: strip dangling trailing conjunctions
    2. Missing articles: targeted patterns (bulk handled in _clean_bullet_for_prose)
    3. Trailing comma before period: fix
    4. Repeated phrases: JD phrase deduplication handled in _build_body_paragraphs
    5. Logical flow: enforced by paragraph templates — no extra pass needed
    6. Sentence length: split any sentence over 25 words
    """
    # Tone rule: no em-dashes anywhere in the letter
    letter_body = re.sub(r"\s*—\s*", ", ", letter_body)

    # Check 3: comma directly before a period e.g. "I compiled data,."
    letter_body = re.sub(r",\s*\.", ".", letter_body)

    # Check 1: sentence that ends with a bare conjunction before the period
    letter_body = re.sub(r"\b(and|but|or|so)\s*\.", ".", letter_body)

    # Check 6: split sentences over 25 words
    paragraphs = letter_body.split("\n\n")
    reviewed = []
    for para in paragraphs:
        parts = re.split(r"(?<=[.!?])\s+", para)
        parts = [_split_if_long(p) for p in parts]
        reviewed.append(" ".join(parts))
    return "\n\n".join(reviewed)


def _enforce_word_count(
    letter_body: str,
    job_title: str,
    company: str,
    selected_experiences: list,
    candidate_name: str,
) -> str:
    """Expand or trim the letter body to stay within 450–650 words."""
    word_count = len(letter_body.split())

    if word_count > _MAX_WORDS:
        return _trim_to_max(letter_body)

    if word_count < _MIN_WORDS:
        expansion_sentences = _generate_expansion_sentences(
            job_title, company, selected_experiences, candidate_name
        )
        idx = 0
        while len(letter_body.split()) < _MIN_WORDS and idx < len(expansion_sentences):
            # Insert into the closing paragraph (last paragraph) BEFORE the final sentence
            # so the call-to-action always remains the last sentence of the letter.
            parts = letter_body.rsplit("\n\n", 1)
            if len(parts) == 2:
                closing = parts[1]
                last_period = closing.rfind(". ")
                if last_period > len(closing) // 3:
                    # Insert the expansion sentence before the final sentence
                    parts[1] = (
                        closing[: last_period + 2]
                        + expansion_sentences[idx]
                        + " "
                        + closing[last_period + 2:]
                    )
                else:
                    parts[1] = closing + " " + expansion_sentences[idx]
                letter_body = "\n\n".join(parts)
            else:
                letter_body = letter_body + " " + expansion_sentences[idx]
            idx += 1

        if len(letter_body.split()) > _MAX_WORDS:
            letter_body = _trim_to_max(letter_body)

    return letter_body


def _trim_to_max(text: str) -> str:
    """Trim text to _MAX_WORDS, cutting at the last sentence boundary."""
    words = text.split()
    if len(words) <= _MAX_WORDS:
        return text
    truncated = " ".join(words[:_MAX_WORDS])
    last_period = truncated.rfind(".")
    if last_period > len(truncated) // 2:
        truncated = truncated[: last_period + 1]
    return truncated


def _generate_expansion_sentences(
    job_title: str, company: str, selected_experiences: list, candidate_name: str
) -> list:
    """Generate additional sentences to reach the minimum word count.
    Phrases here must not duplicate any language used in the body paragraphs."""
    company_ref = company if company else "your organization"
    sentences = []

    if selected_experiences:
        exp = selected_experiences[0]
        sentences.append(
            f"The discipline I developed at {exp['company']}, learning to prioritize clearly "
            f"and follow through reliably, is one I apply to every role."
        )

    sentences.append(
        f"Everything I know about {company_ref} tells me this role has high standards "
        f"and meaningful work, which is exactly what I seek out."
    )

    if len(selected_experiences) >= 2:
        exp = selected_experiences[1]
        sentences.append(
            f"At {exp['company']}, I learned that effective contributors understand "
            f"the broader mission, not just their immediate tasks."
        )

    sentences.append(
        f"I approach every role intent on adding clear, measurable value, "
        f"and the {job_title} position at {company_ref} is no exception."
    )

    if len(selected_experiences) >= 3:
        exp = selected_experiences[2]
        sentences.append(
            f"My work at {exp['company']} reinforced that good judgment "
            f"and reliable execution matter more than any credential."
        )

    return sentences
