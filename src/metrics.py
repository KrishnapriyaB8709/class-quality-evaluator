"""
Linguistic, Pedagogical and Interaction Metrics Extractor
Extracts quantitative signals directly from transcripts/utterances.
Optimized with pre-compiled regex patterns for fast evaluation on full-session transcripts.
"""

import re
from typing import Dict, Any

COMMON_DISALLOWED_NAMES = {
    "the", "a", "an", "is", "are", "was", "were", "to", "in", "on", "at", "for", "and", 
    "or", "but", "so", "it", "this", "that", "i", "you", "we", "they", "he", "she", 
    "what", "how", "when", "where", "why", "teacher", "tutor", "coach", "sir", "ma'am", "madam",
    "yes", "no", "okay", "now", "puzzle", "number", "good", "correct", "let", "hello",
    "everyone", "student", "students", "focus", "check", "turn", "today", "question", 
    "answer", "write", "complete", "next", "please", "see", "chapter", "exercise", 
    "class", "page", "time", "notice", "open", "all", "here", "also", "just", "done",
    "bye", "thank", "because", "welcome", "right", "take", "make", "sure", "superb",
    "awesome", "brilliant", "fantastic", "wonderful", "high", "five", "guys", "sorry",
    "then", "well", "actually", "audio", "video", "screen", "share", "look", "listen",
    "wait", "remember", "great", "nice", "game", "board", "king", "queen", "first",
    "second", "third", "one", "two", "three", "defense", "dragons", "file", "rank",
    "knight", "bishop", "rook", "pawn", "pawns", "checkmate", "mate", "position", "move",
    "side", "like", "there", "say", "mistakes", "others", "pieces", "white", "black",
    "sweetheart", "buddy", "darling", "kid", "kids", "child", "children", "friend", "friends",
    "rakuten", "zoom", "lichess", "teams", "skype", "portal", "website", "link"
}

POSITIVE_REINFORCEMENTS = [
    "good job", "great job", "awesome", "well done", "superb", "excellent",
    "very good", "nice work", "proud of you", "high five", "brilliant",
    "fantastic", "keep it up", "wonderful", "phenomenal", "spot on", "great observation"
]

HOMEWORK_KEYWORDS = [
    "homework", "hw", "practice at home", "submit", "assignment", 
    "home work", "exercise for home", "share hw"
]

JOYFUL_RAPPORT_PATTERNS = [
    r"welcome back", r"lovely to see", r"smiling faces", 
    r"did you enjoy", r"how was your weekend", r"tell me about yourself",
    r"super ready", r"welcome to our class"
]

HARSH_OR_DISMISSIVE_PATTERNS = [
    r"fail the test", r"solve it myself", r"no time", r"behind schedule",
    r"why were you absent", r"just observe and catch up", r"if you don't answer"
]

# Pre-compiled regular expressions for maximum throughput
RE_QUESTION_STARTERS = re.compile(
    r"\b(can you|could you|who can tell|what do you think|do you understand|shall we|are you ready|what is|how many)\b",
    re.IGNORECASE
)
RE_AFFIRMATIONS = [(phrase, re.compile(r"\b" + re.escape(phrase) + r"\b", re.IGNORECASE)) for phrase in POSITIVE_REINFORCEMENTS]
RE_HOMEWORK = [re.compile(r"\b" + re.escape(hw) + r"\b", re.IGNORECASE) for hw in HOMEWORK_KEYWORDS]
RE_JOYFUL = [re.compile(pat, re.IGNORECASE) for pat in JOYFUL_RAPPORT_PATTERNS]
RE_HARSH = [re.compile(pat, re.IGNORECASE) for pat in HARSH_OR_DISMISSIVE_PATTERNS]
RE_CLOSING = re.compile(r"\b(see you|bye|goodbye|take care|have a wonderful|class over|logging off)\b", re.IGNORECASE)

# Universal line speaker regex: supports [HH:MM:SS] Name:, Name:, [Name]:, etc.
RE_LINE_SPEAKER = re.compile(r"(?:^|[\r\n])(?:\[\d{1,2}:\d{2}(?::\d{2})?\]\s*)?([A-Za-z][A-Za-z0-9_'\s]{1,24}?)\s*:", re.MULTILINE)

# Contextual vocatives and direct student addressing patterns
RE_ADDRESS_PATTERNS = [
    re.compile(r"\b(?:hi|hey|hello|good\s+evening|good\s+morning)\s*,?\s*([A-Z][a-z]+)\b"),
    re.compile(r"\b(?:what about|how about|goes to|turn for|over to)\s*,?\s*([A-Z][a-z]+)\b"),
    re.compile(r"\b([A-Z][a-z]+)\s*,\s*(?:can you|could you|please|what do you|tell me|try|solve|unmute|go ahead)\b")
]

def extract_transcript_metrics(transcript_text: str) -> Dict[str, Any]:
    """
    Computes objective pedagogical and interaction metrics from transcript text.
    """
    if not transcript_text or not transcript_text.strip():
        return {
            "total_words": 0,
            "total_lines": 0,
            "questions_count": 0,
            "positive_affirmations_count": 0,
            "affirmations_found": [],
            "detected_students": [],
            "name_mentions_count": 0,
            "has_greeting": False,
            "has_warm_rapport": False,
            "has_homework": False,
            "hw_keywords_found": [],
            "has_closing": False,
            "has_harsh_tones": False,
            "inclusivity_score": 0,
            "energy_density": 0.0
        }
    
    text_lower = transcript_text.lower()
    lines = [line.strip() for line in transcript_text.splitlines() if line.strip()]
    total_words = len(text_lower.split())
    total_lines = len(lines)
    
    # 1. Questions Count (Turn-taking trigger)
    explicit_questions = transcript_text.count("?")
    question_starters = len(RE_QUESTION_STARTERS.findall(text_lower))
    total_questions = max(explicit_questions, question_starters)
    
    # 2. Positive Reinforcements (Vocal warmth & encouragement)
    pos_count = 0
    found_affirmations = []
    for phrase, pat in RE_AFFIRMATIONS:
        matches = len(pat.findall(text_lower))
        if matches > 0:
            pos_count += matches
            found_affirmations.append(f"{phrase} ({matches}x)")
            
    # 3. Homework (HW) Detection
    has_homework = any(pat.search(text_lower) for pat in RE_HOMEWORK)
    hw_matches = [hw for hw in HOMEWORK_KEYWORDS if hw in text_lower]

    # 4. Joyful Warm Greeting & Rapport Detection
    first_portion = text_lower[:int(len(text_lower) * 0.35)] if len(text_lower) > 200 else text_lower
    has_warm_greeting = any(pat.search(first_portion) for pat in RE_JOYFUL)
    has_basic_greeting = any(g in first_portion for g in ("good evening", "good morning", "welcome", "hello"))

    # 5. Harsh / Disengaged tone
    has_harsh = any(pat.search(text_lower) for pat in RE_HARSH)

    # 6. Proper Closure
    last_portion = text_lower[int(len(text_lower) * 0.6):] if len(text_lower) > 200 else text_lower
    has_closing = bool(RE_CLOSING.search(last_portion))
    
    # 7. Robust Speaker & Student Detection Across Multi-Format Transcripts
    from collections import Counter
    raw_speakers = [m.strip() for m in RE_LINE_SPEAKER.findall(transcript_text) if not m.lower().startswith("audio shared")]
    speaker_counts = Counter(raw_speakers)
    total_turns = sum(speaker_counts.values()) or 1

    # Identify the primary teacher/tutor to ensure they are never categorized as a student
    teacher_name = None
    for spk, cnt in speaker_counts.most_common(2):
        if any(role in spk.lower() for role in ["teacher", "tutor", "coach", "sir"]) or (cnt / total_turns > 0.35):
            teacher_name = spk
            break

    # Student speakers identified directly from speaker labels
    student_speakers = set()
    for spk, cnt in speaker_counts.items():
        if spk != teacher_name and spk.lower() not in COMMON_DISALLOWED_NAMES and len(spk) >= 3:
            student_speakers.add(spk.title())

    # Addressed student names (e.g., quiet or called-upon participants)
    addressed_names = set()
    for pat in RE_ADDRESS_PATTERNS:
        for match in pat.findall(transcript_text):
            m_title = match.strip().title()
            if m_title.lower() not in COMMON_DISALLOWED_NAMES and m_title.lower() != (teacher_name or "").lower() and len(m_title) >= 3:
                mention_count = len(re.findall(r"\b" + re.escape(m_title) + r"\b", transcript_text, re.IGNORECASE))
                if mention_count >= 2 or any(m_title in s for s in student_speakers):
                    addressed_names.add(m_title)

    # Deduplicate first name vs full name candidates (e.g. 'Aidan' vs 'Aidan Abraham')
    all_candidate_students = set(student_speakers)
    for addr in addressed_names:
        if not any(addr in full_name for full_name in student_speakers):
            all_candidate_students.add(addr)

    detected_students = sorted(list(all_candidate_students))
    
    # Count frequency of these actual student names in the transcript
    total_name_calls = 0
    for name in detected_students:
        first_token = name.split()[0]
        name_pat = re.compile(r"\b" + re.escape(first_token) + r"\b", re.IGNORECASE)
        total_name_calls += len(name_pat.findall(transcript_text))
    
    # Inclusivity score: calibrated to real 8x8 classes (2-4 students per batch)
    unique_students_count = len(detected_students)
    if unique_students_count >= 3 and total_name_calls >= 6:
        inclusivity_score = 95
    elif unique_students_count >= 2 and total_name_calls >= 4:
        inclusivity_score = 80
    elif unique_students_count >= 1 and total_name_calls >= 2:
        inclusivity_score = 65
    elif unique_students_count >= 1:
        inclusivity_score = 45
    else:
        inclusivity_score = 25

    energy_density = round(((pos_count + total_questions) / max(total_words, 1)) * 100, 2)
    
    return {
        "total_words": total_words,
        "total_lines": total_lines,
        "questions_count": total_questions,
        "positive_affirmations_count": pos_count,
        "affirmations_found": found_affirmations[:5],
        "detected_students": detected_students[:6],
        "name_mentions_count": total_name_calls,
        "has_greeting": has_basic_greeting,
        "has_warm_rapport": has_warm_greeting,
        "has_harsh_tones": has_harsh,
        "has_homework": has_homework,
        "hw_keywords_found": hw_matches,
        "has_closing": has_closing,
        "inclusivity_score": inclusivity_score,
        "energy_density": energy_density
    }
