import streamlit as st
from datetime import datetime
import pandas as pd
from utils import t, append_to_google_sheet
from test_compute_scores import compute_scores # Import your existing scoring logic

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
        q_text = t(lang, f"Q.{q}.q", f"Question {q}")
        opts = t(lang, f"Q.{q}.opts", [])
        st.radio(q_text, opts, key=f"ans_{q}")
        st.session_state.responses[q] = st.session_state.get(f"ans_{q}")

    col1, col2 = st.columns(2)
    with col1: 
        if st.button("Back"): prev_page(); st.rerun()
    with col2:
        if st.button("Next"): st.session_state.page = next_p; st.rerun()

def show_final():
    lang = st.session_state.locked_lang
    scores = compute_scores(st.session_state.responses, lang)
    
    st.balloons()
    st.header("Results")
    st.json(scores) # Display metrics here
    
    # Save Data
    save_data = {"timestamp": datetime.now().isoformat(), "lang": lang, **st.session_state.responses, **scores}
    if append_to_google_sheet(save_data):
        st.success("Data Saved!")

# --- Navigation Logic ---
if st.session_state.page == 1:
    show_intro()
elif st.session_state.page == 2:
    render_section("A", ["A1", "A2", "A3", "A4", "A5", "A6", "A7"], 3)
elif st.session_state.page == 3:
    render_section("B", ["B1", "B2", "B3"], 8) # Example jump to final
elif st.session_state.page == 8:
    show_final()
