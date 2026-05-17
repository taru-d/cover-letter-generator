import re
from io import BytesIO
from PyPDF2 import PdfReader


def extract_text_from_pdf(file) -> str:
    reader = PdfReader(BytesIO(file.read()))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def parse_resume_experiences(text: str) -> list[dict]:
    """Parse resume text into structured work experiences.

    Returns list of dicts with keys: title, company, duration, bullets
    """
    experiences = []
    lines = text.strip().split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    # Patterns for detecting experience entries
    # Matches lines like "Software Engineer | Google | 2020-2023"
    # or "Software Engineer, Google (2020-2023)"
    # or "Software Engineer at Google"
    job_pattern = re.compile(
        r"^(.+?)\s*[\|,\-–—]\s*(.+?)\s*[\|,\-–—(]\s*(\w+\.?\s*\d{4}\s*[-–—to]+\s*\w+\.?\s*\d{4}|\d{4}\s*[-–—to]+\s*\d{4}|\d{4}\s*[-–—to]+\s*[Pp]resent)"
    )
    at_pattern = re.compile(
        r"^(.+?)\s+at\s+(.+?)(?:\s*[\|,\-(]\s*(.+))?"
    )

    current_experience = None

    for line in lines:
        job_match = job_pattern.match(line)
        at_match = at_pattern.match(line) if not job_match else None

        if job_match:
            if current_experience:
                experiences.append(current_experience)
            current_experience = {
                "title": job_match.group(1).strip(),
                "company": job_match.group(2).strip(),
                "duration": job_match.group(3).strip() if job_match.group(3) else "",
                "bullets": [],
            }
        elif at_match and not _is_bullet(line):
            if current_experience:
                experiences.append(current_experience)
            current_experience = {
                "title": at_match.group(1).strip(),
                "company": at_match.group(2).strip(),
                "duration": at_match.group(3).strip() if at_match.group(3) else "",
                "bullets": [],
            }
        elif current_experience and _is_bullet(line):
            bullet = re.sub(r"^[\-•*]\s*", "", line)
            current_experience["bullets"].append(bullet)
        elif current_experience and line and not _looks_like_section_header(line):
            current_experience["bullets"].append(line)

    if current_experience:
        experiences.append(current_experience)

    # If no structured experiences found, treat entire text as one block
    if not experiences:
        experiences.append({
            "title": "Professional Experience",
            "company": "Various",
            "duration": "",
            "bullets": [line for line in lines if len(line) > 20],
        })

    return experiences


def _is_bullet(line: str) -> bool:
    return bool(re.match(r"^[\-•*]\s", line))


def _looks_like_section_header(line: str) -> bool:
    headers = ["education", "skills", "projects", "certifications", "awards",
               "publications", "references", "summary", "objective", "contact"]
    return line.lower().strip(":").strip() in headers or (
        line.isupper() and len(line) < 30
    )
