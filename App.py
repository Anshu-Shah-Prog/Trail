import streamlit as st
from datetime import datetime
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

def show_intro():
    lang = st.session_state.lang_choice
    st.title(t(lang, "title", "Survey"))
    st.write(t(lang, "desc", ""))

    lang_options = ["en", "hi", "mr"]
    lang_labels = {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}
    st.selectbox("Select Language", options=lang_options, format_func=lambda x: lang_labels[x], key="lang_choice")

    if st.button(t(lang, "start", "Start")): st.session_state.locked_lang = st.session_state.lang_choice
    st.session_state.responses = {}
    next_page()
    st.rerun()


# --- Unified Section Renderer ---
def render_section(section_id, q_list, next_p):
    lang = st.session_state.locked_lang
    st.header(t(lang, f"sections.{section_id}", f"Section {section_id}"))
    
    for q in q_list:
        data = t_question(lang, q)
        q_text = data.get("q", f"Question {q}")
        opts = data.get("opts", [])
        
        # index=None makes it so NO option is selected by default
        choice = st.radio(q_text, opts, index=None, key=f"ans_{q}")
        st.session_state.responses[q] = choice

        # B14 Special Text Box
        if q == "B14" and choice in ["Yes", "हाँ", "होय"]:
            st.session_state.responses["B14_details"] = st.text_input(
                "Please specify / कृपया स्पष्ट करें / कृपया स्पष्ट करा:", 
                key="input_B14_details"
            )

    # CHECK: Are all questions in this section answered?
    unanswered = [q for q in q_list if st.session_state.responses.get(q) is None]
    
    col1, col2 = st.columns(2)
    with col1: 
        if st.button(t(lang, "back", "Back"), key=f"back_{section_id}"): 
            prev_page()
            st.rerun()
    with col2:
        if not unanswered:
            # Added a unique key here to prevent the DuplicateElementId error
            if st.button(t(lang, "next", "Next"), key=f"next_{section_id}"): 
                st.session_state.page = next_p
                st.rerun()
        else:
            st.warning("Please answer all questions to proceed.")

# --- Custom Renderer for Section C (Because of subheaders) ---
def render_section_c():
    lang = st.session_state.locked_lang
    st.header(t(lang, "sections.C"))
    
    qs = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12"]
    
    st.subheader(t(lang, "sections.C_sub_who"))
    for q in qs[:5]:
        data = t_question(lang, q)
        st.session_state.responses[q] = st.radio(data["q"], data["opts"], index=None, key=f"ans_{q}")

    st.divider()

    st.subheader(t(lang, "sections.C_sub_dass"))
    for q in qs[5:]:
        data = t_question(lang, q)
        st.session_state.responses[q] = st.radio(data["q"], data["opts"], index=None, key=f"ans_{q}")

    unanswered = [q for q in qs if st.session_state.responses.get(q) is None]

    col1, col2 = st.columns(2)
    with col1:
        if st.button(t(lang, "back", "Back"), key="back_c"): prev_page(); st.rerun()
    with col2:
        if not unanswered:
            if st.button(t(lang, "next", "Next"), key="next_c"): st.session_state.page = 5; st.rerun()
        else:
            st.warning("Please answer all questions.")

def show_final():
    lang = st.session_state.locked_lang
    scores = compute_scores(st.session_state.responses, lang)
    
    st.header(t(lang, "final_title"))
    
    # Safely get labels
    labels = t(lang, "final_metrics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric(labels["sleep_quality"], scores["sleep_quality"])
        st.metric(labels["WHO_total"], f"{scores['WHO_total']}%")
        st.metric(labels["distress_total"], scores["distress_total"])
    with col2:
        st.metric(labels["cognitive_efficiency"], scores["cognitive_efficiency"])
        st.metric(labels["lifestyle_risk"], scores["lifestyle_risk"])
    
    st.balloons()
    save_data = {"timestamp": datetime.now().isoformat(), "lang": lang, **st.session_state.responses, **scores}
    if append_to_google_sheet(save_data):
        st.success(t(lang, "saved"))

# --- Navigation Logic ---
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
    render_section("E", ["E1","E2","E3","E4"], 7)
elif st.session_state.page == 7:
    render_section("F", ["F1","F2","F3","F4","F5","F6"], 8)
elif st.session_state.page == 8:
    show_final()
