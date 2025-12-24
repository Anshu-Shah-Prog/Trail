# Part 2 — main skeleton + Page 1 (language selection + topic)
import streamlit as st
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

st.set_page_config(page_title="Chronotype & Brain Efficiency", layout="wide")

st.markdown("""
<style>
/* HERO */
.hero {
    background: linear-gradient(135deg, #f5f7fa, #e4ecf7);
    padding: 28px;
    border-radius: 16px;
    margin-bottom: 20px;
}
.hero h1 {
    font-size: 1.8rem;
}
.hero p {
    font-size: 1rem;
    color: #444;
}
.badge {
    display: inline-block;
    background: #e8f5e9;
    color: #2e7d32;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    margin-right: 8px;
}

/* QUESTION CARD */
.q-card {
    background: #ffffff;
    padding: 18px;
    border-radius: 14px;
    margin-bottom: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.q-title {
    font-weight: 600;
    margin-bottom: 10px;
}

/* BUTTONS (mobile friendly) */
div.stButton > button {
    width: 100%;
    padding: 10px;
    border-radius: 10px;
}

/* NEXT BUTTON */
.next-btn button {
    background-color: #1976D2;
    color: white;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# -- Load translations.json (must be in same directory) --
TRANS_PATH = "translations.json"
if not os.path.exists(TRANS_PATH):
    st.error(f"translations.json not found in working directory. Please add the file and reload.")
    st.stop()

with open(TRANS_PATH, "r", encoding="utf-8") as f:
    TRANSLATIONS = json.load(f)

# Helper to get translation dictionary for current language
def t(lang_code, key, default=None):
    """Return translation for `key` under language `lang_code`."""
    # First try: nested lookup under TRANSLATIONS[lang_code]
    lang_block = TRANSLATIONS.get(lang_code, {})
    cur = lang_block
    if key:
        parts = key.split(".")
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                cur = None
                break
        if cur is not None:
            return cur

    # Second try: some keys are stored at top-level mapping to per-language dicts
    top_val = TRANSLATIONS.get(key)
    if isinstance(top_val, dict) and lang_code in top_val:
        return top_val[lang_code]

    # Fallback to English under same lookup rules
    en_block = TRANSLATIONS.get("en", {})
    cur = en_block
    if key:
        parts = key.split(".")
        for p in parts:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                cur = None
                break
        if cur is not None:
            return cur

    # Last resort: english top-level per-lang mapping
    top_val = TRANSLATIONS.get(key)
    if isinstance(top_val, dict) and "en" in top_val:
        return top_val["en"]

    return default

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = 1  # 1 = intro, then 2..8 pages for sections A..Final
if "lang_choice" not in st.session_state:
    st.session_state.lang_choice = "en"
if "locked_lang" not in st.session_state:
    st.session_state.locked_lang = None  # locked language after user presses Start
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "started_at" not in st.session_state:
    st.session_state.started_at = None

# function to reset responses (used when language changed after start)
def reset_responses():
    st.session_state.responses = {}
    st.session_state.started_at = None

# PAGE 1 — Intro + Language selection + Start
def page_intro():
    lang = st.session_state.lang_choice
    # show title and description using current (unlocked) language selection if present
    title = t(lang, "title", TRANSLATIONS["en"]["title"])
    desc = t(lang, "desc", TRANSLATIONS["en"]["desc"])
    topic_dist = t(lang, "topic_distribution", TRANSLATIONS["en"]["topic_distribution"])
    lang_select_label = t(lang, "lang_select", TRANSLATIONS["en"]["lang_select"])
    start_btn_label = t(lang, "start", TRANSLATIONS["en"].get("start", "Start Survey"))
    next_label = t(lang, "next", TRANSLATIONS["en"].get("next", "Next →"))

    st.markdown("""
    <div class="hero">
      <h1>🧠 Morning Minds & Night Owls</h1>
      <p>Please answer honestly. Responses are anonymous.</p>
      <div>
        <span class="badge">⏱ 7–10 minutes</span>
        <span class="badge">🔒 Anonymous</span>
        <span class="badge">📊 Research-based</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Language options shown here on Page 1
    col1, col2 = st.columns([2, 1])
    with col1:
        # Human-readable labels shown; internal codes are "en","hi","mr"
        lang_options = ["en", "hi", "mr"]
        lang_labels = {"en": "English", "hi": "हिन्दी", "mr": "मराठी"}

        # Ensure session_state has a sensible current value
        if "lang_choice" not in st.session_state or st.session_state.lang_choice not in lang_options:
            st.session_state.lang_choice = "en"

        # Use selectbox bound to session_state so selection persists across reruns
        chosen_code = st.selectbox(
            lang_select_label,
            options=lang_options,
            format_func=lambda c: lang_labels.get(c, c),
            index=lang_options.index(st.session_state.lang_choice),
            key="lang_choice",
        )

        # If user changes selection after already starting (locked_lang present), warn before clearing
        prev_locked = st.session_state.locked_lang
        if prev_locked and (chosen_code != prev_locked):
            if st.button("Change language (this will clear previous answers)"):
                reset_responses()
                st.session_state.locked_lang = None
                st.session_state.lang_choice = chosen_code
                st.rerun()

    with col2:
        # intentionally left blank (sample plot removed)
        pass

    st.markdown("---")

    # Show Start button (locks language and proceeds)
    start_col1, start_col2, start_col3 = st.columns([1,1,2])
    with start_col2:
        if st.button(start_btn_label):
            # lock selected language
            st.session_state.locked_lang = st.session_state.lang_choice
            st.session_state.started_at = datetime.now().isoformat()
            # ensure responses cleared for fresh run when starting
            reset_responses()
            # advance to Section A (page 2)
            st.session_state.page = 2
            st.rerun()

# Call page rendering depending on page number
if st.session_state.page == 1:
    page_intro()
else:
    # If we are beyond page 1, ensure language is locked (cannot change)
    if not st.session_state.locked_lang:
        # If somehow locked_lang missing, redirect to page 1
        st.warning("Language not locked. Returning to start page.")
        st.session_state.page = 1
        st.rerun()
    else:
        # Render a small header showing locked language and a Home button
        locked = st.session_state.locked_lang
        lang_label = {"en":"English","hi":"हिन्दी","mr":"मराठी"}.get(locked, locked)
        header_col1, header_col2 = st.columns([4,1])
        with header_col1:
            st.markdown(f"#### {t(locked, 'title', TRANSLATIONS['en']['title'])}  —  **Language:** {lang_label}")
        with header_col2:
            if st.button("Return to Start (change language)"):
                # allow user to go back to page 1 and change language — this will reset responses
                reset_responses()
                st.session_state.locked_lang = None
                st.session_state.page = 1
                st.rerun()

        st.markdown("---")
        TOTAL_PAGES = 8
        progress = st.session_state.page / TOTAL_PAGES
        st.progress(progress)
        st.caption(f"Section {st.session_state.page - 1} of {TOTAL_PAGES - 1}")
        
        st.write("Use the Next/Back buttons at the bottom of each page to navigate through the questionnaire.")
        # Next parts (Section rendering) are in Part 3 — they will pick up st.session_state.locked_lang

def mcq_buttons(qkey, question, options):
    if qkey not in st.session_state.responses:
        st.session_state.responses[qkey] = None

    st.markdown(f"""
    <div class="q-card">
      <div class="q-title">{question}</div>
    """, unsafe_allow_html=True)

    cols = st.columns(len(options))
    for i, opt in enumerate(options):
        selected = st.session_state.responses[qkey] == opt
        label = f"✅ {opt}" if selected else opt

        if cols[i].button(label, key=f"{qkey}_{i}"):
            st.session_state.responses[qkey] = opt
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# PART 3 — SECTION A to SECTION F (Multilingual Pages)
# ---------------------------------------------------------

# Utility: Get translated question text + options via keys like "sections.A.Q1"
def tq(key):
    """Return fully translated question text for locked language."""
    lang = st.session_state.locked_lang
    # Map some legacy keys used in the code to the structure in translations.json
    # Section titles were referenced as 'sections.X.title' -> actual key is 'sections.X'
    if key.startswith("sections.") and key.endswith(".title"):
        newkey = key.replace(".title", "")
        return t(lang, newkey, f"[MISSING TRANSLATION for {newkey}]")

    # Sub-headers for WHO/DASS (not present in translations) - provide sensible defaults
    if key == "sections.C.sub_who5":
        return t(lang, "Q.C1.q", "WHO-5 items")
    if key == "sections.C.sub_dass":
        return t(lang, "Q.C6.q", "DASS-short items")

    # If code asked for a question-like key such as 'sections.A.A1', map to Q.A1.q
    parts = key.split('.')
    if len(parts) >= 2 and parts[0] == 'sections' and len(parts[-1]) >= 2:
        # last part is question code e.g. 'A1'
        qcode = parts[-1]
        return t(lang, f"Q.{qcode}.q", f"[MISSING QUESTION {qcode}]")

    # Generic fallback
    return t(lang, key, f"[MISSING TRANSLATION for {key}]")

def topt(key):
    """Return translated options list."""
    lang = st.session_state.locked_lang
    # If key follows pattern 'sections.X.Y_options', map to Q.Y.opts if possible
    if key.startswith("sections."):
        parts = key.split('.')
        last = parts[-1]
        # handle patterns like 'A.A1_options' or 'A.A1_options' - common code used '{q}_options'
        if last.endswith("_options"):
            qcode = last.replace("_options", "")
            opts = t(lang, f"Q.{qcode}.opts", [])
            return opts if isinstance(opts, list) else []

    # Otherwise try direct lookup
    opts = t(lang, key, [])
    return opts if isinstance(opts, list) else []

# Utility for required-check
def unanswered(required_keys):
    """Return True if any required question is missing."""
    for k in required_keys:
        if st.session_state.responses.get(k) in [None, ""]:
            return True
    return False

# Utility – store responses
def answer(qkey, value):
    st.session_state.responses[qkey] = value

st.markdown("""
<style>
.likert-row {
    margin-bottom: 12px;
}
.likert-cell button {
    width: 100%;
    height: 42px;
    border-radius: 6px;
}
.likert-selected {
    background-color: #2E7D32 !important;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


def likert_row(qkey, question, scale=[1,2,3,4,5]):
    """
    Single-row Likert scale (1–5) with no default selection.
    Stores numeric value as STRING to match your scoring logic.
    """

    if qkey not in st.session_state.responses:
        st.session_state.responses[qkey] = None

    st.markdown(f"<div class='likert-row'><b>{question}</b></div>", unsafe_allow_html=True)

    cols = st.columns(len(scale) + 1)
    cols[0].write("")  # spacer for question column

    for i, val in enumerate(scale):
        selected = st.session_state.responses[qkey] == str(val)
        btn_label = f"✅ {val}" if selected else str(val)

        if cols[i+1].button(
            btn_label,
            key=f"{qkey}_{val}"
        ):
            st.session_state.responses[qkey] = str(val)
            st.rerun()
            
def likert_grid(qkeys):
    lang = st.session_state.locked_lang

    # Header row
    hdr = st.columns(6)
    hdr[0].write("")
    for i in range(1,6):
        hdr[i].markdown(f"**{i}**")

    for q in qkeys:
        qtext = t(lang, f"Q.{q}.q", f"[MISSING QUESTION {q}]")
        likert_row(q, qtext)



# ---------------------------------------------------------
# SECTION A — Demographics (Page 2)
# ---------------------------------------------------------
if st.session_state.page == 2:
    st.header(tq("sections.A.title"))
    lang = st.session_state.locked_lang

    required = ["A1", "A2", "A3", "A4", "A5", "A6", "A7"]

    for q in required:
        qtext = t(lang, f"Q.{q}.q", f"[MISSING QUESTION {q}]")
        opts = t(lang, f"Q.{q}.opts", [])
        mcq_buttons(q, qtext, opts)

    # Navigation buttons
    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        # Back allowed only to Page 1
        if st.button(tq("back")):
            st.session_state.page = 1
            st.rerun()

    with col2:
        disabled = unanswered(required)
        st.markdown('<div class="next-btn">', unsafe_allow_html=True)
        if st.button(tq("next"), disabled=disabled):
            st.session_state.page += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION B — Sleep Behaviour (Page 3)
# ---------------------------------------------------------
if st.session_state.page == 3:
    st.header(tq("sections.B.title"))
    lang = st.session_state.locked_lang

    required = ["B1","B2","B3","B4","B5","B6","B7","B8","B9","B10","B11"]

    for q in required:
        qtext = t(lang, f"Q.{q}.q", f"[MISSING QUESTION {q}]")
        opts = t(lang, f"Q.{q}.opts", [])
        mcq_buttons(q, qtext, opts)

    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        if st.button(tq("back")):
            st.session_state.page = 2
            st.rerun()

    with col2:
        disabled = unanswered(required)
        st.markdown('<div class="next-btn">', unsafe_allow_html=True)
        if st.button(tq("next"), disabled=disabled):
            st.session_state.page += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# SECTION C — Mental Health (Page 4)
# ---------------------------------------------------------
if st.session_state.page == 4:
    st.header(tq("sections.C.title"))
    lang = st.session_state.locked_lang

    required = ["C1","C2","C3","C4","C5",
                "C6","C7","C8","C9","C10","C11","C12"]

    st.subheader(tq("sections.C.sub_who5"))
    likert_grid(required)

    # st.subheader(tq("sections.C.sub_dass"))
    # for q in ["C6","C7","C8","C9","C10","C11","C12"]:
    #     qtext = t(lang, f"Q.{q}.q", f"[MISSING QUESTION {q}]")
    #     opts = t(lang, f"Q.{q}.opts", [])
    #     mcq_buttons(q, qtext, opts)

    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        if st.button(tq("back")):
            st.session_state.page = 3
            st.rerun()

    with col2:
        disabled = unanswered(required)
        st.markdown('<div class="next-btn">', unsafe_allow_html=True)
        if st.button(tq("next"), disabled=disabled):
            st.session_state.page += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION D — Cognitive Performance (Page 5)
# ---------------------------------------------------------
if st.session_state.page == 5:
    st.header(tq("sections.D.title"))
    lang = st.session_state.locked_lang

    required = ["D1","D2","D3","D4","D5","D6","D7","D8","D9"]
    likert_grid(required)
    

    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        if st.button(tq("back")):
            st.session_state.page = 4
            st.rerun()

    with col2:
        disabled = unanswered(required)
        st.markdown('<div class="next-btn">', unsafe_allow_html=True)
        if st.button(tq("next"), disabled=disabled):
            st.session_state.page += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION E — Productivity Pattern (Page 6)
# ---------------------------------------------------------
if st.session_state.page == 6:
    st.header(tq("sections.E.title"))
    lang = st.session_state.locked_lang

    required = ["E1","E2","E3","E4"]

    for q in required:
        qtext = t(lang, f"Q.{q}.q", f"[MISSING QUESTION {q}]")
        opts = t(lang, f"Q.{q}.opts", [])
        mcq_buttons(q, qtext, opts)

    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        if st.button(tq("back")):
            st.session_state.page = 5
            st.rerun()

    with col2:
        disabled = unanswered(required)
        st.markdown('<div class="next-btn">', unsafe_allow_html=True)
        if st.button(tq("next"), disabled=disabled):
            st.session_state.page += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# SECTION F — Lifestyle & Sleep Hygiene (Page 7)
# ---------------------------------------------------------
if st.session_state.page == 7:
    st.header(tq("sections.F.title"))
    lang = st.session_state.locked_lang

    required = ["F1","F2","F3","F4","F5","F6"]

    for q in required:
        qtext = t(lang, f"Q.{q}.q", f"[MISSING QUESTION {q}]")
        opts = t(lang, f"Q.{q}.opts", [])
        mcq_buttons(q, qtext, opts)

    col1, col2, col3 = st.columns([1,1,4])
    with col1:
        if st.button(tq("back")):
            st.session_state.page = 6
            st.rerun()

    with col2:
        disabled = unanswered(required)
        st.markdown('<div class="next-btn">', unsafe_allow_html=True)
        if st.button(tq("next"), disabled=disabled):
            st.session_state.page += 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ---------------------------------------------------------
# PART 4 — SCORE CALCULATION & FINAL PAGE (Page 8)
# ---------------------------------------------------------

import pandas as pd
from datetime import datetime

def score_numeric(qkey, option_text, lang):
    """
    Return a numeric score for a given question key and the selected option text.
    - If the option is a simple digit string like '1'..'5', return int.
    - Otherwise, look up the options list in translations and return (index+1).
    - Fallback to English translations if needed.
    """
    if option_text is None:
        return None
    s = str(option_text).strip()
    # direct numeric
    if s.isdigit():
        try:
            return int(s)
        except:
            return None

    # Try to find in translations for this question
    opts = None
    try:
        opts = TRANSLATIONS.get(lang, {}).get("Q", {}).get(qkey, {}).get("opts")
    except Exception:
        opts = None

    if not opts:
        # fallback to English
        opts = TRANSLATIONS.get("en", {}).get("Q", {}).get(qkey, {}).get("opts")

    if isinstance(opts, list):
        try:
            idx = opts.index(s)
            return idx + 1
        except ValueError:
            # not found
            return None

    return None


def compute_scores(res, lang=None):
    """
    Converts translated responses into numerical scores.
    Returns dictionary of computed metrics.
    """

    if lang is None:
        lang = st.session_state.get("locked_lang")

    # Convert all options to numbers (use question key when possible)
    num = {}
    for k, v in res.items():
        num[k] = score_numeric(k, v, lang)

    # --------------- Sleep Quality Score ---------------
    # Guard against missing numeric conversions
    try:
        refresh_rev = 6 - num["B6"]
        difficulty_rev = 6 - num["B7"]
        env_rev = 6 - num["F4"]
    except Exception:
        raise ValueError("Some required numeric responses are missing or non-numeric. Ensure all questions were answered.")

    sleep_quality = refresh_rev + difficulty_rev + env_rev   # 3–15

    # --------------- WHO-5 Well-being ---------------
    who_items = [num["C1"], num["C2"], num["C3"], num["C4"], num["C5"]]
    who_rev = [6 - x for x in who_items]
    WHO_total = sum(who_rev) * 4   # Scale 0–100

    # --------------- Mental Distress (DASS-short) ---------------
    distress_total = (
        num["C6"] + num["C7"] + num["C8"] +
        num["C9"] + num["C10"] + num["C12"]
    )  # 6–30

    # --------------- Cognitive Efficiency ---------------
    cog_items = [num["D1"],num["D2"],num["D3"],num["D4"],
                 num["D5"],num["D6"],num["D7"],num["D8"]]
    cog_efficiency = sum(cog_items)  # 8–40

    # --------------- Lifestyle Risk ---------------
    # For lifestyle risk, many options are non-numeric strings; here we assume
    # numeric mapping via index+1 of the options list (see score_numeric).
    lifestyle_risk = (
        (num.get("F1") or 0) +
        (num.get("F2") or 0) +
        (5 - (num.get("F3") or 0)) +   # Physical activity reversed (assumes 1..4)
        (6 - (num.get("F4") or 0)) +   # Sleep environment reversed (1..5)
        (num.get("F5") or 0) +
        (num.get("F6") or 0)
    )

    return {
        "sleep_quality": sleep_quality,
        "WHO_total": WHO_total,
        "distress_total": distress_total,
        "cognitive_efficiency": cog_efficiency,
        "lifestyle_risk": lifestyle_risk
    }


# ---------------------------------------------------------
# FINAL PAGE  (Page 8) — SAVE DIRECTLY TO GOOGLE SHEETS
# ---------------------------------------------------------

import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets Setup ---
GSHEET_FILE = "google_key.json"   # service account key file
SHEET_NAME = "Database"             # Google Sheet name
WORKSHEET_NAME = "Sheet1"         # Tab name inside the sheet


def append_to_google_sheet(data_dict):
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )

        client = gspread.authorize(creds)
        sheet = client.open('Database').worksheet('Sheet1')

        # Add headers if sheet is empty
        if not sheet.get_all_values():
            sheet.append_row(list(data_dict.keys()))

        # Append row
        sheet.append_row(list(data_dict.values()))
        return True

    except Exception as e:
        st.error(f"Google Sheets error: {e}")
        return False
        
# ---------------------------------------------------------
# PAGE 8 UI
# ---------------------------------------------------------
if st.session_state.page == 8:
    st.header(tq("final_title"))

    # 🔢 Compute scores (UNCHANGED)
    scores = compute_scores(st.session_state.responses)

    st.success(tq("final_thanks"))
    st.subheader(tq("final_scores"))

    col1, col2 = st.columns(2)

    with col1:
        st.metric("🌙 Sleep Quality (3–15)", scores["sleep_quality"])
        st.metric("🙂 WHO-5 Well-being (0–100)", scores["WHO_total"])
        st.metric("⚠️ Mental Distress (6–30)", scores["distress_total"])

    with col2:
        st.metric("🧠 Cognitive Efficiency (8–40)", scores["cognitive_efficiency"])
        st.metric("🔥 Lifestyle Risk (higher = worse)", scores["lifestyle_risk"])

    # -------------------------------------------------
    # PREPARE DATA FOR GOOGLE SHEET
    # -------------------------------------------------
    save_data = {
        "timestamp": datetime.now().isoformat(),
        "language": st.session_state.locked_lang
    }

    # Add all question responses
    for k, v in st.session_state.responses.items():
        save_data[k] = v

    # Add computed scores
    for k, v in scores.items():
        save_data[k] = v

    # -------------------------------------------------
    # SAVE TO GOOGLE SHEET
    # -------------------------------------------------
    success = append_to_google_sheet(save_data)

    if success:
        st.balloons()
        st.caption("🎉 Thank you for contributing to sleep science!")
    else:
        st.error("❌ Failed to save your response. Please try again later.")

    # -------------------------------------------------
    # SHOW FINAL RECORD (USER VIEW)
    # -------------------------------------------------
    st.write("### 🔽 Your Final Record")
    st.dataframe(pd.DataFrame([save_data]))

    st.write(tq("done_message"))
