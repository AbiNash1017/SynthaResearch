"""
utils/normalizer.py
Robust Domain & Product Context Normalizer for Universal Synthetic User Research.

- Detects and corrects common spelling mistakes, typos, and formatting glitches.
- Infers canonical industry domains, target customer archetypes, and authentic professional roles.
- Maps domain and customer needs to realistic tools, workflows, pain points, and pricing expectations.
- Ensures synthetic personas are strictly aligned with business requirements and target users.
"""

import re
from typing import Dict, Any, List, Optional
from config.archetype_map import UNIVERSAL_ARCHETYPES

# Common business, technology, and industry typos mapped to correct terms
TYPO_MAPPING = {
    # Food & Hospitality / Restaurant / Kitchen
    r"\bresturnt\b": "restaurant",
    r"\brestaurent\b": "restaurant",
    r"\bresturant\b": "restaurant",
    r"\brestraunt\b": "restaurant",
    r"\brestaraunt\b": "restaurant",
    r"\brestaurnt\b": "restaurant",
    r"\bresturants\b": "restaurants",
    r"\brestaurents\b": "restaurants",
    r"\bkithen\b": "kitchen",
    r"\bkitchin\b": "kitchen",
    r"\bkitchens\b": "kitchens",
    r"\boners\b": "owners",
    r"\bonwer\b": "owner",
    r"\bonwers\b": "owners",
    r"\bowenr\b": "owner",
    r"\bowenrs\b": "owners",
    r"\bdecommerce\b": "e-commerce",
    r"\becomerce\b": "e-commerce",
    r"\becomm\b": "e-commerce",
    r"\be\s+commerce\b": "e-commerce",

    # Billing, Finance & Operations
    r"\bfinaces\b": "finances",
    r"\bfinace\b": "finance",
    r"\bfinnace\b": "finance",
    r"\bfinnaces\b": "finances",
    r"\bbiling\b": "billing",
    r"\bacounting\b": "accounting",
    r"\bacount\b": "account",
    r"\bacounts\b": "accounts",
    r"\binvetory\b": "inventory",
    r"\binventry\b": "inventory",
    r"\bdilivery\b": "delivery",
    r"\bdelivry\b": "delivery",

    # Software, Product & UX Research
    r"\bpos\b": "POS",
    r"\bp\.o\.s\b": "POS",
    r"\bai\b": "AI",
    r"\ba\.i\b": "AI",
    r"\bexperine\b": "experience",
    r"\bexperiance\b": "experience",
    r"\bexperince\b": "experience",
    r"\bvalidat\b": "validate",
    r"\bvalidte\b": "validate",
    r"\bvalidat\s+ethe\b": "validate the",
    r"\bvalidat\s+the\b": "validate the",
    r"\bsoftwear\b": "software",
    r"\bworkflo\b": "workflow",
    r"\bwork flows\b": "workflows",
    r"\bplateform\b": "platform",
    r"\bplatfrom\b": "platform",
    r"\bintergration\b": "integration",
    r"\bintergrations\b": "integrations",
    r"\bsubcription\b": "subscription",
    r"\bsubcriptions\b": "subscriptions",
    r"\bmanag\b": "manage",
    r"\bmanagment\b": "management",
    r"\bcustmize\b": "customize",
    r"\bcustomisable\b": "customizable",
    r"\bcustmer\b": "customer",
    r"\bcustmers\b": "customers",
    r"\bcustmor\b": "customer",
    r"\banalitics\b": "analytics",
    r"\bethe\b": "the",
    r"\ban\s+(?:decommerce|e-commerce)\b": "and e-commerce",
    r"\bin\s+agentic\s+way\b": "in an agentic way",
    r"\bthere\s+(bills|needs|orders|finances|clients|users|inventory)\b": r"their \1",
}

# Domain knowledge base with authentic roles, daily tools, realistic pain points, and pricing tolerance
DOMAIN_PROFILES = {
    "restaurant_hospitality": {
        "keywords": [
            "restaurant", "restaurent", "resturnt", "food", "kitchen", "cloud kitchen",
            "pos", "billing", "cafe", "dining", "hospitality", "qsr", "takeaway", "swiggy",
            "zomato", "kot", "menu", "table", "catering", "bistro", "chef", "eatery"
        ],
        "canonical_domain": "Restaurant & Hospitality Tech / Cloud Kitchen POS",
        "canonical_roles": [
            "Multi-Unit Restaurant Chain Owner",
            "Cloud Kitchen Operations Director & Executive Chef",
            "Restaurant General Manager & Head of Billing",
            "Food & Beverage Finance & Inventory Controller",
            "Fast-Casual Cafe Franchisee & Cashier Lead",
            "Hospitality Operations & POS Administrator"
        ],
        "canonical_tools": [
            "Toast POS, Excel daily register sheets, and manual cash drawer logs",
            "Petpooja / POSist and Swiggy/Zomato live partner merchant portals",
            "Square for Restaurants, paper kitchen order tickets (KOT), and QuickBooks",
            "Legacy Micros POS terminal and multi-outlet spreadsheet summaries",
            "Lightspeed Restaurant POS and Deliverect order aggregator tablet",
            "Revel Systems POS and manual physical inventory tally sheets"
        ],
        "canonical_pains": [
            "Order routing delays between front-of-house billing and kitchen tickets during peak rush hours",
            "End-of-day billing reconciliation discrepancies across dine-in, takeaway, and delivery aggregators",
            "High aggregator commission cuts and lack of synchronized multi-platform menu pricing",
            "Complex split-billing, tip tracking, and tax invoice compliance across multiple branches",
            "Real-time inventory deduction failures causing stockouts and canceled customer orders",
            "Staff training friction on complex legacy POS terminals leading to long checkout queues"
        ],
        "canonical_wtp": "Willing to invest $60–$180/month per outlet if it noticeably speeds up table turnover and automates reconciliation",
        "canonical_churn": "POS freezes during peak dinner hours, synchronization failures between kitchen and register, or slow support"
    },
    "ecommerce_retail": {
        "keywords": [
            "ecommerce", "e-commerce", "retail", "shop", "store", "checkout", "cart",
            "shipping", "d2c", "inventory", "merchandise", "fulfillment", "order management", "shopify"
        ],
        "canonical_domain": "E-Commerce & Omni-Channel Retail Operations",
        "canonical_roles": [
            "Direct-to-Consumer (D2C) Brand Founder",
            "E-Commerce Operations & Inventory Lead",
            "Omni-Channel Retail Store General Manager",
            "Digital Merchandising & Conversion Specialist",
            "Fulfillment & Warehouse Logistics Coordinator",
            "Retail Customer Experience Supervisor"
        ],
        "canonical_tools": [
            "Shopify Plus, Klaviyo, and Excel stock reconciliation sheets",
            "WooCommerce, ShipStation, and QuickBooks Online",
            "Amazon Seller Central and manual inventory tracking spreadsheets",
            "BigCommerce, Gorgias helpdesk, and return management portals",
            "Square for Retail and warehouse barcode scanners",
            "NetSuite ERP and automated order fulfillment pipelines"
        ],
        "canonical_pains": [
            "Multi-warehouse stockout sync lag and overselling during major sales events",
            "High return shipping handling costs and restocking bottlenecks",
            "Cart abandonment and checkout friction on mobile web traffic",
            "Fragmented order data across Shopify, Amazon, and offline store registers",
            "Rising customer acquisition costs making paid advertising unprofitable",
            "Complex multi-currency tax calculation and international customs compliance"
        ],
        "canonical_wtp": "Willing to pay $100–$300/month if it reduces stockouts and increases checkout conversion rates by 5%+",
        "canonical_churn": "Checkout downtime during flash sales, payment gateway glitches, or inventory desync"
    },
    "fintech_billing": {
        "keywords": [
            "fintech", "finance", "billing", "invoicing", "payment", "accounting", "tax",
            "reconciliation", "payroll", "banking", "credit", "ledger", "bookkeeping", "stripe"
        ],
        "canonical_domain": "FinTech, Automated Invoicing & Financial Operations",
        "canonical_roles": [
            "Small Business Head of Finance & Controller",
            "SaaS Billing & Revenue Operations Manager",
            "Independent Corporate Bookkeeper & Tax Advisor",
            "Enterprise Accounts Receivable Specialist",
            "FinTech Product Operations Lead",
            "Chief Financial Officer (SME)"
        ],
        "canonical_tools": [
            "Stripe Invoicing, QuickBooks Online, and manual CSV reconciliation",
            "Xero, Bill.com, and multi-bank portal exports",
            "NetSuite Financials and custom SQL revenue recognition dashboards",
            "Chargebee, Brex corporate cards, and Excel cash flow projections",
            "FreshBooks, PayPal Business, and bank statement spreadsheets",
            "Sage Intacct and automated dunning notification workflows"
        ],
        "canonical_pains": [
            "Manual reconciliation delays and matching unallocated customer bank transfers",
            "Involuntary churn from failed recurring card transactions and weak dunning recovery",
            "Multi-entity tax calculation errors and manual compliance reporting across jurisdictions",
            "Lack of real-time cash flow visibility and delayed customer invoice payments",
            "Complex custom pricing contracts that break standard automated billing cycles",
            "Disputed transactions and slow chargeback resolution pipelines"
        ],
        "canonical_wtp": "Willing to pay $150–$500/month or 0.5% of processed volume if it eliminates manual reconciliation and dunning churn",
        "canonical_churn": "Inaccurate ledger calculations, compliance vulnerabilities, or unhandled payment webhook drops"
    },
    "devtools_b2b": {
        "keywords": [
            "developer", "devtool", "code", "software", "api", "git", "devops", "cloud",
            "infrastructure", "ci/cd", "engineering", "kubernetes", "testing", "monitoring"
        ],
        "canonical_domain": "Developer Tooling & Cloud Infrastructure",
        "canonical_roles": [
            "Senior Backend Engineer & API Architect",
            "DevOps & Cloud Infrastructure Lead",
            "Engineering Manager & Delivery Lead",
            "Full-Stack Application Developer",
            "Site Reliability Engineer (SRE)",
            "Staff Platform Architect"
        ],
        "canonical_tools": [
            "GitHub Actions, Jira, Docker, and terminal CLI utilities",
            "Datadog, AWS Console, Slack alerts, and Terraform scripts",
            "GitLab CI/CD, VS Code, and Kubernetes manifests",
            "Postman, Sentry error monitoring, and Grafana dashboards",
            "Linear, Notion engineering docs, and GitHub PR reviews",
            "CircleCI, PagerDuty, and custom shell automation scripts"
        ],
        "canonical_pains": [
            "Pull request review bottlenecks and flaky CI/CD build pipelines wasting engineer hours",
            "Noisy false-positive alerts and context switching across fragmented observability tools",
            "Outdated or incomplete API documentation slowing down team onboarding",
            "Managing complex cloud infrastructure costs without clear resource attribution",
            "Debugging elusive production race conditions and distributed microservice failures",
            "Security compliance checks that block rapid deployment cycles"
        ],
        "canonical_wtp": "Willing to pay $25–$60 per seat/month if it saves 3+ engineering hours weekly per developer",
        "canonical_churn": "Lack of programmatic API/CLI access, slow response latency, or forced intrusive UI wrappers"
    },
    "health_wellness": {
        "keywords": [
            "health", "fitness", "wellness", "nutrition", "medical", "clinic", "patient",
            "workout", "gym", "diet", "mental health", "telehealth", "trainer", "habit"
        ],
        "canonical_domain": "Digital Health, Wellness & Clinical Care",
        "canonical_roles": [
            "Private Wellness Clinic Operations Lead",
            "Certified Nutritionist & Lifestyle Coach",
            "Boutique Fitness Studio Founder & Trainer",
            "Health-Conscious Active Professional",
            "Physical Therapist & Rehabilitation Specialist",
            "Holistic Healthcare Practitioner"
        ],
        "canonical_tools": [
            "Mindbody, paper intake forms, and Google Sheets client scheduling",
            "MyFitnessPal, Apple Health, and WhatsApp client check-ins",
            "SimplePractice, Stripe payments, and encrypted telehealth video",
            "Strava, Whoop band, and manual daily habit journal",
            "Cliniko EHR and paper patient appointment cards",
            "Trainerize and direct Instagram direct messages with clients"
        ],
        "canonical_pains": [
            "Tedious manual client intake paperwork and scheduling double-bookings",
            "Low long-term client adherence and high drop-off after the first 30 days",
            "Fragmented health data across wearables, apps, and clinical records",
            "Nagging, generic notifications that irritate clients rather than motivating them",
            "Complex medical billing and insurance reimbursement claim rejections",
            "Cluttered patient apps requiring too much manual daily data entry"
        ],
        "canonical_wtp": "Willing to pay $40–$120/month if it improves client retention and cuts administrative booking overhead",
        "canonical_churn": "Inaccurate sensor metrics, complex client onboarding, or intrusive advertising"
    },
    "edtech_education": {
        "keywords": [
            "education", "edtech", "learning", "student", "teacher", "course", "tutor",
            "school", "university", "classroom", "training", "curriculum", "academy"
        ],
        "canonical_domain": "EdTech & Educational Workflow Systems",
        "canonical_roles": [
            "Independent Online Academy Educator",
            "Higher Education Course Coordinator",
            "Corporate L&D Training Specialist",
            "High School STEM Department Head",
            "Professional Certification Self-Paced Learner",
            "Private Academic Tutor & Mentor"
        ],
        "canonical_tools": [
            "Canvas LMS, Zoom, and Google Classroom",
            "Teachable, Loom video recordings, and Discord student community",
            "Moodle, Notion course syllabus, and grading spreadsheets",
            "Blackboard, Turnitin plagiarism checker, and email threads",
            "Coursera, PDF assignment worksheets, and WhatsApp study groups",
            "Kajabi and Stripe course subscription portal"
        ],
        "canonical_pains": [
            "Low student engagement and completion rates in asynchronous courses",
            "Hours wasted manually grading repetitive assignments and tracking submissions",
            "Difficulty providing individualized feedback across cohorts of 100+ students",
            "Complex LMS user interfaces that confuse both faculty and students",
            "Lack of actionable student comprehension analytics before exam dropouts happen",
            "High subscription costs for enterprise educational software with poor usability"
        ],
        "canonical_wtp": "Willing to pay $30–$90/month if it measurably boosts cohort completion rates and saves grading time",
        "canonical_churn": "Clunky student mobile experience, rigid non-customizable course structures, or poor export options"
    },
    "social_media_community": {
        "keywords": [
            "social", "community", "audio", "voice", "podcast", "creator", "meetup",
            "hobby", "hobbyist", "friendship", "feed", "network", "micro-community",
            "vibecircle", "anti-doomscroll", "affinity", "burnout"
        ],
        "canonical_domain": "Social Media, Audio Communities & Interest Networks",
        "canonical_roles": [
            "Creative Audio Micro-Blogger & Hobbyist",
            "Local Interest Group & Meetup Organizer",
            "Digital Wellbeing Advocate & Community Moderator",
            "Casual Social Audio Explorer & Listener",
            "Independent Creator & Storyteller",
            "Active Affinity Club Member"
        ],
        "canonical_tools": [
            "Discord, Voice Memos app, and local meetup WhatsApp groups",
            "Substack, Spotify podcasts, and Instagram broadcast channels",
            "Clubhouse, Telegram interest groups, and Notion hobby journals",
            "BeReal, Apple Voice Notes, and event ticketing apps",
            "Reddit micro-subreddits and community Discord servers",
            "Luma event RSVPs and group chats"
        ],
        "canonical_pains": [
            "Exhausting algorithmic ragebait feeds that induce social burnout and anxiety",
            "Difficulty finding genuine, high-trust local connections with shared creative interests",
            "Awkwardness and friction in audio-only interactions without transcripts or visual context",
            "Invasive data tracking, ads, and engagement traps designed to hook screen time",
            "Toxicity and low-quality anonymous trolling in large unmoderated social platforms",
            "Lack of accessible audio tools (like smart transcripts, highlights, or searchability)"
        ],
        "canonical_wtp": "Willing to pay $5–$15/month for private, ad-free community spaces with verified members and high-trust moderation",
        "canonical_churn": "Spam accounts, creepy direct messages, buggy voice playback, or toxic feed algorithms"
    },
    "food_beverage": {
        "keywords": [
            "food", "recipe", "cooking", "grocery", "meal", "pantry", "beverage",
            "culinary", "ingredient", "diet", "mealcraft", "kitchen", "cook", "eater"
        ],
        "canonical_domain": "Food, Culinary Planning & Grocery Technology",
        "canonical_roles": [
            "Busy Professional & Home Cook",
            "Weekly Family Meal Planner & Grocery Buyer",
            "Nutrition-Focused Culinary Enthusiast",
            "Budget-Conscious Household Shopper",
            "Specialty Diet & Allergy Meal Coordinator",
            "Food Waste Reduction & Eco-Living Advocate"
        ],
        "canonical_tools": [
            "Instacart, Apple Notes grocery lists, and Paprika Recipe Manager",
            "Google Keep pantry checklists, NYT Cooking, and supermarket apps",
            "Mealime, MyFitnessPal, and refrigerator magnetic whiteboard",
            "HelloFresh delivery portal and Pinterest recipe boards",
            "Yummly and physical handwritten family recipe notebooks",
            "Amazon Fresh cart and spreadsheet weekly meal calendars"
        ],
        "canonical_pains": [
            "Hours wasted every weekend deciding what to cook and drafting fragmented grocery lists",
            "Fresh produce spoiling in the fridge and costly ingredient food waste",
            "Unreliable grocery delivery substitutions that ruin planned dinner recipes",
            "Juggling multiple conflicting dietary preferences and allergies within one household",
            "Cluttered recipe websites filled with invasive popups and endless life stories",
            "Difficulty budgeting grocery expenses amid rising supermarket food inflation"
        ],
        "canonical_wtp": "Willing to pay $8–$20/month if it saves 2+ hours of meal planning and eliminates weekly grocery waste",
        "canonical_churn": "Unrealistic or overly complex recipe ingredients, inaccurate grocery cart synchronization, or repetitive suggestions"
    }
}


def clean_typos(text: Optional[str]) -> str:
    """
    Cleans typos, misspellings, phonetic errors, and stray punctuation from a text string.
    Preserves proper capitalization and trims extraneous trailing characters.
    """
    if not text or not isinstance(text, str):
        return ""

    cleaned = text.strip()

    # Strip unmatched dangling trailing punctuation like ], ), }
    cleaned = re.sub(r"[\)\]\}]+$", "", cleaned).strip()

    # Apply typo pattern replacements (case-insensitive search, preserving case context)
    for pattern, replacement in TYPO_MAPPING.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # Clean double spaces
    cleaned = re.sub(r"[ \t]+", " ", cleaned).strip()

    # If starts with lowercase letter in sentence context, capitalize first letter
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    return cleaned


def detect_domain_profile(product_name: str, industry: str, description: str, audience: str) -> Dict[str, Any]:
    """
    Analyzes product details and identifies the closest domain profile,
    extracting authentic roles, tools, and pain points.
    """
    combined_text = f"{product_name} {industry} {description} {audience}".lower()

    best_match_key = None
    best_match_score = 0

    for domain_key, profile in DOMAIN_PROFILES.items():
        score = 0
        for kw in profile["keywords"]:
            if kw in combined_text:
                score += 1
                # Higher weight for keywords matched in industry or audience
                if kw in industry.lower():
                    score += 2
                if kw in audience.lower():
                    score += 2
        if score > best_match_score:
            best_match_score = score
            best_match_key = domain_key

    if best_match_key and best_match_score >= 1:
        return DOMAIN_PROFILES[best_match_key]

    # Dynamic fallback: synthesize aligned profile from audience words
    clean_aud = clean_typos(audience)
    # Filter out non-profession demographic words
    excluded_words = {
        "and", "for", "the", "with", "gen", "millennial", "aged", "years", "who", "are",
        "all", "any", "seeking", "experiencing", "their", "our", "from", "into"
    }
    words = [w.capitalize() for w in re.findall(r"\b[A-Za-z]{3,}\b", clean_aud) if w.lower() not in excluded_words]
    role_base = words[0] if words else "Active Participant"

    return {
        "canonical_domain": clean_typos(industry) or "General Business & Technology",
        "canonical_roles": [
            f"{role_base} Specialist",
            f"Active {role_base} Enthusiast",
            f"Independent {role_base} Explorer",
            f"Senior {role_base} Coordinator",
            f"Daily {role_base} User",
            f"Experienced {role_base} Practitioner"
        ],
        "canonical_tools": [
            f"Standard industry software, spreadsheets, and manual daily tracking registers for {clean_aud}",
            f"Traditional tools and email threads commonly used by {clean_aud}",
            f"Specialized niche software and legacy databases for {clean_aud}",
            f"Mobile apps and manual checklist sheets for {clean_aud}",
            f"Spreadsheets, messaging groups, and paper records for {clean_aud}",
            f"Cloud SaaS dashboards and manual data exports for {clean_aud}"
        ],
        "canonical_pains": [
            f"Excessive manual data entry and wasted administrative hours in {clean_aud} workflows",
            f"Lack of unified workflow integration causing errors and delays for {clean_aud}",
            f"High costs and complex learning curves with existing solutions in this space",
            f"Friction and time lost when syncing data between different tools used by {clean_aud}",
            f"Unreliable software performance and slow customer support during busy work cycles",
            f"Difficulty customizing existing software to match the unique daily needs of {clean_aud}"
        ],
        "canonical_wtp": "Strictly value-driven; requires clear proof of time and cost savings before purchase",
        "canonical_churn": "Steep learning curves, complicated setup, price increases, or unaddressed bugs"
    }


def normalize_experiment(experiment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Takes an experiment dictionary (which may contain typos or unpolished phrasing),
    cleans all text fields, infers the true domain profile, and returns an enriched,
    typo-free experiment dictionary.
    """
    if not isinstance(experiment, dict):
        return {}

    raw_name = experiment.get("product_name", "Innovative Product")
    raw_industry = experiment.get("industry_domain", "General Technology")
    raw_desc = experiment.get("product_description", "")
    raw_audience = experiment.get("target_audience", "General Users")
    raw_objs = experiment.get("research_objectives", [])

    clean_name = clean_typos(raw_name)
    if clean_name:
        clean_name = " ".join(w if w.isupper() else w.capitalize() for w in clean_name.split())

    clean_industry = clean_typos(raw_industry)
    clean_desc = clean_typos(raw_desc)
    clean_audience = clean_typos(raw_audience)
    clean_audience = re.sub(r"\bcloud kitchen\b(?!\s+operator)", "cloud kitchen operators", clean_audience, flags=re.IGNORECASE)

    # Clean research objectives list
    clean_objs = []
    if isinstance(raw_objs, list):
        for obj in raw_objs:
            co = clean_typos(str(obj))
            if co:
                clean_objs.append(co)
    elif isinstance(raw_objs, str):
        clean_objs = [clean_typos(raw_objs)]

    if not clean_objs:
        clean_objs = ["Validate target user experience and value proposition"]

    # Detect domain profile
    domain_prof = detect_domain_profile(clean_name, clean_industry, clean_desc, clean_audience)

    # If industry was generic or messy, prefer canonical domain title
    if len(clean_industry) < 4 or any(t in clean_industry.lower() for t in ["general technology", "restaurent", "decommerce", "restaurant an", "restaurant and e-commerce"]):
        if domain_prof and "canonical_domain" in domain_prof:
            clean_industry = domain_prof["canonical_domain"]

    normalized = {
        "product_name": clean_name,
        "industry_domain": clean_industry,
        "product_description": clean_desc,
        "target_audience": clean_audience,
        "research_objectives": clean_objs,
        "created_at": experiment.get("created_at", ""),
        "_domain_profile": domain_prof
    }

    return normalized


def generate_aligned_personas_fallback(
    experiment: Dict[str, Any],
    count: int = 5,
    seed: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Generates realistic, diverse synthetic user personas strictly aligned with
    the target customer, business requirements, and industry domain.
    Guarantees ZERO typos in personas, authentic occupations, tools, and pain points,
    with a rich demographic pool and non-repetitive backgrounds across runs.
    """
    from datetime import datetime
    import random

    norm_exp = normalize_experiment(experiment)
    p_name = norm_exp.get("product_name", "Product")
    p_desc = norm_exp.get("product_description", "")
    audience = norm_exp.get("target_audience", "Target Users")
    prof = norm_exp.get("_domain_profile", detect_domain_profile(p_name, norm_exp.get("industry_domain", ""), p_desc, audience))

    archetype_keys = list(UNIVERSAL_ARCHETYPES.keys())

    # Diverse global demographics pool
    female_names = [
        "Maya Patel", "Sofia Rodriguez", "Chloe Bennett", "Sunita Rao", "Leila Hosseini",
        "Amara Okafor", "Rachel Goldstein", "Mei-Ling Wu", "Freya Lindberg", "Nadia Chernova",
        "Camila Morales", "Zahra Al-Hashimi", "Jessica Barnes", "Ananya Iyer", "Emma Watson-Hall",
        "Yasmine Belkacem", "Olivia Vance", "Naomi Tanaka", "Fatima Al-Zahra", "Grace O'Malley",
        "Ingrid Bergman", "Chiara Rossi", "Kavita Sharma", "Linh Nguyen", "Hannah Arendt-Meyer"
    ]
    male_names = [
        "Mateo Fernandez", "Rohan Mehra", "Kai Tanaka", "David Miller", "Samuel Adebayo",
        "Liam O'Connor", "Carlos Mendez", "Tariq Hassan", "Daniel Kowalski", "Kenji Sato",
        "Zachary Taylor", "Andre Washington", "Henrik Lindqvist", "Vikram Joshi", "Julian Rossi",
        "Kwesi Appiah", "Lucas Silva", "Aaron Chen", "Nathan Brooks", "Aris Thorne",
        "Dmitri Ivanov", "Marcus Vance", "Siddharth Verma", "Antoine Dubois", "Felix Weber"
    ]
    neutral_names = [
        "Jordan Blake", "Morgan Ellis", "Alex Chen", "Riley Campbell", "Quinn Davies",
        "Taylor Kim", "Casey Rivera", "Samira Jensen", "Cameron Diaz", "Avery Brooks"
    ]

    locations = [
        "San Francisco, USA", "Austin, USA", "Chicago, USA", "New York, USA", "Seattle, USA",
        "Toronto, Canada", "Vancouver, Canada", "London, UK", "Manchester, UK", "Berlin, Germany",
        "Munich, Germany", "Amsterdam, Netherlands", "Stockholm, Sweden", "Paris, France",
        "Dublin, Ireland", "Zurich, Switzerland", "Barcelona, Spain", "Bengaluru, India",
        "Mumbai, India", "Singapore", "Tokyo, Japan", "Seoul, South Korea", "Sydney, Australia",
        "Melbourne, Australia", "Dubai, UAE", "Tel Aviv, Israel", "Nairobi, Kenya",
        "Cape Town, South Africa", "São Paulo, Brazil", "Mexico City, Mexico", "Taipei, Taiwan"
    ]

    educations = [
        "Bachelor's in Business Administration (BBA)",
        "B.S. in Computer Science & Information Systems",
        "Master of Business Administration (MBA)",
        "Bachelor's in Hospitality & Service Operations",
        "Associate Degree in Applied Management",
        "B.A. in Communications & Digital Media",
        "M.S. in Data Analytics & Operations Research",
        "Certified Professional (Industry Accreditations)",
        "Bachelor's in Finance & Accounting",
        "Diploma in Technical Project Management",
        "B.S. in Industrial Engineering",
        "Executive Certificate in Strategic Operations",
        "Bachelor's in Culinary Arts & Food Service",
        "Self-Taught Practitioner with 8+ Years Industry Experience",
        "M.S. in Human-Computer Interaction"
    ]

    incomes = ["middle", "upper-middle", "middle", "lower-middle", "upper-middle", "middle", "upper"]
    usage_frequencies = [
        "Daily throughout standard 8-hour operational shifts",
        "4 to 5 times per week during peak business hours",
        "Continuous background use throughout workdays",
        "Twice daily during reconciliation and operational handoffs",
        "Regularly during sprint planning and high-priority cycles"
    ]

    roles = prof.get("canonical_roles", [f"{audience} Lead"])
    tools = prof.get("canonical_tools", [f"Traditional tools and spreadsheets for {audience}"])
    pains = prof.get("canonical_pains", [f"Operational friction and wasted time for {audience}"])
    wtp_base = prof.get("canonical_wtp", "Carefully weighs pricing against tangible time and cost savings")
    churn_base = prof.get("canonical_churn", "Unreliable system performance, bugs during critical work hours, or unhelpful support")

    personas = []
    now_iso = datetime.now().isoformat()
    rng = random.Random(seed) if seed is not None else random.Random()

    # Create shuffled pools for unique selection in this batch
    shuffled_females = list(female_names)
    shuffled_males = list(male_names)
    shuffled_neutrals = list(neutral_names)
    shuffled_locations = list(locations)
    shuffled_educations = list(educations)
    shuffled_roles = list(roles)
    shuffled_tools = list(tools)
    shuffled_pains = list(pains)

    rng.shuffle(shuffled_females)
    rng.shuffle(shuffled_males)
    rng.shuffle(shuffled_neutrals)
    rng.shuffle(shuffled_locations)
    rng.shuffle(shuffled_educations)
    rng.shuffle(shuffled_roles)
    rng.shuffle(shuffled_tools)
    rng.shuffle(shuffled_pains)

    # Balanced archetype distribution with randomized ordering
    shuffled_archetypes = []
    while len(shuffled_archetypes) < count:
        batch = list(archetype_keys)
        rng.shuffle(batch)
        shuffled_archetypes.extend(batch)
    shuffled_archetypes = shuffled_archetypes[:count]

    gender_cycle = ["Female", "Male", "Female", "Male", "Non-binary", "Male", "Female", "Male"]
    rng.shuffle(gender_cycle)

    for i in range(count):
        arch_key = shuffled_archetypes[i]
        arch_data = UNIVERSAL_ARCHETYPES[arch_key]

        gender = gender_cycle[i % len(gender_cycle)]
        if gender == "Female":
            name = shuffled_females[i % len(shuffled_females)]
        elif gender == "Male":
            name = shuffled_males[i % len(shuffled_males)]
        else:
            name = shuffled_neutrals[i % len(shuffled_neutrals)]

        loc = shuffled_locations[i % len(shuffled_locations)]
        edu = shuffled_educations[i % len(shuffled_educations)]
        income = rng.choice(incomes)
        age = rng.randint(24, 54)
        usage_freq = rng.choice(usage_frequencies)

        occ = shuffled_roles[i % len(shuffled_roles)]
        current_tool = shuffled_tools[i % len(shuffled_tools)]
        pain = shuffled_pains[i % len(shuffled_pains)]

        # Archetype-specific willingness to pay adjustments
        if "Budget" in arch_key:
            wtp = f"Cautious and ROI-focused: {wtp_base}. Prefers low upfront risk, transparent pricing, or clear trial period."
            feat_pri = "Cost predictability, transparent tiers, essential core stability, and straightforward setup"
        elif "Power" in arch_key:
            wtp = f"High budget tolerance for depth: {wtp_base}, provided deep customization, robust APIs, and automation are included."
            feat_pri = "Extensibility, advanced automation, keyboard shortcuts, fast execution, and granular controls"
        elif "Busy" in arch_key:
            wtp = f"Willing to pay a premium immediately if onboarding takes under 5 minutes and eliminates {pain.lower()[:50]}."
            feat_pri = "Frictionless onboarding, rapid time-to-value, mobile accessibility, and streamlined workflows"
        elif "Traditionalist" in arch_key:
            wtp = f"Skeptical about new software fees: Requires proven track record and data safety before replacing {current_tool.split(',')[0]}."
            feat_pri = "Uptime stability, data security, zero habit disruption, and backwards compatibility"
        else:
            wtp = f"Flexible and experience-driven: {wtp_base}, with strong emphasis on intuitive UI and peer endorsements."
            feat_pri = "Intuitive user interface, visual clarity, low cognitive load, and engaging user experience"

        churn_risk = arch_data["behavioral_patterns"]["churn_trigger"]
        combined_churn = f"{churn_base}, or {churn_risk}"

        base_seeds = dict(arch_data["opinion_seeds"])
        opinion_seeds = {
            k: round(min(1.0, max(0.0, v + rng.uniform(-0.08, 0.08))), 2)
            for k, v in base_seeds.items()
        }

        # Dynamic, varied narrative structures for background stories
        story_templates = [
            # Style 1: Operational & Daily Workflow
            (
                f"{name} is a {age}-year-old {occ} based in {loc}. "
                f"In their day-to-day work dealing with {audience.lower()}, they rely heavily on {current_tool}. "
                f"Their primary operational bottleneck is {pain.lower()}, making them judge {p_name} strictly by how reliably it solves this issue."
            ),
            # Style 2: Strategic & ROI Focus
            (
                f"Operating out of {loc}, {name} ({age}) oversees critical operational workflows as a {occ}. "
                f"While currently managing with {current_tool}, persistent challenges around {pain.lower()} drain valuable time and focus. "
                f"They approach {p_name} with a clear return-on-investment expectation: it must prove tangible productivity gains to justify any migration."
            ),
            # Style 3: Hands-on Practitioner / Power User
            (
                f"With extensive practical experience in {loc}, {name} ({age}) serves as a {occ}. "
                f"Their core operations currently depend on {current_tool}, but frustration with {pain.lower()} has created significant day-to-day friction. "
                f"When evaluating {p_name}, they look for real architectural depth, speed, and dependable execution rather than superficial marketing promises."
            ),
            # Style 4: Habit Preservation & Pragmatic Skepticism
            (
                f"As an established {occ} in {loc}, {name} ({age}) values stability and proven reliability above all else. "
                f"They have well-honed routines built around {current_tool}; while {pain.lower()} is a known pain point, "
                f"they remain cautious about adopting {p_name} until long-term reliability and zero data disruption are convincingly demonstrated."
            ),
            # Style 5: Velocity & Cross-Functional Collaboration
            (
                f"Located in {loc}, {name} ({age}) is an active {occ} working closely with {audience.lower()}. "
                f"Having cycled through tools like {current_tool}, they find {pain.lower()} to be their biggest recurring obstacle. "
                f"They are actively seeking modern solutions like {p_name} that can streamline day-to-day workflows and eliminate administrative drag."
            )
        ]

        bg_story = story_templates[i % len(story_templates)]

        persona = {
            "id": f"persona_{i+1:03d}",
            "name": name,
            "age": age,
            "gender": gender,
            "occupation": occ,
            "location": loc,
            "income_bracket": income,
            "education": edu,
            "archetype": arch_key,
            "personality_traits": list(arch_data["personality_traits"]),
            "behavioral_patterns": {
                "current_tools": current_tool,
                "usage_frequency": usage_freq,
                "primary_pain_points": pain,
                "willingness_to_pay": wtp,
                "churn_triggers": combined_churn,
                "feature_priorities": feat_pri
            },
            "psychological_profile": dict(arch_data["psychological_profile"]),
            "background_story": bg_story,
            "opinion_seeds": opinion_seeds,
            "memory": {
                "conversation_history": [],
                "established_opinions": {},
                "last_updated": now_iso
            }
        }
        personas.append(persona)

    return personas
