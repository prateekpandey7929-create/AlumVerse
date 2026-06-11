def chatbot_response(query):
    """
    Parses application support queries and returns helpful instructions
    on how to use AlumVerse capabilities. Returns HTML-compatible text.
    """
    q = query.lower().strip()

    # Greetings
    if any(greet in q for greet in ["hi", "hello", "hey", "greetings", "yo", "help"]):
        return (
            "Welcome to the **AlumVerse Support Assistant!** 🎓<br><br>"
            "I can help you with anything on the platform. Ask me about:<br>"
            "1. 🔑 <b>Verification</b>: How to request verified alumni access.<br>"
            "2. 📄 <b>Resume ATS Analyzer</b>: How to check compatibility against Job Descriptions.<br>"
            "3. 🚨 <b>Forgot / Change Password</b>: Resetting credentials.<br>"
            "4. 💬 <b>Group & Direct Chats</b>: Contacting mentors or posting doubts.<br>"
            "5. 💼 <b>Jobs & Placements</b>: Accessing postings or sharing opportunities.<br>"
            "6. 🛠️ <b>Skill Gap Analyzer</b>: Closing target career mismatches."
        )

    # Verification / Alumni access
    if any(k in q for k in ["verify", "approval", "alumni access", "request", "access", "approve"]):
        return (
            "<b>🎓 How to get Alumni Access:</b><br><br>"
            "1. Go to the <a href='/alumni-request/'>Request Alumni Access</a> page.<br>"
            "2. Enter your scholar number, department, and graduation year.<br>"
            "3. After you submit, the administrator team will verify your record and approve you.<br>"
            "4. <b>Dynamic Registration</b>: Upon admin approval, the system will automatically create/upgrade your alumni profile and email you your login credentials!"
        )

    # Forgot Password & Reset
    if any(k in q for k in ["forgot password", "reset password", "forgot", "password reset", "recover"]):
        return (
            "<b>🔑 Forgot Password Recovery:</b><br><br>"
            "If you forgot your password, follow these steps:<br>"
            "1. Go to the <a href='/forgot-password/'>Forgot Password</a> page.<br>"
            "2. Enter your registered college email or personal email address.<br>"
            "3. The system will dispatch an actual verification OTP to your email (via admin.alumverse@gmail.com).<br>"
            "4. Enter the OTP code on the verification screen, choose a new password, and verify to complete the reset!"
        )

    # Change Password
    if any(k in q for k in ["change password", "update password", "modify password", "new password"]):
        return (
            "<b>🔒 How to Change Password:</b><br><br>"
            "If you are logged in and want to change your password:<br>"
            "1. Navigate to your <a href='/profile/'>My Profile</a> dashboard.<br>"
            "2. Under the 'Account Security' section, click on **Change Password** (or go to <a href='/profile/change-password/'>Change Password Page</a>).<br>"
            "3. Input your current password followed by your new password, then save."
        )

    # Resume ATS Analyzer
    if any(k in q for k in ["resume", "ats", "analyzer", "pdf", "cv", "job description", "jd"]):
        return (
            "<b>📄 AI Resume ATS Analyzer:</b><br><br>"
            "We have implemented a semantic TF-IDF matcher to check resume compatibility:<br>"
            "1. Visit the <a href='/resume-analyzer/'>Resume Analyzer Page</a>.<br>"
            "2. Upload your CV/Resume in <b>PDF format</b>.<br>"
            "3. Copy and paste the specific **Job Description (JD)** from any job post in the text field.<br>"
            "4. The system computes a semantic matching score using local NLP models and lists exactly which technical terms are found, missing, and layout recommendations."
        )

    # Group Chat / Community doubts
    if any(k in q for k in ["group chat", "community", "doubts", "group", "forum", "chat room"]):
        return (
            "<b>👥 Community Chatroom:</b><br><br>"
            "1. Navigate to the <a href='/messages/community/'>Community Chat</a> forum.<br>"
            "2. You can read, create, or respond to career doubts shared by fellow IIST students.<br>"
            "3. Verified alumni profiles will display a green check badge so students know they are getting direct, reliable industry guidance."
        )

    # 1-to-1 Messaging
    if any(k in q for k in ["chat", "message", "inbox", "send", "contact", "mentor", "pm"]):
        return (
            "<b>💬 Direct 1-on-1 Chats with Alumni:</b><br><br>"
            "1. Go to the <a href='/alumni/'>Alumni Directory</a>.<br>"
            "2. Find a mentor you would like to connect with and click 'View Profile'.<br>"
            "3. Click **Message Alumni** to start a direct thread.<br>"
            "4. You can check all incoming messages and replies anytime from your <a href='/inbox/'>Inbox</a> page."
        )

    # Jobs & Opportunities
    if any(k in q for k in ["job", "internship", "opportunity", "hiring", "post", "placement"]):
        return (
            "<b>💼 Jobs & Internships Hub:</b><br><br>"
            "- <b>For Students</b>: Browse through active postings shared by alumni on the <a href='/jobs/'>Jobs Directory</a>. You can view deadlines and click 'Apply'.<br>"
            "- <b>For Alumni</b>: Share job opportunities from your firm by clicking <a href='/post-job/'>Post Opportunity</a> and filling in target details."
        )

    # Skill Gap
    if any(k in q for k in ["skill", "gap", "skill gap", "career path", "recommendation"]):
        return (
            "<b>🛠️ AI Skill Gap Analyzer & Career Paths:</b><br><br>"
            "- <b>Skill Gap Analyzer</b>: Go to the <a href='/skill-gap/'>Skill Gap Analyzer</a>, enter any target job title (e.g. 'Cloud Architect'), and our NLP engine matches standard industry requirements against your profile skills to return missing competencies.<br>"
            "- <b>Career Paths</b>: Check <a href='/ai-recommendations/'>Career Paths</a> to get top mentor recommendations dynamically compiled based on your skills profile."
        )

    # Troubleshooting / Bugs / Issues
    if any(k in q for k in ["bug", "error", "broken", "issue", "not working", "fail", "logout"]):
        return (
            "<b>🛠️ Troubleshooting Steps:</b><br><br>"
            "1. <b>Authentication Check</b>: Ensure you are logged in to use direct messaging, resume checks, and skill analysis.<br>"
            "2. <b>Resume Formatting</b>: ATS analyzer expects text-based PDF documents. Ensure your file is not scanned as an image.<br>"
            "3. <b>Email verification issues?</b>: Make sure correct SMTP settings are configured at the bottom of settings.py to receive actual emails."
        )

    # Default fallback
    return (
        "I'm not sure I understood that question. You can ask me about:<br>"
        "- 'How to reset my password?'<br>"
        "- 'How does the ATS analyzer work?'<br>"
        "- 'Where can I change my password?'<br>"
        "- 'How do I request alumni verification?'"
    )
