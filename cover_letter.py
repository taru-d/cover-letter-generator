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

_MIN_WORDS = 450
_MAX_WORDS = 650


def generate_cover_letter(
    matches: list,
    job_title: str,
    company: str,
    experiences: list,
    candidate_name: str = "",
    job_description: str = "",
) -> str:
    """Generate a 5-paragraph cover letter (450–650 words):
    opening (2+ sentences) → 3 body paragraphs (3+ sentences each) → closing (3+ sentences).
    Never references skills explicitly. Always names companies from the resume.
    Uses 'As a [role] at [company]' structure without pulling from bullet points.
    """
    real_experiences = [
        e for e in experiences
        if e["title"] != "Professional Experience" and e["company"].lower() != "various"
    ]

    selected_experiences = _select_experiences(matches, real_experiences)

    opening = _build_opening(job_title, company, selected_experiences, candidate_name, job_description)
    body_paragraphs = _build_body_paragraphs(selected_experiences, job_title, company, job_description)
    closing = _build_closing(job_title, company, selected_experiences, candidate_name)

    sign_off = f"Sincerely,\n{candidate_name}" if candidate_name else "Sincerely,\n[Your Name]"
    all_paragraphs = [p for p in [opening] + body_paragraphs + [closing] if p.strip()]
    letter_body = "\n\n".join(all_paragraphs)
    letter_body = _enforce_word_count(letter_body, job_title, company, selected_experiences, candidate_name)
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
    """Select up to 3 experiences to feature, ranked by match relevance."""
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
) -> str:
    company_phrase = f" at {company}" if company else ""

    if candidate_name:
        sentence1 = (
            f"My name is {candidate_name} and I am writing to express my strong interest "
            f"in the {job_title} position{company_phrase}."
        )
    else:
        sentence1 = f"I am writing to express my strong interest in the {job_title} position{company_phrase}."

    if selected_experiences:
        recent = selected_experiences[0]
        article = "an" if recent["title"][0].lower() in "aeiou" else "a"
        descriptor = _company_descriptor(recent["company"])
        sentence2 = (
            f"As {article} {recent['title']} at {recent['company']}, {descriptor}, "
            f"I have developed a deep understanding of what it takes to deliver meaningful "
            f"results in a fast-paced, technically demanding environment."
        )
    else:
        sentence2 = (
            "Throughout my career, I have developed a deep understanding of what it takes to "
            "deliver meaningful results in a fast-paced, technically demanding environment."
        )

    company_ref = company if company else "your team"
    sentence3 = (
        f"My professional background aligns closely with what this role demands, and I am "
        f"confident that I can contribute meaningfully to {company_ref} from the very first day."
    )

    return f"{sentence1} {sentence2} {sentence3}"


def _build_body_paragraphs(
    selected_experiences: list,
    job_title: str,
    company: str,
    job_description: str,
) -> list:
    """Return exactly 3 body paragraphs. If fewer than 3 experiences exist,
    generate additional paragraphs that still reference available experiences
    from different angles."""
    paragraphs = []
    jd_themes = _extract_jd_themes(job_description)
    company_ref = company if company else "your organization"

    for i in range(3):
        if i < len(selected_experiences):
            para = _build_single_body_paragraph(
                selected_experiences[i], job_title, company, job_description, jd_themes, i
            )
        else:
            para = _build_supplemental_body_paragraph(
                selected_experiences, job_title, company_ref, jd_themes, i
            )
        paragraphs.append(para)

    return paragraphs


def _build_single_body_paragraph(
    exp: dict,
    job_title: str,
    hiring_company: str,
    job_description: str,
    jd_themes: list,
    index: int,
) -> str:
    """3+ sentence body paragraph for one experience. Uses 'As a [role] at [company]' structure.
    Does NOT pull from bullet points — describes the experience in general professional terms.
    """
    title = exp["title"]
    exp_company = exp["company"]
    article = "an" if title[0].lower() in "aeiou" else "a"
    company_ref = hiring_company if hiring_company else "your organization"

    descriptor = _company_descriptor(exp_company)

    _role_descriptions = [
        (
            f"As {article} {title} at {exp_company}, {descriptor}, I took ownership of complex "
            f"projects that required both technical depth and clear communication with stakeholders "
            f"across the organization."
        ),
        (
            f"As {article} {title} at {exp_company}, {descriptor}, I was responsible for driving "
            f"initiatives that had a direct impact on the quality and reliability of the products "
            f"my team delivered to users."
        ),
        (
            f"As {article} {title} at {exp_company}, {descriptor}, I contributed to work that "
            f"demanded creative problem solving, attention to detail, and the ability to deliver "
            f"under tight deadlines while maintaining high standards."
        ),
    ]
    sentence1 = _role_descriptions[index % len(_role_descriptions)]

    _growth_descriptions = [
        (
            f"Working at {exp_company} challenged me to grow as both a technical contributor and "
            f"a collaborator, and I consistently delivered work that exceeded expectations and "
            f"earned the trust of my colleagues and leadership."
        ),
        (
            f"Through this experience at {exp_company}, I refined my ability to break down ambiguous "
            f"problems into actionable steps and drive them through to completion, which strengthened "
            f"both my individual output and my value to the broader team."
        ),
        (
            f"My time at {exp_company} gave me the opportunity to build strong working relationships "
            f"across teams, develop a sharp sense of prioritization, and consistently deliver high-quality "
            f"work that moved the needle on meaningful outcomes."
        ),
    ]
    sentence2 = _growth_descriptions[index % len(_growth_descriptions)]

    theme = jd_themes[index] if index < len(jd_themes) else ""
    if theme:
        sentence3 = (
            f"The experience I gained at {exp_company} directly prepared me to {theme} "
            f"in the {job_title} role at {company_ref}, and I am eager to bring that same "
            f"level of commitment and impact to this position."
        )
    else:
        sentence3 = (
            f"I am confident that the lessons I learned and the discipline I developed at "
            f"{exp_company} will translate directly into strong performance as a {job_title} "
            f"at {company_ref}."
        )

    return f"{sentence1} {sentence2} {sentence3}"


def _build_supplemental_body_paragraph(
    selected_experiences: list,
    job_title: str,
    company_ref: str,
    jd_themes: list,
    index: int,
) -> str:
    """Generate an additional body paragraph when fewer than 3 experiences exist.
    References available experiences from a different angle."""
    if selected_experiences:
        exp = selected_experiences[0]
        exp_company = exp["company"]
        descriptor = _company_descriptor(exp_company)
    else:
        exp_company = "my previous organization"
        descriptor = "an organization with high standards"

    _supplemental_openers = [
        (
            f"Beyond my core responsibilities at {exp_company}, I also took initiative on "
            f"cross-functional efforts that expanded my understanding of how teams collaborate "
            f"to deliver complex outcomes under pressure."
        ),
        (
            f"In addition to my primary work at {exp_company}, I sought out opportunities to "
            f"contribute beyond my defined role, which gave me a broader perspective on how "
            f"organizations operate and deliver value at scale."
        ),
        (
            f"One of the most valuable aspects of my time at {exp_company} was the exposure "
            f"I gained to challenges outside my immediate scope, which taught me how to think "
            f"about problems holistically rather than in isolation."
        ),
    ]
    sentence1 = _supplemental_openers[index % len(_supplemental_openers)]

    _supplemental_growth = [
        (
            f"This broader involvement sharpened my ability to communicate across disciplines, "
            f"manage competing priorities, and deliver results that served the needs of multiple "
            f"stakeholders simultaneously."
        ),
        (
            f"These experiences strengthened my ability to adapt quickly to new contexts, build "
            f"credibility with unfamiliar teams, and produce work that met the standards of "
            f"an environment as demanding as {exp_company}."
        ),
        (
            f"As a result, I developed the kind of professional versatility that allows me to "
            f"step into new challenges with confidence, knowing that I can draw on a well-rounded "
            f"foundation of experience to deliver meaningful contributions."
        ),
    ]
    sentence2 = _supplemental_growth[index % len(_supplemental_growth)]

    theme = jd_themes[index] if index < len(jd_themes) else ""
    if theme:
        sentence3 = (
            f"I am confident that this background has prepared me to {theme} "
            f"in the {job_title} role at {company_ref}, and I look forward to applying "
            f"that same discipline and drive in this new context."
        )
    else:
        sentence3 = (
            f"I am confident that this well-rounded background will serve me well as a "
            f"{job_title} at {company_ref}, where I expect to encounter the kind of complex, "
            f"rewarding challenges that bring out my best work."
        )

    return f"{sentence1} {sentence2} {sentence3}"


def _build_closing(
    job_title: str,
    company: str,
    selected_experiences: list,
    candidate_name: str,
) -> str:
    company_ref = company if company else "your organization"

    company_names = [e["company"] for e in selected_experiences[:3]]
    if len(company_names) >= 2:
        companies_str = _join_list(company_names)
        sentence1 = (
            f"Across my experiences at {companies_str}, each with its own demanding standards "
            f"and high expectations, I have built a professional foundation that is well suited "
            f"to the demands of this role and the caliber of work I know {company_ref} produces."
        )
    elif company_names:
        descriptor = _company_descriptor(company_names[0])
        sentence1 = (
            f"My experience at {company_names[0]}, {descriptor}, has given me a strong "
            f"professional foundation that aligns directly with what this role requires."
        )
    else:
        sentence1 = (
            f"My professional experience has given me a strong foundation that aligns directly "
            f"with what this role requires."
        )

    hiring_descriptor = _company_descriptor(company_ref)
    sentence2 = (
        f"{company_ref} stands out to me as {hiring_descriptor}, and I am genuinely motivated "
        f"by the opportunity to contribute to an organization operating at that level."
    )

    sentence3 = (
        f"The {job_title} position represents the kind of opportunity I have been working toward "
        f"throughout my career, and I am fully prepared to deliver results from day one."
    )

    sentence4 = (
        f"I would welcome the opportunity to speak with your team about how my background "
        f"and drive align with what {company_ref} is looking for, and I am available to "
        f"connect at your earliest convenience."
    )

    return f"{sentence1} {sentence2} {sentence3} {sentence4}"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _company_descriptor(company_name: str) -> str:
    """Return a specific descriptor for a known company, or a generic professional one."""
    key = company_name.strip().lower()
    for known, desc in _COMPANY_DESCRIPTORS.items():
        if known in key or key in known:
            return desc
    return "an organization with a strong reputation for delivering high-quality work"


def _extract_jd_themes(job_description: str) -> list:
    """Extract action-oriented themes from the JD for use in body paragraph sentence 3."""
    if not job_description:
        return []

    _JD_VERBS = re.compile(
        r"\b(build|design|develop|create|implement|maintain|lead|manage|deliver|"
        r"architect|optimize|deploy|analyze|support|scale|drive|own|collaborate|work\s+on)\b",
        re.IGNORECASE,
    )

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
            if len(result) > 10:
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
            parts = letter_body.rsplit("\n\n", 1)
            if len(parts) == 2:
                parts[0] = parts[0] + " " + expansion_sentences[idx]
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
    """Generate additional sentences to reach the minimum word count."""
    company_ref = company if company else "your organization"
    sentences = []

    if selected_experiences:
        exp = selected_experiences[0]
        sentences.append(
            f"My time at {exp['company']} taught me that consistent execution and clear "
            f"communication are the foundations of any successful team, and I carry that "
            f"mindset into every role I take on."
        )

    sentences.append(
        f"I thrive in environments that value both independent ownership and collaborative "
        f"teamwork, and I believe {company_ref} offers exactly that kind of culture."
    )
    sentences.append(
        f"Throughout my career, I have consistently sought opportunities to grow beyond my "
        f"defined responsibilities and contribute to the broader success of the organizations "
        f"I have been a part of."
    )

    if len(selected_experiences) >= 2:
        exp = selected_experiences[1]
        sentences.append(
            f"The work I did at {exp['company']} reinforced my belief that strong results come "
            f"from combining technical rigor with a genuine commitment to understanding the "
            f"needs of the people your work serves."
        )

    sentences.append(
        f"I am committed to continuous learning and professional development, which I see "
        f"as essential to thriving in a role like {job_title} where expectations evolve quickly."
    )

    if len(selected_experiences) >= 3:
        exp = selected_experiences[2]
        sentences.append(
            f"What I took away from my experience at {exp['company']} is that adaptability and "
            f"a willingness to step outside your comfort zone are what separate good professionals "
            f"from great ones."
        )

    sentences.append(
        f"I bring a track record of reliability, a strong sense of ownership, and the kind of "
        f"professional maturity that allows me to navigate complex challenges without losing sight "
        f"of the bigger picture."
    )

    return sentences
