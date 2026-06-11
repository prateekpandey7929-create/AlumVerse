def recommend_career(skills):
    """
    Suggests the top 3 matching career tracks based on user skills.
    Matches against Web Development, Data Science, DevOps, UI/UX, and Mobile tracks.
    """
    if not skills:
        return ["Software Engineer", "Backend Developer", "Frontend Developer"]

    skills_lower = skills.lower()
    careers = []

    # Data Science & Machine Learning
    if any(s in skills_lower for s in ["machine learning", "pandas", "numpy", "scikit-learn", "tensorflow", "statistics", "data analysis"]):
        careers.append("Data Scientist")
        careers.append("Data Analyst")
        
    # Backend Engineering
    if any(s in skills_lower for s in ["django", "api", "python", "sql", "postgresql", "node", "express", "java", "c#", "backend"]):
        careers.append("Backend Developer")
        careers.append("Software Engineer")

    # Frontend & UI/UX
    if any(s in skills_lower for s in ["html", "css", "javascript", "react", "vue", "angular", "ui/ux", "figma", "frontend"]):
        careers.append("Frontend Developer")
        careers.append("UI/UX Designer")

    # Cloud & DevOps
    if any(s in skills_lower for s in ["docker", "kubernetes", "aws", "cloud", "devops", "cicd", "git"]):
        careers.append("DevOps Engineer")
        careers.append("Cloud Architect")

    # Mobile Development
    if any(s in skills_lower for s in ["flutter", "react native", "android", "ios", "swift", "kotlin"]):
        careers.append("Mobile App Developer")

    # Defaults fallback
    if not careers:
        careers = ["Software Engineer", "Backend Developer", "Frontend Developer"]
    else:
        # Add general Software Engineer as general fallback
        careers.append("Software Engineer")

    # Clean duplicates and return top 3 recommendations
    unique_careers = []
    for c in careers:
        if c not in unique_careers:
            unique_careers.append(c)
            
    return unique_careers[:3]
