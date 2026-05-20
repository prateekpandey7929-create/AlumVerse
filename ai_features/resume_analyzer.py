import pdfplumber

keywords = [
"python",
"django",
"machine learning",
"sql",
"data analysis",
"api",
]

def extract_text_from_pdf(file):

    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def analyze_resume(file):

    text = extract_text_from_pdf(file)
    text = text.lower()
    found = []
    for word in keywords:
        if word in text:
            found.append(word)
    score = int((len(found) / len(keywords)) * 100)
    missing = list(set(keywords) - set(found))
    return score, missing
