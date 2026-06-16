import pdfplumber
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Standard sections to verify layout quality
STANDARD_SECTIONS = {
    "education": ["education", "academic", "university", "college", "degree", "school", "qualification"],
    "experience": ["experience", "employment", "work history", "professional history", "internship", "work"],
    "projects": ["projects", "personal projects", "academic projects", "key projects"],
    "skills": ["skills", "technical skills", "competencies", "expertise", "technologies", "tools"]
}

# A comprehensive list of technical and professional skills to extract from JD and match
TECH_KEYWORDS = {
    "python", "django", "flask", "fastapi", "sql", "postgresql", "mysql", "sqlite", "oracle",
    "javascript", "typescript", "react", "vue", "angular", "node", "nodejs", "express",
    "html", "css", "bootstrap", "tailwind", "jquery", "sass", "git", "github", "docker",
    "kubernetes", "aws", "gcp", "azure", "ci/cd", "jenkins", "terraform", "ansible",
    "linux", "bash", "shell", "c", "c++", "c#", "java", "kotlin", "swift", "flutter", "react native",
    "machine learning", "deep learning", "nlp", "computer vision", "statistics", "pandas",
    "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "tableau", "powerbi",
    "spark", "hadoop", "mongodb", "redis", "elasticsearch", "rest api", "graphql",
    "agile", "scrum", "jira", "figma", "ui", "ux", "wireframing", "prototyping",
    "testing", "qa", "unit testing", "selenium", "cybersecurity", "security", "network",
    "devops", "cloud", "api", "restful", "microservices", "html5", "css3", "sass",
    "webpack", "npm", "yarn", "redox", "nextjs", "gatsby", "sass", "graphql", "redux"
}

# Simple list of English stop words to filter tokens without requiring NLTK downloads
ENGLISH_STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "cannot", "could", "did",
    "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have", "having",
    "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its",
    "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so", "some", "such", "than",
    "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who",
    "whom", "why", "with", "would", "you", "your", "yours", "yourself", "yourselves", "will", "shall", "please", "should",
    "would", "could", "also", "using", "work", "team", "experience", "role", "development", "project", "design", "manage"
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

def clean_text(text):
    """
    Cleans text: lowercase, extracts words and tags.
    """
    text = text.lower()
    # Normalize some common tags
    text = text.replace("c++", "cpp").replace("c#", "csharp").replace(".net", "dotnet")
    # Replace other non-alphanumeric characters with space
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    words = text.split()
    return words

def extract_skills(words_list):
    """
    Extracts technical and professional skills from list of words.
    """
    skills = set()
    for w in words_list:
        if w in TECH_KEYWORDS:
            skills.add(w)
    return skills

def analyze_resume(file, jd_text):
    """
    Evaluates the resume text against the Job Description.
    Returns:
        score (int): Combined compatibility score (15 to 98)
        missing (list): Job Description requirements not found in resume
        found (list): Job Description requirements successfully found in resume
        advice (list): Practical layout/content tips to boost score
    """
    resume_text = extract_text_from_pdf(file)
    
    if not resume_text.strip():
        return 15, ["No text could be extracted from PDF"], [], ["Please upload a valid PDF file containing text (not scanned images)."]
    
    if not jd_text.strip():
        return 15, ["Job Description is empty"], [], ["Please provide a Job Description to compare against."]

    # Try using Groq Llama 3
    from .groq_api import call_groq_completions
    system_prompt = "You are a professional ATS Resume Analyzer. Analyze the user's resume against the Job Description and return a structured report."
    prompt = f"""
Analyze this resume text against the provided job description.
Return a structured output in this format EXACTLY:
ATS SCORE: <number between 15 and 98>
STRENGTHS:
- <strength 1>
- <strength 2>
- <strength 3>
WEAKNESSES:
- <weakness 1>
- <weakness 2>
- <weakness 3>
ADVICE:
- <advice 1>
- <advice 2>
- <advice 3>

Job Description:
{jd_text}

Resume Text:
{resume_text}
"""
    
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
        res = call_groq_completions(messages, temperature=0.4)
        if res:
            # Parse score
            score_match = re.search(r'ATS SCORE:\s*(\d+)', res, re.IGNORECASE)
            score = int(score_match.group(1)) if score_match else 70
            score = max(15, min(score, 98))
            
            strengths = []
            weaknesses = []
            advice_list = []
            
            parts = re.split(r'(STRENGTHS:|WEAKNESSES:|ADVICE:)', res, flags=re.IGNORECASE)
            current_header = None
            for part in parts:
                clean_part = part.strip()
                if clean_part.upper() in ["STRENGTHS:", "WEAKNESSES:", "ADVICE:"]:
                    current_header = clean_part.upper()
                elif current_header:
                    lines = [line.strip().lstrip('-*•').strip() for line in clean_part.split('\n') if line.strip()]
                    lines = [l for l in lines if l]
                    if current_header == "STRENGTHS:":
                        strengths.extend(lines)
                    elif current_header == "WEAKNESSES:":
                        weaknesses.extend(lines)
                    elif current_header == "ADVICE:":
                        advice_list.extend(lines)
            
            found_display = strengths[:20] if strengths else ["Good technical keyword alignment", "Clear layout structure", "Has relevant project descriptions"]
            missing_display = weaknesses[:20] if weaknesses else ["Missing some industry-standard terms", "Need more metric achievements", "Expand on tools used"]
            advice_display = advice_list[:20] if advice_list else ["Incorporate more key terms from the JD", "Include numbers & metrics in project bullets"]
            
            return score, missing_display, found_display, advice_display
    except Exception as e:
        print(f"Groq Resume Analyzer failed, falling back to local: {e}")

    resume_lower = resume_text.lower()
    
    # 1. Section presence evaluation (20 pts)
    section_score = 0
    found_sections = []
    missing_sections = []
    
    for section_name, keywords in STANDARD_SECTIONS.items():
        found = False
        for kw in keywords:
            if kw in resume_lower:
                found = True
                break
        if found:
            section_score += 5
            found_sections.append(section_name.title())
        else:
            missing_sections.append(section_name.title())
            
    # 2. Text density & formatting layout (20 pts)
    length_score = 0
    word_count = len(resume_text.split())
    if 250 <= word_count <= 1000:
        length_score = 20
    elif 100 <= word_count < 250:
        length_score = 10
    else:
        length_score = 5 # Too short or excessively long
        
    # 3. TF-IDF Cosine Similarity & Keyword match (60 pts)
    # TF-IDF Cosine Similarity Contribution (30 pts)
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf = vectorizer.fit_transform([resume_text, jd_text])
        cos_sim = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        cos_score = int(cos_sim * 30)
    except Exception as e:
        print(f"Error computing cosine similarity: {e}")
        cos_sim = 0.1
        cos_score = 3
        
    # Keyword Overlap Contribution (30 pts)
    jd_words = clean_text(jd_text)
    resume_words = clean_text(resume_text)
    
    # Extract technical skills
    jd_skills = extract_skills(jd_words)
    resume_skills = extract_skills(resume_words)
    
    # Fallback to general terms if no tech keywords found in JD
    if not jd_skills:
        jd_skills = {w for w in jd_words if len(w) > 3 and w not in ENGLISH_STOP_WORDS}
        resume_skills = {w for w in resume_words if len(w) > 3 and w not in ENGLISH_STOP_WORDS}
        
    found_skills = jd_skills.intersection(resume_skills)
    missing_skills = jd_skills.difference(resume_skills)
    
    skill_match_percentage = len(found_skills) / len(jd_skills) if jd_skills else 0
    keyword_score = int(skill_match_percentage * 30)
    
    # Combined score
    total_score = section_score + length_score + cos_score + keyword_score
    # Clamp score to realistic range
    total_score = max(15, min(total_score, 98))
    
    # Actionable advice compilation
    advice = []
    if missing_sections:
        advice.append(f"Missing sections: Add clearly labelled sections for {', '.join(missing_sections)}.")
    if word_count < 250:
        advice.append("Resume is too brief: Expand experience or projects bullets to provide detail (aim for 300-800 words).")
    elif word_count > 1000:
        advice.append("Resume is too dense: Consolidate details to fit onto 1 or 2 pages (aim under 900 words).")
    
    if missing_skills:
        # Give advice on top missing skills (format display names nicely)
        top_missing = list(missing_skills)[:6]
        top_missing_display = [s.replace("cpp", "C++").replace("csharp", "C#").replace("dotnet", ".NET").upper() for s in top_missing]
        advice.append(f"Add key terms from the Job Description: incorporate keywords like: {', '.join(top_missing_display)}.")
        
    if not advice:
        advice.append("Your formatting and content match the Job Description perfectly! Keep updating metrics on your projects.")
        
    # Format display list for UI
    found_display = [s.replace("cpp", "C++").replace("csharp", "C#").replace("dotnet", ".NET").upper() for s in list(found_skills)[:20]]
    missing_display = [s.replace("cpp", "C++").replace("csharp", "C#").replace("dotnet", ".NET").upper() for s in list(missing_skills)[:20]]
    
    return total_score, missing_display, found_display, advice
