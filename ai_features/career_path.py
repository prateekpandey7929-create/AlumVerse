def recommend_career(skills):
    if not skills:
        return ["Software Developer", "Backend Developer", "Frontend Developer"]

    skills = skills.lower()

    careers = []

    if "machine learning" in skills or "pandas" in skills:
        careers.append("Data Scientist")

    if "django" in skills or "api" in skills or "python" in skills:
        careers.append("Backend Developer")

    if "html" in skills or "css" in skills or "javascript" in skills:
        careers.append("Frontend Developer")

    if "python" in skills:
        careers.append("Software Developer")

    if not careers:
        careers = ["Software Developer", "Backend Developer", "Data Analyst"]

    return list(set(careers))[:3]
