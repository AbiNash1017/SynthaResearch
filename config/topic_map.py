import re

TOPIC_KEYWORDS = {
    "price": [
        "price", "pay", "cost", "subscription", "rupee", "rupees", "dollar",
        "expensive", "cheap", "sale", "discount", "fee", "afford", "pricing", "plan",
        "membership", "money", "free", "freemium"
    ],
    "gamification": [
        "streak", "streaks", "xp", "points", "badge", "badges", "leaderboard",
        "leaderboards", "game", "gamif", "gamification", "ga,ification", "level",
        "reward", "rewards", "rank", "competition", "compete", "freeze", "hearts", "gems"
    ],
    "lesson_length": [
        "minute", "minutes", "length", "long", "short", "bite", "hour", "duration",
        "time", "lecture", "video length", "quick", "snackable", "daily time"
    ],
    "completion": [
        "abandon", "finish", "complete", "drop", "quit", "retention", "consistency",
        "progress", "motivation", "not able to complete", "why", "stop", "stuck", "give up"
    ],
    "certification": [
        "certificate", "credential", "resume", "cv", "job", "career", "hiring",
        "portfolio", "linkedin", "interview", "recruiter", "accreditation"
    ],
    "curriculum_quality": [
        "quality", "depth", "theory", "practice", "instructor", "project", "syllabus",
        "content", "thorough", "exercises", "hands-on", "coding", "notes", "advanced"
    ],
    "acknowledgement": [
        "okay", "ok", "got it", "cool", "fine", "alright", "all right", "great",
        "nice", "interesting", "understood", "makes sense", "sure"
    ],
    "greeting": [
        "hello", "hi", "hey", "good morning", "good evening", "how are you", "who are you"
    ]
}

def detect_topic(text: str) -> str:
    """Matches text against topic keywords and returns the most relevant topic or 'general'."""
    text_clean = re.sub(r"[^\w\s]", " ", text.lower())
    words = text_clean.split()
    
    # Check exact multi-word / substring or word-level match
    text_lower = text.lower().replace(",", " ")
    for topic, keywords in TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower or any(w == kw for w in words):
                return topic
    return "general"
