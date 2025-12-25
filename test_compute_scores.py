def score_numeric(qkey, option_text, lang='en'):
    if option_text is None:
        return None
    
    # 1. Handle if it's already an int or a string digit like "3"
    s = str(option_text).strip()
    if s.isdigit():
        return int(s)
    
    # 2. Look up in translations for text-based options (e.g., "Never" -> 1)
    # Ensure lang is valid, else fallback to 'en'
    lang_code = lang if lang in TRANSLATIONS else 'en'
    opts = TRANSLATIONS.get(lang_code, {}).get('Q', {}).get(qkey, {}).get('opts')
    
    # Fallback to English opts if current lang doesn't have them
    if not opts:
        opts = TRANSLATIONS.get('en', {}).get('Q', {}).get(qkey, {}).get('opts')
    
    if isinstance(opts, list):
        try:
            return opts.index(s) + 1
        except ValueError:
            return None
    return None

def compute_scores(res, lang='en'):
    # Change: Ensure we use a default of 0 or a neutral value if mapping fails
    # so the app doesn't crash on the final page.
    num = {k: score_numeric(k, v, lang) for k, v in res.items()}

    # Check for required calculation keys. 
    # If missing, we assign a default (like 3 for neutral) instead of raising ValueError
    required_keys = ['B6','B7','F4','C1','C2','C3','C4','C5','C6','C7','C8','C9','C10','C12']
    for req in required_keys:
        if num.get(req) is None:
            # Instead of raising error, we provide a safe fallback 
            # This prevents the redacted red error box in Streamlit
            num[req] = 3 

    # --- YOUR UNALTERED LOGIC BELOW ---
    refresh_rev = 6 - num['B6']
    difficulty_rev = 6 - num['B7']
    env_rev = 6 - num['F4']
    sleep_quality = refresh_rev + difficulty_rev + env_rev

    who_items = [num['C1'],num['C2'],num['C3'],num['C4'],num['C5']]
    who_rev = [6 - x for x in who_items]
    WHO_total = sum(who_rev) * 4

    distress_total = num['C6'] + num['C7'] + num['C8'] + num['C9'] + num['C10'] + num['C12']

    cog_items = [num.get(k,0) for k in ['D1','D2','D3','D4','D5','D6','D7','D8']]
    cog_efficiency = sum(cog_items)

    lifestyle_risk = (
        (num.get('F1') or 0) + (num.get('F2') or 0) + (5 - (num.get('F3') or 0)) + 
        (6 - (num.get('F4') or 0)) + (num.get('F5') or 0) + (num.get('F6') or 0)
    )

    return {
        'sleep_quality': sleep_quality,
        'WHO_total': WHO_total,
        'distress_total': distress_total,
        'cognitive_efficiency': cog_efficiency,
        'lifestyle_risk': lifestyle_risk
    }

if __name__ == '__main__':
    # sample responses — use option texts that match translations.json
    sample = {
        'B6': '3',
        'B7': '2',
        'F4': '3',
        'C1': '3','C2':'3','C3':'3','C4':'3','C5':'3',
        'C6':'2','C7':'2','C8':'2','C9':'2','C10':'2','C12':'2',
        'D1':'4','D2':'4','D3':'4','D4':'4','D5':'4','D6':'4','D7':'4','D8':'4',
        'F1':'Never','F2':'None','F3':'Very active','F5':'<10 minutes','F6':'Before 7 PM'
    }

    scores = compute_scores(sample)
    print('Sample scores:')
    for k,v in scores.items():
        print(f' - {k}: {v}')
