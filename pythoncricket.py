import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from src.tabs.team_analysis import teams_analysis
from src.tabs.stadium_analysis import stadium_data
from src.tabs.player_stats import player_stats
from src.tabs.single_match import run_app
from assets.styles import apply_styles
from src.tabs.feedback import reviews
import streamlit.components.v1 as components


st.set_page_config(layout="wide", page_title="IPL Analytics | Personal Project")


st.write("")
components.html("""
<style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { margin: 0 !important; padding: 0 !important; overflow: hidden; }
</style>
<div style="width: 40%; margin: 0 auto;">
<div id="welcome-banner" style="
    background: #E0115F;
    border-radius: 40px;
    width: 100%;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    font-size: 17px;
    font-weight: 700;
    color: #FADADD;
    font-family: 'Poppins', sans-serif;
    text-align: center;
">🏏 Welcome to IPL Analytics</div>
</div>

<script>
    const messages = [
        "Welcome to IPL Analytics",
        "IPL एनालिटिक्स में स्वागत है।",
        "आयपीएल ॲनालिटिक्समध्ये आपले स्वागत आहे.",
        "ഐപിഎൽ അനലിറ്റിക്സിലേക്ക് സ്വാഗതം."
    ];

    let index = 0;
    const el = document.getElementById("welcome-banner");

    setInterval(() => {
        el.style.transition = "opacity 0.4s ease";
        el.style.opacity = "0";
        setTimeout(() => {
            index = (index + 1) % messages.length;
            el.innerText = messages[index];
            el.style.opacity = "1";
        }, 400);
    }, 3000);
</script>
""", height=52)

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
    st.session_state["active_tab"] = "Match Center"

TAB_LABELS = ["Single match data", "Stadium Analytics", "Player Analytics", "Team Analytics", "Feedback"]


with st.container():
    st.markdown('<div style="width:100%; display:block;">', unsafe_allow_html=True)
    selected = st.radio("", TAB_LABELS, key="active_tab", horizontal=True, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="native-wrapper-box">', unsafe_allow_html=True)
    selected = st.session_state["active_tab"]
    if selected == "Single match data":     run_app()
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
        Cricket ball image generated via <a href="https://www.bing.com/images/create" target="_blank">Microsoft Bing Image Creator</a>
    </div>
""", unsafe_allow_html=True)