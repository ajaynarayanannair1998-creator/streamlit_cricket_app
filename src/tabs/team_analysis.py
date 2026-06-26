import json
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd
import re
import numpy as np


def render_comparison_row(bg_left, txt_left, left_content, bg_right, txt_right, right_content, center_label, border_radius="0px"):
    html = f"""
    <div style="display:flex; width:100%; border-radius:{border_radius};
                position:relative; height:46px;
                font-family:'Poppins',sans-serif; font-weight:700;">
        <div style="flex:1; background:{bg_left}; color:{txt_left};
                    display:flex; align-items:center; padding:0 85px 0 22px;
                    font-size:15px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
                    border-radius:{border_radius} 0 0 {border_radius};">
            {left_content}
        </div>
        <div style="flex:1; background:{bg_right}; color:{txt_right};
                    display:flex; align-items:center; justify-content:flex-end;
                    padding:0 22px 0 85px; font-size:15px;
                    white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
                    border-radius:0 {border_radius} {border_radius} 0;">
            {right_content}
        </div>
        <div style="position:absolute; top:0; bottom:0; left:50%; transform:translateX(-50%);
                    width:200px; background:#FFFFFF; color:#007BFF;
                    font-size:13px; font-family:'Comic Sans MS', cursive; font-weight:1000;
                    letter-spacing:1.5px; border-radius:0;
                    display:flex; align-items:center; justify-content:center;
                    z-index:10;">
            {center_label}
        </div>
    </div>
    """
    return re.sub(r'\s+', ' ', html).strip()


def teams_analysis():
    st.markdown("""
    <style>
    
    </style>
    """, unsafe_allow_html=True)
    col1,col2=st.columns([0.8,2.2])
    with col1:
        view_mode = st.radio(
            "Select Analytics Mode",
            options=["Team Analysis", "Team Comparison"],
            horizontal=True,
            label_visibility="collapsed"
        )

    with open('data/ipl_franchise_perfect_analytics.json') as json_data:
        match_data = json.load(json_data)

    with open("data/colors.json") as f:
        team_color = json.load(f)

    team_map = match_data.get('team', {})
    team_names = list(team_map.keys())

    if not team_names:
        st.warning("No team data discovered in the database file.")
        return

    tc = team_color.get("team", {})

    if view_mode == "Team Analysis":
        team_selection = st.selectbox("Select Team", team_names, label_visibility="collapsed")

        COLOR_A = tc.get(team_selection, {}).get("bg-color", "#006C67")
        a_txt = tc.get(team_selection, {}).get("text_color", "#FFFFFF")

        def stat_card(title, value, bg_color, text_color):
            return f"""
            <div style="background:{bg_color}; padding:16px 20px; border-radius:18px;
                        margin-bottom:14px; box-shadow:0 4px 12px rgba(0,0,0,0.15); color:{text_color};">
                <div style="font-size:12px; font-family:'Poppins'; letter-spacing:0.5px; opacity:0.8; text-transform: uppercase;">{title}</div>
                <div style="font-size:20px; font-family:'Poppins'; font-weight:800; margin-top:4px;">{value}</div>
            </div>"""

        selected_team_data = team_map[team_selection]
        overall = selected_team_data.get('overall', {})

        st.markdown("### Team Overview")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(stat_card('Total Matches', overall.get('total_matches', 0), COLOR_A, a_txt), unsafe_allow_html=True)
        with col2:
            st.markdown(stat_card('Total Wins', overall.get('total_wins', 0), COLOR_A, a_txt), unsafe_allow_html=True)
        with col3:
            st.markdown(stat_card('Win Percentage', f"{overall.get('win_%', 0.0)}%", COLOR_A, a_txt), unsafe_allow_html=True)

        col4, col5, col6 = st.columns(3)
        with col4:
            bs_display = str(overall.get('best_season', 'N/A'))
            st.markdown(stat_card('Best Season (Year)', bs_display, COLOR_A, a_txt), unsafe_allow_html=True)
        with col5:
            st.markdown(stat_card('Most Runs Leader', str(overall.get('most_runs_player', 'N/A')), COLOR_A, a_txt), unsafe_allow_html=True)
        with col6:
            st.markdown(stat_card('Most Wickets Leader', str(overall.get('most_wickets_player', 'N/A')), COLOR_A, a_txt), unsafe_allow_html=True)

        col7, col8 = st.columns([1, 2])
        with col7:
            st.markdown(stat_card('Highest Inning Total', overall.get('best_team_score', 'N/A'), COLOR_A, a_txt), unsafe_allow_html=True)
        with col8:
            champs = overall.get('champions', [])
            champs_display = ", ".join(map(str, champs)) if champs else "None"
            st.markdown(stat_card('Championship Years', champs_display, COLOR_A, a_txt), unsafe_allow_html=True)

        season_wise = selected_team_data.get('season_wise', [])

        if season_wise:
            st.write("")
            st.markdown("### Year-on-Year Win Trajectory")

            sorted_seasons = sorted(season_wise, key=lambda x: int(x.get('year', 0)))
            years = [int(item.get('year')) for item in sorted_seasons]
            win_percentages = [item.get('win%', 0.0) for item in sorted_seasons]
            hover_text = [f"Wins: {item.get('wins', 0)}/{item.get('matches', 0)}<br>Finish Stage: {item.get('result', 'N/A')}" for item in sorted_seasons]

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=years, y=win_percentages, mode='lines+markers', name='Win %',
                line=dict(color=a_txt, width=3),
                marker=dict(size=8, color=a_txt, line=dict(color=COLOR_A, width=1.5)),
                text=hover_text,
                hovertemplate="<b>Year %{x}</b><br>Win Rate: %{y}%<br>%{text}<extra></extra>"
            ))

            fig.update_layout(
                plot_bgcolor=COLOR_A, paper_bgcolor=COLOR_A, font=dict(family="Poppins", color=a_txt),
                margin=dict(t=20, b=40, l=15, r=15), height=350,
                xaxis=dict(tickmode='linear', tick0=min(years) if years else 0, dtick=1, showgrid=False, tickfont=dict(color=a_txt)),
                yaxis=dict(title=dict(text="Win Percentage (%)", font=dict(size=12, color=a_txt)), showgrid=False, tickfont=dict(color=a_txt)),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No historical season data available to render timeline profiles.")

    elif view_mode == "Team Comparison":
        st.markdown("### Head-to-Head Comparison")

        TEAM_NAME_MAPPING = {
            "deccan chargers": "Sunrisers Hyderabad",
            "delhi daredevils": "Delhi Capitals",
            "royal challengers bangalore": "Royal Challengers Bengaluru",
            "kings xi punjab": "Punjab Kings",
            "rising pune supergiants": "Rising Pune Supergiant",
        }

        REVERSE_NAME_MAPPING = {v: k.title() for k, v in TEAM_NAME_MAPPING.items()}

        def get_former_name(team_name):
            return REVERSE_NAME_MAPPING.get(team_name, team_name)

        @st.cache_data
        def load_teams_from_schedule():
            try:
                df = pd.read_csv("data/datasets/fixtures.csv")
                df["team1"] = df["team1"].astype(str).str.strip()
                df["team2"] = df["team2"].astype(str).str.strip()

                all_teams = pd.concat([df["team1"], df["team2"]])
                all_teams = all_teams[~all_teams.isin(["", "Nan", "None", "N/A", "Na"])]
                all_teams = all_teams.dropna()

                seen = {}
                for name in all_teams:
                    mapped = TEAM_NAME_MAPPING.get(name.lower().strip(), name.strip())
                    key = mapped.lower()
                    if key not in seen:
                        seen[key] = mapped

                return sorted(seen.values())

            except FileNotFoundError:
                st.error("fixtures.csv not found.")
                return []

        @st.cache_data
        def get_team_year_range(team_name):
            try:
                df = pd.read_csv("data/datasets/fixtures.csv")
                df["team1"] = df["team1"].astype(str).str.strip()
                df["team2"] = df["team2"].astype(str).str.strip()
                df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

                df["team1_mapped"] = df["team1"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["team2_mapped"] = df["team2"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))

                mask = (df["team1_mapped"].str.lower() == team_name.lower()) | \
                       (df["team2_mapped"].str.lower() == team_name.lower())
                filtered = df[mask].dropna(subset=["date"])

                if filtered.empty:
                    return "N/A"

                start_year = int(filtered["date"].min().year)
                end_year = int(filtered["date"].max().year)
                current_year = datetime.now().year

                if start_year == end_year:
                    return str(start_year)
                elif end_year >= current_year:
                    return f"{start_year}–Present"
                else:
                    return f"{start_year}–{end_year}"

            except Exception as e:
                return f"ERR: {e}"

        @st.cache_data
        def get_total_matches(team_name):
            try:
                df = pd.read_csv("data/datasets/fixtures.csv")
                df["team1"] = df["team1"].astype(str).str.strip()
                df["team2"] = df["team2"].astype(str).str.strip()

                df["team1_mapped"] = df["team1"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["team2_mapped"] = df["team2"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))

                mask = (df["team1_mapped"].str.lower() == team_name.lower()) | \
                       (df["team2_mapped"].str.lower() == team_name.lower())

                return str(df[mask].shape[0])

            except Exception as e:
                return f"ERR: {e}"

        team_names = load_teams_from_schedule()

        comp_col1, vs_spacer, comp_col2 = st.columns([2, 1, 2])
        with comp_col1:
            team_left = st.selectbox("Select Team A", team_names, index=0, key="team_left")
        with comp_col2:
            team_right = st.selectbox("Select Team B", team_names, index=min(1, len(team_names)-1), key="team_right")

        bg_left = tc.get(team_left, {}).get("bg-color", "#006C67")
        txt_left = tc.get(team_left, {}).get("text_color", "#FFFFFF")
        bg_right = tc.get(team_right, {}).get("bg-color", "#1D2A44")
        txt_right = tc.get(team_right, {}).get("text_color", "#FFFFFF")

        year_left = get_team_year_range(team_left)
        year_right = get_team_year_range(team_right)

        former_left = get_former_name(team_left)
        former_right = get_former_name(team_right)

        matches_left = get_total_matches(team_left)
        matches_right = get_total_matches(team_right)
        df = pd.read_csv("data/datasets/fixtures.csv")

        @st.cache_data
        def get_final_record(team_name,df):
            try:
#                 df = pd.read_csv("fixtures.csv")
                df["team1"] = df["team1"].astype(str).str.strip()
                df["team2"] = df["team2"].astype(str).str.strip()
                df["winner"] = df["winner"].astype(str).str.strip()
                df["group"] = df["group"].astype(str).str.strip()

                df["team1_mapped"] = df["team1"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["team2_mapped"] = df["team2"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["winner_mapped"] = df["winner"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))

                finals = df[df["group"].str.lower() == "final"]

                mask = (finals["team1_mapped"].str.lower() == team_name.lower()) | \
                       (finals["team2_mapped"].str.lower() == team_name.lower())
                team_finals = finals[mask]

                champions = team_finals[team_finals["winner_mapped"].str.lower() == team_name.lower()].shape[0]
                runner_up = team_finals[team_finals["winner_mapped"].str.lower() != team_name.lower()].shape[0]

                return str(champions), str(runner_up)

            except Exception as e:
                return "ERR", "ERR"

        if team_left == team_right:
            st.markdown("""
                <div style="background-color: #FF4B4B; color: #FFFFFF;
                            padding: 12px 20px; border-radius: 8px;
                            font-size: 15px; font-weight: 600;
                            text-align: center; margin: 10px 0;
                            box-shadow: 0 2px 8px rgba(255,75,75,0.4);">
                    Please select two different teams to compare.
                </div>
            """, unsafe_allow_html=True)
            st.stop()

        vs_html = render_comparison_row(
            bg_left, txt_left, team_left,
            bg_right, txt_right, team_right,
            "VS", border_radius="25px"
        )
        since_html = render_comparison_row(
            bg_left, txt_left, year_left,
            bg_right, txt_right, year_right,
            "Started", border_radius="25px"
        )
        former_html = render_comparison_row(
            bg_left, txt_left, former_left,
            bg_right, txt_right, former_right,
            "Formerly", border_radius="25px"
        )
        matches_html = render_comparison_row(
            bg_left, txt_left, matches_left,
            bg_right, txt_right, matches_right,
            "Matches", border_radius="25px"
        )

        @st.cache_data
        def get_win_percentage(team_name):
            try:
                df = pd.read_csv("data/datasets/fixtures.csv")
                df["winner"] = df["winner"].astype(str).str.strip()
                df["team1"] = df["team1"].astype(str).str.strip()
                df["team2"] = df["team2"].astype(str).str.strip()

                df["team1_mapped"] = df["team1"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["team2_mapped"] = df["team2"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["winner_mapped"] = df["winner"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))

                mask = (df["team1_mapped"].str.lower() == team_name.lower()) | \
                       (df["team2_mapped"].str.lower() == team_name.lower())
                total = df[mask].shape[0]

                if total == 0:
                    return "N/A"

                wins = df[mask & (df["winner_mapped"].str.lower() == team_name.lower())].shape[0]
                pct = (wins / total) * 100
                return f"{pct:.1f}%"

            except Exception as e:
                return f"ERR: {e}"

        @st.cache_data
        def get_playoff_chances(team_name):
            try:
                

                df = pd.read_csv("data/datasets/fixtures.csv")

                df["team1"] = df["team1"].astype(str).str.strip()
                df["team2"] = df["team2"].astype(str).str.strip()
                df["winner"] = df["winner"].astype(str).str.strip()
                df["group"] = df["group"].astype(str).str.strip()

                df["date"] = pd.to_datetime(df["date"], errors="coerce")
                df["year"] = df["date"].dt.year

                df["team1_mapped"] = df["team1"].apply(
                    lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip())
                )
                df["team2_mapped"] = df["team2"].apply(
                    lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip())
                )
                df["winner_mapped"] = df["winner"].apply(
                    lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip())
                )

                latest_year = int(df["year"].max())
                seasons = [latest_year, latest_year - 1, latest_year - 2]

                recent_df = df[df["year"].isin(seasons)]

                active_teams = set(recent_df["team1_mapped"]).union(
                    set(recent_df["team2_mapped"])
                )

                if team_name not in active_teams:
                    return "N/A"

                weights = {
                    latest_year: 0.60,
                    latest_year - 1: 0.30,
                    latest_year - 2: 0.10
                }

                ratings = {}

                for team in active_teams:
                    total_score = 0

                    for season in seasons:
                        season_df = recent_df[recent_df["year"] == season]

                        team_matches = season_df[
                            (season_df["team1_mapped"] == team) |
                            (season_df["team2_mapped"] == team)
                        ]

                        if team_matches.empty:
                            continue

                        w = weights[season]
                        matches = len(team_matches)
                        wins = len(team_matches[team_matches["winner_mapped"] == team])
                        win_rate = wins / matches if matches > 0 else 0

                        q1 = season_df[season_df["group"].str.lower().eq("qualifier 1")]
                        elim = season_df[season_df["group"].str.lower().eq("eliminator")]

                        playoff_teams = set(
                            pd.concat([
                                q1["team1_mapped"],
                                q1["team2_mapped"],
                                elim["team1_mapped"],
                                elim["team2_mapped"]
                            ]).dropna()
                        )

                        made_playoff = int(team in playoff_teams)

                        finals = season_df[season_df["group"].str.lower().eq("final")]

                        made_final = int(
                            (finals["team1_mapped"] == team).any() or
                            (finals["team2_mapped"] == team).any()
                        )

                        won_title = int((finals["winner_mapped"] == team).any())

                        season_score = (
                            win_rate * 70 +
                            made_playoff * 15 +
                            made_final * 10 +
                            won_title * 5
                        )

                        total_score += season_score * w

                    ratings[team] = total_score

                scores = pd.Series(ratings)

                if scores.max() == scores.min():
                    return "40%"

                normalized = (scores - scores.min()) / (scores.max() - scores.min())
                probabilities = 25 + (normalized * 55)

                return f"{round(probabilities[team_name])}%"

            except Exception as e:
                return "N/A"

        playoff_left = get_playoff_chances(team_left)
        playoff_right = get_playoff_chances(team_right)

        playoff_html = render_comparison_row(
            bg_left, txt_left, playoff_left,
            bg_right, txt_right, playoff_right,
            "2027 Playoff Chances", border_radius="25px"
        )

        winpct_left = get_win_percentage(team_left)
        winpct_right = get_win_percentage(team_right)

        winpct_html = render_comparison_row(
            bg_left, txt_left, winpct_left,
            bg_right, txt_right, winpct_right,
            "Win %", border_radius="25px"
        )

        champ_left, runnerup_left = get_final_record(team_left,df)
        champ_right, runnerup_right = get_final_record(team_right,df)

        champ_html = render_comparison_row(
            bg_left, txt_left, champ_left,
            bg_right, txt_right, champ_right,
            "Titles", border_radius="25px"
        )
        runnerup_html = render_comparison_row(
            bg_left, txt_left, runnerup_left,
            bg_right, txt_right, runnerup_right,
            "Runner Up", border_radius="25px"
        )

        st.markdown(
            '<div style="margin:20px 0;display:flex;flex-direction:column;gap:0.8px;">'
            + vs_html
            + since_html
            + former_html
            + matches_html
            + winpct_html
            + champ_html
            + runnerup_html
            + playoff_html
            + '</div>',
            unsafe_allow_html=True
        )

        @st.cache_data
        def get_head_to_head(team1, team2):
            try:
                df = pd.read_csv("data/datasets/fixtures.csv")
                df["team1"] = df["team1"].astype(str).str.strip()
                df["team2"] = df["team2"].astype(str).str.strip()
                df["winner"] = df["winner"].astype(str).str.strip()

                df["team1_mapped"] = df["team1"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["team2_mapped"] = df["team2"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["winner_mapped"] = df["winner"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))

                mask = (
                    (df["team1_mapped"].str.lower() == team1.lower()) & (df["team2_mapped"].str.lower() == team2.lower())
                ) | (
                    (df["team1_mapped"].str.lower() == team2.lower()) & (df["team2_mapped"].str.lower() == team1.lower())
                )

                h2h_df = df[mask]
                total = str(h2h_df.shape[0])
                team1_wins = str(h2h_df[h2h_df["winner_mapped"].str.lower() == team1.lower()].shape[0])
                team2_wins = str(h2h_df[h2h_df["winner_mapped"].str.lower() == team2.lower()].shape[0])

                return total, team1_wins, team2_wins

            except Exception as e:
                return "ERR", "ERR", "ERR"

        @st.cache_data
        def get_h2h_details(team1, team2, df):
            try:
                df["team1"] = df["team1"].astype(str).str.strip()
                df["team2"] = df["team2"].astype(str).str.strip()
                df["winner"] = df["winner"].astype(str).str.strip()
                df["group"] = df["group"].astype(str).str.strip()
                df["date"] = pd.to_datetime(df["date"], errors="coerce")

                df["team1_mapped"] = df["team1"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["team2_mapped"] = df["team2"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))
                df["winner_mapped"] = df["winner"].apply(lambda x: TEAM_NAME_MAPPING.get(x.lower().strip(), x.strip()))

                mask = (
                    (df["team1_mapped"].str.lower() == team1.lower()) & (df["team2_mapped"].str.lower() == team2.lower())
                ) | (
                    (df["team1_mapped"].str.lower() == team2.lower()) & (df["team2_mapped"].str.lower() == team1.lower())
                )
                h2h_df = df[mask].copy()

                last3 = h2h_df.sort_values("date", ascending=False).head(3)

                finals = h2h_df[h2h_df["group"].str.lower() == "final"]

                knockout_keywords = ["qualifier", "eliminator", "semi final", "q1", "q2", "q3", "q4"]
                knockouts = h2h_df[
                    h2h_df["group"].str.lower().apply(
                        lambda x: any(k in x for k in knockout_keywords)
                    )
                ]

                return last3, finals, knockouts

            except Exception as e:
                return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        def get_wl_list(df, team_name):
            results = []
            for _, row in df.sort_values("date", ascending=False).iterrows():
                if row["winner_mapped"].lower() == team_name.lower():
                    results.append("W")
                elif row["winner_mapped"].lower() in ["no result", "abandoned", "tie", "unknown"]:
                    results.append("NR")
                else:
                    results.append("L")
            return results

        def render_wl_pill(results_list, bg_color, txt_color):
            pills = ""
            for r in results_list:
                if r == "W":
                    pills += f'<span style="background:rgba(0,200,100,0.25);color:#00C864;border:1px solid #00C864;padding:3px 10px;border-radius:20px;font-weight:700;font-size:13px;margin:2px;">{r}</span>'
                elif r == "NR":
                    pills += f'<span style="background:rgba(200,200,200,0.25);color:#AAAAAA;border:1px solid #AAAAAA;padding:3px 10px;border-radius:20px;font-weight:700;font-size:13px;margin:2px;">{r}</span>'
                else:
                    pills += f'<span style="background:rgba(255,75,75,0.25);color:#FF4B4B;border:1px solid #FF4B4B;padding:3px 10px;border-radius:20px;font-weight:700;font-size:13px;margin:2px;">{r}</span>'
            return f'<div style="display:flex;gap:4px;justify-content:center;align-items:center;flex-wrap:wrap;">{pills}</div>'

        h2h_total, h2h_wins_left, h2h_wins_right = get_head_to_head(team_left, team_right)
        last3, finals_df, knockouts_df = get_h2h_details(team_left, team_right, df)

        wl_last3_left = get_wl_list(last3, team_left)
        wl_last3_right = get_wl_list(last3, team_right)
        wl_final_left = get_wl_list(finals_df, team_left)
        wl_final_right = get_wl_list(finals_df, team_right)
        wl_ko_left = get_wl_list(knockouts_df, team_left)
        wl_ko_right = get_wl_list(knockouts_df, team_right)

        h2h_total_html = render_comparison_row(
            bg_left, txt_left, h2h_total,
            bg_right, txt_right, h2h_total,
            "Matches", border_radius="25px"
        )
        h2h_wins_html = render_comparison_row(
            bg_left, txt_left, h2h_wins_left,
            bg_right, txt_right, h2h_wins_right,
            "Wins", border_radius="25px"
        )
        last3_html = render_comparison_row(
            bg_left, txt_left, render_wl_pill(wl_last3_left, bg_left, txt_left),
            bg_right, txt_right, render_wl_pill(wl_last3_right, bg_right, txt_right),
            "Last 3", border_radius="25px"
        )
        final_html = render_comparison_row(
            bg_left, txt_left, render_wl_pill(wl_final_left, bg_left, txt_left) if not finals_df.empty else "Yet to meet",
            bg_right, txt_right, render_wl_pill(wl_final_right, bg_right, txt_right) if not finals_df.empty else "Yet to meet",
            "Final", border_radius="25px"
        )
        ko_html = render_comparison_row(
            bg_left, txt_left, render_wl_pill(wl_ko_left, bg_left, txt_left) if not knockouts_df.empty else "Yet to meet",
            bg_right, txt_right, render_wl_pill(wl_ko_right, bg_right, txt_right) if not knockouts_df.empty else "Yet to meet",
            "Knockouts", border_radius="25px"
        )

        st.markdown("### Head to Head")
        st.markdown(
            '<div style="margin:20px 0;display:flex;flex-direction:column;gap:0.8px;">'
            + h2h_total_html
            + h2h_wins_html
            + last3_html
            + final_html
            + ko_html
            + '</div>',
            unsafe_allow_html=True
        )