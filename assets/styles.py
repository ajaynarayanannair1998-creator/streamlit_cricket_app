import streamlit as st


def apply_styles():
    st.markdown(f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800;900&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@1&display=swap" rel="stylesheet">

    <style>
    .stApp {{
        background: linear-gradient(135deg, #5F0A87, #A4508B, #FEC260);
        color: white;
        font-family: 'Poppins', sans-serif;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        display: flex;
        width: 100%;
        background: linear-gradient(135deg, #111, #222);
        padding: 10px;
        border-radius: 12px;
        gap: 0;
    }}

    .stTabs [data-baseweb="tab"] {{
        flex: 1;
        text-align: center;
        font-size: 18px;
        font-weight: 700;
        color: white;
        background: transparent;
        border-radius: 10px;
        padding: 12px 0;
        transition: all 0.3s ease;
    }}

    .stTabs [data-baseweb="tab"]:hover,
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #FFD700, #FF8C00) !important;
        color: black !important;
    }}

    .stTabs [aria-selected="true"] {{
        box-shadow: 0 4px 15px rgba(255,215,0,0.4);
    }}

    .stTabs [data-baseweb="tab-border"] {{ display: none; }}
    
    div[data-testid="stElementContainer"]:has(div[data-testid="stRadio"]) {{
        width: 100% !important;
    }}

    div[data-testid="stWidgetLabel"]:has(+ div[role="radiogroup"]) {{
        width: 100% !important;
    }}
    
    div[data-testid="stRadio"] > label {{ display: none; }}

    div[data-testid="stRadio"],
    div[data-testid="stRadio"] > div,
    div[data-testid="stRadio"] > div > div {{
        width: 100% !important;
        min-width: 100% !important;
        display: block !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex !important;
        flex-wrap: nowrap !important;
        background: #e8eaed;
        border-radius: 40px;
        padding: 6px !important;
        gap: 0;
        width: 100% !important;
        box-sizing: border-box !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] > label {{
        flex: 1 1 0 !important;
        min-width: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 14px 8px !important;
        border-radius: 36px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        white-space: nowrap !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) {{
        background: #1A73E8;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) p,
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) span {{
        color: #fff !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] > label:not(:has(input:checked)) p,
    div[data-testid="stRadio"] > div[role="radiogroup"] > label:not(:has(input:checked)) span {{
        color: #111 !important;
    }}

    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {{ display: none !important; }}
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child {{ display: block !important; }}

    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:last-child p {{
        font-size: 13px !important;
        font-weight: 500;
        margin: 0;
        text-align: center;
    }}

    div[data-testid="stHeader"], header[data-testid="stHeader"] {{
        display: none !important;
    }}

    div[data-testid="stAppViewBlockContainer"] {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }}

    div.stButton > button {{
        width: 100%;
        border-radius: 999px;
        background-color: #192841;
        color: #FF6E00;
        padding: 12px 20px;
        font-weight: 600;
        border: none;
        height: 50px;
        font-size: 16px;
        text-align: left;
        padding-left: 15px;
    }}

    div.stButton > button:hover {{ 
        background-color: #223a5e; 
        color: white; 
    }}

    .stApp .active-btn button {{ background-color: #4CAF50 !important; color: white !important; border: none !important; }}

    div[data-testid="stPopover"] button {{
        background: linear-gradient(135deg, #FFD700, #FF8C00) !important;
        color: black !important;
        border: none !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        width: 100% !important;
        border-radius: 10px !important;
        padding: 12px 0 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(255,215,0,0.4) !important;
        height: auto !important;
        text-align: center !important;
    }}

    div[data-testid="stPopover"] button:hover {{
        background: linear-gradient(135deg, #FF8C00, #FFD700) !important;
    }}

    div[data-baseweb="select"] > div {{ background-color: #192841 !important; border: 1.5px solid #FF6E00 !important; border-radius: 10px !important; }}
    div[data-baseweb="select"] div {{ background-color: #192841 !important; color: #FFD700 !important; font-family: 'Poppins', sans-serif !important; font-weight: 600 !important; }}
    .stSelectbox div[data-baseweb="select"] input {{ color: white !important; }}

    div[data-baseweb="popover"] ul {{ background-color: #192841 !important; }}
    div[data-baseweb="popover"] li {{ background-color: #192841 !important; color: #FFD700 !important; font-family: 'Poppins', sans-serif !important; }}
    div[data-baseweb="popover"] li:hover {{ background-color: #0f1c33 !important; }}
    div[data-baseweb="popover"] li:hover span,
    div[data-baseweb="popover"] li:hover div {{ color: #FF6E00 !important; }}

    svg {{ fill: #FF6E00 !important; }}

    .stApp .match-header-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        gap: 0;
    }}

    .stApp .team-box {{
        padding: 0;
        border-radius: 0;
        font-size: 18px;
        font-weight: 700;
        color: white;
        height: 140px;
        width: 100%;
        display: flex;
        align-items: center;
        overflow: hidden;
    }}

    .stApp .team-box .logo-container {{ width: 140px; height: 140px; flex-shrink: 0; }}
    .stApp .team-box .logo {{ width: 100%; height: 100%; object-fit: cover; }}
    .stApp .team-box .text {{ flex: 1; text-align: center; padding: 10px; }}

    .stApp .grass-box {{
        position: relative;
        overflow: hidden;
        background: linear-gradient(180deg, #2e7d32 0%, #388e3c 30%, #43a047 60%, #2e7d32 100%);
    }}

    .stApp .grass-box::before {{
        content: "";
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(90deg, rgba(255,255,255,0.05) 0px, rgba(255,255,255,0.05) 40px, rgba(0,0,0,0.05) 40px, rgba(0,0,0,0.05) 80px);
        pointer-events: none;
    }}

    .stApp .grass-box::after {{
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(to bottom, rgba(255,255,255,0.1), transparent 40%);
        pointer-events: none;
    }}

    .stApp .result-row {{ display: flex; align-items: center; gap: 0; margin-top: 10px; }}
    .stApp .result-left {{ flex: 1; display: flex; }}

    .stApp .result-pill {{
        width: 100%;
        padding: 14px 20px;
        font-size: 18px;
        font-weight: 800;
        color: white;
        border-radius: 0 60px 60px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    }}

    .stApp .pom-right {{ flex: 1; display: flex; justify-content: flex-end; }}

    .stApp .pom-pill {{
        width: 100%;
        padding: 14px 20px;
        font-size: 18px;
        font-weight: 800;
        color: white;
        border-radius: 60px 0 0 60px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    }}

    .stApp .format-box {{
        background-color: #FFBF00;
        color: #000;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        height: 140px;
        width: 140px;
        z-index: 10;
        position: relative;
        padding-top: 8px;
    }}

    .stApp .format-box .small-text {{ font-size: 14px; opacity: 0.8; }}
    .stApp .format-box .big-text {{ font-size: 64px; font-weight: 900; line-height: 1; flex-grow: 1; display: flex; align-items: center; }}

    div.stFormSubmitButton > button {{
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 2rem !important;
    }}

    div.stFormSubmitButton > button:hover {{ background-color: #ff2020 !important; }}
    
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea {{
        background-color: #192841 !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
    }}

    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder {{ color: rgba(255,255,255,0.45) !important; }}

    .stTextInput label, .stTextInput label p,
    .stTextArea label, .stTextArea label p {{ color: white !important; font-weight: 600 !important; }}

    .stApp .toss-venue-container {{ display: flex; align-items: stretch; gap: 0; }}

    .stApp .date-strip, .stApp .event-strip {{
        margin: 0 auto;
        display: flex;
        width: 50%;
        height: 60px;
        background: linear-gradient(135deg, #111, #333);
        color: #FFD700;
        font-weight: 800;
        font-size: 18px;
        letter-spacing: 1px;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.6);
    }}
    
    .stApp .date-strip {{ clip-path: polygon(10% 0%, 90% 0%, 100% 100%, 0% 100%); }}
    .stApp .event-strip {{ clip-path: polygon(0% 0%, 100% 0%, 90% 100%, 10% 100%); }}

    div[data-testid="stExpander"] {{
        background-color: #192841 !important;
        border: 1.5px solid #FF6E00 !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }}
    div[data-testid="stExpander"] details,
    div[data-testid="stExpander"] details summary,
    div[data-testid="stExpander"] details > div[data-testid="stExpanderDetails"] {{
        background-color: #192841 !important;
    }}
    div[data-testid="stExpander"] details summary {{
        color: #FFD700 !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 12px 18px !important;
        border-radius: 10px !important;
    }}
    div[data-testid="stExpander"] details summary:hover {{ background-color: #0f1c33 !important; }}
    div[data-testid="stExpander"] details[open] summary {{ border-bottom: 1px solid rgba(255,110,0,0.3) !important; border-radius: 10px 10px 0 0 !important; }}
    div[data-testid="stExpander"] details > div[data-testid="stExpanderDetails"] {{ padding: 16px 18px !important; }}
    div[data-testid="stExpander"] * {{ background-color: transparent !important; }}
    div[data-testid="stExpander"] svg {{ fill: #FF6E00 !important; }}

    .stApp .panel-header {{ background:#192841; border:1.5px solid #FF6E00; border-radius:10px; padding:10px 16px; margin-bottom:12px; width:100%; box-sizing:border-box; display:flex; align-items:center; justify-content:space-between; }}
    .stApp .panel-title  {{ font-family:'Poppins',sans-serif; font-weight:800; font-size:0.95rem; color:#FFD700; }}
    .stApp .panel-sub    {{ font-family:'Poppins',sans-serif; font-size:0.7rem; color:rgba(255,255,255,0.4); margin-top:2px; display:block; }}
    .stApp .ai-badge     {{ background:linear-gradient(135deg,#FFD700,#FF8C00); color:#192841; font-family:'Poppins',sans-serif; font-weight:800; font-size:0.62rem; padding:3px 8px; border-radius:999px; white-space:nowrap; }}
    /* OLD — doesn't exist, ADD this new block */
    .bat-panel,
    .bowl-panel {{
        display: contents;
    }}

    .stApp .metric-card {{ background:#192841; border:1px solid #FF6E00; border-radius:10px; padding:9px 4px; text-align:center; margin-bottom:8px; }}
    .stApp .metric-card.team-colored {{
    /* overridden at runtime by injected style — no changes needed here */
    }}
    /* NEW — remove color from these, let panel scope control it */
    .stApp .metric-val  {{ font-family:'Poppins',sans-serif; font-size:1.2rem; font-weight:900; color:#FFD700; line-height:1.2; }}
    .stApp .metric-lbl  {{ font-size:0.6rem; color:rgba(255,255,255,0.5); text-transform:uppercase; letter-spacing:0.1em; font-weight:700; }}
    .stApp .bat-panel .metric-val, .stApp .bowl-panel .metric-val {{ color:inherit !important; }}
    .stApp .bat-panel .metric-lbl, .stApp .bowl-panel .metric-lbl {{ color:inherit !important; opacity:0.85; }}

    /* NEW */
    .stApp .info-box {{ background:#192841; border:1px solid #FF6E00; border-radius:10px; padding:12px 16px 14px 16px; font-family:'Poppins',sans-serif; font-size:0.8rem; color:#FFD700; line-height:1.8; margin-top:4px; }}
    .stApp .info-box b {{ color:#FF6E00; }}
    .stApp .bat-panel .info-box, .stApp .bowl-panel .info-box {{ background:inherit !important; border-color:inherit !important; color:inherit !important; }}
    .stApp .bat-panel .info-box b, .stApp .bowl-panel .info-box b {{ color:inherit !important; }}

    .stApp .player-name {{ font-family:'Poppins',sans-serif; font-weight:900; font-size:1rem; color:#FFD700; margin:10px 0; display:block; }}

    div[data-testid="stChatMessage"] {{ background:#192841 !important; border-radius:12px !important; border:1px solid rgba(255,110,0,0.3) !important; margin-bottom:8px !important; }}
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] td,
    div[data-testid="stChatMessage"] th {{ color:#FFD700 !important; font-family:'Poppins',sans-serif !important; font-size:0.88rem !important; }}

    div[data-testid="stTextArea"] label {{ display:none !important; }}
    div[data-testid="stTextArea"] > div {{ background-color: #192841 !important; border: 2px solid #FF6E00 !important; border-radius: 10px !important; }}
    div[data-testid="stTextArea"] textarea {{ background-color: #192841 !important; color: #FFD700 !important; font-family: 'Poppins', sans-serif !important; font-weight: 600 !important; font-size: 0.88rem !important; caret-color: #FFD700 !important; resize: none !important; }}
    div[data-testid="stTextArea"] textarea::placeholder {{ color:rgba(255,215,0,0.35) !important; font-style:italic !important; }}
    div[data-testid="stTextArea"]:focus-within > div {{ border-color:#FFD700 !important; box-shadow:0 0 10px rgba(255,215,0,0.15) !important; }}

    div[data-testid="stNumberInput"] input {{ background-color: #1035AC !important; color: white !important; border: 2px solid #FFFF00 !important; border-radius: 8px !important; font-weight: 600; }}
    div[data-testid="stNumberInput"] label {{ color: white !important; font-weight: 600; }}
    div[data-testid="stNumberInput"] button {{ background-color: #FFFF00 !important; color: #1E3A8A !important; border: none !important; font-weight: 800; }}

    div[data-testid="stRadio"] * {{ color: white !important; }}
    div[data-testid="stSelectbox"] label {{ color: white !important; font-weight: 600; }}

    .stApp .ai-hint    {{ background:#192841; border:1px solid #FFD700; border-radius:8px; padding:8px 14px; color:#FFD700; font-size:0.8rem; font-weight:600; margin-bottom:6px; font-family:'Poppins',sans-serif; }}
    .stApp .ai-caption {{ font-size:0.68rem; color:rgba(255,215,0,0.4); margin-top:4px; font-family:'Poppins',sans-serif; }}

    .stApp .custom-expander {{ margin-top: 10px; border-radius: 12px; overflow: hidden; }}
    .stApp .custom-expander summary {{ padding: 12px; font-weight: 700; cursor: pointer; list-style: none; text-align: center; }}
    .stApp .custom-expander summary::-webkit-details-marker {{ display: none; }}
    .stApp .custom-expander .content {{ padding: 18px; background: rgba(255,255,255,0.08); text-align: center; }}
    .stApp .stat-line {{ margin: 6px 0; font-size: 15px; }}
    .stApp .flex-reverse {{ flex-direction: row-reverse; }}

    .stApp .pill-container {{ display: flex; border-radius: 999px; overflow: hidden; font-family: Arial, sans-serif; font-weight: 600; margin-bottom: 10px; }}
    .stApp .pill-left {{ flex: 3.5; padding: 12px 20px; }}
    .stApp .pill-right {{ flex: 1.5; display: flex; align-items: center; justify-content: center; }}

    .stApp .custom-warning {{ background-color: #1E3A8A; border: 2px solid #FFFF00; border-radius: 10px; padding: 14px 20px; color: white; font-family: Arial, sans-serif; font-weight: 600; font-size: 15px; margin-top: 10px; }}
    </style>
    """, unsafe_allow_html=True)


def pill(text, value, left_color="#1035AC", right_color="#FFFF00", text_color="white", value_color="#1E3A8A", width="400px"):
    st.markdown(f"""
    <div class="pill-container" style="width:{width};">
        <div class="pill-left" style="background:{left_color}; color:{text_color};">{text}</div>
        <div class="pill-right" style="background:{right_color}; color:{value_color};">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def info_box(message, border_color="#FFFF00"):
    st.markdown(f"""
    <div class="custom-warning" style="border-color:{border_color};">
        {message}
    </div>
    """, unsafe_allow_html=True)


def custom_expander(title, content_html, team_color, team_text_color, font_size="15px"):
    return f"""
    <div class="custom-expander">
        <details>
            <summary style="background:{team_color}; color:{team_text_color}; padding:12px; font-weight:700; cursor:pointer; list-style:none; border-bottom:1px solid rgba(0,0,0,0.1); font-size:18px;">
                {title}
            </summary>
            <div class="content" style="padding:18px; background:{team_color}; color:{team_text_color}; text-align:center; font-size:{font_size}; font-weight:900; font-family:'Libre Baskerville', serif; font-style:italic;">
                {content_html}
            </div>
        </details>
    </div>
    """


def custom_expander1(title, content_html, team_color, team_text_color, font_size="15px"):
    return custom_expander(title, content_html, team_color, team_text_color, font_size)


def team_box_html(team_name, score, overs, img_b64, box_color, team_text_color, reverse=False):
    reverse_class = "flex-reverse" if reverse else ""
    return f"""
    <div class='team-box {reverse_class}' style='background:{box_color};'>
        <div class="logo-container">
            <img class='logo' src='data:image/png;base64,{img_b64}'>
        </div>
        <div class='text'>
            <span style="font-size:17px; color:{team_text_color}; opacity:0.9;">{team_name}</span><br>
            <span class='score-number' style="color:{team_text_color};">{score}</span><br>
            <span style="font-size:17px; color:{team_text_color};">({overs})</span>
        </div>
    </div>
    """


def information_box(title, value, bg_color, toss_text_color, extra_class=""):
    return f"""
    <div class='team-box {extra_class}' style='background:{bg_color}; color:{toss_text_color}; justify-content:center;'>
        <div class='text'>
            <div style="font-size:14px; opacity:0.85; text-transform:uppercase;">{title}</div>
            <div style="font-size:22px; margin-top:6px; font-weight:900;">{value}</div>
        </div>
    </div>
    """


def box_data(COLORS, date, TEAM_A, TEAM_B, final_teamAscore, final_teamBscore,
             ateamplayed_overs, bteamplayed_overs, team_a_b64, team_b_b64,
             COLOR_A, COLOR_B, a_textcolor, b_textcolor, event_name):
    st.markdown("# MATCH ANALYSIS")
    st.markdown(f"""
    <style>
    .stApp .team-vs-wrapper {{
        margin-top: 24px;
        margin-bottom: 24px;
        width: 100%;
    }}
    .stApp .vs-box {{
        background-color: {COLORS["NAVY"]};
        color: {COLORS["BLACK"]};
        font-weight: 900;
        font-size: 60px;
        display: flex;
        justify-content: center;
        align-items: center;
        height: 140px;
        width: 140px;
        margin-left: -20px;
        margin-right: -20px;
        z-index: 10;
        position: relative;
    }}
    .stApp .team-vs-container {{
        display: flex;
        align-items: center;
        width: 100%;
        gap: 0;
        margin: 0;
    }}
    .stApp .date-strip, .stApp .event-strip {{ margin: 0 auto; display: flex; }}
    </style>
    
    <div class="team-vs-wrapper">
        <div class="date-strip">DATE: {date}</div>
        <div class="team-vs-container">
            <div style="flex:1;">{team_box_html(TEAM_A, final_teamAscore, ateamplayed_overs, team_a_b64, COLOR_A, a_textcolor)}</div>
            <div class="vs-box">VS</div>
            <div style="flex:1;">{team_box_html(TEAM_B, final_teamBscore, bteamplayed_overs, team_b_b64, COLOR_B, b_textcolor, reverse=True)}</div>
        </div>
        <div class="event-strip">EVENT: {event_name}</div>
    </div>
    """, unsafe_allow_html=True)