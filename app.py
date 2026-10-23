"""
8x8 Class Quality Evaluator
AI-Powered Assessment of Online Live Children's Classes
Built for the Humaniti AI Recruitment Challenge
"""

import streamlit as st
import json
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
from src.rubric import EVALUATION_DIMENSIONS
from src.metrics import extract_transcript_metrics
from src.evaluator import run_evaluation
from src.vtt_parser import parse_vtt
from src.video_analyzer import extract_key_frames, analyze_video_frames_with_gemini
from src.audio_transcriber import extract_and_transcribe_video

# Auto-load API keys from .env if present
load_dotenv(override=True)
default_gemini_key = os.getenv("GEMINI_API_KEY", "")
default_grok_key = os.getenv("GROK_API_KEY", "")

# Page Configuration
st.set_page_config(
    page_title="8x8 Class Quality Evaluator | Humaniti AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8, #818CF8, #C084FC);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 8px 0;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.05rem;
        margin-bottom: 0;
    }
    
    .badge-excellent {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(5, 150, 105, 0.4));
        color: #34D399;
        border: 1px solid #10B981;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.8rem;
        display: inline-block;
        text-align: center;
        letter-spacing: 1px;
    }
    
    .badge-good {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.2), rgba(37, 99, 235, 0.4));
        color: #60A5FA;
        border: 1px solid #3B82F6;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.8rem;
        display: inline-block;
        text-align: center;
        letter-spacing: 1px;
    }
    
    .badge-average {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.4));
        color: #FBBF24;
        border: 1px solid #F59E0B;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.8rem;
        display: inline-block;
        text-align: center;
        letter-spacing: 1px;
    }
    
    .badge-poor {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.4));
        color: #F87171;
        border: 1px solid #EF4444;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.8rem;
        display: inline-block;
        text-align: center;
        letter-spacing: 1px;
    }
    
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    
    .metric-lbl {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }

    .observation-box {
        background: rgba(15, 23, 42, 0.6);
        border-left: 4px solid #38BDF8;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Evaluator Settings")
    
    engine_choice = st.selectbox(
        "AI Evaluation Engine",
        [
            "🌟 Dual-AI Hybrid (Grok + Gemini)",
            "⚡ Grok Engine",
            "♊ Google Gemini",
            "🛡️ Deterministic Engine (100% Free / Offline)"
        ],
        index=0,
        help="Select the AI reasoning backend. Dual-AI Hybrid seamlessly leverages Gemini Vision for video frames and Grok for rapid speech & pedagogical dialogue reasoning with automatic failover."
    )
    
    with st.expander("⚙️ Optional Key Overrides", expanded=False):
        custom_grok = st.text_input("Grok API Key", value="", type="password", placeholder="gsk_...")
        custom_gemini = st.text_input("Gemini API Key", value="", type="password", placeholder="AIza...")

    # Resolve effective keys: overrides take priority over .env defaults
    effective_grok_key = custom_grok.strip() if custom_grok and custom_grok.strip() else default_grok_key
    effective_gemini_key = custom_gemini.strip() if custom_gemini and custom_gemini.strip() else default_gemini_key

    if effective_grok_key:
        os.environ["GROK_API_KEY"] = effective_grok_key
    if effective_gemini_key:
        os.environ["GEMINI_API_KEY"] = effective_gemini_key

    st.markdown("##### 🔑 Connected AI Engines")
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        if effective_grok_key:
            st.success("Grok: Active")
        else:
            st.warning("Grok: Missing")
    with col_k2:
        if effective_gemini_key:
            st.success("Gemini: Active")
        else:
            st.warning("Gemini: Missing")

    api_key = effective_grok_key if "Grok" in engine_choice else effective_gemini_key

    st.markdown("---")
    st.markdown("### 📋 8x8 Evaluation Rubric")
    with st.expander("View 5 Core Dimensions", expanded=False):
        for key, dim in EVALUATION_DIMENSIONS.items():
            st.markdown(f"**{dim['name']}** (Weight: {int(dim['weight']*100)}%)")
            st.caption(dim["description"])
            
    st.markdown("---")
    st.caption("Humaniti AI • Recruitment Challenge 2026")
    st.caption("Candidate Assessment Submission Prototype")

# Main Header
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🎯 8x8 Class Quality Evaluator</h1>
    <p class="hero-subtitle">Multimodal AI system trained to evaluate online live classes for children against pedagogical rapport, inclusivity, vocal delivery, visual setup, and lesson structure.</p>
</div>
""", unsafe_allow_html=True)

selected_transcript = ""
visual_setup_data = {
    "camera_status": "Continuously ON",
    "background_status": "Official 8x8 Virtual Background",
    "lighting_status": "Clear Front Lighting"
}
ground_truth_note = None

# ==============================================================================
# MULTIMODAL VIDEO ASSESSMENT (DIRECT GENERAL-PURPOSE WORKFLOW)
# ==============================================================================
st.markdown("#### 🎥 Multimodal Video Assessment (General-Purpose)")
st.caption("Upload any recorded online class (.mp4) or transcript (.vtt/.txt).")

uploaded_file = st.file_uploader(
    "Upload Class Video (.mp4) or Subtitle / Transcript (.vtt, .txt):",
    type=["mp4", "mov", "avi", "mkv", "vtt", "txt"],
    help="Upload any MP4 video for automated frame-by-frame computer vision and speech analysis"
)

if uploaded_file is not None:
    file_size_mb = round(uploaded_file.size / (1024*1024), 2)
    file_sig = f"{uploaded_file.name}_{uploaded_file.size}"
    
    # Invalidate old cached runs when a new file is uploaded
    if st.session_state.get("current_file_sig") != file_sig:
        st.session_state["current_file_sig"] = file_sig
        
        # Clean up previous temporary video from disk if it exists
        old_vid = st.session_state.get("active_video_path")
        if old_vid and os.path.exists(old_vid) and "data" in old_vid:
            try:
                os.remove(old_vid)
            except OSError:
                pass

        # Clear ALL file-specific session state so new files start fresh
        for k in [
            "cached_frames", "cached_vision", "cached_audio_transcript", 
            "cached_video_path", "active_video_path", "custom_uploaded_transcript", 
            "last_eval", "last_metrics", "ground_truth"
        ]:
            if k in st.session_state:
                del st.session_state[k]
                
    st.session_state["uploaded_file_name"] = uploaded_file.name
    st.success(f"Loaded File: **{uploaded_file.name}** ({file_size_mb} MB)")
    
    if uploaded_file.name.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        import uuid
        temp_vid_path = os.path.join(os.path.dirname(__file__), "data", f"upload_{uuid.uuid4().hex[:8]}.mp4")
        os.makedirs(os.path.dirname(temp_vid_path), exist_ok=True)
        with open(temp_vid_path, "wb") as f:
            f.write(uploaded_file.read())
        st.session_state["active_video_path"] = temp_vid_path
        if "custom_uploaded_transcript" in st.session_state:
            del st.session_state["custom_uploaded_transcript"]
                
    elif uploaded_file.name.lower().endswith(".vtt"):
        raw_vtt = uploaded_file.read().decode("utf-8", errors="ignore")
        st.session_state["custom_uploaded_transcript"] = parse_vtt(raw_vtt)
        if "active_video_path" in st.session_state:
            del st.session_state["active_video_path"]
        
    elif uploaded_file.name.lower().endswith(".txt"):
        st.session_state["custom_uploaded_transcript"] = uploaded_file.read().decode("utf-8", errors="ignore")
        if "active_video_path" in st.session_state:
            del st.session_state["active_video_path"]

active_video = st.session_state.get("active_video_path")

# Step 1: Computer Vision Frame Analysis across 6 Temporal Milestones
if active_video and os.path.exists(active_video):
    col_cv_hdr, col_cv_reset = st.columns([3, 1])
    with col_cv_hdr:
        st.markdown("##### 🤖 Automated Computer Vision Frame Analysis (6 Milestones)")
        st.caption("Inspects 6 keyframes across the session (5% Setup, 20% Intro, 40% Puzzles, 60% Turn-Taking, 80% Revision, 95% Closure) for 8x8 virtual background, camera continuity, and lighting.")
    with col_cv_reset:
        if st.button("🔄 Re-Analyze Video", help="Wipes cached vision and audio to run a fresh multi-modal inspection"):
            for k in ["cached_frames", "cached_vision", "cached_audio_transcript", "last_eval", "last_metrics"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()
    
    if "cached_frames" not in st.session_state or "cached_vision" not in st.session_state:
        with st.spinner("Extracting 6 distributed keyframes across video and analyzing visual compliance with Gemini Vision..."):
            frames = extract_key_frames(active_video, num_frames=6)
            gemini_vision_key = effective_gemini_key or os.getenv("GEMINI_API_KEY", "")
            vision_analysis = analyze_video_frames_with_gemini(frames, gemini_vision_key)
            st.session_state["cached_frames"] = frames
            st.session_state["cached_vision"] = vision_analysis
            st.session_state["cached_video_path"] = active_video
            
    cached_frames = st.session_state.get("cached_frames", [])
    vision_analysis = st.session_state.get("cached_vision", {})
    
    if cached_frames:
        captions = [
            "Frame 1 (5% - Greeting & Setup)",
            "Frame 2 (20% - Concept & Slides)",
            "Frame 3 (40% - Interactive Puzzles)",
            "Frame 4 (60% - Turn-Taking)",
            "Frame 5 (80% - Revision)",
            "Frame 6 (95% - Wrap-up & HW)"
        ]
        
        # Display Row 1
        col_r1_1, col_r1_2, col_r1_3 = st.columns(3)
        r1_cols = [col_r1_1, col_r1_2, col_r1_3]
        for i in range(min(3, len(cached_frames))):
            with r1_cols[i]:
                st.image(cached_frames[i], caption=captions[i] if i < len(captions) else f"Frame {i+1}", use_container_width=True)
                
        # Display Row 2
        if len(cached_frames) > 3:
            col_r2_1, col_r2_2, col_r2_3 = st.columns(3)
            r2_cols = [col_r2_1, col_r2_2, col_r2_3]
            for j in range(3, min(6, len(cached_frames))):
                with r2_cols[j-3]:
                    st.image(cached_frames[j], caption=captions[j] if j < len(captions) else f"Frame {j+1}", use_container_width=True)
        
    if vision_analysis:
        visual_setup_data = {
            "camera_status": vision_analysis.get("camera_status", "Continuously ON"),
            "background_status": vision_analysis.get("background_status", "Official 8x8 Virtual Background"),
            "lighting_status": vision_analysis.get("lighting_status", "Moderate Lighting")
        }
        
        # Display automated vision report card
        st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 12px; padding: 16px; margin-top: 12px; margin-bottom: 12px;">
            <h5 style="color: #38BDF8; margin: 0 0 8px 0;">🎯 Automated Vision Assessment (Zero Human Selection)</h5>
            <p style="margin: 0 0 4px 0;"><strong>8x8 Virtual Background:</strong> {visual_setup_data['background_status']}</p>
            <p style="margin: 0 0 4px 0;"><strong>Webcam Continuity:</strong> {visual_setup_data['camera_status']}</p>
            <p style="margin: 0 0 8px 0;"><strong>Workstation Lighting:</strong> {visual_setup_data['lighting_status']}</p>
            <p style="margin: 0; color: #94A3B8; font-size: 0.9rem;"><strong>Observations:</strong> {', '.join(vision_analysis.get('visual_observations', []))}</p>
        </div>
        """, unsafe_allow_html=True)

# Step 2: Classroom Dialogue & Audio Track
st.markdown("##### 💬 Classroom Dialogue & Spoken Audio Track")

st.markdown("""
<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 12px; font-size: 0.9rem; color: #CBD5E1;">
    <strong>📌 Why is a transcript required?</strong>
    The 8x8 rubric evaluates 4 spoken pedagogical dimensions: <em>Rapport & Warmth (20%)</em>, <em>Individual Inclusivity (25%)</em>, <em>Vocal Energy & Praise (20%)</em>, and <em>Homework Assignment (20%)</em>. 
    Without spoken dialogue, the AI cannot verify if the teacher greeted each child by name or assigned homework.
</div>
""", unsafe_allow_html=True)

# Priority for dialogue:
# 1. Custom uploaded VTT / TXT
# 2. Whisper transcribed audio directly from the video file
# 3. User pasted text

auto_transcribe_opt = st.checkbox(
    "⚡ Automatically transcribe spoken audio when video is uploaded (Powered by Grok Whisper)",
    value=True,
    help="Extracts audio track via ffmpeg and uses Grok Whisper large-v3-turbo to generate timestamped classroom dialogue in ~1 second."
)

if active_video and os.path.exists(active_video):
    # Auto-transcribe if option is enabled and transcript not yet cached
    if auto_transcribe_opt and not st.session_state.get("cached_audio_transcript") and not st.session_state.get("custom_uploaded_transcript"):
        with st.spinner("🎙️ Extracting audio and auto-transcribing spoken dialogue with Grok Whisper AI..."):
            try:
                transcribed = extract_and_transcribe_video(active_video)
                st.session_state["cached_audio_transcript"] = transcribed
                st.success("✅ Spoken classroom dialogue transcribed successfully using Grok Whisper!")
            except Exception as e:
                st.warning(f"Audio auto-transcription notice: {e}. You can paste dialogue below or retry.")

    # Manual transcribe / re-transcribe button
    col_tr1, col_tr2 = st.columns([2, 3])
    with col_tr1:
        btn_label = "🔄 Re-Transcribe Audio (Grok Whisper)" if st.session_state.get("cached_audio_transcript") else "🎙️ Generate Transcript from Video Audio (Grok Whisper)"
        if st.button(btn_label, help="Extracts audio track via ffmpeg and transcribes spoken classroom dialogue using Grok Whisper"):
            with st.spinner("Extracting audio with ffmpeg and transcribing dialogue using Grok Whisper..."):
                try:
                    transcribed = extract_and_transcribe_video(active_video)
                    st.session_state["cached_audio_transcript"] = transcribed
                    st.success("Classroom dialogue transcribed successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Audio transcription error: {e}")
    with col_tr2:
        st.caption("Extracts speech from the uploaded video into timestamped dialogue `[HH:MM:SS] Speaker: text`.")

if st.session_state.get("custom_uploaded_transcript"):
    selected_transcript = st.session_state["custom_uploaded_transcript"]
    st.info(f"✨ Using dialogue from uploaded subtitle file ({len(selected_transcript.splitlines())} dialogue lines).")
elif st.session_state.get("cached_audio_transcript"):
    selected_transcript = st.session_state["cached_audio_transcript"]
    st.info(f"🎙️ Using speech transcribed directly from video audio via Grok Whisper ({len(selected_transcript.splitlines())} dialogue lines).")
elif not active_video:
    st.caption("💡 *Upload an MP4 video above to auto-generate dialogue, or paste a transcript directly below.*")

custom_dialogue = st.text_area(
    "Active Classroom Dialogue / Transcript to Evaluate:",
    value=selected_transcript,
    height=180,
    placeholder="Upload a video (.mp4) to auto-transcribe with Grok Whisper, or paste classroom dialogue here:\n[00:00:05] Teacher: Hello everyone! Welcome to class!..."
)
if custom_dialogue.strip() != selected_transcript:
    selected_transcript = custom_dialogue.strip()



st.markdown("---")

# Execution Button
col_btn, col_msg = st.columns([1, 3])
with col_btn:
    analyze_btn = st.button("🚀 Run AI Assessment", type="primary", use_container_width=True)

if analyze_btn:
    if not selected_transcript.strip():
        st.error("⚠️ Please upload a class video or provide classroom dialogue before running the evaluation.")
    else:
        with st.spinner("Analyzing classroom dynamics, pedagogical interactions, and visual compliance..."):
            evaluation = run_evaluation(
                transcript=selected_transcript,
                visual_info=visual_setup_data,
                api_choice=engine_choice,
                api_key=api_key
            )
            # Compute quantitative metrics for dashboard
            metrics = extract_transcript_metrics(selected_transcript)
            st.session_state["last_eval"] = evaluation
            st.session_state["last_metrics"] = metrics
            st.session_state["ground_truth"] = ground_truth_note

if "last_eval" in st.session_state:
    
    eval_res = st.session_state["last_eval"]
    met_res = st.session_state["last_metrics"]
    gt_note = st.session_state.get("ground_truth")

    if "warning" in eval_res:
        st.warning(eval_res["warning"])

    st.markdown("## 📊 Assessment Report")
    
    # 1. Executive Top Bar
    quality = eval_res.get("overall_quality", "Average")
    score = eval_res.get("overall_score", 70)
    badge_class = f"badge-{quality.lower()}"
    
    col_score1, col_score2, col_score3 = st.columns([1.5, 2.5, 1.5])
    with col_score1:
        st.markdown(f'<div class="{badge_class}">{quality.upper()}</div>', unsafe_allow_html=True)
        st.caption(f"Engine: {eval_res.get('model_used', '8x8 Engine')}")
    with col_score2:
        st.markdown("#### Executive Pedagogical Verdict")
        st.write(eval_res.get("evaluator_verdict_summary", ""))
        if gt_note:
            st.markdown(f"**8x8 Benchmark Note:** *{gt_note}*")
    with col_score3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{score}/100</div>
            <div class="metric-lbl">Overall Quality Score</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # 2. Hard Quantitative Metrics
    st.markdown("### 📈 Measured Interaction Signals")
    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    with mcol1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{met_res['questions_count']}</div>
            <div class="metric-lbl">Questions Asked</div>
        </div>
        """, unsafe_allow_html=True)
    with mcol2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{len(met_res['detected_students'])}</div>
            <div class="metric-lbl">Students Called by Name</div>
        </div>
        """, unsafe_allow_html=True)
    with mcol3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{met_res['positive_affirmations_count']}</div>
            <div class="metric-lbl">Positive Affirmations</div>
        </div>
        """, unsafe_allow_html=True)
    with mcol4:
        hw_status = "✅ Given" if met_res['has_homework'] else "❌ Missing"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{hw_status}</div>
            <div class="metric-lbl">Homework (HWs)</div>
        </div>
        """, unsafe_allow_html=True)
    with mcol5:
        cam_ok = "✅ Compliant" if "continuously" in visual_setup_data["camera_status"].lower() else "⚠️ Issue"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-val">{cam_ok}</div>
            <div class="metric-lbl">Camera & Setup</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 3. Radar Chart & Dimension Breakdown
    dim_scores = eval_res.get("dimension_scores", {})
    col_chart, col_dim_details = st.columns([1.2, 1.8])
    
    with col_chart:
        st.markdown("#### 🎯 8x8 Rubric Radar")
        categories = [dim["name"] for dim in EVALUATION_DIMENSIONS.values()]
        values = [dim_scores.get(key, 70) for key in EVALUATION_DIMENSIONS.keys()]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(56, 189, 248, 0.25)',
            line=dict(color='#38BDF8', width=2),
            name='Session Score'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#94A3B8"),
                angularaxis=dict(color="#F8FAFC")
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(l=40, r=40, t=20, b=20),
            height=320
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_dim_details:
        st.markdown("#### 📑 Dimension Score Breakdown")
        for key, dim in EVALUATION_DIMENSIONS.items():
            sc = dim_scores.get(key, 70)
            st.write(f"**{dim['name']}**: **{sc}/100**")
            st.progress(sc / 100.0)

    st.markdown("---")

    # 4. Strengths & Growth Areas
    col_str, col_gro = st.columns(2)
    with col_str:
        st.markdown("### 🌟 Key Pedagogical Strengths")
        for item in eval_res.get("key_strengths", []):
            st.markdown(f"✅ {item}")
            
    with col_gro:
        st.markdown("### 💡 Specific Growth Recommendations")
        for item in eval_res.get("growth_areas", []):
            st.markdown(f"📌 {item}")

    # 5. Phased / Timestamped Observations
    st.markdown("---")
    st.markdown("### ⏱️ Phased Classroom Observations")
    obs_list = eval_res.get("timestamped_observations", [])
    if obs_list:
        for obs in obs_list:
            t = obs.get("timestamp", "--:--")
            phase = obs.get("phase", "General")
            note = obs.get("observation", "")
            icon = "🟢" if obs.get("type") == "positive" else ("🔴" if obs.get("type") == "critical" else "🟡")
            st.markdown(f"""
            <div class="observation-box">
                <strong>{icon} [{t}] {phase}:</strong> {note}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.caption("No timestamped anomalies noted.")

    # 6. Export Options
    st.markdown("---")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.download_button(
            "📥 Download JSON Evaluation Report",
            data=json.dumps(eval_res, indent=2),
            file_name=f"8x8_class_evaluation_{quality.lower()}.json",
            mime="application/json",
            use_container_width=True
        )
    with col_exp2:
        markdown_summary = f"""# 8x8 Class Evaluation Report
**Overall Quality:** {quality} ({score}/100)
**Engine Used:** {eval_res.get('model_used')}

## Executive Verdict
{eval_res.get('evaluator_verdict_summary')}

## Dimension Breakdown
- Rapport Building & Greeting: {dim_scores.get('rapport_building')}/100
- Individual Consideration & Inclusivity: {dim_scores.get('individual_inclusivity')}/100
- Energy & Tone: {dim_scores.get('energy_and_pleasantness')}/100
- Visual Setup & Hygiene: {dim_scores.get('visual_setup_hygiene')}/100
- Lesson Structure & Homework: {dim_scores.get('structure_and_homework')}/100

## Key Strengths
{chr(10).join(['- ' + s for s in eval_res.get('key_strengths', [])])}

## Growth Areas
{chr(10).join(['- ' + g for g in eval_res.get('growth_areas', [])])}
"""
        st.download_button(
            "📄 Download Markdown Assessment Summary",
            data=markdown_summary,
            file_name=f"8x8_assessment_{quality.lower()}.md",
            mime="text/markdown",
            use_container_width=True
        )
