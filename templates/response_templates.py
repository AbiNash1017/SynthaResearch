import re
import random
from typing import Dict, Any, List

def normalize_text(text: str) -> str:
    """Normalizes typos like ga,ification (comma instead of m) and punctuation."""
    t = text.lower()
    # Handle common keyboard typo where ',' is right next to 'm'
    t = re.sub(r"ga[,.]ification", "gamification", t)
    t = re.sub(r"ga[,.]if", "gamif", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.split())

def detect_question_type(question: str) -> str:
    q = normalize_text(question)
    
    # 1. Check conversational / acknowledgements
    if any(q == w or q.startswith(w + " ") for w in ["okay", "ok", "got it", "cool", "fine", "alright", "all right", "great", "nice", "understood", "sure", "makes sense"]):
        return "acknowledgement"
    if any(w in q for w in ["hello", "hi", "hey", "who are you", "introduce"]):
        return "greeting"
        
    # 2. Key Domain Topics
    if any(w in q for w in ["pay", "price", "cost", "subscription", "rupee", "rupees", "dollar", "monthly", "affordable", "cheap", "sale", "discount"]):
        return "price"
    elif any(w in q for w in ["streak", "streaks", "gamif", "gamification", "badge", "badges", "points", "xp", "leaderboard", "reward", "rewards", "freeze", "competition", "game"]):
        return "gamification"
    elif any(w in q for w in ["minute", "minutes", "duration", "length", "long", "short", "bite", "hour", "daily time", "pace", "lecture"]):
        return "lesson_length"
    elif any(w in q for w in ["certificate", "credential", "resume", "cv", "job", "career", "hiring", "portfolio"]):
        return "certification"
    elif any(w in q for w in ["theory", "practical", "quality", "depth", "curriculum", "instructor", "hands-on", "exercise"]):
        return "curriculum_quality"
    elif any(w in q for w in ["complete", "finish", "abandon", "drop", "stop", "not able", "give up", "quit", "retention", "leave"]):
        return "completion"
    elif any(w in q for w in ["problem", "frustration", "pain", "annoying", "hate"]):
        return "pain_point"
    elif any(w in q for w in ["would you", "do you agree", "rate", "how likely", "scale"]):
        return "likert"
    elif any(w in q for w in ["rank", "prefer", "feature", "important", "priority", "choose", "what do you look"]):
        return "feature_rank"
    return "open"

# Multiple varied, highly-directive response options per archetype and category
RESPONSE_TEMPLATES_MULTI: Dict[str, Dict[str, List[str]]] = {
    "Impulse Buyer": {
        "greeting": [
            "Hey! I'm currently looking through my course library trying to figure out what to tackle next.",
            "Hi there! Glad to chat. Ask me anything about my learning habits or why I keep hoarding courses!"
        ],
        "acknowledgement": [
            "Yeah, exactly. That's why traditional 40-hour lecture dumps never work for someone like me.",
            "Glad you see where I'm coming from! It's an uphill battle against my own attention span.",
            "Right. Unless the interface keeps me hooked every 3 minutes, I'll drift off to Twitter or YouTube."
        ],
        "completion": [
            "Honestly, it starts with huge excitement on day 1. But by day 3, the instructor dives into 45-minute abstract slides with no code demo, and I completely lose steam.",
            "I've bought over 15 courses during Udemy sales for 499 rupees each, but finished maybe one. I get overwhelmed by how massive the syllabus looks and there are no quick milestones to celebrate.",
            "The finish line always feels hopelessly far away. If an app doesn't break a 20-hour topic into bite-sized daily chunks, my brain treats it like an intimidating chore and I abandon it."
        ],
        "gamification": [
            "Yes! Gamification definitely works on me. If I get an XP bonus or a streak alert at 9 PM saying 'Keep your 5-day streak alive!', I will open the app and do a 5-minute quiz just to keep the streak.",
            "Streaks and badges trigger my impulse psychology in a good way. The problem is when I lose a 10-day streak—it feels demoralizing, so having a 'streak freeze' feature like Duolingo has is crucial for me.",
            "Leaderboards give me a quick adrenaline rush. Even if it's just friendly competition, seeing my name jump up 3 spots makes me want to complete one more quick session."
        ],
        "lesson_length": [
            "Lessons have to be under 8 to 10 minutes max. If I see a 50-minute video lecture, I immediately put it off for the weekend, and that weekend never arrives.",
            "5 to 7 minutes is my golden window. Give me one clear concept, an interactive test question right away, and wrap it up. That builds momentum.",
            "Short videos are everything. I usually study on my phone after dinner, so if a lesson feels like a movie, I will just open Netflix instead."
        ],
        "price": [
            "I strongly prefer one-time sales. When Udemy drops a course from 3,499 down to 499 rupees, my brain screams 'deal!' and I swipe my card immediately.",
            "Monthly subscriptions scare me. I've signed up for memberships before and ended up paying for 4 months without logging in once. That guilt makes me avoid subscription apps.",
            "If it has to be a subscription, it would need to be very low—say 299 to 399 rupees a month—with the option to pause anytime without penalty."
        ],
        "pain_point": [
            "My number one frustration is 20-minute theoretical monologues before showing any real-world screen or project. I need hands-on action within the first 60 seconds.",
            "Lack of momentum. Most platforms make you feel like you haven't achieved anything until you finish an entire 10-hour module. I need daily micro-accomplishments.",
            "Information overload and guilt. Opening a dashboard that says 'You are 4% done with 38 hours remaining' makes me want to close the tab instantly."
        ],
        "certification": [
            "Certificates are nice to show off on LinkedIn for a few likes, but honestly, I don't care that much about accreditation. I just want to learn practical skills quickly.",
            "A digital certificate gives me a temporary dopamine hit, but since I rarely reach 100% completion, I've barely earned any."
        ],
        "curriculum_quality": [
            "It doesn't need to be PhD-level theoretical rigor. I prefer instructors who speak plainly, use humor, cut out the fluff, and build something cool right away.",
            "Give me cheat sheets, downloadable summary cards, and quick quizzes rather than 100-page slide decks."
        ],
        "likert": [
            "I'd rate that a solid 4 out of 5! It addresses my exact pain point, assuming the execution is snappy.",
            "About 3.5 out of 5. It sounds promising in theory, but my self-discipline is my biggest enemy so the app has to do the heavy lifting."
        ],
        "feature_rank": [
            "1. 5-minute micro-lessons, 2. Daily streak reminder with streak freeze, 3. Progress percentage circle, 4. Instant flash-quizzes.",
            "Bite-sized video clips first, daily habit streak second, and sale-based pricing third."
        ],
        "open": [
            "As someone who has 15 courses sitting untouched in my Udemy library, I need a platform that doesn't overwhelm me. I need quick momentum right from the first minute.",
            "What really matters to me is low friction. The minute a course feels like heavy university homework, I drop it. Keep it fast, visually stimulating, and rewarding."
        ]
    },
    "Streak Chaser": {
        "greeting": [
            "Hey! Just checking in right after finishing my morning streak lesson. What would you like to explore?",
            "Hello! Always happy to talk about study habits, streaks, and gamified learning!"
        ],
        "acknowledgement": [
            "Totally agree! Daily habits are the only way skills actually stick over time.",
            "Exactly. Once a habit loop is established in your routine, missing a day feels completely unnatural.",
            "Spot on! Gamification turns what used to feel like boring study time into a genuine daily highlight."
        ],
        "completion": [
            "I actually have a great completion record, but only if the app maintains daily continuity. If an app gives me a streak counter, I will show up 365 days in a row.",
            "My dropouts only happen if an app breaks my habit chain—like an unexpected server downtime or overly long weekend assignments that I can't fit into my schedule.",
            "I treat learning like a workout streak. If the app visually celebrates my daily attendance, I finish the full program. If it's just static video files with no tracking, I lose interest."
        ],
        "gamification": [
            "Streaks, XP, and weekly leagues are what keep me alive! The psychological urge to protect my streak counter is way stronger than my desire to read a textbook.",
            "I love the Duolingo league system where you compete in Bronze, Silver, Diamond divisions. Fighting to stay out of the demotion zone pushes me to do 3 extra lessons every Sunday night!",
            "Badges and visual quest chests give me an incredible feeling of progression. Without gamification, online learning feels lonely and dry."
        ],
        "lesson_length": [
            "3 to 7 minutes is the absolute sweet spot. That fits perfectly into my morning metro commute or right before sleeping.",
            "Keep them short and rapid-fire. A 5-minute interactive lesson with drag-and-drop questions feels energetic. Anything over 15 minutes breaks the micro-learning habit."
        ],
        "price": [
            "I am happy to pay 399 to 599 rupees per month for a premium tier like Duolingo Super, mainly to remove disruptive ads and get unlimited streak freezes.",
            "A subscription model makes total sense for daily habit apps because you're using it every single day. Just keep it affordable for students and early-career folks."
        ],
        "pain_point": [
            "Losing a 200-day streak due to a technical bug or confusing timezone logic is the most heartbreaking thing ever. It makes me want to delete the app.",
            "When the app suddenly throws an impossibly hard exercise with zero explanation and drains all my 'hearts', it penalizes learning instead of encouraging practice.",
            "Long, passive lectures with zero interactive touchpoints. If I'm just staring at a screen for 30 minutes without tapping anything, I get bored."
        ],
        "certification": [
            "Certificates are nice, but what I really want to share on my profile is my 365-day consistency badge and total XP earned.",
            "A shareable completion milestone card for social media with my streak stats would be awesome."
        ],
        "curriculum_quality": [
            "The curriculum needs to be gamified into skill trees with unlockable nodes. Unlocking the next branch feels like clearing a game stage.",
            "Spaced repetition is critical. Re-introducing old concepts through quick 2-minute review rounds keeps everything fresh."
        ],
        "likert": [
            "Strongly agree, 5 out of 5! Habit loops and gamification are the future of self-study.",
            "A definite 4.5 out of 5! If you nail the streak mechanics, you have a user for life."
        ],
        "feature_rank": [
            "1. Streak Counter & Freezes, 2. Weekly Competitive Leagues, 3. Bite-sized interactive drills, 4. Daily quest challenges.",
            "Daily streak first, push notifications second, and XP leaderboard third."
        ],
        "open": [
            "I love the Duolingo model. Learning should feel like playing a rewarding mobile game where you build consistency naturally without mental friction.",
            "The secret to retention isn't longer videos—it's lowering the activation barrier so showing up every single day requires almost zero willpower."
        ]
    },
    "Deep Learner": {
        "greeting": [
            "Hello. I'm currently reviewing my course notes and reference documentation. How can I assist?",
            "Good day. I am always open to discussing curriculum depth and academic standards in edtech."
        ],
        "acknowledgement": [
            "Indeed. Pedagogical integrity should always take precedence over superficial retention hacks.",
            "Precisely. A student seeking true professional competence needs substance, not animated celebrations.",
            "I agree. Superficial metrics only create an illusion of competence without real understanding."
        ],
        "completion": [
            "I actually finish almost all courses I enroll in—often 40 to 60 hours long—provided the instructor is an authoritative expert and explains first principles thoroughly.",
            "My primary reason for abandoning a course is discovering that it's just a surface-level overview masquerading as an advanced tutorial. If there are no challenging architectural problems, I leave.",
            "I measure completion by mastery, not badge counts. I will re-watch a 45-minute lecture 3 times until my local implementation matches production specifications."
        ],
        "gamification": [
            "To be blunt, I find cartoon badges, confetti animations, and sound effects juvenile and distracting. I am not playing Candy Crush; I am investing in professional expertise.",
            "Leaderboards encourage speed and guessing rather than deep contemplation. In software and engineering, rushing through a problem leads to terrible habits.",
            "If an app has gamification, please allow an option in settings to disable XP, badges, and cartoon mascots so serious learners can focus."
        ],
        "lesson_length": [
            "25 to 45 minutes is appropriate. You simply cannot explore distributed systems, statistical modeling, or nuanced architecture in a 3-minute video.",
            "Short snippets often fragment knowledge. I prefer comprehensive, end-to-end lectures accompanied by downloadable code repositories, schematics, and text transcripts."
        ],
        "price": [
            "I am completely willing to pay premium prices—2,000 to 5,000 rupees monthly or 25,000 annually—if the instructors are distinguished researchers or senior industry fellows.",
            "Price is secondary to signal-to-noise ratio. A 499 rupee course that wastes 10 hours of my time is vastly more expensive than a 10,000 rupee masterclass that delivers real expertise."
        ],
        "pain_point": [
            "Trivial examples. Instructors who demonstrate 'Hello World' and then leave production-level error handling as 'an exercise for the reader.'",
            "Outdated syllabus with instructors who clearly haven't worked in the modern industry for 5 years.",
            "Platforms that prioritize retention metrics and short videos at the expense of comprehensive mathematical or technical rigor."
        ],
        "certification": [
            "A generic certificate of completion has almost zero market value. What holds value is a rigorous proctored exam or a code review by an expert.",
            "Recruiters care about my GitHub code and problem-solving depth, not an automated participation certificate."
        ],
        "curriculum_quality": [
            "Rigorous syllabus, clear prerequisites, deep-dive problem sets, and verified instructor credentials are my baseline requirements.",
            "Comprehensive text notes and searchability inside video transcripts are essential for post-lecture review."
        ],
        "likert": [
            "I would rate that a skeptical 2 out of 5. It may appeal to casual consumers, but it lacks academic depth.",
            "A measured 2.5 out of 5. The risk is prioritizing user dopamine over genuine skill acquisition."
        ],
        "feature_rank": [
            "1. Advanced comprehensive curriculum, 2. Downloadable code/notebooks, 3. Direct Q&A with instructor, 4. Rigorous project assignments.",
            "Content depth first, documentation second, and distraction-free playback interface third."
        ],
        "open": [
            "Real mastery requires deliberate, uninterrupted practice. If a platform prioritizes genuine depth over vanity completion metrics, I will be a loyal subscriber.",
            "Education is not entertainment. When a platform respects the student's intellect with thorough explanations, the retention problem solves itself."
        ]
    },
    "Career Switcher": {
        "greeting": [
            "Hi! Taking a quick break from my evening coding session. What would you like to discuss?",
            "Hello! As someone transitioning into tech, I have a lot of thoughts on what works and what doesn't."
        ],
        "acknowledgement": [
            "That makes complete sense. When you have bills to pay and a career to pivot, efficiency is everything.",
            "Exactly right. Every study hour has an opportunity cost, so the return on investment must be crystal clear.",
            "Spot on. I need to walk into an interview and demonstrate tangible project skills immediately."
        ],
        "completion": [
            "I finish courses when I can clearly trace every module to a bullet point on a job description. If a course promises a portfolio project that impresses recruiters, I stick with it to the end.",
            "I drop out when a course turns out to be purely academic without explaining how things are actually done on a real company team.",
            "Time is my biggest constraint. Studying 2 hours each evening after a tiring day job is tough; if the course roadmap isn't crystal clear with weekly milestones, I burn out."
        ],
        "gamification": [
            "Streaks are helpful for accountability when I feel exhausted on a Wednesday night. Seeing my daily study calendar filled keeps me honest.",
            "Badges are fun, but let's be real: a recruiter doesn't care about my 50-day streak badge. They want to see a live deployed web app or a GitHub portfolio.",
            "Progress bars tied to job readiness—like 'You are 65% ready for Junior Cloud Roles'—are 100x more motivating to me than generic cartoon XP."
        ],
        "lesson_length": [
            "12 to 18 minutes is optimal. Long enough to build a real component, but short enough that I can finish one or two modules before dinner.",
            "Bite-sized modules that chain together into a weekly mini-project work best for my busy schedule."
        ],
        "price": [
            "I am ready to invest 1,500 to 3,000 rupees a month. I view this as an investment in my next salary bracket, so I'm willing to pay for career coaching or portfolio reviews.",
            "If a platform offers job placement assistance or resume reviews with industry mentors, I'd even consider a higher-tier subscription."
        ],
        "pain_point": [
            "Outdated curriculum. Spending 3 weeks learning a tool only to find out that companies haven't used it since 2021 is infuriating.",
            "Lack of hands-on debugging. Real software development is about resolving errors, not just copying an instructor's typing without understanding the bugs.",
            "No career transition guidance. Many platforms teach you syntax but don't teach you how to write a tech resume or talk through technical decisions in an interview."
        ],
        "certification": [
            "Certificates that carry industry weight—like AWS, Google, or university-backed credentials—are very valuable on my resume during a career change.",
            "A verified digital certificate plus a capstone portfolio project gives me credibility when competing against candidates with CS degrees."
        ],
        "curriculum_quality": [
            "Focus on industry standard workflows: Git, Docker, deployment pipelines, and teamwork simulation rather than isolated toy algorithms.",
            "Real-world capstone projects that I can confidently demo in an interview."
        ],
        "likert": [
            "I'd rate that 4 out of 5. It aligns well with my career transition objectives if it keeps me accountable.",
            "Strong 4.5 out of 5! Streamlining daily consistency while building real skills is exactly what working career switchers need."
        ],
        "feature_rank": [
            "1. Capstone portfolio builder, 2. Verified career certificate, 3. Job competency progress tracker, 4. Daily study schedule reminders.",
            "Portfolio projects first, industry mentorship second, and structured daily study schedule third."
        ],
        "open": [
            "I have limited time and high stakes because I'm switching careers. Every hour I invest on this platform must translate directly into interview confidence.",
            "I need an edtech app to be my career transition bridge—structured, accountable, and hyper-focused on modern industry requirements."
        ]
    },
    "Casual Browser": {
        "greeting": [
            "Hey there! Just exploring some fun apps on my phone. What's up?",
            "Hi! Happy to share my thoughts as a casual user."
        ],
        "acknowledgement": [
            "Yeah, totally! If it feels like school or work, I'm just going to close the app.",
            "Exactly. Learning should be relaxing and entertaining, not another stress factor in life.",
            "For sure. Simple, colorful, and fun is the only way to keep casual learners like me engaged."
        ],
        "completion": [
            "I rarely finish long courses. I'll open an app when I'm curious about a topic like digital illustration or conversational Spanish, browse for 3 days, and move on.",
            "If a course requires 30 hours of commitment, I won't even start. But if it's a 7-day mini challenge with 3-minute lessons, I actually finish it.",
            "I treat learning like browsing Instagram. If it's engaging and zero-stress, I stay; the moment it feels tedious, I uninstall."
        ],
        "gamification": [
            "I love fun animations, quirky character mascots, and colorful celebrations when I get an answer right. It makes my day a little brighter!",
            "Mini-games and flashcard swipes are super fun. If it feels like playing a puzzle game while picking up random facts, I'm hooked.",
            "I don't care about serious leaderboards, but collecting cute sticker badges or milestone rewards is very enjoyable."
        ],
        "lesson_length": [
            "Under 5 minutes for sure! I usually use learning apps while waiting for a friend at a cafe or on the bus. Anything longer doesn't fit my lifestyle.",
            "3 to 4 minutes max. Quick interactive questions with instant feedback work best."
        ],
        "price": [
            "I prefer 100% free apps supported by non-intrusive ads. If an app blocks basic lessons behind a 1,000 rupee paywall, I will immediately delete it.",
            "I might pay a tiny one-time fee like 99 rupees to remove ads, but I won't commit to a recurring monthly subscription."
        ],
        "pain_point": [
            "Strict penalties! Apps that lock you out for 5 hours when you make 3 mistakes are so annoying.",
            "Guilt-tripping push notifications that make you feel like a failure for missing a day. Keep the reminders cheerful, not passive-aggressive.",
            "Complex interfaces with too many menus, academic jargon, and dry text walls."
        ],
        "certification": [
            "I don't need a certificate. I'm just learning for personal fun and curiosity.",
            "A cute badge to save as a phone wallpaper would be cool, but formal certificates don't matter to me."
        ],
        "curriculum_quality": [
            "Keep it fun, accessible, and practical for daily conversation or creative hobbies.",
            "Interactive tap-and-match quizzes, audio snippets, and colorful illustrations."
        ],
        "likert": [
            "Around 3 out of 5 for me. It sounds cool, but my attention is pretty spontaneous.",
            "3.5 out of 5! If it stays free and lightweight, I'd definitely check it out."
        ],
        "feature_rank": [
            "1. Free bite-sized mini-lessons, 2. Fun animations and themes, 3. Low-pressure quizzes, 4. Offline mode.",
            "Free access first, snackable 3-minute content second, and cheerful mascot rewards third."
        ],
        "open": [
            "I treat learning apps as productive entertainment. If it feels like school or chores, I won't stick around. Make it effortless and fun.",
            "The best learning apps are the ones you can dip into for 3 minutes without guilt or pressure. Keep it delightful and easy."
        ]
    }
}

def get_varied_response(archetype: str, q_type: str, used_indices: List[int]) -> str:
    """Selects a fresh, non-repetitive response from the archetype's template pool."""
    arch_dict = RESPONSE_TEMPLATES_MULTI.get(archetype, RESPONSE_TEMPLATES_MULTI["Impulse Buyer"])
    options = arch_dict.get(q_type)
    
    # Fallback cascade
    if not options:
        if q_type == "pain_point":
            options = arch_dict.get("completion")
        elif q_type == "acknowledgement":
            options = arch_dict.get("open")
            
    if not options:
        options = arch_dict.get("open", ["I have shared my main thoughts on this."])

    # Pick an unused option if available
    available = [i for i in range(len(options)) if i not in used_indices]
    if not available:
        chosen_idx = random.randint(0, len(options) - 1)
    else:
        chosen_idx = available[0]
        used_indices.append(chosen_idx)
        
    return options[chosen_idx]

def apply_tone(response: str, traits: List[str]) -> str:
    """Subtly adjusts response phrasing to reflect persona traits if not already present."""
    # If the response already contains rich character dialogue, keep it clean
    if len(response) > 80:
        return response

    adjusted = response
    if "deal-seeking" in traits and "sale" not in adjusted.lower() and "price" not in adjusted.lower():
        adjusted += " I always look for a bargain or discount."
    elif "competitive" in traits and "compete" not in adjusted.lower() and "leaderboard" not in adjusted.lower():
        adjusted += " I always want to stay ahead on the leaderboard."
    elif "analytical" in traits and "data" not in adjusted.lower() and "substance" not in adjusted.lower():
        adjusted += " I look for clear empirical outcomes rather than surface hype."
    elif "easily distracted" in traits and "focus" not in adjusted.lower() and "drift" not in adjusted.lower():
        adjusted += " If it gets too slow, I quickly lose focus."
    return adjusted

def extract_stance(response: str) -> str:
    """Derives a stance (positive, neutral, negative) based on keywords in response."""
    r = response.lower()
    pos_words = ["love", "definitely", "strongly agree", "ideal", "ready to invest", "great", "loyal", "absolutely", "crucial", "yes", "works on me"]
    neg_words = ["distracting", "trap", "frustration", "uninstall", "never", "waste", "juvenile", "drifts", "sacrifice", "demoralizing", "overwhelmed", "abandon"]
    
    pos_hits = sum(1 for w in pos_words if w in r)
    neg_hits = sum(1 for w in neg_words if w in r)
    
    if pos_hits > neg_hits:
        return "positive"
    elif neg_hits > pos_hits:
        return "negative"
    return "neutral"
