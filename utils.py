import streamlit as st
import json
import os
import gspread
from google.oauth2.service_account import Credentials

TRANS_PATH = "translations.json"

@st.cache_data
def load_translations():
    if not os.path.exists(TRANS_PATH):
        st.error("Missing translations.json file!")
        return {}
    try:
        with open(TRANS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        st.error(f"Error in translations.json syntax: {e}")
        return {}

TRANSLATIONS = load_translations()

def t(lang_code, key, default=None):
    """Core translation lookup logic"""
    # Safety check if JSON failed to load
    if not TRANSLATIONS:
        return default or key
        
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
        if cur is not None: return cur

    return default

def t_question(lang_code, q_id):
    """Specific helper to get question data safely"""
    q_data = t(lang_code, f"Q.{q_id}")
    if q_data and isinstance(q_data, dict):
        return q_data
    return {"q": f"Question {q_id} not found", "opts": []}
    
def append_to_google_sheet(data_dict, sheet_name="Database"):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
        client = gspread.authorize(creds)
        sheet = client.open(sheet_name).sheet1
        
        if not sheet.get_all_values():
            sheet.append_row(list(data_dict.keys()))
        
        sheet.append_row(list(data_dict.values()))
        return True
    except Exception as e:
        st.error(f"Google Sheets error: {e}")
        return False
