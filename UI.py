import streamlit as st

def render_mcq_card(q_text, options, key=None, card_color="#f0f4f8"):
    """
    Render a single MCQ inside a styled card.
    """
    # Wrap the question in a styled div
    st.markdown(
        f"""
        <div style="
            background-color: {card_color};
            padding: 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        ">
        <strong>{q_text}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Render the options below inside the same card visually
    choice = st.radio(
        label="",
        options=options,
        key=key
    )
    return choice
