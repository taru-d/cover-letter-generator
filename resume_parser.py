import re
from io import BytesIO


def extract_text_from_pdf(file) -> str:
    """Extract text from a PDF, preferring pdfplumber for complex layouts."""
    data = file.read()
    try:
        import pdfplumber
        with pdfplumber.open(BytesIO(data)) as pdf:
            pages = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    pages.append(t)
            text = "\n".join(pages)
    except Exception:
        from PyPDF2 import PdfReader
        reader = PdfReader(BytesIO(data))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

    # Normalise bullet variants → standard hyphen-space so the parser detects them
    text = text.replace("●", "-").replace("▪", "-").replace("◦", "-").replace("·", "-")
    return text


def parse_resume_experiences(text: str) -> list[dict]:
    """Parse resume text into structured work experiences.

    Returns list of dicts with keys: title, company, duration, bullets

    Handles common resume formats:
      - "Title | Company | Jun 2024 – Aug 2024"
      - "Title, Company (2020–2023)"
      - "Title at Company"
      - "Title\\nCompany | Jun 2024 – Aug 2024"
      - "Title\\nCompany                Jun 2024 – Aug 2024"
      - Two-line: title on one line, company (+ optional date) on the next
    """
    experiences = []
    lines = text.strip().split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    # --- Date pattern (reused in several regexes) ---
    _DATE_RE = (
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|June|July|August|September|October|November|December)"
        r"\.?\s*\d{4}"
        r"|\d{4}"
    )
    _DATE_RANGE_RE = re.compile(
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|June|July|August|September|October|November|December)"
        r"\.?\s*\d{4}|\d{4})"
        r"\s*[-–—to]+\s*"
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|June|July|August|September|October|November|December)"
        r"\.?\s*\d{4}|\d{4}|[Pp]resent|[Cc]urrent)",
        re.IGNORECASE,
    )

    # Pattern 1: all on one line — "Title | Company | date range"
    # or "Title, Company (date range)"
    job_pattern = re.compile(
        r"^(.+?)\s*[\|,]\s*(.+?)\s*[\|,(]\s*"
        r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|June|July|August|September|October|November|December)"
        r"\.?\s*\d{4}\s*[-–—to]+\s*"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|June|July|August|September|October|November|December)"
        r"\.?\s*\d{4}"
        r"|\d{4}\s*[-–—to]+\s*\d{4}"
        r"|\d{4}\s*[-–—to]+\s*[Pp]resent"
        r"|\d{4}\s*[-–—to]+\s*[Cc]urrent)"
    )

    # Pattern 2: "Title at Company" (no date on same line)
    # Must not look like a bullet or section header, and must have a plausible
    # job title (starts with a capital letter, reasonable length).
    at_pattern = re.compile(
        r"^([A-Z][A-Za-z '/&,.\-]{1,60}?)\s+at\s+([A-Z][A-Za-z0-9 '/&,.\-]{1,60}?)"
        r"(?:\s*[\|,\-(]\s*(.+?))?$"
    )

    # Pattern 3: second line is "Company  <date range>" or "Company | <date range>"
    # used when we already have a pending title-only line
    # Handles: Month Year – Month Year, Month Year – Present, Year – Year, Year – Present
    _MON = (r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
            r"January|February|March|April|June|July|August|September|"
            r"October|November|December)\.?\s*")
    company_date_pattern = re.compile(
        r"^([A-Z][A-Za-z0-9 '/&,.\-]{1,60}?)"
        r"\s*[\|,\-–—]?\s*"
        r"(" + _MON + r"\d{4}\s*[-–—to]+\s*(?:" + _MON + r"\d{4}|[Pp]resent|[Cc]urrent)"
        r"|\d{4}\s*[-–—to]+\s*(?:\d{4}|[Pp]resent|[Cc]urrent))"
    )

    # Pattern 4: a lone date-range line (sometimes dates appear alone after a title+company pair)
    lone_date_pattern = re.compile(
        r"^((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|June|July|August|September|October|November|December)"
        r"\.?\s*\d{4}\s*[-–—to]+\s*"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
        r"January|February|March|April|June|July|August|September|October|November|December)"
        r"\.?\s*\d{4}"
        r"|\d{4}\s*[-–—to]+\s*\d{4}"
        r"|\d{4}\s*[-–—to]+\s*[Pp]resent"
        r"|\d{4}\s*[-–—to]+\s*[Cc]urrent)$",
        re.IGNORECASE,
    )

    # Heuristic: does a line look like a job title? (capital start, 2–8 words, no sentence punctuation)
    def _looks_like_title(line: str) -> bool:
        if _is_bullet(line) or _looks_like_section_header(line):
            return False
        if not re.match(r"^[A-Z]", line):
            return False
        words = line.split()
        if not (1 <= len(words) <= 8):
            return False
        if re.search(r"\. .+", line):
            return False
        if re.search(r"\d+%|\$\d+|\d+x\b", line):
            return False
        # Reject if the line contains a year — it's likely a header+date line, not a bare title
        if re.search(r"\b(19|20)\d{2}\b", line):
            return False
        return True

    current_experience = None
    pending_title = None  # title line waiting for a company line

    for line in lines:
        if _looks_like_section_header(line):
            pending_title = None
            continue

        job_match = job_pattern.match(line)
        at_match = at_pattern.match(line) if not job_match and not _is_bullet(line) else None
        comp_date_match = company_date_pattern.match(line) if pending_title else None
        lone_date_match = lone_date_pattern.match(line)

        if job_match:
            # e.g. "Software Engineer | Google | Jun 2024 – Aug 2024"
            if current_experience:
                experiences.append(current_experience)
            current_experience = {
                "title": job_match.group(1).strip(),
                "company": job_match.group(2).strip(),
                "duration": job_match.group(3).strip(),
                "bullets": [],
            }
            pending_title = None

        elif pending_title and comp_date_match:
            # Two-line format. Determine which line is the title and which is the company.
            # Some resumes put Company+Location on line 1 and Title+Date on line 2 (inverted).
            candidate_title = comp_date_match.group(1).strip()
            if _contains_title_keywords(candidate_title) or _ends_with_location(pending_title):
                # Inverted format: pending_title is company+location, candidate is title
                real_title = candidate_title
                real_company = _strip_trailing_location(pending_title)
            else:
                real_title = pending_title
                real_company = candidate_title
            if current_experience:
                experiences.append(current_experience)
            current_experience = {
                "title": real_title,
                "company": real_company,
                "duration": comp_date_match.group(2).strip(),
                "bullets": [],
            }
            pending_title = None

        elif pending_title and lone_date_match:
            # Title was on the previous line; this line is just a date range — need company from title
            # Keep pending; we'll try to pair on the next line instead.
            # If we never get a company line, we'll flush with the title as a placeholder.
            # For now, update duration on the current pending (we store it temporarily).
            # We'll handle this by creating an entry with company = title and adjusting
            # only if the next line provides a company. Use a special flag.
            pending_title = pending_title  # stay pending, skip this date-only line for now
            if current_experience:
                # Attach duration to the most recently opened experience if it's missing one
                if not current_experience.get("duration"):
                    current_experience["duration"] = lone_date_match.group(1).strip()

        elif at_match and not _is_bullet(line):
            # e.g. "Software Engineer at Google" or "Intern at Acme Corp (Summer 2023)"
            candidate_title = at_match.group(1).strip()
            candidate_company = at_match.group(2).strip()
            # Reject if title looks like a section header or too short
            if (len(candidate_title) >= 3 and len(candidate_company) >= 2
                    and not _looks_like_section_header(candidate_title)):
                if current_experience:
                    experiences.append(current_experience)
                current_experience = {
                    "title": candidate_title,
                    "company": candidate_company,
                    "duration": at_match.group(3).strip() if at_match.group(3) else "",
                    "bullets": [],
                }
                pending_title = None

        elif _is_bullet(line):
            pending_title = None
            if current_experience:
                bullet = re.sub(r"^[\-•*]\s*", "", line).strip()
                if bullet and _is_action_bullet(bullet):
                    current_experience["bullets"].append(bullet)

        elif _looks_like_title(line) and not current_experience:
            # Could be the start of a two-line job entry — remember it
            pending_title = line

        elif _looks_like_title(line) and current_experience:
            # Could be a new job title (two-line format) — hold it as pending
            pending_title = line

        elif current_experience and line and not _looks_like_section_header(line):
            # If we have a pending_title, this might be the company line (no date)
            if pending_title:
                # This line is the company name with no explicit date
                if re.match(r"^[A-Z]", line) and len(line.split()) <= 7 and not _is_bullet(line):
                    if current_experience:
                        experiences.append(current_experience)
                    current_experience = {
                        "title": pending_title,
                        "company": line,
                        "duration": "",
                        "bullets": [],
                    }
                    pending_title = None
                else:
                    if _is_action_bullet(line):
                        current_experience["bullets"].append(line)
            else:
                if _is_action_bullet(line):
                    current_experience["bullets"].append(line)

        elif pending_title and line and not _looks_like_section_header(line) and not _is_bullet(line):
            # Pending title with a possible company line (no date, no current_experience yet)
            if re.match(r"^[A-Z]", line) and len(line.split()) <= 6:
                if current_experience:
                    experiences.append(current_experience)
                current_experience = {
                    "title": pending_title,
                    "company": line,
                    "duration": "",
                    "bullets": [],
                }
                pending_title = None

    # Flush the last pending title if it never got a company
    if pending_title and not current_experience:
        current_experience = {
            "title": pending_title,
            "company": "Unknown",
            "duration": "",
            "bullets": [],
        }

    if current_experience:
        experiences.append(current_experience)

    # Remove spurious entries: Unknown companies with no bullets, education entries,
    # and entries where the "company" is actually a section header
    experiences = [
        e for e in experiences
        if not (e["company"] == "Unknown" and not e["bullets"])
        and e["title"].upper() not in {"HIGH SCHOOL DIPLOMA", "BACHELOR OF ARTS",
                                        "BACHELOR OF SCIENCE", "MASTER OF SCIENCE",
                                        "ASSOCIATE DEGREE"}
        and not (e["title"].lower() in {"high school diploma", "bachelor of arts",
                                         "bachelor of science", "master of science"})
        and not _looks_like_section_header(e["company"])
        and e["company"].upper() != e["company"]  # all-caps company = section header
    ]

    # If no structured experiences found, treat entire text as one block
    if not experiences:
        experiences.append({
            "title": "Professional Experience",
            "company": "Various",
            "duration": "",
            "bullets": [line for line in lines if len(line) > 20 and _is_action_bullet(line)],
        })

    return experiences


_TITLE_KEYWORDS = {
    "intern", "research", "analyst", "engineer", "developer", "manager",
    "director", "staff", "head", "coordinator", "associate", "consultant",
    "advisor", "specialist", "technician", "officer", "lead", "senior",
    "junior", "assistant", "applied", "fellow", "scientist", "researcher",
    "executive", "president", "vice", "principal", "architect",
}

_STATES_RE = (
    r"Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|"
    r"Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|"
    r"Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|"
    r"Nebraska|Nevada|New Hampshire|New Jersey|New Mexico|New York|North Carolina|"
    r"North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode Island|South Carolina|"
    r"South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West Virginia|"
    r"Wisconsin|Wyoming|D\.C\.|DC|CA|NY|TX|FL|IL|PA|OH|GA|NC|MI|NJ|VA|WA|MA|AZ|"
    r"TN|IN|MO|MD|WI|MN|CO|AL|SC|LA|KY|OR|OK|CT|UT|IA|NV|AR|MS|KS|NE|NM|WV|"
    r"ID|HI|NH|ME|MT|RI|DE|SD|ND|AK|VT|WY"
)

# Matches the state name (or D.C.) at the very end of a line, optionally after a comma
_STATE_AT_END = re.compile(
    r",?\s+(?:" + _STATES_RE + r")\s*$",
    re.IGNORECASE,
)

# Prefixes of known two-word US cities (San Jose, Palo Alto, New York, etc.)
_TWO_WORD_CITY = re.compile(
    r"\b(San|Palo|Los|New|Fort|North|South|East|West|Mount|Santa|El|La|St\.?)\s+\S+$",
    re.IGNORECASE,
)


def _contains_title_keywords(text: str) -> bool:
    words = {w.lower().strip(",-") for w in text.split()}
    return bool(words & _TITLE_KEYWORDS)


def _ends_with_location(text: str) -> bool:
    return bool(_STATE_AT_END.search(text))


def _strip_trailing_location(text: str) -> str:
    """Remove trailing 'City [City], State' from a company+location string."""
    m = _STATE_AT_END.search(text)
    if not m:
        return text.strip()
    # Remove the state → left with "Company City [City]"
    without_state = text[:m.start()].strip()
    # Check if trailing 2 words form a two-word city (San Mateo, Palo Alto, etc.)
    if _TWO_WORD_CITY.search(without_state):
        parts = without_state.rsplit(None, 2)
        return (parts[0].strip().rstrip(",") if len(parts) >= 2 else without_state)
    # Otherwise remove the last single city word
    parts = without_state.rsplit(None, 1)
    return (parts[0].strip().rstrip(",") if len(parts) >= 2 else without_state)


def _is_bullet(line: str) -> bool:
    return bool(re.match(r"^[\-•*]\s", line))


_INLINE_SKILL_LABELS = (
    "skills", "technical skills", "tools", "technologies", "frameworks",
    "languages", "proficiencies", "competencies", "certifications",
    "expertise", "areas of expertise", "key skills", "core skills",
    "programming languages", "software", "platforms",
)


def _looks_like_section_header(line: str) -> bool:
    headers = [
        "education", "skills", "projects", "certifications", "awards",
        "publications", "references", "summary", "objective", "contact",
        "experience", "work experience", "professional experience",
        "employment", "employment history", "work history",
        "technical skills", "core competencies", "volunteer", "interests",
        "languages", "activities", "honors", "achievements",
    ]
    normalized = line.lower().strip(":").strip()
    if normalized in headers or (line.isupper() and len(line) < 40):
        return True
    # Catch "Skills: Python, Java, ..." style inline skill dump lines
    lower = line.lower()
    for label in _INLINE_SKILL_LABELS:
        if lower.startswith(label + ":") or lower.startswith(label + " :"):
            return True
    return False


def _is_action_bullet(text: str) -> bool:
    """Return True if text reads as a genuine action statement, not a raw skills list.

    Rejects lines that are comma-separated skill enumerations — the root cause of
    "As a [role], I skills: Python, SQL, ..." breakage in generated cover letters.
    """
    if not text:
        return False
    lower = text.lower().strip()
    # Reject anything that starts with a skills/tools label
    for label in _INLINE_SKILL_LABELS:
        if lower.startswith(label + ":") or lower.startswith(label + " :"):
            return False
    # Reject comma-dense lists where each item is very short (avg ≤ 2.5 words)
    parts = re.split(r",\s*", text)
    if len(parts) >= 3:
        avg_words = sum(len(p.split()) for p in parts) / len(parts)
        if avg_words <= 2.5:
            return False
    return True
