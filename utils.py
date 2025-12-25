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
    """Translation lookup that works for nested questions or top-level keys."""
    if not TRANSLATIONS:
        return default or key

    # 1. First, check if key exists as top-level
    top_val = TRANSLATIONS.get(key)
    if isinstance(top_val, dict) and lang_code in top_val:
        return top_val[lang_code]

    # 2. Otherwise, check inside lang_code block (like questions)
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

    return default or key

def t_question(lang_code, q_id):
    """Specific helper to get question data safely"""
    # Force check the Q block directly
    lang_block = TRANSLATIONS.get(lang_code, {})
    q_dict = lang_block.get("Q", {})
    q_data = q_dict.get(q_id)
    
    if q_data and isinstance(q_data, dict):
        return q_data
    
    # Fallback if ID is missing
    return {"q": f"Question {q_id} missing", "opts": ["Error: Options not found"]}
    
def append_to_google_sheet(data_dict, sheet_name="Database"):
    """
    Append a row to a Google Sheet using a service account.
    
    Args:
        data_dict (dict): Dictionary of key-value pairs to append.
        sheet_name (str): Name of the Google Sheet to append data to.
    
    Returns:
        bool: True if data appended successfully, False otherwise.
    """
    try:
        # Define scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        # Load credentials from Streamlit secrets
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"], scopes=scopes
        )

        client = gspread.authorize(creds)
        sheet = client.open(sheet_name).sheet1

        # Get existing values
        existing_values = sheet.get_all_values()

        # If sheet is empty, add headers first
        if not existing_values:
            sheet.append_row(list(data_dict.keys()))
            st.info("Header row added.")

        # Append new row
        sheet.append_row(list(data_dict.values()))
        st.success("Data appended successfully!")
        return True

    except gspread.exceptions.APIError as e:
        st.error(f"Google Sheets API error: {e}")
        return False
    except Exception as e:
        st.error(f"Error saving to Google Sheet: {e}")
        return False
