import streamlit as st
import json
import os
import gspread
from google.oauth2.service_account import Credentials

TRANS_PATH = "translations.json"

@st.cache_data
def load_translations():
    with open(TRANS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

TRANSLATIONS = load_translations()

def t_question(lang_code, q_id):
    """Specific helper to get question text and options dictionary"""
    # Navigates to TRANSLATIONS[lang][Q][q_id]
    q_data = t(lang_code, f"Q.{q_id}")
    if q_data and isinstance(q_data, dict):
        return q_data
    return {"q": f"Missing Question {q_id}", "opts": []}

def t(lang_code, key, default=None):
    """Core translation lookup logic"""
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

    top_val = TRANSLATIONS.get(key)
    if isinstance(top_val, dict) and lang_code in top_val:
        return top_val[lang_code]
    
    return default

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
