import streamlit as st

def render_mcq_card(q_text, options, key=None, card_color="#f0f4f8"):
    """
    Render a single MCQ inside a styled card that works in Light and Dark mode.
    """
    # Use CSS variables: 
    # var(--text-color) ensures text is dark in light mode and white in dark mode.
    # var(--secondary-background-color) provides a subtle contrast in both modes.
    
    st.markdown(
        f"""
        <div style="
            background-color: var(--secondary-background-color);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(128, 128, 128, 0.2);
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 10px;
            color: var(--text-color);
        ">
        <strong style="font-size: 1.1rem;">{q_text}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render the radio options
    choice = st.radio(
        label=f"Select an option for: {q_text}", # Added label for accessibility, but hidden via CSS if needed
        options=options,
        index=None,
        key=key,
        label_visibility="collapsed" # Hides the redundant label
    )
    return choice
