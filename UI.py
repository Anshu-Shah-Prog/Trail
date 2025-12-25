import streamlit as st

def render_mcq_card(q_text, options, key=None, card_color=None):
    """
    Enhanced MCQ card that uses theme-aware variables for perfect contrast.
    """
    # Using 'secondary-background' provides a card-like feel that 
    # automatically flips from light gray to dark gray based on the theme.
    st.markdown(
        f"""
        <div style="
            background-color: var(--secondary-background-color);
            padding: 24px;
            border-radius: 15px;
            border: 1px solid rgba(128, 128, 128, 0.1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 12px;
        ">
            <div style="
                color: var(--text-color);
                font-size: 1.1rem;
                font-weight: 600;
                line-height: 1.5;
            ">
                {q_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # We use a container to slightly pull the radio buttons up 
    # so they appear inside/near the card without overlapping text.
    with st.container():
        choice = st.radio(
            label=q_text,
            options=options,
            index=None,
            key=key,
            label_visibility="collapsed"
        )
    return choice
