"""
WebVTT (.vtt) Transcript Parser
Converts standard WebVTT subtitle files into clean structured classroom dialogue.
"""

import re
from typing import List, Dict, Any

def parse_vtt(vtt_text: str) -> str:
    """
    Parses WebVTT content and returns formatted dialogue with timestamps.
    Example output line: [00:01:41] Ahna: Good evening, sir!
    """
    if not vtt_text:
        return ""
        
    lines = vtt_text.splitlines()
    clean_dialogue = []
    
    # Regex to match WebVTT timestamp line: 00:01:41.190 --> 00:01:42.590
    timestamp_pattern = re.compile(r"^(\d{2}:\d{2}:\d{2})\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}")
    
    current_timestamp = None
    last_speaker = None
    last_text = None
    
    for line in lines:
        line = line.strip()
        if not line or line == "WEBVTT" or line.isdigit():
            continue
            
        ts_match = timestamp_pattern.match(line)
        if ts_match:
            current_timestamp = ts_match.group(1)
            continue
            
        if current_timestamp and line:
            # Check if line contains "Speaker: message"
            if ":" in line:
                speaker_part, msg_part = line.split(":", 1)
                speaker = speaker_part.strip()
                message = msg_part.strip()
                
                # Check for consecutive repetition
                if speaker == last_speaker and message == last_text:
                    continue
                    
                formatted_entry = f"[{current_timestamp}] {speaker}: {message}"
                clean_dialogue.append(formatted_entry)
                last_speaker = speaker
                last_text = message
            else:
                # Text without explicit speaker prefix
                if line != last_text:
                    formatted_entry = f"[{current_timestamp}] {line}"
                    clean_dialogue.append(formatted_entry)
                    last_text = line
                    
    return "\n".join(clean_dialogue)
