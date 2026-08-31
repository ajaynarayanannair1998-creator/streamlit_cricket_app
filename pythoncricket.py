import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import time
from src.tabs.home import home
from src.tabs.team_analysis import teams_analysis
from src.tabs.stadium_analysis import stadium_data
from src.tabs.player_stats import player_stats
from src.tabs.single_match import run_app
from assets.styles import apply_styles,set_background
from src.tabs.feedback import reviews
import streamlit.components.v1 as components


st.set_page_config(layout="wide", page_title="IPL Analytics | Personal Project")

TAB_BACKGROUNDS = {
    "Home": "assets/bat_celebration.jpg",
    "Single match data": "assets/cricketjersey.jpg",
    "Stadium Analytics": "assets/stadium_analy.jpg",
    "Player Analytics": "assets/4k_batsman.jpg",
    "Team Analytics": "assets/team_image.jpg",
    "Feedback": "assets/feedback.jpg",
}


if "initialized" not in st.session_state:
    st.session_state["initialized"] = True
    st.rerun()

apply_styles()

st.markdown("""
    <style>
        /* Keeps the top page padding minimal */
        .block-container { 
            padding-top: 0.5rem !important; 
        }
        
        /* Adjusted layout gap for micro-control over content breathing room */
        [data-testid="stVerticalBlock"] {
            gap: 0.45rem !important;
        }

        /* Incremented by another tiny pinch to hit the sweet-spot gap */
        .native-wrapper-box {
            margin-top: 30px !important;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

if "open_pill" not in st.session_state:
    st.session_state.open_pill = False
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Home"

TAB_LABELS = ["Home","Single match analysis", "Stadium Analytics", "Player Analytics", "Team Analytics", "Feedback"]


with st.container():
    st.markdown('<div style="width:100%; display:block;">', unsafe_allow_html=True)
    selected = st.radio("", TAB_LABELS, key="active_tab", horizontal=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    # Apply background for the currently active tab
    set_background(TAB_BACKGROUNDS[selected])

    # Let the background render before content loads
#     time.sleep(2)

    st.markdown('<div class="native-wrapper-box">', unsafe_allow_html=True)
    selected = st.session_state["active_tab"]
    if selected=="Home" : home()
    elif selected == "Single match analysis":     run_app()
    elif selected == "Stadium Analytics":     stadium_data()
    elif selected == "Player Analytics":    player_stats()
    elif selected == "Team Analytics": teams_analysis()
    elif selected == "Feedback":       reviews()
    st.markdown('</div>', unsafe_allow_html=True)
st.markdown("""
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #0e1117;
            color: #6c757d;
            text-align: center;
            padding: 8px;
            font-size: 12px;
            z-index: 999;
        }
    </style>
    <div class="footer">
        All cricket data sourced from <a href="https://cricsheet.org" target="_blank">cricsheet.org</a> 
        &nbsp;|&nbsp; 
        AI Chat powered by <a href="https://groq.com" target="_blank">Groq</a>
        &nbsp;|&nbsp;
        Background images and cricket ball image used in this project were generated using <a href="https://www.bing.com/images/create" target="_blank">Microsoft Bing Image Creator</a> and are used as visual assets for this personal project. 
    </div>
""", unsafe_allow_html=True)
