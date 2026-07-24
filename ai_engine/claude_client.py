"""
Thin wrapper around the Google Gemini API for the two AI-powered features:
interview question generation and learning recommendations.

If GEMINI_API_KEY isn't set, both functions fall back to simple
rule-based output so the rest of the app still works in dev/demo mode
without requiring an API key.
"""
import json
import logging
import asyncio

from django.conf import settings

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.5-flash"


def _get_client():
    if not settings.GEMINI_API_KEY:
        return None

    # google-genai's Client() creates an asyncio.Lock() on init, which on
    # Python <3.10 requires the current thread to already have an event
    # loop registered. Django serves requests from worker threads that
    # don't have one by default, so we create/register one here first.
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    from google import genai
    return genai.Client(api_key=settings.GEMINI_API_KEY)


def generate_interview_questions(job_title: str, skills: list[str], num_questions: int = 8) -> list[dict]:
    """
    Returns a list of {"question": str, "category": str, "difficulty": str}.
    """
    client = _get_client()
    if client is None:
        return _fallback_interview_questions(job_title, skills, num_questions)

    skills_str = ", ".join(skills) if skills else "general professional skills"
    prompt = f"""You are a technical interviewer preparing questions for a candidate applying to a "{job_title}" role.
Their resume shows these skills: {skills_str}.

Generate exactly {num_questions} interview questions covering a mix of technical and behavioral topics relevant
to this role and these skills. Respond ONLY with a JSON array, no other text, in this exact format:
[{{"question": "...", "category": "technical|behavioral", "difficulty": "easy|medium|hard"}}]"""

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt,
        )
        text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)
    except Exception:
        logger.exception("Gemini API call failed for interview questions; using fallback.")
        return _fallback_interview_questions(job_title, skills, num_questions)


def generate_learning_recommendations(missing_skills: list[str]) -> list[dict]:
    """
    Returns a list of {"skill": str, "why_it_matters": str, "how_to_learn": str}.
    """
    if not missing_skills:
        return []

    client = _get_client()
    if client is None:
        return _fallback_learning_recommendations(missing_skills)

    skills_str = ", ".join(missing_skills)
    prompt = f"""A job candidate is missing these skills that a target job requires: {skills_str}.

For each skill, give a short, encouraging, practical recommendation. Respond ONLY with a JSON array,
no other text, in this exact format:
[{{"skill": "...", "why_it_matters": "1 sentence", "how_to_learn": "1-2 concrete suggestions, e.g. a course type or project idea"}}]"""

    try:
        response = client.models.generate_content(
            model=DEFAULT_MODEL,
            contents=prompt,
        )
        text = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(text)
    except Exception:
        logger.exception("Gemini API call failed for learning recommendations; using fallback.")
        return _fallback_learning_recommendations(missing_skills)


# --- Fallbacks (no API key required) ---

import random

# Specific, realistic questions for common skills, each with its own
# category/difficulty. Skills not listed here fall back to the generic
# rotating templates below instead of a single repeated phrasing.
SKILL_QUESTION_BANK = {
    "python": [
        {"question": "Walk me through how you'd debug a Python script that's running much slower than expected.", "category": "technical", "difficulty": "medium"},
        {"question": "What's the difference between a list and a generator in Python, and when would you choose one over the other?", "category": "technical", "difficulty": "medium"},
        {"question": "Tell me about a Python project where you had to work with someone else's messy codebase. How did you approach it?", "category": "behavioral", "difficulty": "medium"},
    ],
    "javascript": [
        {"question": "How would you explain closures in JavaScript to a junior developer?", "category": "technical", "difficulty": "medium"},
        {"question": "Describe a time a bug in production JavaScript code turned out to be caused by something unexpected. What was it?", "category": "behavioral", "difficulty": "hard"},
        {"question": "How do you handle asynchronous operations in JavaScript, and what pitfalls have you run into?", "category": "technical", "difficulty": "medium"},
    ],
    "java": [
        {"question": "How does Java's garbage collection affect the way you design memory-intensive applications?", "category": "technical", "difficulty": "hard"},
        {"question": "Tell me about a time you had to optimize a slow Java application. What did you find?", "category": "behavioral", "difficulty": "medium"},
    ],
    "c++": [
        {"question": "What's your approach to managing memory manually in C++, and have you dealt with a memory leak before?", "category": "technical", "difficulty": "hard"},
        {"question": "Explain the difference between a pointer and a reference in C++.", "category": "technical", "difficulty": "medium"},
    ],
    "c#": [
        {"question": "How do you handle exception management in a C# application you've built?", "category": "technical", "difficulty": "medium"},
        {"question": "Tell me about a project where you used C# with .NET. What was the architecture like?", "category": "behavioral", "difficulty": "medium"},
    ],
    "sql": [
        {"question": "How would you optimize a SQL query that's taking too long to run against a large table?", "category": "technical", "difficulty": "medium"},
        {"question": "Explain the difference between an INNER JOIN and a LEFT JOIN, with an example of when you'd use each.", "category": "technical", "difficulty": "easy"},
        {"question": "Describe a time you had to design a database schema from scratch. What tradeoffs did you make?", "category": "behavioral", "difficulty": "medium"},
    ],
    "react": [
        {"question": "How do you decide when to lift state up versus keeping it local to a component in React?", "category": "technical", "difficulty": "medium"},
        {"question": "Tell me about a performance issue you diagnosed in a React app. How did you fix it?", "category": "behavioral", "difficulty": "hard"},
    ],
    "django": [
        {"question": "How do you structure a Django project once it grows past a handful of apps?", "category": "technical", "difficulty": "medium"},
        {"question": "Walk me through how Django's ORM handles a complex query versus writing raw SQL. When would you use raw SQL instead?", "category": "technical", "difficulty": "hard"},
    ],
    "node.js": [
        {"question": "How do you handle error handling in a Node.js API with lots of async operations?", "category": "technical", "difficulty": "medium"},
        {"question": "Tell me about a time you had to scale a Node.js service under increased load.", "category": "behavioral", "difficulty": "hard"},
    ],
    "aws": [
        {"question": "Walk me through how you'd design a highly available system on AWS.", "category": "technical", "difficulty": "hard"},
        {"question": "Tell me about a time an AWS service didn't behave the way you expected. How did you troubleshoot it?", "category": "behavioral", "difficulty": "medium"},
    ],
    "docker": [
        {"question": "What problems have you run into with Docker containers in production, and how did you resolve them?", "category": "behavioral", "difficulty": "medium"},
        {"question": "How do you decide what should and shouldn't go into a Docker image to keep it lean?", "category": "technical", "difficulty": "medium"},
    ],
    "git": [
        {"question": "Tell me about a time you had to resolve a messy merge conflict. How did you approach it?", "category": "behavioral", "difficulty": "easy"},
        {"question": "How do you structure your branching strategy when working on a team?", "category": "technical", "difficulty": "easy"},
    ],
    "machine learning": [
        {"question": "Walk me through how you'd approach a machine learning problem where your model is overfitting.", "category": "technical", "difficulty": "hard"},
        {"question": "Tell me about a machine learning project where the data itself turned out to be the biggest challenge.", "category": "behavioral", "difficulty": "medium"},
    ],
    "leadership": [
        {"question": "Tell me about a time you had to lead a project without formal authority over the team.", "category": "behavioral", "difficulty": "medium"},
        {"question": "Describe a situation where you had to give a teammate difficult feedback.", "category": "behavioral", "difficulty": "medium"},
    ],
    "project management": [
        {"question": "Tell me about a project that started falling behind schedule. How did you get it back on track?", "category": "behavioral", "difficulty": "medium"},
        {"question": "How do you handle competing priorities from different stakeholders on the same project?", "category": "behavioral", "difficulty": "medium"},
    ],
}

# Rotating templates for any skill not covered above, so consecutive
# skills don't all get the exact same sentence structure.
GENERIC_SKILL_TEMPLATES = [
    {"question": "Walk me through a project where you used {skill}. What was the hardest part?", "category": "technical", "difficulty": "medium"},
    {"question": "How would you explain {skill} to someone who's never used it before?", "category": "technical", "difficulty": "easy"},
    {"question": "Tell me about a mistake you made while working with {skill}, and what you learned from it.", "category": "behavioral", "difficulty": "medium"},
    {"question": "What's a limitation of {skill} that surprised you once you started using it in a real project?", "category": "technical", "difficulty": "hard"},
    {"question": "How do you stay current with best practices in {skill}?", "category": "behavioral", "difficulty": "easy"},
]

GENERIC_BEHAVIORAL_POOL = [
    {"question": "Tell me about a time you disagreed with a teammate. How did you resolve it?", "category": "behavioral", "difficulty": "medium"},
    {"question": "How do you prioritize tasks when everything feels urgent?", "category": "behavioral", "difficulty": "medium"},
    {"question": "Describe a time you missed a deadline. What happened, and what would you do differently?", "category": "behavioral", "difficulty": "medium"},
    {"question": "Tell me about a time you had to learn something completely new under time pressure.", "category": "behavioral", "difficulty": "medium"},
    {"question": "What's a piece of feedback you received that changed how you work?", "category": "behavioral", "difficulty": "easy"},
    {"question": "Tell me about a time you had to make a decision without all the information you needed.", "category": "behavioral", "difficulty": "hard"},
    {"question": "Describe a project you're proud of. What was your specific role in it?", "category": "behavioral", "difficulty": "easy"},
]


def _fallback_interview_questions(job_title, skills, num_questions):
    questions = []

    for i, skill in enumerate(skills):
        skill_key = skill.lower().strip()
        if skill_key in SKILL_QUESTION_BANK:
            bank = SKILL_QUESTION_BANK[skill_key]
            questions.append(dict(bank[i % len(bank)]))
        else:
            template = GENERIC_SKILL_TEMPLATES[i % len(GENERIC_SKILL_TEMPLATES)]
            questions.append({
                "question": template["question"].format(skill=skill),
                "category": template["category"],
                "difficulty": template["difficulty"],
            })

    # Always open with a role-specific question, then fill remaining slots
    # with a mix of skill-based and behavioral questions.
    opener = {"question": f"Why are you interested in this {job_title} role?", "category": "behavioral", "difficulty": "easy"}
    behavioral = random.sample(GENERIC_BEHAVIORAL_POOL, k=min(len(GENERIC_BEHAVIORAL_POOL), max(0, num_questions - 1)))

    combined = [opener] + questions + behavioral
    # De-dupe while preserving order, in case a skill-bank question happens
    # to match a behavioral one.
    seen = set()
    deduped = []
    for q in combined:
        if q["question"] not in seen:
            seen.add(q["question"])
            deduped.append(q)

    return deduped[:num_questions]


def _fallback_learning_recommendations(missing_skills):
    return [
        {
            "skill": skill,
            "why_it_matters": f"'{skill}' was listed as a requirement in the job description you're targeting.",
            "how_to_learn": f"Look for a beginner course or official docs for '{skill}', then build one small project with it.",
        }
        for skill in missing_skills
    ]