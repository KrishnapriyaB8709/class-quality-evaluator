"""
Pre-loaded benchmark classes and synthetic transcripts calibrated to 8x8 evaluation cases.
Enables immediate 1-click testing for evaluators and demonstration.
"""

import os
from typing import Dict, Any, List

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_REAL_SUMIT_PATH = os.path.join(_CURRENT_DIR, "..", "data", "samples", "B435_sumit_ranjan.txt")
_REAL_PAVAN_PATH = os.path.join(_CURRENT_DIR, "..", "data", "samples", "B392_pavan_babu.txt")

def _load_transcript(path: str, fallback: str) -> str:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
    return fallback

BENCHMARK_SAMPLES: Dict[str, Dict[str, Any]] = {
    "B491 - Ayswarya Joseph (Excellent)": {
        "batch_id": "B491",
        "date": "29/06/2026",
        "tutor_name": "Ayswarya Joseph",
        "expected_quality": "Excellent",
        "evaluator_ground_truth": "Good one-to-one interaction, 8x8 background was there, asked questions by calling individually, plays topic related video and shares HWs clearly.",
        "camera_status": "Continuously ON",
        "background_status": "Official 8x8 Virtual Background (Sharp & Clear)",
        "lighting_status": "Bright, Clear Front Lighting",
        "transcript": """[00:00:05] Teacher Ayswarya: Good evening everyone! Welcome back to our 8x8 class! It's so lovely to see your smiling faces today!
[00:00:20] Teacher Ayswarya: Aarav, how are you doing today? Did you enjoy your weekend?
[00:00:28] Aarav: Yes teacher! I went to the park!
[00:00:32] Teacher Ayswarya: That sounds wonderful! And Diya, welcome! I see your camera is shining bright! How about you, Rohan? Are you ready for today's exciting challenge?
[00:00:45] Rohan: Yes teacher, I'm super ready!
[00:00:50] Teacher Ayswarya: Awesome! Today we have a very fun session on geometric patterns. Before we dive into puzzles, let's watch this quick 2-minute animation video showing how bees use hexagons in nature. Watch closely!
[00:03:10] Teacher Ayswarya: Superb! What shape did the bees use, Diya? Can you tell me?
[00:03:16] Diya: Hexagons! Because it has six sides!
[00:03:20] Teacher Ayswarya: Brilliant answer, Diya! High five! You are absolutely spot on!
[00:03:30] Teacher Ayswarya: Now let's turn to Puzzle Number 1 on your screen. Rohan, I want you to take the first attempt. Tell me which pattern comes next?
[00:03:45] Rohan: I think the blue triangle with two dots?
[00:03:50] Teacher Ayswarya: Great observation, Rohan! Let's verify together. Maya, do you agree with Rohan's answer?
[00:04:02] Maya: Yes teacher, because the dots increase by one every step!
[00:04:10] Teacher Ayswarya: Fantastic team work, both of you! You both cracked it so quickly!
[00:04:25] Teacher Ayswarya: Now Aarav, here is Puzzle Number 2 specially for you. Take your time and let us know your thought process.
[00:04:40] Aarav: It's the green square with four stars!
[00:04:45] Teacher Ayswarya: Incredible! You all solved every puzzle with zero errors! I am so proud of your progress today!
[00:05:05] Teacher Ayswarya: Now before we say goodbye, please take out your notebooks. For today's Homework, please complete Exercise 4 on Page 28. Also, try to find 2 objects in your room that have a hexagon or octagon shape, and we will share them at the start of next class!
[00:05:28] Teacher Ayswarya: Make sure to submit your HW photos in the app portal by Thursday evening.
[00:05:35] Teacher Ayswarya: You all did a phenomenal job today. Take care, have a wonderful evening, and see you all on Friday! Bye-bye everyone!
[00:05:45] Students: Bye teacher! Thank you!"""
    },
    
    "B552 - Bleson Bastin (Good)": {
        "batch_id": "B552",
        "date": "02/09/2026",
        "tutor_name": "Bleson Bastin",
        "expected_quality": "Good",
        "evaluator_ground_truth": "Good intro and introduction, fixed 8*8 background, given HWs, need more pleasant and energetic interaction with children.",
        "camera_status": "Continuously ON",
        "background_status": "Official 8x8 Virtual Background",
        "lighting_status": "Good Lighting",
        "transcript": """[00:00:05] Teacher Bleson: Good evening students. Welcome to today's 8x8 session.
[00:00:15] Teacher Bleson: Today we are covering division with remainder. Please open your textbooks to chapter 3.
[00:00:30] Teacher Bleson: Kabir, are you on page 42?
[00:00:35] Kabir: Yes sir, opened.
[00:00:40] Teacher Bleson: Good. Ananya, please read the first problem out loud.
[00:00:52] Ananya: 47 divided by 5 equals nine with remainder two.
[00:00:58] Teacher Bleson: Correct. That is right. Let's do the second problem now. Kabir, what is 58 divided by 7?
[00:01:15] Kabir: 8 remainder 2.
[00:01:20] Teacher Bleson: Correct. Let us move to the next slide on the whiteboard.
[00:01:40] Teacher Bleson: Ananya, solve number 4 on the screen.
[00:01:55] Ananya: 9 remainder 1.
[00:02:00] Teacher Bleson: Good. Now note down your homework. Complete questions 5 to 10 on page 43. Submit the homework before tomorrow 5 PM in the portal.
[00:02:25] Teacher Bleson: That concludes today's class. Thank you. See you next class."""
    },

    "B516 - Reshma P M (Average)": {
        "batch_id": "B516",
        "date": "03/09/2026",
        "tutor_name": "Reshma P M",
        "expected_quality": "Average",
        "evaluator_ground_truth": "Kept 8*8 background, individually considering each and every one in class in the beginning and during puzzles solving time also, given HWs, some clarity issues were there while keeping the background.",
        "camera_status": "Continuously ON",
        "background_status": "8x8 Background with halo/clarity edge artifacts",
        "lighting_status": "Moderate Lighting",
        "transcript": """[00:00:05] Teacher Reshma: Hello everyone. Good evening. Can you hear me properly?
[00:00:15] Students: Yes ma'am.
[00:00:20] Teacher Reshma: Okay, welcome. Neha, how are you? And Siddharth, are you able to see the screen?
[00:00:30] Siddharth: Yes ma'am, but your screen is slightly blurry around the edges.
[00:00:38] Teacher Reshma: Okay, I will adjust my background filter. Let us continue with our puzzle solving session.
[00:01:10] Teacher Reshma: Neha, can you look at puzzle 1 and tell me what you notice?
[00:01:25] Neha: The numbers are doubling every step, so next is 32.
[00:01:32] Teacher Reshma: Yes, correct Neha. Now Siddharth, puzzle 2 is for you.
[00:01:55] Siddharth: Is it 45?
[00:02:02] Teacher Reshma: Check once again Siddharth. Subtract 5 from 50.
[00:02:12] Siddharth: Ah, 45, yes.
[00:02:18] Teacher Reshma: Okay. Don't forget your homework. Practice worksheet number 2 from the app. See you next week."""
    },

    "B435 - Sumit Ranjan (Average - Real 8x8 Recording)": {
        "batch_id": "B435",
        "date": "28/08/2026",
        "tutor_name": "Sumit Ranjan",
        "expected_quality": "Average",
        "evaluator_ground_truth": "Background was there, one-to-one consideration was there, individually ask questions, need more energetic communication and more pleasant interaction, should give HWs, can sit in space where have light.",
        "camera_status": "Continuously ON",
        "background_status": "8x8 Background Present",
        "lighting_status": "Dim / Needs better front lighting",
        "transcript": _load_transcript(_REAL_SUMIT_PATH, """[00:01:41] Ahna: Good evening, sir!
[00:01:49] Sumit Ranjan: Hey, good evening, Anna.
[00:03:23] Sumit Ranjan: So, today, we'll unmute you, okay? But today, we'll be learning about King Apojis.
[00:37:30] Sumit Ranjan: Today, we will be ending the session 5 minutes early, okay? In the next class, we'll do a lot of puzzles. Okay? So, that's it for today. Bye-bye.""")
    },
    
    "B558 - Pranav Kumar (Poor)": {
        "batch_id": "B558",
        "date": "05/09/2026",
        "tutor_name": "Pranav Kumar",
        "expected_quality": "Poor",
        "evaluator_ground_truth": "Kept background, need a better intro and conclusion, should give time for the new joiners for self-introduction, need more energetic and pleasant interaction, abrupt start.",
        "camera_status": "Continuously ON",
        "background_status": "8x8 Background Present",
        "lighting_status": "Dim Lighting",
        "transcript": """[00:00:02] Teacher Pranav: Okay, let's start. Open question 5.
[00:00:10] Student Tanmay: Teacher, today is my first day in this batch...
[00:00:16] Teacher Pranav: Okay, you can just observe and catch up. We don't have much time today because we are behind schedule.
[00:00:30] Teacher Pranav: Question 5: solve for x when 2x + 10 = 30.
[00:00:45] Teacher Pranav: Anyone? Nobody knows? It is 10. You subtract 10 and divide by 2.
[00:01:05] Teacher Pranav: Next question. If you don't answer quickly I will just solve it myself.
[00:01:30] Teacher Pranav: Okay time is up. Class over."""
    },

    "B482 - TSP Abhishek (Poor)": {
        "batch_id": "B482",
        "date": "02/09/2026",
        "tutor_name": "TSP Abhishek",
        "expected_quality": "Poor",
        "evaluator_ground_truth": "Kept background, ask questions individually, directly go to revision without proper rapport building, should give time for new joiners, tutor camera was turned off while teaching, forgot HW.",
        "camera_status": "Turned OFF during lesson explanation (Violation)",
        "background_status": "8x8 Background visible when camera was on",
        "lighting_status": "Poor / Backlit",
        "transcript": """[00:00:03] Teacher Abhishek: Okay directly revising previous chapter. Turn to question 12.
[00:00:15] Student Riya: Sir, good evening sir.
[00:00:20] Teacher Abhishek: Yes yes good evening. Question 12, Varun, what is the answer to question 12 from last class?
[00:00:35] Varun: Sir I was absent last class.
[00:00:40] Teacher Abhishek: Why were you absent? You must watch recordings.
[00:00:55] [Camera turned off by tutor]
[00:01:10] Teacher Abhishek: I am turning off video to save bandwidth. Look at the slide.
[00:01:40] Teacher Abhishek: Varun, answer question 13 now.
[00:02:00] Varun: 14?
[00:02:05] Teacher Abhishek: No, 16. Okay, that's enough for today. Logging off."""
    },

    "B441 - Yasar Abdullah (Known Quality Issue - Poor)": {
        "batch_id": "B441",
        "date": "26/09/2026",
        "tutor_name": "Yasar Abdullah",
        "expected_quality": "Poor",
        "evaluator_ground_truth": "Kept background but cannot see his face, directly entered into class without proper rapport building, need a good happier communication.",
        "camera_status": "Face obstructed / Poor camera angle (Only forehead visible)",
        "background_status": "8x8 Background present",
        "lighting_status": "Dark room / Harsh backlighting",
        "transcript": """[00:00:02] Teacher Yasar: Hello. Everyone look at page 10.
[00:00:12] Student: Sir your camera is pointing at the ceiling, we can only see your forehead.
[00:00:22] Teacher Yasar: It's fine, just look at the screen share. Focus on the lesson.
[00:00:40] Teacher Yasar: Write this formula down. If you don't write it you will fail the test.
[00:01:10] Teacher Yasar: Next step, compute the area. Done?
[00:01:30] Teacher Yasar: Okay class is done. See you."""
    },

    "B392 - Pavan Babu (Known Quality Issue - Poor - Real 8x8 Recording)": {
        "batch_id": "B392",
        "date": "02/09/2026",
        "tutor_name": "Pavan Babu",
        "expected_quality": "Poor",
        "evaluator_ground_truth": "Interaction was there, but NO 8x8 background, need a better happy interaction with the kids, informed about the quality issues several times, no HW given.",
        "camera_status": "Continuously ON",
        "background_status": "No Virtual Background (Company Policy Violation)",
        "lighting_status": "Inadequate / Dim Workstation Lighting",
        "transcript": _load_transcript(_REAL_PAVAN_PATH, """[00:01:55] Aarit mittal: Good evening, sir.
[00:02:01] Pavan Babu: Good evening, guys, can you hear me?
[00:02:37] Pavan Babu: Yes, what was the previous topic, guys?
[00:02:46] Pavan Babu: Okay, we were doing Sicilian defense, right?
[00:59:55] Pavan Babu: Okay. Esman, thank you. Bye, Avishek!""")
    }
}
