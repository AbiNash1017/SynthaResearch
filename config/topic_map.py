import re

UNIVERSAL_TOPIC_KEYWORDS = {
    "pricing": [
        "price", "pay", "cost", "subscription", "rupee", "rupees", "dollar", "dollars",
        "expensive", "cheap", "sale", "discount", "fee", "afford", "pricing", "plan",
        "membership", "money", "free", "freemium", "billing", "tier", "license", "budget"
    ],
    "usability_ux": [
        "easy", "simple", "complex", "intuitive", "interface", "ux", "ui", "navigation",
        "confusing", "design", "layout", "onboarding", "cluttered", "clean", "friction",
        "steep", "learning curve", "effort"
    ],
    "features_functionality": [
        "feature", "features", "capabilities", "tool", "tools", "integration", "api",
        "sync", "export", "import", "functionality", "workflow", "customize", "customization",
        "automation", "shortcut", "dashboard", "analytics", "reporting"
    ],
    "reliability_performance": [
        "speed", "fast", "slow", "lag", "bug", "bugs", "crash", "security", "privacy",
        "reliable", "reliability", "uptime", "stable", "stability", "offline", "data protection"
    ],
    "switching_friction": [
        "alternative", "alternatives", "competitor", "competitors", "switch", "migrate",
        "migration", "replace", "current tool", "habit", "existing setup", "lock-in"
    ],
    "value_roi": [
        "worth", "value", "roi", "benefit", "benefits", "outcome", "save time", "return",
        "result", "results", "impact", "productivity", "solve", "useful"
    ],
    "support_community": [
        "support", "documentation", "docs", "help", "tutorial", "tutorials", "customer service",
        "guide", "community", "forum", "onboarding support"
    ],
    "acknowledgement": [
        "okay", "ok", "got it", "cool", "fine", "alright", "all right", "great",
        "nice", "interesting", "understood", "makes sense", "sure", "thanks", "thank you"
    ],
    "adoption_intent": [
        "would you use", "would you buy", "would you pay", "will you use", "would use",
        "adopt", "adoption", "recommend", "try", "switch to", "sign up", "purchase",
        "install", "use this product", "likely to use", "likelihood", "interest in using",
        "worth buying", "intend to use", "decision to buy"
    ],
    "greeting": [
        "hello", "hi", "hey", "good morning", "good evening", "how are you", "who are you"
    ]
}

def detect_topic(text: str) -> str:
    """Matches text against universal product topic keywords and returns the most relevant topic or 'general'."""
    text_clean = re.sub(r"[^\w\s]", " ", text.lower())
    words = text_clean.split()
    text_lower = text.lower().replace(",", " ")

    for topic, keywords in UNIVERSAL_TOPIC_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower or any(w == kw for w in words):
                return topic
    return "general"
