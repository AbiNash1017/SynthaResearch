"""
Universal Archetype Profiles for Product Research Simulations.
Designed to represent diverse consumer and professional behaviors across any industry domain.
"""

UNIVERSAL_ARCHETYPES = {
    "Budget-Conscious Pragmatist": {
        "description": "Carefully weighs price against utility, prioritizes free tiers or discounts, hates unexpected recurring charges.",
        "personality_traits": ["practical", "frugal", "analytical", "value-driven"],
        "behavioral_patterns": {
            "tech_adoption": "late majority — waits for proven solutions and deals",
            "decision_speed": "slow and deliberative",
            "primary_driver": "cost efficiency and tangible value",
            "churn_trigger": "price increases, hidden fees, or low perceived return on spend",
            "device_usage": "mobile and desktop"
        },
        "psychological_profile": {
            "mbti": "ISTJ",
            "risk_tolerance": "low",
            "motivation_type": "extrinsic-economic",
            "decision_style": "value-maximizing",
            "attention_span": "focused on terms and pricing"
        },
        "opinion_seeds": {
            "price_sensitivity": 0.90,
            "openness_to_change": 0.35,
            "tech_comfort": 0.60,
            "feature_complexity_tolerance": 0.40,
            "overall_sentiment_bias": 0.45
        }
    },
    "Power User / Optimizer": {
        "description": "Deeply explores features, seeks maximum control, customization, and efficiency; hates dumbed-down interfaces.",
        "personality_traits": ["analytical", "exacting", "tech-savvy", "detail-oriented"],
        "behavioral_patterns": {
            "tech_adoption": "early adopter / enthusiast",
            "decision_speed": "fast once technical specs and performance are verified",
            "primary_driver": "productivity boost, depth of capability, and workflow integration",
            "churn_trigger": "simplistic design, lack of keyboard shortcuts/APIs, or performance lags",
            "device_usage": "multi-monitor desktop and high-end devices"
        },
        "psychological_profile": {
            "mbti": "INTJ",
            "risk_tolerance": "high",
            "motivation_type": "intrinsic-mastery",
            "decision_style": "evidence-based",
            "attention_span": "long and meticulous"
        },
        "opinion_seeds": {
            "price_sensitivity": 0.30,
            "openness_to_change": 0.85,
            "tech_comfort": 0.95,
            "feature_complexity_tolerance": 0.90,
            "overall_sentiment_bias": 0.60
        }
    },
    "Busy Professional / Outcome-Driven": {
        "description": "Extremely time-pressured; needs instant clarity and quick time-to-value; gladly pays if it saves time.",
        "personality_traits": ["goal-oriented", "decisive", "pragmatic", "impatient"],
        "behavioral_patterns": {
            "tech_adoption": "early majority — adopts whatever solves their immediate bottleneck",
            "decision_speed": "rapid if immediate ROI is evident",
            "primary_driver": "time-saving, friction-free onboarding, and tangible outcomes",
            "churn_trigger": "steep learning curves, complicated setup, or unreliable workflows",
            "device_usage": "laptop and smartphone on the go"
        },
        "psychological_profile": {
            "mbti": "ENTJ",
            "risk_tolerance": "medium",
            "motivation_type": "extrinsic-career",
            "decision_style": "ROI-driven",
            "attention_span": "short-burst and task-focused"
        },
        "opinion_seeds": {
            "price_sensitivity": 0.35,
            "openness_to_change": 0.70,
            "tech_comfort": 0.75,
            "feature_complexity_tolerance": 0.50,
            "overall_sentiment_bias": 0.65
        }
    },
    "Casual Explorer": {
        "description": "Browses with low initial commitment; driven by curiosity, social proof, or sleek aesthetics.",
        "personality_traits": ["curious", "spontaneous", "aesthetic-minded", "easily distracted"],
        "behavioral_patterns": {
            "tech_adoption": "trend follower — joins via social buzz or casual recommendations",
            "decision_speed": "impulsive but non-committal",
            "primary_driver": "entertainment, curiosity, and enjoyable user experience",
            "churn_trigger": "rigid setup, overwhelming cognitive load, or early paywalls",
            "device_usage": "primarily mobile"
        },
        "psychological_profile": {
            "mbti": "ENFP",
            "risk_tolerance": "medium",
            "motivation_type": "intrinsic-recreational",
            "decision_style": "spontaneous",
            "attention_span": "short"
        },
        "opinion_seeds": {
            "price_sensitivity": 0.80,
            "openness_to_change": 0.75,
            "tech_comfort": 0.65,
            "feature_complexity_tolerance": 0.25,
            "overall_sentiment_bias": 0.55
        }
    },
    "Skeptical Traditionalist": {
        "description": "Satisfied with their existing habits or legacy tools; highly resistant to change unless reliability is guaranteed.",
        "personality_traits": ["conservative", "thorough", "cautious", "habit-driven"],
        "behavioral_patterns": {
            "tech_adoption": "late adopter / laggard",
            "decision_speed": "very slow; requires external validation and proven track record",
            "primary_driver": "stability, data privacy, and zero disruption to routine",
            "churn_trigger": "bugs, unannounced UI overhauls, or feeling patronized",
            "device_usage": "desktop or standard mobile"
        },
        "psychological_profile": {
            "mbti": "ISFJ",
            "risk_tolerance": "very low",
            "motivation_type": "status-quo preservation",
            "decision_style": "risk-averse",
            "attention_span": "methodical"
        },
        "opinion_seeds": {
            "price_sensitivity": 0.65,
            "openness_to_change": 0.15,
            "tech_comfort": 0.45,
            "feature_complexity_tolerance": 0.30,
            "overall_sentiment_bias": 0.35
        }
    }
}

# Alias for backwards compatibility
ARCHETYPE_PROFILES = UNIVERSAL_ARCHETYPES
