import pdfplumber

# Career path required skills inventory
career_skills_map = {
    "backend developer": ["python", "django", "sql", "postgresql", "rest api", "git", "docker", "aws", "redis", "fastapi", "flask"],
    "data scientist": ["python", "pandas", "numpy", "machine learning", "scikit-learn", "sql", "statistics", "tableau", "tensorflow", "pytorch"],
    "frontend developer": ["html", "css", "javascript", "react", "tailwind", "bootstrap", "git", "ui/ux", "figma", "typescript"],
    "devops engineer": ["docker", "kubernetes", "aws", "git", "jenkins", "terraform", "ansible", "linux", "bash", "cicd"],
    "mobile app developer": ["flutter", "react native", "swift", "kotlin", "java", "dart", "ios", "android", "firebase", "git"],
    "ui/ux designer": ["figma", "sketch", "adobe xd", "wireframe", "prototype", "user research", "usability", "mockup"],
    "software engineer": ["python", "java", "c++", "javascript", "sql", "git", "data structures", "algorithms", "oop", "testing"]
}

# Standard sections to verify layout quality
standard_sections = {
    "education": ["education", "academic", "university", "college", "degree", "school"],
    "experience": ["experience", "employment", "work history", "professional history", "internship"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "skills": ["skills", "technical skills", "competencies", "expertise", "technologies"]
}

def extract_text_from_pdf(file):
    """
    Extracts text from an uploaded Django InMemoryUploadedFile PDF object.
    """
    text = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def analyze_resume(file, target_career):
    """
    Evaluates the resume text against the target career requirements.
    Returns:
        score (int): Combined compatibility score (15 to 98)
        missing (list): Required keywords not found
        found (list): Required keywords successfully found
        advice (list): Practical layout/content tips to boost score
    """
    text = extract_text_from_pdf(file)
    text_lower = text.lower()
    
    if not text.strip():
        return 15, ["No text could be extracted from PDF"], [], ["Please upload a valid PDF file containing text (not scanned images)."]
    
    # 1. Section presence evaluation (20 pts)
    section_score = 0
    found_sections = []
    missing_sections = []
    
    for section_name, keywords in standard_sections.items():
        found = False
        for kw in keywords:
            if kw in text_lower:
                found = True
                break
        if found:
            section_score += 5
            found_sections.append(section_name.title())
        else:
            missing_sections.append(section_name.title())
            
    # 2. Text density & formatting layout (20 pts)
    length_score = 0
    word_count = len(text.split())
    if 250 <= word_count <= 1200:
        length_score = 20
    elif 100 <= word_count < 250:
        length_score = 10
    else:
        length_score = 5 # Too short or excessively long
        
    # 3. Target Career Keyword Match Rate (60 pts)
    target_career_clean = target_career.lower().strip()
    required_skills = career_skills_map.get(target_career_clean, career_skills_map["software engineer"])
    
    found_skills = []
    missing_skills = []
    
    for skill in required_skills:
        # Match using word boundaries or simple substring search
        if skill in text_lower:
            found_skills.append(skill.upper())
        else:
            missing_skills.append(skill.title())
            
    skill_match_percentage = len(found_skills) / len(required_skills) if required_skills else 0
    skill_score = int(skill_match_percentage * 60)
    
    # Combined score
    total_score = section_score + length_score + skill_score
    # Clamp score to realistic range
    total_score = max(15, min(total_score, 98))
    
    # Actionable advice compilation
    advice = []
    if missing_sections:
        advice.append(f"Missing sections: Add clearly labelled sections for {', '.join(missing_sections)}.")
    if word_count < 250:
        advice.append("Resume is too brief: Expand experience or projects bullets to provide detail (aim for 300-800 words).")
    elif word_count > 1200:
        advice.append("Resume is too dense: Consolidate details to fit onto 1 or 2 pages (aim under 1000 words).")
    
    if missing_skills:
        # Give advice on top missing skills
        top_missing = missing_skills[:4]
        advice.append(f"Add target technical terms for {target_career.title()}: incorporate keywords like {', '.join(top_missing)}.")
        
    if not advice:
        advice.append("Your formatting and content looks solid. Keep updating projects with metrics or numerical results.")
        
    return total_score, missing_skills, found_skills, advice
