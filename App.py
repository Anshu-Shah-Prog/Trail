import streamlit as st
from datetime import datetime
import pandas as pd

from utils import t, t_question, append_to_google_sheet, TRANSLATIONS, map_to_english
from UI import render_mcq_card
from test_compute_scores import compute_scores
import uuid

# --- Generate a unique survey ID at the start of the session ---
if "survey_id" not in st.session_state:
    st.session_state.survey_id = str(uuid.uuid4())
    st.session_state.data_saved = False  # Guard to prevent multiple saves

survey_id = st.session_state.survey_id

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Chronotype & Brain Efficiency",
    layout="wide"
)

# --------------------------------------------------
# Initialize Session State
# --------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = 1

if "responses" not in st.session_state:
    st.session_state.responses = {}

if "lang_choice" not in st.session_state:
    st.session_state.lang_choice = "en"

if "locked_lang" not in st.session_state:
    st.session_state.locked_lang = None


def next_page():
    st.session_state.page += 1


def prev_page():
    st.session_state.page -= 1

def scroll_to_top():
    st.markdown(
        """
        <script>
        const mainContent = window.parent.document.querySelector('main');
        if (mainContent) {
            mainContent.scrollTo({ top: 0, behavior: 'smooth' });
        }
        </script>
        """,
        unsafe_allow_html=True
    )

TOTAL_PAGES = 6  # excluding intro

def show_progress():
    if st.session_state.page > 1:
        progress = (st.session_state.page - 1) / TOTAL_PAGES
        st.progress(min(progress, 1.0))

# --------------------------------------------------
# Intro Page
# --------------------------------------------------
def show_intro():
    lang = st.session_state.lang_choice

    st.title(t(lang, "title", "Survey"))
    st.write(t(lang, "desc", ""))

    lang_options = ["en", "hi", "mr"]
    lang_labels = {
        "en": "English",
        "hi": "हिन्दी",
        "mr": "मराठी"
    }

    st.selectbox(
        "Select Language",
        options=lang_options,
        format_func=lambda x: lang_labels[x],
        key="lang_choice"
    )

    if st.button(t(lang, "start", "Start")):
        st.session_state.locked_lang = st.session_state.lang_choice
        st.session_state.responses = {}
        next_page()
        scroll_to_top()
        st.rerun()


# --------------------------------------------------
# Generic Section Renderer (A, B, D, E, F)
# --------------------------------------------------
def render_section(section_id, q_list, next_p):
    lang = st.session_state.locked_lang
    
    st.header(t(lang, "title"))

    show_progress()
    
    st.subheader(t(lang, f"sections.{section_id}", f"Section {section_id}"))

    for q in q_list:
        data = t_question(lang, q)
        q_text = data.get("q", f"Question {q}")
        opts = data.get("opts", [])

        choice = render_mcq_card(q_text, opts, key=f"ans_{q}", card_color="#e8f4f8")
        st.session_state.responses[q] = choice

        if q == "B14" and choice in ["Yes", "हाँ", "होय"]:
            st.session_state.responses["B14_details"] = st.text_input(
                "Please specify / कृपया स्पष्ट करें / कृपया स्पष्ट करा:",
                key="input_B14_details"
            )

    unanswered = [
        q for q in q_list
        if st.session_state.responses.get(q) is None
    ]

    col1, col2 = st.columns(2)

    with col1:
        if st.button(t(lang, "back", "Back")):
            prev_page()
            scroll_to_top()
            st.rerun()

    with col2:
        if st.button(
            t(lang, "next", "Next"),
            disabled=bool(unanswered)
        ):
            st.session_state.page = next_p
            scroll_to_top()
            st.rerun()
    if unanswered:
        st.info("Please answer all questions to continue.")

# --------------------------------------------------
# Section C (Custom layout)
# --------------------------------------------------
def render_section_c():
    lang = st.session_state.locked_lang
    st.title(t(lang, "title"))

    show_progress()
    
    st.header(t(lang, "sections.C"))

    qs = ["C1","C2","C3","C4","C5","C6","C7","C8","C9","C10","C11","C12"]

    st.subheader(t(lang, "sections.C_sub_who"))
    for q in qs[:5]:
        data = t_question(lang, q)
        st.session_state.responses[q] = render_mcq_card(q_text, opts, key=f"ans_{q}", card_color="#e8f4f8")

    st.divider()

    st.subheader(t(lang, "sections.C_sub_dass"))
    for q in qs[5:]:
        data = t_question(lang, q)
        st.session_state.responses[q] = render_mcq_card(q_text, opts, key=f"ans_{q}", card_color="#e8f4f8")

    unanswered = [
        q for q in qs
        if st.session_state.responses.get(q) is None
    ]

    col1, col2 = st.columns(2)

    with col1:
        if st.button(t(lang, "back", "Back")):
            prev_page()
            scroll_to_top()
            st.rerun()

    with col2:
        if st.button(
            t(lang, "next", "Next"),
            disabled=bool(unanswered)
        ):
            st.session_state.page = 5
            scroll_to_top()
            st.rerun()
    if unanswered:
        st.info("Please answer all questions to continue.")

# --------------------------------------------------
# Final Page
# --------------------------------------------------
def show_final():
    lang = st.session_state.locked_lang
    scores = compute_scores(st.session_state.responses, lang)
    st.title(t(lang, "title"))

    st.success(t(lang, "final_thanks", "Thank you for completing the assessment!"))
    st.subheader(t(lang, "final_scores", "Your Scores"))

    # Display metrics using translations
    metrics = TRANSLATIONS.get("final_metrics", {}).get(lang, {})
    col1, col2 = st.columns(2)

    with col1:
        st.metric(metrics.get("sleep_quality", "🌙 Sleep Quality (3–15)"), scores.get("sleep_quality", 0))
        st.metric(metrics.get("WHO_total", "🙂 WHO-5 Well-being (0–100)"), scores.get("WHO_total", 0))
        st.metric(metrics.get("distress_total", "⚠️ Mental Distress (6–30)"), scores.get("distress_total", 0))

    with col2:
        st.metric(metrics.get("cognitive_efficiency", "🧠 Cognitive Efficiency (8–40)"), scores.get("cognitive_efficiency", 0))
        st.metric(metrics.get("lifestyle_risk", "🔥 Lifestyle Risk (higher = worse)"), scores.get("lifestyle_risk", 0))

    st.balloons()

    # Convert all responses to English before saving
    english_responses = {}
    for q, ans in st.session_state.responses.items():
        english_responses[q] = map_to_english(q, ans, st.session_state.locked_lang)

    # Save data only once per session
    if not st.session_state.get("data_saved", False):
        save_data = {
            "survey_id": st.session_state.survey_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "lang": "en",
            **english_responses,
            **scores
        }

        # # Debug log to check data
        # st.write("Saving data to Google Sheets:", save_data)

        if append_to_google_sheet(save_data):
            st.success(t(lang, "final_saved"))
            st.write(t(lang, "done_message"))
            st.session_state.data_saved = True  # prevent duplicate saves
        else:
            st.error("Failed to save data to Google Sheets. Please contact admin.")
            
# --------------------------------------------------
# Navigation Controller
# --------------------------------------------------
if st.session_state.page == 1:
    show_intro()

elif st.session_state.page == 2:
    render_section("A", ["A1", "A2", "A3", "A4", "A5", "A6", "A7"], 3)

elif st.session_state.page == 3:
    render_section("B", [f"B{i}" for i in range(1, 15)], 4)

elif st.session_state.page == 4:
    render_section_c()

elif st.session_state.page == 5:
    render_section("D", [f"D{i}" for i in range(1, 10)], 6)

elif st.session_state.page == 6:
    render_section("E", ["E1", "E2", "E3", "E4"], 7)

elif st.session_state.page == 7:
    render_section("F", ["F1", "F2", "F3", "F4", "F5", "F6"], 8)

elif st.session_state.page == 8:
    show_final()
