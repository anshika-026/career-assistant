"""
Rule-based ATS scoring + skill extraction.

No ML model here on purpose: ATS scoring is fundamentally about matching
well-known, explainable heuristics (real ATS systems like Workday/Greenhouse
work similarly) -- keyword presence, section structure, formatting red flags,
and length. This keeps the logic transparent, fast, and free to run.
"""
import re

from .skills_data import ALL_SKILLS

SECTION_PATTERNS = {
    "contact_info": r"(email|phone|linkedin|@\w+\.\w+)",
    "summary": r"(summary|objective|profile)\b",
    "experience": r"(experience|employment|work history)\b",
    "education": r"(education|degree|university|college|bachelor|master)\b",
    "skills": r"(skills|technologies|technical skills|competencies)\b",
}

EMAIL_REGEX = r"[\w.+-]+@[\w-]+\.[\w.-]+"
PHONE_REGEX = r"(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"

IDEAL_WORD_COUNT_RANGE = (350, 900)


def extract_skills(text: str) -> dict:
    """
    Return {skill_name: category} for every known skill found in the text.
    Uses word-boundary matching so 'r' doesn't match inside 'server', etc.
    """
    text_lower = text.lower()
    found = {}
    for skill, category in ALL_SKILLS.items():
        # Escape special regex chars in skills like "c++", "ci/cd"
        pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
        if re.search(pattern, text_lower):
            found[skill] = category
    return found


def check_sections(text: str) -> dict:
    """Return {section_name: bool} for whether each expected resume section was found."""
    text_lower = text.lower()
    return {
        section: bool(re.search(pattern, text_lower))
        for section, pattern in SECTION_PATTERNS.items()
    }


def check_contact_info(text: str) -> dict:
    return {
        "has_email": bool(re.search(EMAIL_REGEX, text)),
        "has_phone": bool(re.search(PHONE_REGEX, text)),
    }


def score_resume(text: str) -> dict:
    """
    Compute an ATS-friendliness score (0-100) plus a breakdown explaining it.
    Weighting:
      - Sections present:      40 pts (8 pts each of the 5 sections)
      - Contact info complete: 15 pts
      - Skill keyword count:   30 pts (capped, scaled)
      - Length appropriate:    15 pts
    """
    word_count = len(text.split())
    sections = check_sections(text)
    contact = check_contact_info(text)
    skills_found = extract_skills(text)

    section_score = sum(8 for present in sections.values() if present)

    contact_score = 0
    if contact["has_email"]:
        contact_score += 8
    if contact["has_phone"]:
        contact_score += 7

    # Scale skill count to a max of 30 points (20+ skills = full marks)
    skill_score = min(30, round(len(skills_found) / 20 * 30))

    min_words, max_words = IDEAL_WORD_COUNT_RANGE
    if min_words <= word_count <= max_words:
        length_score = 15
    elif word_count < min_words:
        length_score = max(0, round(15 * (word_count / min_words)))
    else:
        # Penalize gently for being too long
        overflow_ratio = min(1, (word_count - max_words) / max_words)
        length_score = round(15 * (1 - 0.5 * overflow_ratio))

    total = section_score + contact_score + skill_score + length_score

    issues = []
    for section, present in sections.items():
        if not present:
            issues.append(f"Missing or unclear '{section.replace('_', ' ')}' section.")
    if not contact["has_email"]:
        issues.append("No email address detected.")
    if not contact["has_phone"]:
        issues.append("No phone number detected.")
    if word_count < min_words:
        issues.append(f"Resume seems short ({word_count} words); aim for {min_words}-{max_words}.")
    elif word_count > max_words:
        issues.append(f"Resume seems long ({word_count} words); consider trimming to {min_words}-{max_words}.")
    if len(skills_found) < 5:
        issues.append("Few recognizable technical/professional skills detected -- consider adding more relevant keywords.")

    return {
        "ats_score": min(100, total),
        "word_count": word_count,
        "sections_found": sections,
        "contact_info": contact,
        "skills_found": skills_found,
        "score_breakdown": {
            "sections": section_score,
            "contact_info": contact_score,
            "skills": skill_score,
            "length": length_score,
        },
        "issues": issues,
    }
