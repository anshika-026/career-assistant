"""
Master skill keyword list used for skill extraction from resumes and job
descriptions. This is intentionally a simple, editable Python list rather
than an ML model -- it's transparent, fast, and easy for anyone to extend.

Organized by category so results can be grouped in the UI later.
"""

SKILL_CATEGORIES = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql",
    ],
    "web_frameworks": [
        "django", "flask", "fastapi", "react", "angular", "vue", "next.js",
        "node.js", "express", "spring", "spring boot", "asp.net", "ruby on rails",
        "laravel",
    ],
    "databases": [
        "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle",
        "elasticsearch", "dynamodb", "cassandra", "mariadb",
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
        "jenkins", "ci/cd", "github actions", "ansible", "linux", "nginx",
    ],
    "data_ml": [
        "machine learning", "deep learning", "pandas", "numpy", "tensorflow",
        "pytorch", "scikit-learn", "data analysis", "nlp", "computer vision",
        "power bi", "tableau", "spark", "hadoop", "airflow",
    ],
    "tools": [
        "git", "github", "gitlab", "jira", "confluence", "figma", "postman",
        "rest api", "graphql", "microservices",
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "project management", "agile", "scrum", "time management",
        "critical thinking", "collaboration",
    ],
}

# Flattened lookup: lowercase skill -> category
ALL_SKILLS = {
    skill: category
    for category, skills in SKILL_CATEGORIES.items()
    for skill in skills
}
