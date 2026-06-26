import streamlit as st
import pandas as pd
import json
from pathlib import Path
import time
from assets.styles import apply_styles, custom_expander1, custom_expander, team_box_html, pill, info_box

apply_styles()

EXAMPLE_QUESTIONS = [
    "How did Rohit Sharma perform in death overs?",
    "Compare Virat Kohli and AB de Villiers",
    "Who has the best knockout average?",
    "Show MS Dhoni's year by year stats",
    "Which player has the highest strike rate in phase 3?",
    "How does SKY perform under pressure?",
    "Top 3 batters by total runs?",
    "Compare Hardik Pandya and Andre Russell",
    "How many wickets did Bumrah take in knockouts?",
    "Who has the best economy in death overs?",
    "Compare Bumrah and Malinga bowling stats",
    "Which bowler has most 3 wicket hauls?",
]

@st.cache_data
def load_base_data():
    encodings = ["utf-8", "latin-1"]

    def read_csv_safe(filename):
        for enc in encodings:
            try:
                df = pd.read_csv(filename, encoding=enc)
                df.columns = df.columns.str.strip()
                return df
            except Exception:
                continue
        return pd.DataFrame()

    batter_df       = read_csv_safe("data/datasets/batter_summary.csv")
    batter_yearly   = read_csv_safe("data/datasets/batter_yearly.csv")
    batter_phase    = read_csv_safe("data/datasets/batter_phase.csv")
    batter_knockout = read_csv_safe("data/datasets/batter_knockout.csv")

    bowler_df       = read_csv_safe("data/datasets/bowler_summary.csv")
    bowler_yearly   = read_csv_safe("data/datasets/bowler_yearly.csv")
    bowler_phase    = read_csv_safe("data/datasets/bowler_phase.csv")
    bowler_knockout = read_csv_safe("data/datasets/bowler_knockout.csv")

    return (
        batter_df, batter_yearly, batter_phase, batter_knockout,
        bowler_df, bowler_yearly, bowler_phase, bowler_knockout,
    )


@st.cache_data
def load_aliases():
    try:
        with open("data/player_aliases.json.txt", "r", encoding="utf-8") as f:
            raw = json.load(f)
        alias_map      = {name.lower(): key for key, names in raw.items() for name in names}
        csv_to_display = {key: names[0] for key, names in raw.items() if names}
        return alias_map, csv_to_display
    except FileNotFoundError:
        return {}, {}


@st.cache_data
def load_team_colors():
    try:
        with open("data/colors.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("team", {})
    except Exception:
        return {}


_EMPTY_TEAM_VALUES = {"n/a", "nan", "none", "null", ""}


def get_player_colors(team_name, color_map):
    if not color_map:
        return None, None
    t_raw = str(team_name).strip()
    if t_raw.lower() in _EMPTY_TEAM_VALUES:
        return None, None
    t_clean = t_raw.lower()
    for team_key, config in color_map.items():
        override_teams = {"gujarat titans"}
        key_clean = team_key.strip().lower()
        if t_clean == key_clean or key_clean in t_clean or t_clean in key_clean:
            bg_color = config.get("bg-color")
            text_color = config.get("text_color")
        
            if key_clean in override_teams:
                bg_color = "#F4DD8C"
                text_color="#192841"
                
            return bg_color, text_color
    return None, None


def _resolve_team_name(row, *column_candidates):
    for col in column_candidates:
        val = row.get(col, "")
        if val and str(val).strip().lower() not in _EMPTY_TEAM_VALUES:
            return str(val).strip()
    return ""

def safe_int(val, default=0):
    try:
        return int(val) if pd.notna(val) else default
    except Exception:
        return default

def safe_float(val, default=0.0):
    try:
        return float(val) if pd.notna(val) else default
    except Exception:
        return default

def _inject_panel_styles(scope_class, bg_color, text_color):
    st.markdown(
        f"<style>"
        f".stApp .{scope_class} .metric-card {{"
        f"  background: {bg_color} !important;"
        f"  background-color: {bg_color} !important;"
        f"  border-color: {bg_color} !important;"
        f"  color: {text_color} !important;"
        f"}}"
        f".stApp .{scope_class} .metric-val {{"
        f"  color: {text_color} !important;"
        f"  font-weight: bold;"
        f"}}"
        f".stApp .{scope_class} .metric-lbl {{"
        f"  color: {text_color} !important;"
        f"  opacity: 0.85;"
        f"}}"
        f".stApp .{scope_class} .info-box {{"
        f"  background: {bg_color} !important;"
        f"  background-color: {bg_color} !important;"
        f"  border-color: {bg_color} !important;"
        f"  color: {text_color} !important;"
        f"}}"
        f".stApp .{scope_class} .info-box b {{"
        f"  color: {text_color} !important;"
        f"}}"
        f"</style>",
        unsafe_allow_html=True,
    )


def render_metric_card(label, value):
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-val">{value}</div>'
        f'<div class="metric-lbl">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_info_box(content):
    st.markdown(f'<div class="info-box">{content}</div>', unsafe_allow_html=True)
    st.write("")


def find_players_in_query(query, all_names, alias_map):
    try:
        from rapidfuzz import fuzz, process
        has_rf = True
    except ImportError:
        has_rf = False

    q_low   = query.lower()
    matched = {}

    for alias, key in alias_map.items():
        if alias in q_low:
            matched[key] = "alias"

    for name in all_names:
        if name in matched:
            continue
        nl = name.lower()
        if nl in q_low:
            matched[name] = "exact"
            continue
        for tok in nl.split():
            if len(tok) >= 4 and tok in q_low:
                matched[name] = "token"
                break

    if has_rf:
        toks  = q_low.split()
        cands = toks + [f"{toks[i]} {toks[i+1]}" for i in range(len(toks) - 1)]
        pool  = list(alias_map.keys()) if alias_map else all_names
        for c in cands:
            if len(c) < 4:
                continue
            r = process.extractOne(c, pool, scorer=fuzz.WRatio, score_cutoff=82)
            if r:
                key = alias_map.get(r[0], r[0])
                if key not in matched:
                    matched[key] = f"fuzzy ({r[1]:.0f}%)"

    return list(matched.keys()), [k for k, v in matched.items() if "fuzzy" in str(v)]


def detect_query_type(query):
    q  = query.lower()
    bs = sum(k in q for k in ["wicket", "bowl", "economy", "haul", "delivery", "yorker", "spinner", "pacer"])
    bt = sum(k in q for k in ["run", "score", "bat", "century", "fifty", "boundary", "strike rate", "batting_average", "innings"])
    if bs == 0 and bt == 0:
        return "both"
    if abs(bs - bt) <= 1:
        return "both"
    return "bowler" if bs > bt else "batter"

def compute_batter_comparison(players, df):
    if len(players) < 2 or df.empty:
        return ""
    valid_players = [p for p in players if p in df["batter"].values]
    if len(valid_players) < 2:
        return ""
    rows  = df[df["batter"].isin(valid_players)].set_index("batter")
    notes = ["=== BATTER COMPARISON ==="]
    metrics = {
        "total_runs":          "Most runs",
        "total_matches":       "Most matches",
        "batting_average":     "Higher avg",
        "overall_strike_rate": "Higher SR",
        "fifties":             "More 50s",
        "hundreds":            "More 100s",
    }
    for col, lbl in metrics.items():
        if col not in rows.columns:
            continue
        v = rows[col].dropna()
        if v.empty:
            continue
        leader = v.idxmax()
        vals   = ", ".join(f"{p}: {rows.loc[p, col]}" for p in valid_players if p in rows.index)
        notes.append(f"- {lbl}: {leader} ({vals})")
    return "\n".join(notes)


def compute_bowler_comparison(players, df):
    if len(players) < 2 or df.empty:
        return ""
    rows  = df[df["bowler"].isin(players)].set_index("bowler")
    notes = ["=== BOWLER COMPARISON ==="]
    metrics = {
        "total_wickets":      "Most wickets",
        "total_matches":      "Most matches",
        "overall_economy":    "Better economy",
        "three_wicket_hauls": "More 3W",
        "five_wicket_hauls":  "More 5W",
    }
    for col, lbl in metrics.items():
        if col not in rows.columns:
            continue
        v = rows[col].dropna()
        if v.empty:
            continue
        leader = v.idxmin() if col == "overall_economy" else v.idxmax()
        vals   = ", ".join(f"{p}: {rows.loc[p, col]}" for p in players if p in rows.index)
        notes.append(f"- {lbl}: {leader} ({vals})")
    return "\n".join(notes)

def build_context(query, dfs, alias_map):
    bat_sum, bat_yr, bat_ph, bat_ko, bowl_sum, bowl_yr, bowl_ph, bowl_ko = dfs

    qt = detect_query_type(query)
    ab = bat_sum["batter"].tolist()  if not bat_sum.empty  else []
    aw = bowl_sum["bowler"].tolist() if not bowl_sum.empty else []

    matched_players, fuzzy_notes = find_players_in_query(query, list(set(ab + aw)), alias_map)

    if not matched_players:
        if qt == "bowler" and not bowl_sum.empty:
            matched_players = bowl_sum.nlargest(3, "total_wickets")["bowler"].tolist()
        elif not bat_sum.empty:
            matched_players = bat_sum.nlargest(3, "total_runs")["batter"].tolist()

    parts = []

    if qt in ("batter", "both") and not bat_sum.empty:
        bp = [p for p in matched_players if p in ab] or matched_players
        if bp:
            b_sum_slice = bat_sum[bat_sum["batter"].isin(bp)]
            b_yr_slice  = (
                bat_yr[bat_yr["batter"].isin(bp)].sort_values("year").groupby("batter").tail(3)
                if not bat_yr.empty else pd.DataFrame()
            )
            b_ph_slice  = (
                bat_ph[bat_ph["batter"].isin(bp)]
                if not bat_ph.empty and "batter" in bat_ph.columns else pd.DataFrame()
            )
            b_ko_slice  = bat_ko[bat_ko["batter"].isin(bp)] if not bat_ko.empty else pd.DataFrame()
            parts.append(
                f"=== BATTER PROFILE & SUMMARY ===\n{b_sum_slice.to_string(index=False)}\n\n"
                f"=== BATTER RECENT SEASONS ===\n{b_yr_slice.to_string(index=False) if not b_yr_slice.empty else 'N/A'}\n\n"
                f"=== BATTER INNINGS PHASES SPLIT ===\n{b_ph_slice.to_string(index=False) if not b_ph_slice.empty else 'N/A'}\n\n"
                f"=== BATTER LEAGUE VS KNOCKOUT PRESSURE ===\n{b_ko_slice.to_string(index=False) if not b_ko_slice.empty else 'N/A'}"
            )
            if len(bp) > 1:
                parts.append(compute_batter_comparison(bp, bat_sum))

    if qt in ("bowler", "both") and not bowl_sum.empty:
        wp = [p for p in matched_players if p in aw]
        if not wp:
            wp = [p for p in matched_players if p in bowl_sum["bowler"].values]
        if wp:
            w_sum_slice = bowl_sum[bowl_sum["bowler"].isin(wp)]
            w_yr_slice  = (
                bowl_yr[bowl_yr["bowler"].isin(wp)].sort_values("year").groupby("bowler").tail(3)
                if not bowl_yr.empty else pd.DataFrame()
            )
            w_ph_slice  = (
                bowl_ph[bowl_ph["bowler"].isin(wp)]
                if not bowl_ph.empty and "bowler" in bowl_ph.columns else pd.DataFrame()
            )
            w_ko_slice  = bowl_ko[bowl_ko["bowler"].isin(wp)] if not bowl_ko.empty else pd.DataFrame()
            parts.append(
                f"=== BOWLER PROFILE & SUMMARY ===\n{w_sum_slice.to_string(index=False)}\n\n"
                f"=== BOWLER RECENT SEASONS ===\n{w_yr_slice.to_string(index=False) if not w_yr_slice.empty else 'N/A'}\n\n"
                f"=== BOWLER INNINGS PHASES SPLITS ===\n{w_ph_slice.to_string(index=False) if not w_ph_slice.empty else 'N/A'}\n\n"
                f"=== BOWLER LEAGUE VS KNOCKOUT PRESSURE ===\n{w_ko_slice.to_string(index=False) if not w_ko_slice.empty else 'N/A'}"
            )
            if len(wp) > 1:
                parts.append(compute_bowler_comparison(wp, bowl_sum))

    context_string = "\n\n".join(p for p in parts if p.strip())
    if len(context_string) > 9000:
        context_string = context_string[:9000] + "\n...[Context size limit reached, safely truncated]"

    return context_string, matched_players, fuzzy_notes

def ask_ai(question, context, history):
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if not api_key:
        return "No API key found in Streamlit Secrets setup configurations."
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
    except ImportError:
        return "Missing dependencies. Run: pip install groq"

    hist = "".join(
        f"\nUser: {t['user']}\nAssistant: {t['assistant']}"
        for t in history[-2:]
    )

    prompt = f"""You are an expert T20/IPL cricket analyst speaking directly to a fan.
Batter phases definitions: phase_1_10=balls 1-10 faced, phase_10_40=balls 11-40 faced, phase_40plus=balls 41+ faced
Bowler phases definitions: powerplay=overs 1-6, middle=overs 7-15, death=overs 16-20
league=regular round-robin phase matches, knockout=playoffs & tournament finals matches

METRIC INTERPRETATION RULES (apply these strictly when drawing conclusions):
- For BATTERS: higher strike_rate = BETTER, higher batting_average = BETTER, lower dot_percentage = BETTER, more runs = BETTER
- For BOWLERS: lower economy = BETTER, more wickets = BETTER, lower average = BETTER
- When comparing two players, state who leads each metric explicitly and WHY it matters.
- Your final conclusion MUST be logically consistent with the numbers you just presented.
  Example: if Player A has SR 158 and Player B has SR 107, you MUST say Player A is the better death-over striker — never the reverse.
- Never contradict the numbers in your summary.

CRITICAL INSTRUCTIONS:
1. Provide a direct, clean, conversational final answer.
2. DO NOT write or generate SQL code, SELECT statements, pseudo-code, or programming logic.
3. Extract the requested numbers from the data tables below and present them clearly.
4. Keep the presentation natural, precise, and visually clean (use 2 decimal places for rates/averages).
5. End with a clear, one-sentence verdict that matches the data.

=== PLAYERS HISTORICAL DATA STRUCTURE ===
{context}
{f"=== RECENT INTERACTION HISTORY ==={hist}" if hist.strip() else ""}
Q: {question}
A:"""

    try:
        time.sleep(0.5)
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
            temperature=0.3,
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"Groq runtime error: {str(e)}"


def render_batter_lookup(batter_df, csv_to_display):
    st.markdown(
        '<div class="panel-header"><div>'
        '<span class="panel-title">Batter Lookup</span>'
        '<span class="panel-sub">Career batting stats</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    if batter_df.empty:
        return None, None

    display_to_csv = {}
    for csv_name in batter_df["batter"].tolist():
        display_name = csv_to_display.get(csv_name) or csv_to_display.get(csv_name.lower(), csv_name)
        display_to_csv[display_name] = csv_name

    options = ["— select batter —"] + sorted(display_to_csv.keys())
    selected_display = st.selectbox(
        "batter_lookup", options=options,
        label_visibility="collapsed", key="batter_select",
    )
    if selected_display == "— select batter —":
        return None, None
    return selected_display, display_to_csv[selected_display]


def render_batter_stats(batter_df, display_name, csv_name, color_map):
    row = batter_df[batter_df["batter"] == csv_name].iloc[0]

    team_name = _resolve_team_name(row, "last_known_team", "last_team", "team")
    bg_color, text_color = get_player_colors(team_name, color_map)

    if bg_color and text_color:
        _inject_panel_styles("bat-panel", bg_color, text_color)

    sr_col = "overall_strike_rate" if "overall_strike_rate" in batter_df.columns else "strike_rate"

    html_content = []
    html_content.append('<div class="bat-panel">')
    html_content.append(f'<span class="player-name">{display_name}</span>')

    metrics = [
        ("Matches", safe_int(row["total_matches"])),
        ("Runs",    safe_int(row["total_runs"])),
        ("Avg",      f"{safe_float(row['batting_average']):.1f}"),
        ("SR",      f"{safe_float(row[sr_col]):.1f}"),
        ("50s",     safe_int(row["fifties"])),
        ("100s",    safe_int(row["hundreds"])),
    ]
    for lbl, val in metrics:
        html_content.append(
            f'<div class="metric-card">'
            f'<div class="metric-val">{val}</div>'
            f'<div class="metric-lbl">{lbl}</div>'
            f'</div>'
        )

    first_year  = safe_int(row.get("debut_year", 0))
    last_year   = safe_int(row.get("final_year", 0))
    year_range  = f"{first_year} – {last_year}" if first_year else "N/A"
    batting_pos = row.get("predominant_batting_position", "N/A")

    html_content.append(f'<div class="info-box"><b>Active:</b> {year_range}</div>')
    html_content.append(f'<div class="info-box"><b>Usual batting position:</b> {batting_pos}</div>')
    html_content.append(f'<div class="info-box"><b>Teams:</b> {row.get("teams_represented", "N/A")}</div>')
    
    html_content.append('</div>')

    st.markdown("\n".join(html_content), unsafe_allow_html=True)
    st.markdown("")

def render_bowler_lookup(bowler_df, csv_to_display):
    st.markdown(
        '<div class="panel-header"><div>'
        '<span class="panel-title">Bowler Lookup</span>'
        '<span class="panel-sub">Career bowling stats</span>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    if bowler_df.empty:
        return None, None

    display_to_csv = {}
    for csv_name in bowler_df["bowler"].tolist():
        display_name = csv_to_display.get(csv_name) or csv_to_display.get(csv_name.lower(), csv_name)
        display_to_csv[display_name] = csv_name

    options = ["— select bowler —"] + sorted(display_to_csv.keys())
    selected_display = st.selectbox(
        "bowler_lookup", options=options,
        label_visibility="collapsed", key="bowler_select",
    )
    if selected_display == "— select bowler —":
        return None, None
    return selected_display, display_to_csv[selected_display]


def render_bowler_stats(bowler_df, display_name, csv_name, color_map):
    row = bowler_df[bowler_df["bowler"] == csv_name].iloc[0]

    team_name = _resolve_team_name(row, "last_team", "last_known_team", "team")
    bg_color, text_color = get_player_colors(team_name, color_map)

    if bg_color and text_color:
        _inject_panel_styles("bowl-panel", bg_color, text_color)

    best_wkt = row.get("highest_match_wickets", row.get("most_wickets_in_match", 0))
    html_content = []
    html_content.append('<div class="bowl-panel">')
    html_content.append(f'<span class="player-name">{display_name}</span>')

    metrics = [
        ("Matches",  safe_int(row["total_matches"])),
        ("Wickets",  safe_int(row["total_wickets"])),
        ("Economy",  f"{safe_float(row['overall_economy']):.2f}"),
        ("Best",     f"{safe_int(best_wkt)}W"),
        ("3W Hauls", safe_int(row["three_wicket_hauls"])),
        ("5W Hauls", safe_int(row["five_wicket_hauls"])),
    ]
    
    # Render all metric cards as children inside the panel string
    for lbl, val in metrics:
        html_content.append(
            f'<div class="metric-card">'
            f'<div class="metric-val">{val}</div>'
            f'<div class="metric-lbl">{lbl}</div>'
            f'</div>'
        )

    html_content.append(f'<div class="info-box"><b>Best Season:</b> {safe_int(row.get("best_season", 0))}</div>')
    html_content.append(f'<div class="info-box"><b>Main Dismissal:</b> {row.get("most_dismissals", "N/A")}</div>')
    html_content.append(f'<div class="info-box"><b>Teams:</b> {row.get("teams_represented", "N/A")}</div>')
    
    html_content.append('</div>')

    st.markdown("\n".join(html_content), unsafe_allow_html=True)
    st.markdown("")

BANNED_KEYWORDS = ["salary", "contract", "personal", "fight", "controversy", "ipl auction price"]

def render_ai_chat(dfs, alias_map):
    if "ai_messages"      not in st.session_state: st.session_state["ai_messages"]      = []
    if "ai_placeholder_i" not in st.session_state: st.session_state["ai_placeholder_i"] = 0
    if "ai_pending"       not in st.session_state: st.session_state["ai_pending"]        = []

    ph = EXAMPLE_QUESTIONS[st.session_state["ai_placeholder_i"] % len(EXAMPLE_QUESTIONS)]

    st.markdown(
    f'<div class="panel-header"><div>'
    f'<span class="panel-title">Cricket AI Analyst</span>'
    f'<span class="panel-sub">Ask about batters, bowlers, comparisons & knockouts</span>'
    f'</div><span class="ai-badge">Llama 3.1 · CSV Query Engine</span></div>',
    unsafe_allow_html=True,
    )

    for msg in st.session_state["ai_messages"]:
        with st.chat_message("user",      avatar="🧑"): st.markdown(msg["user"])
        with st.chat_message("assistant", avatar="🏏"): st.markdown(msg["assistant"])

    st.write("")
    st.text_area(
        "Ask anything", placeholder=ph,
        label_visibility="collapsed", key="ai_typed_input", height=68,
    )

    with st.form(key="ai_form", clear_on_submit=False):
        ask_clicked = st.form_submit_button("Ask 🏏", use_container_width=True)

    if ask_clicked:
        question = st.session_state.get("ai_typed_input", "").strip().replace("\n", " ")
        if question:
            # 2. Check for banned keywords
            contains_banned_word = any(word in question.lower() for word in BANNED_KEYWORDS)
            
            if contains_banned_word:
                # Alert the user and do not set st.session_state["ai_pending"]
                st.error("⚠️ Your question contains off-topic keywords. Please recheck your question and try again.")
            else:
                # Proceed normally if no restricted keywords are found
                st.session_state["ai_pending"]        = question
                st.session_state["ai_placeholder_i"] += 1
                st.rerun()

    pending = st.session_state.pop("ai_pending", "")
    if pending:
        with st.chat_message("user", avatar="🧑"):
            st.markdown(pending)
        with st.chat_message("assistant", avatar="🏏"):
            with st.spinner("Analysing performance matrix splits..."):
                ctx, players, fuzzy = build_context(pending, dfs, alias_map)
                response = ask_ai(pending, ctx, st.session_state["ai_messages"])
            if fuzzy:
                st.markdown(
                    f'<div class="ai-hint">💡 Did you mean: {", ".join(fuzzy)}?</div>',
                    unsafe_allow_html=True,
                )
            if players:
                st.markdown(
                    f'<div class="ai-caption">📊 Loaded Data Context For: {", ".join(players)}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown(response)
        st.session_state["ai_messages"].append({"user": pending, "assistant": response})
        st.rerun()

def player_stats():
    apply_styles()

    dfs                       = load_base_data()
    batter_df                 = dfs[0]
    bowler_df                 = dfs[4]
    alias_map, csv_to_display = load_aliases()
    color_map                 = load_team_colors()

    if batter_df.empty and bowler_df.empty:
        st.error("Engine failure: Could not verify or read required base summary CSV outputs.")
        return

    with st.expander("Click here for player stats (Batting and Bowling)", expanded=False):
        bat_col, bowl_col = st.columns(2, gap="large")
        with bat_col:
            bat_display, bat_csv = render_batter_lookup(batter_df, csv_to_display)
        with bowl_col:
            bowl_display, bowl_csv = render_bowler_lookup(bowler_df, csv_to_display)

        if bat_display or bowl_display:
            stat_bat, stat_bowl = st.columns(2, gap="large")
            with stat_bat:
                if bat_display:
                    render_batter_stats(batter_df, bat_display, bat_csv, color_map)
            with stat_bowl:
                if bowl_display:
                    render_bowler_stats(bowler_df, bowl_display, bowl_csv, color_map)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("Click here and ask about a player to our AI Analyst", expanded=False):
        render_ai_chat(dfs, alias_map)


if __name__ == "__main__":
    player_stats()