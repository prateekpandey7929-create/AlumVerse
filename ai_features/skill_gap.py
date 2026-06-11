import difflib

# Comprehensive set of tech roles and standard industry required skills
career_skills = {
    "backend developer": ["python", "django", "sql", "postgresql", "rest api", "git", "docker", "redis"],
    "frontend developer": ["html", "css", "javascript", "react", "tailwind", "git", "typescript", "webpack"],
    "fullstack developer": ["python", "django", "javascript", "react", "sql", "git", "rest api", "docker", "node"],
    "data scientist": ["python", "pandas", "numpy", "machine learning", "statistics", "sql", "scikit-learn", "tensorflow"],
    "data engineer": ["python", "sql", "spark", "hadoop", "etl", "aws", "postgresql", "data pipelines"],
    "devops engineer": ["docker", "kubernetes", "aws", "git", "jenkins", "terraform", "linux", "ci/cd"],
    "cloud architect": ["aws", "cloud security", "terraform", "kubernetes", "linux", "networking", "system architecture"],
    "mobile app developer": ["flutter", "react native", "swift", "kotlin", "java", "git", "firebase", "mobile design"],
    "android developer": ["kotlin", "java", "android sdk", "git", "gradle", "firebase", "sqlite"],
    "ios developer": ["swift", "objective-c", "xcode", "ios sdk", "git", "cocoapods", "core data"],
    "ui/ux designer": ["figma", "sketch", "adobe xd", "wireframing", "prototyping", "user research", "usability testing"],
    "software engineer": ["python", "java", "c++", "javascript", "git", "data structures", "algorithms", "oop"],
    "qa engineer": ["selenium", "testing", "qa", "unit testing", "javascript", "python", "bug tracking", "test automation"],
    "machine learning engineer": ["python", "pandas", "machine learning", "deep learning", "tensorflow", "pytorch", "numpy", "scikit-learn"],
    "cybersecurity analyst": ["cybersecurity", "security", "network security", "linux", "cryptography", "wireshark", "penetration testing"],
    "database administrator": ["sql", "mysql", "oracle", "postgresql", "database tuning", "backup recovery", "nosql"],
    "network engineer": ["networking", "cisco", "routers", "switches", "tcp/ip", "dns", "vpn", "firewalls"],
    "product manager": ["agile", "scrum", "product roadmap", "user research", "jira", "market analysis", "wireframing"],
    "embedded systems engineer": ["c", "c++", "embedded systems", "microcontrollers", "rtos", "linux", "firmware", "iot"],
    "blockchain developer": ["solidity", "ethereum", "smart contracts", "cryptography", "web3", "go", "javascript"]
}

def analyze_skill_gap(student_skills, career_goal):
    """
    Compares the student's skills list against standard career track skills.
    Returns:
        missing (list): Technical terms/skills missing from student profile.
    """
    # Parse student skills (handling comma separation and stripping whitespaces)
    student_skills_set = {s.strip().lower() for s in student_skills.replace(",", " ").split() if s.strip()}
    
    goal_clean = career_goal.lower().strip()
    
    # Check exact match first
    required = career_skills.get(goal_clean)
    
    if not required:
        # Check substring match (e.g. "python developer" contains "developer" or matches "backend developer")
        for role, skills in career_skills.items():
            if role in goal_clean or goal_clean in role:
                required = skills
                break
                
    if not required:
        # Use difflib close matches to find closest tech role
        close_matches = difflib.get_close_matches(goal_clean, list(career_skills.keys()), n=1, cutoff=0.3)
        if close_matches:
            required = career_skills[close_matches[0]]
            
    if not required:
        # Default fallback to general software engineer track if nothing matches
        required = career_skills["software engineer"]
        
    missing = []
    for skill in required:
        # Match word bounds / exact text checks
        if skill not in student_skills_set:
            # Also check if substring of the skill is in any of student skills
            matched = False
            for s in student_skills_set:
                if s == skill or (len(s) > 2 and s in skill):
                    matched = True
                    break
            if not matched:
                missing.append(skill.upper())
            
    return missing
