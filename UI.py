import streamlit as st

def render_mcq_card(q_text, options, key=None, card_color=None):
    """
    Render a single MCQ inside a styled card that adapts to light/dark themes.
    """
    # Using CSS variables ensures the card background and text color
    # adjust automatically to the user's system theme.
    st.markdown(
        f"""
        <div style="
            background-color: var(--secondary-background-color);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(128, 128, 128, 0.2);
            margin-bottom: -40px; 
            color: var(--text-color);
        ">
            <strong style="font-size: 1.1rem;">{q_text}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Render radio options. We use label_visibility="collapsed" 
    # because the question text is already displayed in the HTML card above.
    choice = st.radio(
        label=q_text,
        options=options,
        index=None,
        key=key,
        label_visibility="collapsed"
    )
    return choice
