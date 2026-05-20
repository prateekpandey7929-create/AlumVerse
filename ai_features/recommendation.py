import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from accounts.models import Profile

def recommend_alumni(student_profile):
    alumni_profiles = Profile.objects.filter(user__role="alumni")

    data = []

    for alum in alumni_profiles:

        skills = alum.skills if alum.skills else ""

        data.append({
            "id": alum.user.id,
            "skills": skills
        })

    df = pd.DataFrame(data)

    if df.empty:
        return []

    df["skills"] = df["skills"].fillna("")

    if student_profile.skills:
        student_skills = student_profile.skills
    else:
        student_skills = ""

    vectorizer = TfidfVectorizer()

    try:

        tfidf_matrix = vectorizer.fit_transform(df["skills"])

        student_vector = vectorizer.transform([student_skills])

        similarity = cosine_similarity(student_vector, tfidf_matrix)

        scores = similarity[0]

        df["score"] = scores

        df = df.sort_values(by="score", ascending=False)

        return df.head(5)["id"].tolist()

    except:
        return []
