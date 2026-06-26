import streamlit as st
import requests
from assets.styles import apply_styles
def reviews():

    st.title("Feedback")
    st.markdown("Please provide your valuable feedback and suggestions. Your reviews are valuable")

    with st.form("feedback_form", clear_on_submit=True):
        name = st.text_input("Name (Optional)", placeholder="Enter your name")
        position = st.text_input("You are a (optional)", placeholder="Data Analyst")
        st.markdown("Enter your feedback")
        message = st.text_area("", placeholder="Write your feedback here...")
        submit = st.form_submit_button("Submit")

    if submit:
        if not message.strip():
            st.markdown("""
                <div style="background-color: #FF4B4B; color: #FFFFFF; 
                            padding: 12px 20px; border-radius: 8px; 
                            font-size: 15px; font-weight: 600; 
                            text-align: center; margin: 10px 0;
                            box-shadow: 0 2px 8px rgba(255,75,75,0.4);">
                    Please fill the feedback.
                </div>
            """, unsafe_allow_html=True)
        else:
            response = requests.post(
                f"https://formspree.io/f/{st.secrets['FORMSPREE_ID']}",
                json={
                    "name": name if name.strip() else "Anonymous",
                    "position":position if position.strip() else 'not mentioned',
                    "message": message
                }
            )
            if response.status_code == 200:
                st.markdown("""
                <div style="background-color: #23C55E; color: #FFFFFF; 
                            padding: 12px 20px; border-radius: 8px; 
                            font-size: 15px; font-weight: 600; 
                            text-align: center; margin: 10px 0;
                            box-shadow: 0 2px 8px rgba(255,75,75,0.4);">
                    Thanks for feedback.
                </div>
            """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="background-color: #FF4B4B; color: #FFFFFF; 
                            padding: 12px 20px; border-radius: 8px; 
                            font-size: 15px; font-weight: 600; 
                            text-align: center; margin: 10px 0;
                            box-shadow: 0 2px 8px rgba(35,197,94,0.4);">
                    Some issue from backend. Please try again
                </div>
            """, unsafe_allow_html=True)