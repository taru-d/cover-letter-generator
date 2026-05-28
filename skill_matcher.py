import re
from typing import Optional

# Common skill categories and their variations
SKILL_SYNONYMS = {
    "python": ["python", "python3", "python programming"],
    "java": ["java", "java programming"],
    "javascript": ["javascript", "js", "es6", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "reactjs", "react.js"],
    "node": ["node", "nodejs", "node.js"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite"],
    "aws": ["aws", "amazon web services", "cloud computing"],
    "docker": ["docker", "containerization", "containers"],
    "kubernetes": ["kubernetes", "k8s"],
    "git": ["git", "github", "version control"],
    "machine learning": ["machine learning", "ml", "deep learning", "ai", "artificial intelligence"],
    "data analysis": ["data analysis", "data analytics", "analytics", "data-driven"],
    "communication": ["communication", "communicate", "written communication", "verbal communication"],
    "leadership": ["leadership", "lead", "leading", "mentoring", "mentorship"],
    "project management": ["project management", "program management", "agile", "scrum"],
    "problem solving": ["problem solving", "problem-solving", "analytical", "troubleshooting"],
    "teamwork": ["teamwork", "collaboration", "collaborative", "cross-functional"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous deployment", "devops"],
    "testing": ["testing", "unit testing", "test automation", "qa", "quality assurance"],
    "rest api": ["rest", "restful", "api", "apis", "microservices"],
    "database": ["database", "databases", "db", "data modeling"],
    "security": ["security", "cybersecurity", "infosec", "information security"],
    "cloud": ["cloud", "cloud computing", "cloud infrastructure", "saas"],
}


def extract_required_skills(job_description: str) -> list[str]:
    """Extract skills and requirements from a job description."""
    text = job_description.lower()
    found_skills = []

    for canonical, variations in SKILL_SYNONYMS.items():
        for variation in variations:
            pattern = r"\b" + re.escape(variation) + r"\b"
            if re.search(pattern, text):
                found_skills.append(canonical)
                break

    return found_skills


def match_skills_to_experiences(
    required_skills: list[str], experiences: list[dict]
) -> list[dict]:
    """Match required skills to specific resume experiences that demonstrate them."""
    matches = []
    used_evidence = set()

    for skill in required_skills:
        best_match = _find_best_experience_for_skill(skill, experiences, used_evidence)
        if best_match:
            matches.append(best_match)
            used_evidence.add(best_match["evidence"])

    return matches


def _find_best_experience_for_skill(
    skill: str, experiences: list[dict], used_evidence: set
) -> Optional[dict]:
    """Find the experience bullet that best demonstrates a skill."""
    skill_lower = skill.lower()
    variations = SKILL_SYNONYMS.get(skill_lower, [skill_lower])

    best_score = 0
    best_result = None

    for exp in experiences:
        for bullet in exp["bullets"]:
            if bullet in used_evidence:
                continue

            score = _score_bullet_for_skill(bullet, variations)
            if score > best_score:
                best_score = score
                best_result = {
                    "skill": skill,
                    "job_title": exp["title"],
                    "company": exp["company"],
                    "evidence": bullet,
                    "score": score,
                }

    return best_result


def _score_bullet_for_skill(bullet: str, skill_variations: list[str]) -> int:
    """Score how well a bullet point demonstrates a skill."""
    bullet_lower = bullet.lower()
    score = 0

    for variation in skill_variations:
        pattern = r"\b" + re.escape(variation) + r"\b"
        if re.search(pattern, bullet_lower):
            score += 3

    # Bonus for action verbs that suggest accomplishment
    action_verbs = ["developed", "built", "designed", "implemented", "led",
                    "managed", "created", "optimized", "reduced", "increased",
                    "improved", "delivered", "architected", "automated"]
    for verb in action_verbs:
        if verb in bullet_lower:
            score += 1
            break

    # Bonus for quantified results
    if re.search(r"\d+%|\$\d+|\d+x", bullet_lower):
        score += 1

    return score


_SKILL_SUGGESTIONS = {
    "python": "Add Python projects to GitHub or earn a Python certification (e.g., PCEP/PCAP).",
    "java": "Build a Java project or complete a course on Spring Boot to demonstrate server-side Java.",
    "javascript": "Build a small front-end project or complete a JavaScript curriculum on freeCodeCamp.",
    "typescript": "Migrate an existing JS project to TypeScript to show type-safety proficiency.",
    "react": "Build a portfolio app with React and deploy it to Vercel or Netlify.",
    "node": "Build a REST API with Node.js and Express and publish it on GitHub.",
    "sql": "Complete a SQL course on Mode Analytics or LeetCode's database problems to demonstrate query skills.",
    "aws": "Earn the AWS Certified Cloud Practitioner or Solutions Architect — Associate certification.",
    "docker": "Containerize an existing project and publish the Dockerfile on GitHub.",
    "kubernetes": "Set up a local Kubernetes cluster with minikube and deploy a sample app.",
    "git": "Contribute to open source or create a GitHub portfolio showcasing your version control workflow.",
    "machine learning": "Complete a course (Fast.ai, Coursera ML) and publish a Kaggle notebook or GitHub project.",
    "data analysis": "Build an analysis notebook in Jupyter (pandas/matplotlib) and share it on GitHub or Kaggle.",
    "communication": "Highlight presentations, documentation, or cross-team project work in your resume bullets.",
    "leadership": "Add mentorship, on-call ownership, or cross-functional project lead experience to your resume.",
    "project management": "Earn a PMP, PMI-ACP, or Scrum Master certification, or highlight sprint planning experience.",
    "problem solving": "Add quantified examples of debugging, optimization, or root-cause analysis to resume bullets.",
    "teamwork": "Highlight cross-functional projects, code reviews, or open-source contributions on your resume.",
    "ci/cd": "Set up a GitHub Actions or GitLab CI pipeline for a personal project and link it on your resume.",
    "testing": "Add unit/integration tests to a project using pytest, Jest, or JUnit and show coverage metrics.",
    "rest api": "Build and document a RESTful API with OpenAPI/Swagger and publish it publicly.",
    "database": "Design a schema, write migrations, and publish a sample project using PostgreSQL or MySQL.",
    "security": "Earn a CompTIA Security+ or complete OWASP Top 10 training and add it to your resume.",
    "cloud": "Complete a cloud provider's free tier project and earn a foundational cloud certification.",
}


def analyze_skills_gap(required_skills: list[str], experiences: list[dict]) -> dict:
    """Return which required skills are present in the resume and which are missing."""
    matched = []
    missing = []

    for skill in required_skills:
        variations = SKILL_SYNONYMS.get(skill.lower(), [skill.lower()])
        found = False
        for exp in experiences:
            for bullet in exp.get("bullets", []):
                bullet_lower = bullet.lower()
                for var in variations:
                    if re.search(r"\b" + re.escape(var) + r"\b", bullet_lower):
                        found = True
                        break
                if found:
                    break
            if found:
                break

        if found:
            matched.append(skill)
        else:
            missing.append(skill)

    return {
        "matched": matched,
        "missing": missing,
        "suggestions": {skill: _SKILL_SUGGESTIONS.get(skill.lower(), f"Look for courses, certifications, or projects that demonstrate {skill} and add them to your resume.") for skill in missing},
    }


def _is_requirement_line(line: str) -> bool:
    """Check if a line looks like a job requirement."""
    return bool(re.match(r"^[\-•*]\s", line)) or bool(
        re.match(r"^\d+[.)]\s", line)
    )


def _clean_requirement(line: str) -> str:
    """Clean a requirement line into a readable skill."""
    cleaned = re.sub(r"^[\-•*\d.)\s]+", "", line).strip()
    cleaned = re.sub(r"^(experience with|proficiency in|knowledge of|familiarity with|ability to)\s+",
                     "", cleaned, flags=re.IGNORECASE)
    return cleaned


# ── Verb-to-skill inference ───────────────────────────────────────────────────

_VERB_SKILLS: dict[str, list[str]] = {
    "wrote": ["written communication", "research synthesis", "documentation"],
    "write": ["written communication", "research synthesis", "documentation"],
    "authored": ["written communication", "documentation"],
    "drafted": ["written communication", "documentation"],
    "draft": ["written communication", "documentation"],
    "edited": ["editing", "written communication", "attention to detail"],
    "edit": ["editing", "written communication", "attention to detail"],
    "presented": ["public speaking", "communication"],
    "present": ["public speaking", "communication"],
    "briefed": ["communication", "written communication"],
    "brief": ["communication", "written communication"],
    "communicated": ["communication", "stakeholder management"],
    "communicate": ["communication", "stakeholder management"],
    "analyzed": ["data analysis", "research", "problem solving"],
    "analyse": ["data analysis", "research", "problem solving"],
    "analyze": ["data analysis", "research", "problem solving"],
    "researched": ["research", "information synthesis"],
    "research": ["research", "information synthesis"],
    "investigated": ["research", "problem solving"],
    "investigate": ["research", "problem solving"],
    "evaluated": ["analysis", "judgment"],
    "evaluate": ["analysis", "judgment"],
    "assessed": ["analysis", "evaluation"],
    "assess": ["analysis", "evaluation"],
    "reviewed": ["attention to detail", "analysis"],
    "review": ["attention to detail", "analysis"],
    "managed": ["project management", "leadership", "organization"],
    "manage": ["project management", "leadership", "organization"],
    "led": ["leadership", "project management"],
    "lead": ["leadership", "project management"],
    "directed": ["leadership", "project management"],
    "direct": ["leadership", "project management"],
    "supervised": ["leadership", "management"],
    "supervise": ["leadership", "management"],
    "mentored": ["leadership", "teaching"],
    "mentor": ["leadership", "teaching"],
    "trained": ["teaching", "leadership"],
    "train": ["teaching", "leadership"],
    "coordinated": ["coordination", "project management", "organization"],
    "coordinate": ["coordination", "project management", "organization"],
    "organized": ["organization", "project management"],
    "organize": ["organization", "project management"],
    "scheduled": ["organization", "time management"],
    "schedule": ["organization", "time management"],
    "planned": ["planning", "project management"],
    "plan": ["planning", "project management"],
    "facilitated": ["facilitation", "communication", "coordination"],
    "facilitate": ["facilitation", "communication", "coordination"],
    "collaborated": ["teamwork", "communication"],
    "collaborate": ["teamwork", "communication"],
    "supported": ["teamwork", "customer service"],
    "support": ["teamwork", "customer service"],
    "assisted": ["teamwork", "support"],
    "assist": ["teamwork", "support"],
    "responded": ["communication", "stakeholder management", "customer service"],
    "respond": ["communication", "stakeholder management", "customer service"],
    "handled": ["organization", "problem solving"],
    "handle": ["organization", "problem solving"],
    "developed": ["development", "problem solving"],
    "develop": ["development", "problem solving"],
    "built": ["development", "problem solving"],
    "build": ["development", "problem solving"],
    "created": ["creativity", "development"],
    "create": ["creativity", "development"],
    "designed": ["design", "problem solving"],
    "design": ["design", "problem solving"],
    "implemented": ["project management", "execution"],
    "implement": ["project management", "execution"],
    "launched": ["project management", "execution", "initiative"],
    "launch": ["project management", "execution", "initiative"],
    "delivered": ["project management", "execution"],
    "deliver": ["project management", "execution"],
    "monitored": ["attention to detail", "analysis"],
    "monitor": ["attention to detail", "analysis"],
    "tracked": ["attention to detail", "organization"],
    "track": ["attention to detail", "organization"],
    "maintained": ["attention to detail", "reliability"],
    "maintain": ["attention to detail", "reliability"],
    "ensured": ["attention to detail", "quality assurance"],
    "ensure": ["attention to detail", "quality assurance"],
    "improved": ["problem solving", "initiative"],
    "improve": ["problem solving", "initiative"],
    "optimized": ["analysis", "efficiency"],
    "optimize": ["analysis", "efficiency"],
    "streamlined": ["efficiency", "process improvement"],
    "streamline": ["efficiency", "process improvement"],
    "identified": ["research", "problem solving"],
    "identify": ["research", "problem solving"],
    "proposed": ["communication", "initiative"],
    "propose": ["communication", "initiative"],
    "recommended": ["judgment", "communication"],
    "recommend": ["judgment", "communication"],
    "advised": ["judgment", "stakeholder management"],
    "advise": ["judgment", "stakeholder management"],
    "reported": ["communication", "documentation"],
    "report": ["communication", "documentation"],
    "compiled": ["data analysis", "attention to detail"],
    "compile": ["data analysis", "attention to detail"],
    "gathered": ["research", "data collection"],
    "gather": ["research", "data collection"],
    "collected": ["data collection", "research"],
    "collect": ["data collection", "research"],
    "interviewed": ["communication", "research"],
    "interview": ["communication", "research"],
    "negotiated": ["negotiation", "communication"],
    "negotiate": ["negotiation", "communication"],
    "established": ["initiative", "leadership"],
    "establish": ["initiative", "leadership"],
    "conducted": ["research", "project management"],
    "conduct": ["research", "project management"],
    "processed": ["attention to detail", "organization"],
    "process": ["attention to detail", "organization"],
    "prepared": ["organization", "planning"],
    "prepare": ["organization", "planning"],
    "updated": ["attention to detail", "communication"],
    "update": ["attention to detail", "communication"],
    "drafted": ["written communication", "documentation"],
    "draft": ["written communication", "documentation"],
}


def infer_skills_from_bullet(bullet: str) -> list[str]:
    """Infer professional skills implied by action verbs in a bullet or duty."""
    bullet_lower = bullet.lower()
    inferred: list[str] = []
    seen: set[str] = set()
    for verb, skills in _VERB_SKILLS.items():
        if re.search(r"\b" + re.escape(verb) + r"\b", bullet_lower):
            for s in skills:
                if s not in seen:
                    seen.add(s)
                    inferred.append(s)
    return inferred


def extract_jd_requirements(job_description: str) -> list[dict]:
    """Parse a JD into individual duty lines, each annotated with implied skills."""
    requirements = []
    lines = job_description.split("\n")
    for line in lines:
        line = line.strip().lstrip("-•* \t")
        if not line or len(line) < 15:
            continue
        # Skip short header-like lines
        if len(line.split()) <= 3 and line.rstrip(":").istitle():
            continue
        implied = infer_skills_from_bullet(line)
        line_lower = line.lower()
        for canonical, variations in SKILL_SYNONYMS.items():
            for var in variations:
                if re.search(r"\b" + re.escape(var) + r"\b", line_lower):
                    if canonical not in implied:
                        implied.append(canonical)
                    break
        if implied:
            requirements.append({
                "duty": line[:200],
                "implied_skills": implied[:4],
            })
    return requirements


def _is_action_bullet(text: str) -> bool:
    """Return True if text reads as a genuine action statement, not a raw skills list."""
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


def rank_bullets_for_jd(
    experiences: list[dict], jd_requirements: list[dict]
) -> list[dict]:
    """Score and rank resume bullets by relevance to JD requirements.

    Returns a flat list sorted by score (highest first). Each entry has:
    {bullet, job_title, company, jd_duty, score}
    """
    scored = []
    for exp in experiences:
        for bullet in exp.get("bullets", []):
            if not _is_action_bullet(bullet):
                continue
            bullet_skills: set[str] = set(infer_skills_from_bullet(bullet))
            b_lower = bullet.lower()
            for canonical, variations in SKILL_SYNONYMS.items():
                for var in variations:
                    if re.search(r"\b" + re.escape(var) + r"\b", b_lower):
                        bullet_skills.add(canonical)
                        break

            best_duty = None
            best_overlap = 0
            for req in jd_requirements:
                overlap = len(bullet_skills & set(req["implied_skills"]))
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_duty = req["duty"]

            if best_overlap > 0:
                scored.append({
                    "bullet": bullet,
                    "job_title": exp["title"],
                    "company": exp["company"],
                    "jd_duty": best_duty,
                    "score": best_overlap,
                })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored


def analyze_skills_gap_detailed(
    experiences: list[dict], job_description: str
) -> list[dict]:
    """Return detailed gap-analysis rows suitable for table display.

    Each row: {skill, required_by, found_bullet, found_company, match_quality, suggestion}
    match_quality: 'Strong' | 'Transferable' | 'Not found'
    """
    from collections import defaultdict as _defaultdict

    jd_reqs = extract_jd_requirements(job_description)

    skill_to_duty: dict[str, str] = {}
    for req in jd_reqs:
        for skill in req["implied_skills"]:
            if skill not in skill_to_duty:
                skill_to_duty[skill] = req["duty"]

    jd_lower = job_description.lower()
    for canonical, variations in SKILL_SYNONYMS.items():
        for var in variations:
            if re.search(r"\b" + re.escape(var) + r"\b", jd_lower):
                if canonical not in skill_to_duty:
                    skill_to_duty[canonical] = "Explicitly required in job description"
                break

    rows = []
    for skill, duty in skill_to_duty.items():
        found_bullet = None
        found_company = None
        match_quality = "Not found"

        variations = SKILL_SYNONYMS.get(skill.lower(), [skill.lower()])
        for exp in experiences:
            for bullet in exp.get("bullets", []):
                b_lower = bullet.lower()
                for var in variations:
                    if re.search(r"\b" + re.escape(var) + r"\b", b_lower):
                        found_bullet = bullet
                        found_company = exp["company"]
                        match_quality = "Strong"
                        break
                if found_bullet:
                    break
            if found_bullet:
                break

        if not found_bullet:
            for exp in experiences:
                for bullet in exp.get("bullets", []):
                    if skill in infer_skills_from_bullet(bullet):
                        found_bullet = bullet
                        found_company = exp["company"]
                        match_quality = "Transferable"
                        break
                if found_bullet:
                    break

        rows.append({
            "skill": skill,
            "required_by": duty[:120] + ("..." if len(duty) > 120 else ""),
            "found_bullet": found_bullet,
            "found_company": found_company,
            "match_quality": match_quality,
            "suggestion": _SKILL_SUGGESTIONS.get(
                skill.lower(),
                f"Seek opportunities to develop {skill} through coursework, projects, or relevant experience.",
            ),
        })

    _order = {"Strong": 0, "Transferable": 1, "Not found": 2}
    rows.sort(key=lambda r: _order.get(r["match_quality"], 3))
    return rows
