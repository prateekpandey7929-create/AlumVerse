def chatbot_response(query):
    """
    Parses application support queries and returns helpful instructions
    on how to use AlumVerse capabilities. Returns HTML-compatible text.
    """
    q = query.lower().strip()

    # Greetings
    if any(greet in q for greet in ["hi", "hello", "hey", "greetings", "yo"]):
        return (
            "Welcome to the AlumVerse Support Assistant! 🎓<br>"
            "I can help you navigate the system. Ask me about:<br>"
            "1. <b>Verification</b>: How to request alumni access.<br>"
            "2. <b>Resume ATS</b>: How to analyze your CV score.<br>"
            "3. <b>Group Chat</b>: How to post public doubts.<br>"
            "4. <b>Jobs & Messaging</b>: Contacting mentors or viewing careers."
        )

    # Verification / Alumni access
    if any(k in q for k in ["verify", "approval", "alumni access", "request", "access"]):
        return (
            "<b>How to get Alumni Access:</b><br>"
            "1. Click the 'Request Alumni Access' button on the navbar (or navigate to /alumni-request/).<br>"
            "2. Enter your scholar number, branch, and graduation year.<br>"
            "3. After submission, the administration team will check database credentials and approve you.<br>"
            "4. Once approved, your role will be upgraded to Alumni, enabling job posting and mentorship booking."
        )

    # Resume ATS
    if any(k in q for k in ["resume", "ats", "analyzer", "pdf", "cv"]):
        return (
            "<b>How to use the AI Resume Analyzer:</b><br>"
            "1. Go to the 'Resume Analyzer' from your student dashboard (/resume-analyzer/).<br>"
            "2. Select your target career path (e.g. Backend Developer) from the dropdown.<br>"
            "3. Browse and upload your resume as a <b>PDF file</b>, then click 'Analyze'.<br>"
            "4. The system will calculate an ATS score and list missing industry keywords."
        )

    # Group Chat / Community doubts
    if any(k in q for k in ["group chat", "community", "doubts", "group", "forum"]):
        return (
            "<b>How to use the Community Chatroom:</b><br>"
            "1. Click 'Community Chat' on the navigation bar (/messages/community/).<br>"
            "2. You can read questions or career doubts posted by IIST students.<br>"
            "3. Any student or verified alumni can reply to these doubts in real-time.<br>"
            "4. Alumni profiles display a distinct green badge next to their names so you know it's a verified response."
        )

    # 1-to-1 Messaging
    if any(k in q for k in ["chat", "message", "inbox", "send", "contact"]):
        return (
            "<b>Connecting with Mentors:</b><br>"
            "1. Go to the 'Alumni Directory' from the top menu or dashboard.<br>"
            "2. Click 'View Profile' on any alumni you want to reach out to.<br>"
            "3. Click 'Message Alumni' to start a direct 1-to-1 conversation.<br>"
            "4. Direct messages can be accessed and replied to from your 'Inbox' page (/inbox/)."
        )

    # Jobs & Opportunities
    if any(k in q for k in ["job", "internship", "opportunity", "hiring", "post"]):
        return (
            "<b>Jobs and Placements:</b><br>"
            "- <b>Students</b>: View opportunities shared by alumni by clicking 'Jobs' or 'Explore' (/jobs/). Click 'Apply' to send applications.<br>"
            "- <b>Alumni</b>: Post jobs by clicking 'Post Opportunity' (/post-job/) from the dashboard or jobs menu. Specify job type and deadline."
        )

    # Skill Gap
    if any(k in q for k in ["skill", "gap", "skill gap", "career path", "recommendation"]):
        return (
            "<b>AI Skill Gap & Career Paths:</b><br>"
            "- <b>Skill Gap Analyzer</b>: Select a target career, and the analyzer compares your listed skills against industry requirements.<br>"
            "- <b>Career Path Recommendations</b>: Examines your skills list to recommend the top 3 career tracks you align with."
        )

    # Troubleshooting / Bugs / Issues
    if any(k in q for k in ["bug", "error", "broken", "issue", "not working", "fail"]):
        return (
            "<b>Troubleshooting Steps:</b><br>"
            "1. <b>Not Logged In?</b>: Most features require authentication. Please log in or register first.<br>"
            "2. <b>Database Errors?</b>: Run migrations using `python manage.py migrate` in your console.<br>"
            "3. <b>File Issues?</b>: Ensure files uploaded to the Resume Analyzer are valid PDF text files (not images).<br>"
            "4. <b>Still Stuck?</b>: Send us a detailed report via the 'Contact Us' form."
        )

    # Default fallback
    return (
        "I'm not sure I understood that question. You can ask me about:<br>"
        "- 'How to request verification?'<br>"
        "- 'How to analyze my resume?'<br>"
        "- 'Where is the group chat?'<br>"
        "- 'How do I post a job?'"
    )
