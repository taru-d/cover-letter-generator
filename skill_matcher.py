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
