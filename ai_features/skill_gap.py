career_skills = {
"backend developer": ["python", "django", "sql", "rest api"],
"data scientist": ["python", "pandas", "machine learning", "statistics"],
"frontend developer": ["html", "css", "javascript", "react"],
}

def analyze_skill_gap(student_skills, career_goal):
    student_skills = student_skills.lower().split(",")

    required = career_skills.get(career_goal.lower(), [])

    missing = []

    for skill in required:
        if skill not in student_skills:
            missing.append(skill)

    return missing
