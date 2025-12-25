import streamlit as st
from datetime import datetime
import pandas as pd
from utils import t, t_question, append_to_google_sheet
from test_compute_scores import compute_scores 

st.set_page_config(page_title="Chronotype & Brain Efficiency", layout="wide")

# --- Initialize State ---
if "page" not in st.session_state: st.session_state.page = 1
if "responses" not in st.session_state: st.session_state.responses = {}
if "lang_choice" not in st.session_state: st.session_state.lang_choice = "en"
if "locked_lang" not in st.session_state: st.session_state.locked_lang = None

def next_page(): st.session_state.page += 1
def prev_page(): st.session_state.page -= 1

# --- Page Renderers ---
def show_intro():
    lang = st.session_state.lang_choice
    st.title(t(lang, "title", "Survey"))
    st.write(t(lang, "desc", ""))
    
    lang_options = ["en", "hi", "mr"]
    lang_labels = {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}
    
    st.selectbox("Select Language", options=lang_options, 
                 format_func=lambda x: lang_labels[x], key="lang_choice")
    
    if st.button(t(lang, "start", "Start")):
        st.session_state.locked_lang = st.session_state.lang_choice
        st.session_state.responses = {}
        next_page()
        st.rerun()

def render_section(section_id, q_list, next_p):
    lang = st.session_state.locked_lang
    st.header(t(lang, f"sections.{section_id}", f"Section {section_id}"))
    
    for q in q_list:
        data = t_question(lang, q)
        # index=None ensures NO radio button is selected by default
        choice = st.radio(data.get("q"), data.get("opts", []), index=None, key=f"ans_{q}")
        st.session_state.responses[q] = choice

        if q == "B14" and choice in ["Yes", "हाँ", "होय"]:
            st.session_state.responses["B14_details"] = st.text_input("Specify:", key="input_B14_details")

    # Check if all questions in this section have been answered
    answered_all = all(st.session_state.responses.get(q) is not None for q in q_list)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t(lang, "back", "Back")): prev_page(); st.rerun()
    with col2:
        if answered_all:
            if st.button(t(lang, "next", "Next")): st.session_state.page = next_p; st.rerun()
        else:
            st.warning("Please answer all questions to continue / कृपया आगे बढ़ने के लिए सभी प्रश्नों के उत्तर दें")

def render_section_c():
    lang = st.session_state.locked_lang
    st.header(t(lang, "sections.C"))
    
    # --- Sub-section 1: WHO-5 ---
    st.subheader(t(lang, "sections.C_sub_who"))
    for q in ["C1", "C2", "C3", "C4", "C5"]:
        data = t_question(lang, q)
        choice = st.radio(data["q"], data["opts"], key=f"ans_{q}")
        st.session_state.responses[q] = choice

    st.divider()

    # --- Sub-section 2: DASS ---
    st.subheader(t(lang, "sections.C_sub_dass"))
    for q in ["C6", "C7", "C8", "C9", "C10", "C11", "C12"]:
        data = t_question(lang, q)
        choice = st.radio(data["q"], data["opts"], key=f"ans_{q}")
        st.session_state.responses[q] = choice

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t(lang, "back", "Back")): prev_page(); st.rerun()
    with col2:
        if st.button(t(lang, "next", "Next")): st.session_state.page = 5; st.rerun()

def show_final():
    lang = st.session_state.locked_lang
    scores = compute_scores(st.session_state.responses, lang)

    st.header(t(lang, "final_title"))
    
    # Access the metrics labels correctly
    # This pulls "final_metrics" -> "en" (or "hi"/"mr")
    labels = t(lang, f"final_metrics") 
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🌙 Sleep Quality (3–15)", scores["sleep_quality"])
        st.metric("🙂 WHO-5 Well-being (0–100)", scores["WHO_total"])
        st.metric("⚠️ Mental Distress (6–30)", scores["distress_total"])

    with col2:
        st.metric("🧠 Cognitive Efficiency (8–40)", scores["cognitive_efficiency"])
        st.metric("🔥 Lifestyle Risk (higher = worse)", scores["lifestyle_risk"])
    
    st.balloons()
    
    save_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
        "lang": lang, 
        **st.session_state.responses, 
        **scores
    }
    
    if append_to_google_sheet(save_data):
        st.success(t(lang, "saved"))

# --- Navigation Logic ---
if st.session_state.page == 1:
    show_intro()
elif st.session_state.page == 2:
    render_section("A", ["A1", "A2", "A3", "A4", "A5", "A6", "A7"], 3)
elif st.session_state.page == 3:
    lang = st.session_state.locked_lang
    st.header(t(lang, "sections.B"))
    q_list = [f"B{i}" for i in range(1, 15)]

    for q in q_list:
        data = t_question(lang, q)
        choice = st.radio(data.get("q"), data.get("opts"), index=None, key=f"ans_{q}")
        st.session_state.responses[q] = choice
        
        if q == "B14" and choice in ["Yes", "हाँ", "होय"]:
            st.session_state.responses["B14_details"] = st.text_input("Specify:", key="b14_reg")

    # Validation
    if all(st.session_state.responses.get(q) is not None for q in q_list):
        if st.button(t(lang, "next", "Next")): st.session_state.page = 4; st.rerun()
    else:
        st.info("Answer all questions to proceed.")

    # Navigation buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button(t(lang, "back", "Back")): prev_page(); st.rerun()
    with col2:
        if st.button(t(lang, "next", "Next")): st.session_state.page = 4; st.rerun()

elif st.session_state.page == 4:
    render_section_c()
elif st.session_state.page == 5:
    render_section("D", [f"D{i}" for i in range(1, 10)], 6)
elif st.session_state.page == 6:
    render_section("E", ["E1","E2","E3","E4"], 7)
elif st.session_state.page == 7:
    render_section("F", ["F1","F2","F3","F4","F5","F6"], 8)
elif st.session_state.page == 8:
    show_final()
