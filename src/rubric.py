"""
8x8 Online Class Quality Assessment Rubric
Calibrated directly against real pedagogical benchmarks from 8x8 evaluator evaluations.
"""

from typing import Dict, Any, List

EVALUATION_DIMENSIONS = {
    "rapport_building": {
        "name": "Rapport Building & Greeting",
        "weight": 0.20,
        "description": "Warm welcome, welcoming new joiners, asking student names, setting a joyful, safe atmosphere before jumping into content.",
        "signals_positive": [
            "Energetic and warm welcome greeting at start",
            "Takes dedicated time for new joiners to introduce themselves",
            "Asks about students' day or checks how they are feeling",
            "Friendly, structured closure with proper wrap-up"
        ],
        "signals_negative": [
            "Abrupt start jumping directly into revision/lesson without greeting",
            "Ignoring new students or giving no time for self-introduction",
            "Cold or rushed transitions into topics"
        ]
    },
    "individual_inclusivity": {
        "name": "Individual Student Consideration & Inclusivity",
        "weight": 0.25,
        "description": "Calling each child individually by name, asking questions turn-by-turn, ensuring no student is left passive or neglected during discussions and puzzle solving.",
        "signals_positive": [
            "Explicitly calls on students by their individual names repeatedly",
            "Distributes turns equally among all participants",
            "Checks in on silent or hesitant students during exercises/puzzles",
            "Acknowledges individual student responses thoughtfully"
        ],
        "signals_negative": [
            "Only interacting with 1-2 vocal students while others remain silent",
            "Calling for general answers without checking individual comprehension",
            "Moving on before ensuring everyone has attempted the task"
        ]
    },
    "energy_and_pleasantness": {
        "name": "Energy, Vocal Modulation & Pleasant Communication",
        "weight": 0.20,
        "description": "Enthusiastic, cheerful, kid-friendly delivery with high vocal variety, patience, and encouraging affirmations (avoiding monotonous or flat delivery).",
        "signals_positive": [
            "High vocal energy and pleasant, encouraging tone suited for children",
            "Frequent positive reinforcement ('Great job!', 'Awesome effort!', 'Superb!')",
            "Patient demeanor when a child struggles or makes a mistake",
            "Engaging storytelling / expressive voice"
        ],
        "signals_negative": [
            "Monotonous, tired, or disengaged vocal delivery",
            "Harsh corrections or visible frustration",
            "Long awkward silences or dead air"
        ]
    },
    "visual_setup_hygiene": {
        "name": "Visual Setup & Camera Hygiene",
        "weight": 0.15,
        "description": "Official 8x8 virtual background present and sharp, tutor face well-lit and centered, camera remains continuously turned ON throughout the session.",
        "signals_positive": [
            "Official 8x8 branded virtual background enabled with clean edges",
            "Tutor camera remains continuously ON throughout teaching",
            "Tutor face well-lit (good front lighting, no harsh backlighting)",
            "Engaged eye-contact towards the camera"
        ],
        "signals_negative": [
            "No virtual background or non-standard messy background",
            "Tutor camera turned off during lesson explanation",
            "Tutor face in shadow, poor lighting, or improper camera angle",
            "Severe visual glitching around the virtual background edges"
        ]
    },
    "structure_and_homework": {
        "name": "Lesson Structure, Interactivity & Homework (HWs)",
        "weight": 0.20,
        "description": "Logical lesson flow: Intro -> Review -> Interactive Concept/Puzzles/Videos -> Clear Homework (HWs) assignment -> Next-step preview.",
        "signals_positive": [
            "Structured flow with clear milestones (revision -> new topic -> puzzles)",
            "Effective use of interactive elements (puzzles, topic-related media/videos)",
            "Explicitly assigns and explains Homework (HWs) before ending class",
            "Clear instructions and expectations for practice"
        ],
        "signals_negative": [
            "Forgot to assign Homework (HWs) before disconnecting",
            "Passive lecture mode with no puzzles, slides, or interactive exercises",
            "Unclear pacing resulting in rushing at the end or cutting off"
        ]
    }
}

QUALITY_TIERS = {
    "Excellent": {
        "score_range": (85, 100),
        "badge_color": "#10B981", # Emerald Green
        "summary": "Outstanding class meeting the highest pedagogical and technical standards.",
        "hallmarks": [
            "Exceptional rapport building and dedicated attention to every child by name",
            "Consistently energetic, joyful, and kid-appropriate communication",
            "Active interactive exercises (puzzles, topic-related videos)",
            "Flawless 8x8 background, excellent lighting, camera ON throughout",
            "Clear Homework (HWs) assigned and explained"
        ]
    },
    "Good": {
        "score_range": (70, 84),
        "badge_color": "#3B82F6", # Bright Blue
        "summary": "Solid, structured, and engaging session with minor opportunities for enhancement.",
        "hallmarks": [
            "Good introduction and covers everyone in class individually",
            "8x8 background maintained, camera kept on",
            "Homework assigned",
            "Minor room for improvement: could be slightly more energetic, or add topic-related video aids"
        ]
    },
    "Average": {
        "score_range": (50, 69),
        "badge_color": "#F59E0B", # Amber / Orange
        "summary": "Covers basic requirements but exhibits noticeable gaps in engagement, energy, or visual setup.",
        "hallmarks": [
            "Basic one-to-one interaction present, but lacks warmth or enthusiasm",
            "Visual background present but has clarity/glitch issues or poor lighting",
            "May occasionally forget Homework or miss engaging quiet students during puzzle time"
        ]
    },
    "Poor": {
        "score_range": (0, 49),
        "badge_color": "#EF4444", # Red
        "summary": "Sub-par session failing critical engagement, pedagogical, or setup standards.",
        "hallmarks": [
            "Directly enters lesson without proper greeting, rapport, or intro for new joiners",
            "Camera turned off while teaching, face hidden, or missing 8x8 background",
            "Flat/monotone/unpleasant communication or lack of individual consideration",
            "No Homework given and minimal interactive elements"
        ]
    }
}
