import streamlit as st

def render_mcq_card(q_text, options, key=None, card_color=None):
    """
    Renders a clean MCQ card that adapts to Light/Dark modes without overlapping.
    """
    # Use a container to group the question and radio buttons together
    with st.container():
        # Styled Question Header
        st.markdown(
            f"""
            <div style="
                background-color: var(--secondary-background-color);
                padding: 16px 20px;
                border-radius: 12px 12px 0px 0px;
                border: 1px solid rgba(128, 128, 128, 0.2);
                border-bottom: none;
                color: var(--text-color);
                font-weight: 600;
                font-size: 1.05rem;
            ">
                {q_text}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Radio buttons inside a matching styled box
        # We use a nested div via markdown to create the bottom half of the card
        st.markdown(
            """
            <div style="
                background-color: transparent;
                padding: 10px 20px;
                border-radius: 0px 0px 12px 12px;
                border: 1px solid rgba(128, 128, 128, 0.2);
                border-top: none;
                margin-bottom: 20px;
            ">
            """, 
            unsafe_allow_html=True
        )
        
        choice = st.radio(
            label=q_text,
            options=options,
            index=None,
            key=key,
            label_visibility="collapsed"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    return choice
