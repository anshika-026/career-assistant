"""
Skill-gap matching between a resume and a job description.
Reuses the same skill extraction used for ATS scoring so the two features
stay consistent (a skill recognized on the resume is the same skill
recognized in a JD).
"""
from analysis.scoring import extract_skills


def match_resume_to_job(resume_text: str, job_text: str) -> dict:
    resume_skills = set(extract_skills(resume_text).keys())
    job_skills_dict = extract_skills(job_text)
    job_skills = set(job_skills_dict.keys())

    if not job_skills:
        return {
            "match_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "required_skills": {},
            "note": "No recognizable skill keywords found in the job description.",
        }

    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)

    match_score = round(len(matched) / len(job_skills) * 100)

    return {
        "match_score": match_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "required_skills": job_skills_dict,
    }
