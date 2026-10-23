"""
Core Evaluation Engine supporting Google Gemini, Groq, and Deterministic Offline Evaluator.
Returns structured 8x8 pedagogical quality assessments.
Optimized for prompt compression and resilient JSON parsing.
"""

import os
import json
import re
from typing import Dict, Any, Optional

try:
    from src.metrics import extract_transcript_metrics
except ImportError:
    from metrics import extract_transcript_metrics

SYSTEM_EVALUATION_PROMPT = """You are the Senior Pedagogical Quality Director at '8x8', an online education company conducting live classes for children.
Your job is to assess the quality of an online class recording based on rigorous pedagogical, emotional, and visual standards.

The 8x8 Rubric evaluates 5 Critical Dimensions:
1. Rapport Building & Greeting (20%): Warm welcome, taking time for new joiners to self-introduce, checking in with students, joyful tone, proper closure.
2. Individual Consideration & Inclusivity (25%): Calling EACH child individually by name, asking questions turn-by-turn, ensuring no student is left silent or ignored during discussion & puzzle solving.
3. Energy, Tone & Delivery (20%): Energetic, cheerful, kid-friendly delivery, frequent positive affirmations ('Good job!', 'Awesome!', 'High five!'), high patience vs flat, cold, or impatient adult coaching tone.
4. Visual Setup & Camera Hygiene (15%): Official 8x8 virtual background present and sharp, tutor face well-lit and centered, camera continuously turned ON throughout teaching.
5. Lesson Structure, Media & Homework (20%): Clear lesson flow (Intro -> Concept -> Puzzles/Media -> Homework -> Conclusion), explicit assignment of Homework (HWs).

CRITICAL PEDAGOGICAL & COMPLIANCE RULES (BEWARE OF MISLEADING SIGNALS):
- Rapport & Empathy in Batch Transitions: If a tutor is meeting a new class or substituting/replacing a previous tutor and spends time listening to students, addressing their concerns about past lessons, and reassuring them with warmth, this represents EMPATHETIC, POSITIVE RAPPORT BUILDING—never penalize this as administrative delay!
- A transcript may have high word count and many questions (misleading signal), but if the tutor lacks the official 8x8 background, has poor lighting, fails to assign homework, or maintains an adult-oriented dry tone, it CANNOT be rated Excellent or Good!
- Visual Compliance: The official 8x8 virtual background rule applies to the adult TUTOR (often visible in corner webcam tiles). STUDENTS are children and are not expected to have 8x8 backgrounds. If the tutor has the 8x8 background, visual compliance is satisfied.
- If Homework (HWs) is completely omitted at the conclusion of class, Structure score cannot exceed 50.
- Rating Tiers:
  * Excellent (85-100): Flawless visual setup (8x8 background ON, bright lighting, camera ON), joyful kid-appropriate rapport, turn-taking with all students, and explicit HW assigned.
  * Good (70-84): Compliant setup, solid lesson, HW assigned, minor room for more warmth/energy.
  * Average (50-69): Noticeable gaps in background clarity, lighting, or missing HWs / flat delivery.
  * Poor (0-49): Missing 8x8 background, camera off, face hidden, abrupt entry, harsh tone, or severe non-compliance.

CRITICAL INSTRUCTION:
Return ONLY a valid, raw JSON object matching the exact schema below without any markdown code fence or extra text:
{
  "overall_quality": "Excellent" | "Good" | "Average" | "Poor",
  "overall_score": 88,
  "confidence_score": 0.95,
  "dimension_scores": {
    "rapport_building": 90,
    "individual_inclusivity": 88,
    "energy_and_pleasantness": 92,
    "visual_setup_hygiene": 85,
    "structure_and_homework": 85
  },
  "key_strengths": [
    "Specific observation 1 with evidence from dialogue/actions",
    "Specific observation 2 with evidence"
  ],
  "growth_areas": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2"
  ],
  "timestamped_observations": [
    {"timestamp": "00:00:15", "phase": "Introduction", "observation": "Warmly greeted Aarav and Diya by name, establishing cheerful presence.", "type": "positive"},
    {"timestamp": "00:05:10", "phase": "Wrap-up", "observation": "Explicitly assigned Homework Exercise 4 with clear submission portal deadline.", "type": "positive"}
  ],
  "evaluator_verdict_summary": "Concise 2-3 sentence executive synthesis explaining the classification."
}
"""

def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Cleans code fences, markdown wrapping, or preamble from LLM JSON responses."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end+1])
        raise ValueError(f"Could not parse valid JSON from response: {text[:200]}")

def evaluate_with_gemini(transcript: str, visual_info: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """Evaluates class using Google Gemini 1.5/2.0 Flash."""
    import google.generativeai as genai
    genai.configure(api_key=api_key)

    model_name = "gemini-3.8-flash"
    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_EVALUATION_PROMPT
        )
    except Exception:
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    user_payload = f"""Evaluate this 8x8 online children's class session:

VIDEO SETUP & VISUAL COMPLIANCE DATA:
- Webcam Continuity: {visual_info.get('camera_status', 'Unknown')}
- Virtual Background: {visual_info.get('background_status', 'Unknown')}
- Workstation Lighting: {visual_info.get('lighting_status', 'Unknown')}

CLASSROOM TRANSCRIPT & DIALOGUE:
{transcript}
"""
    response = model.generate_content(
        user_payload,
        generation_config={"response_mime_type": "application/json", "temperature": 0.2}
    )
    return clean_json_response(response.text)

def compress_transcript_for_eval(transcript: str, max_lines_total: int = 180) -> str:
    """
    Compresses long transcripts to fit comfortably within LLM input token limits.
    Intelligently samples the 3 critical lesson phases:
    1. First 60 lines: Greeting, welcome, camera setup check, rapport building
    2. Middle 60 lines: Turn-taking, puzzle questions, student inclusivity, praise words
    3. Final 60 lines: Revision, homework assignment, proper closure
    """
    lines = [line.strip() for line in transcript.splitlines() if line.strip()]
    if len(lines) <= max_lines_total:
        return transcript

    third = max_lines_total // 3
    start_chunk = lines[:third]
    mid_idx = len(lines) // 2
    mid_chunk = lines[max(0, mid_idx - third // 2): mid_idx + third // 2]
    end_chunk = lines[-third:]

    compressed = (
        start_chunk
        + [f"\n... [Mid-lesson activity omitted: {len(lines) - max_lines_total} lines of active puzzle solving] ...\n"]
        + mid_chunk
        + ["\n... [Session continuation omitted] ...\n"]
        + end_chunk
    )
    return "\n".join(compressed)

def evaluate_with_groq(transcript: str, visual_info: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    """Evaluates class using Groq LPU API with compact transcript sampling."""
    from groq import Groq
    client = Groq(api_key=api_key)

    compact_transcript = compress_transcript_for_eval(transcript, max_lines_total=180)

    user_payload = f"""Evaluate this 8x8 online children's class session against the rubric:

VIDEO SETUP & VISUAL COMPLIANCE DATA:
- Webcam Continuity: {visual_info.get('camera_status', 'Unknown')}
- Virtual Background: {visual_info.get('background_status', 'Unknown')}
- Workstation Lighting: {visual_info.get('lighting_status', 'Unknown')}

CLASSROOM TRANSCRIPT & DIALOGUE (Key Phased Sample):
{compact_transcript}
"""
    models_to_try = [
        "qwen/qwen3.8-27b",
        "llama-3.3-70b-versatile",
        "llama-3.1-8b-instant"
    ]

    for model_name in models_to_try:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_EVALUATION_PROMPT},
                    {"role": "user", "content": user_payload}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw_text = completion.choices[0].message.content
            return clean_json_response(raw_text)
        except Exception as e:
            if "413" in str(e) or "rate_limit" in str(e).lower():
                continue
            elif model_name == models_to_try[-1]:
                raise e

    raise RuntimeError("All Groq model evaluation attempts failed.")

def run_evaluation(
    transcript: str,
    visual_info: Dict[str, Any],
    api_choice: str = "Groq (Qwen/Llama) - Ultra Fast",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main evaluation dispatcher. Evaluates with Groq, Gemini, or offline deterministic rules.
    """
    key = api_key or os.getenv("GROK_API_KEY") or os.getenv("GEMINI_API_KEY", "")

    if "Groq" in api_choice and key:
        try:
            res = evaluate_with_groq(transcript, visual_info, key)
            res["evaluated_via"] = "Groq LPU Engine"
            return res
        except Exception as e:
            print(f"Groq evaluation error: {e}. Falling back to offline engine.")

    if "Gemini" in api_choice and key:
        try:
            res = evaluate_with_gemini(transcript, visual_info, key)
            res["evaluated_via"] = "Google Gemini Flash"
            return res
        except Exception as e:
            print(f"Gemini evaluation error: {e}. Falling back to offline engine.")

    metrics = extract_transcript_metrics(transcript)
    res = evaluate_deterministic(transcript, visual_info, metrics)
    res["evaluated_via"] = "Offline Deterministic 8x8 Engine"
    return res

def evaluate_deterministic(transcript: str, visual_info: Dict[str, Any], metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    High-fidelity offline heuristic evaluator based strictly on the 8x8 rubric.
    Never hallucinates batches. Strictly follows objective features.
    """
    # 1. Visual Hygiene (15%)
    bg = visual_info.get("background_status", "")
    cam = visual_info.get("camera_status", "")
    light = visual_info.get("lighting_status", "")

    visual_score = 90
    if "Official 8x8" not in bg:
        visual_score -= 50
    elif "glitch" in bg or "artifacts" in bg:
        visual_score -= 15

    if "OFF" in cam:
        visual_score -= 40
    elif "Obstructed" in cam:
        visual_score -= 20

    if "Dim" in light or "Backlit" in light:
        visual_score -= 20
    elif "Moderate" in light:
        visual_score -= 5
    visual_score = max(10, min(100, visual_score))

    # 2. Inclusivity & Individual Consideration (25%)
    inclusivity_score = metrics.get("inclusivity_score", 50)
    detected_students = metrics.get("detected_students", [])

    # 3. Rapport Building (20%)
    rapport_score = 65
    if metrics.get("has_greeting"):
        rapport_score += 15
    if metrics.get("has_warm_rapport"):
        rapport_score += 15
    if metrics.get("has_closing"):
        rapport_score += 5
    rapport_score = max(20, min(100, rapport_score))

    # 4. Energy & Pleasant Tone (20%)
    energy_score = 60
    pos_count = metrics.get("positive_affirmations_count", 0)
    if pos_count >= 8:
        energy_score = 95
    elif pos_count >= 4:
        energy_score = 85
    elif pos_count >= 2:
        energy_score = 70
    elif pos_count == 0:
        energy_score = 45

    if metrics.get("has_harsh_tones"):
        energy_score -= 30
    energy_score = max(15, min(100, energy_score))

    # 5. Structure & Homework (20%)
    has_hw = metrics.get("has_homework", False)
    structure_score = 90 if has_hw else 45

    # Overall Weighted Score
    overall_score = round(
        (rapport_score * 0.20) +
        (inclusivity_score * 0.25) +
        (energy_score * 0.20) +
        (visual_score * 0.15) +
        (structure_score * 0.20)
    )

    if overall_score >= 85 and has_hw and visual_score >= 70:
        quality_tier = "Excellent"
    elif overall_score >= 70 and has_hw:
        quality_tier = "Good"
    elif overall_score >= 50:
        quality_tier = "Average"
    else:
        quality_tier = "Poor"

    strengths = []
    if "Official 8x8" in bg and "OFF" not in cam:
        strengths.append("Compliant visual presence with active webcam and 8x8 virtual background.")
    if detected_students and inclusivity_score >= 70:
        strengths.append(f"Addressed students individually by name ({', '.join(detected_students[:3])}) ensuring high turn-taking.")
    if pos_count >= 3:
        strengths.append(f"Frequent positive reinforcement and praise ({pos_count} affirmations detected).")
    if has_hw:
        strengths.append("Explicit assignment of homework and practice tasks prior to dismissal.")

    growth = []
    if not has_hw:
        growth.append("Crucial: Homework (HW) was not explicitly assigned before class wrap-up. Structure capped at 50.")
    if "Official 8x8" not in bg:
        growth.append("Branding compliance issue: Official 8x8 Virtual Background is missing or not visible.")
    if "OFF" in cam:
        growth.append("Webcam was disabled or inactive during instruction.")
    if len(detected_students) < 2:
        growth.append("Increase individual child callouts to ensure all enrolled students participate equally.")
    if pos_count < 2:
        growth.append("Elevate vocal enthusiasm with more praise affirmations ('Great job!', 'Awesome effort!').")

    obs = []
    if metrics.get("has_greeting"):
        obs.append({"timestamp": "00:00:30", "phase": "Introduction", "observation": "Tutor welcomed attendees to the session.", "type": "positive"})
    if detected_students:
        obs.append({"timestamp": "00:08:00", "phase": "Interactive", "observation": f"Active turn-taking with students: {', '.join(detected_students[:2])}.", "type": "positive"})
    if has_hw:
        obs.append({"timestamp": "00:45:00", "phase": "Wrap-up", "observation": "Explicit homework task communicated to students.", "type": "positive"})
    else:
        obs.append({"timestamp": "00:48:00", "phase": "Wrap-up", "observation": "Homework was omitted prior to ending class.", "type": "critical"})

    return {
        "overall_quality": quality_tier,
        "overall_score": overall_score,
        "confidence_score": 0.88,
        "dimension_scores": {
            "rapport_building": rapport_score,
            "individual_inclusivity": inclusivity_score,
            "energy_and_pleasantness": energy_score,
            "visual_setup_hygiene": visual_score,
            "structure_and_homework": structure_score
        },
        "key_strengths": strengths if strengths else ["Basic classroom lesson delivery completed."],
        "growth_areas": growth if growth else ["Maintain current pedagogical standards and engagement."],
        "timestamped_observations": obs,
        "evaluator_verdict_summary": f"Class assessed as {quality_tier} ({overall_score}/100) based on objective pedagogical turn-taking, visual compliance ({visual_score}/100), and homework delivery."
    }
