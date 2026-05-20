def chatbot_response(query):
    query = query.lower()

    if "job" in query:
        return "Go to Jobs section to explore opportunities."

    if "alumni" in query:
        return "Visit Alumni Directory to connect with alumni."

    if "skill" in query:
        return "Use Skill Gap Analyzer for improvement."

    return "Sorry, I didn't understand. Please try again."
