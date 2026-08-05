import streamlit as st
import pandas as pd
from PIL import Image
import base64
import plotly.graph_objects as go
import io
import json
from assets.styles import apply_styles, box_data, custom_expander, custom_expander1, information_box
from src.player_list_and_commentary import team_player_data, dataa, bowler_stats, bowling_summary
from src.phase_chart import show_phase_chart, show_phase_summary, show_phase_section
from src.tab1_loader import load_match_data, get_connection


with open("data/player_aliases.json.txt") as f:
    player_name_aliases = json.load(f)


def convert_image_to_base64(image_path):
    image = Image.open(image_path)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def get_safe_team_color(team_color_hex, fallback_color="#006C67"):
    return fallback_color if team_color_hex == "#050301" else team_color_hex


def get_display_name(raw_player_name):
    return player_name_aliases.get(raw_player_name, [raw_player_name])[0]


def calculate_innings_totals(match_data, innings_index):
    total_runs = 0
    total_legal_deliveries = 0
    retired_hurt_count = 0
    wicket_deliveries = []

    for over in match_data["innings"][innings_index]["overs"]:
        balls_in_over = over["deliveries"]
        total_legal_deliveries += min(len(balls_in_over), 6)
        for delivery in balls_in_over:
            total_runs += delivery["runs"]["total"]
            if "wickets" in delivery:
                dismissal_kind = delivery["wickets"][0]["kind"]
                if dismissal_kind == "retired hurt":
                    retired_hurt_count += 1
                else:
                    wicket_deliveries.append(delivery)

    return total_runs, total_legal_deliveries, wicket_deliveries, retired_hurt_count


def format_deliveries_as_overs(total_legal_deliveries):
    completed_overs, remaining_balls = divmod(total_legal_deliveries, 6)
    return f"{completed_overs} Overs" if remaining_balls == 0 else f"{completed_overs}.{remaining_balls} Overs"


def calculate_run_rate_and_shot_breakdown(match_data, innings_index):
    dot_ball_count = 0
    singles_to_threes_count = 0
    boundary_count = 0
    phase_run_totals = [0, 0, 0]

    for over in match_data["innings"][innings_index]["overs"]:
        over_number = over["over"]
        for delivery in over["deliveries"]:
            total_runs_off_delivery = delivery["runs"]["total"]
            batter_runs_off_delivery = delivery["runs"]["batter"]

            if total_runs_off_delivery == 0:
                dot_ball_count += 1
            if "extras" not in delivery:
                if 1 <= total_runs_off_delivery < 4:
                    singles_to_threes_count += 1
                if batter_runs_off_delivery == total_runs_off_delivery and total_runs_off_delivery in (4, 6):
                    boundary_count += 1

            if over_number <= 5:
                phase_run_totals[0] += total_runs_off_delivery
            elif over_number <= 14:
                phase_run_totals[1] += total_runs_off_delivery
            else:
                phase_run_totals[2] += total_runs_off_delivery

    phase_run_rates = [
        round((phase_run_totals[0] / 36) * 6, 2),
        round((phase_run_totals[1] / 54) * 6, 2),
        round((phase_run_totals[2] / 30) * 6, 2),
    ]
    return phase_run_rates, dot_ball_count, singles_to_threes_count, boundary_count


def get_cumulative_runs_per_over(match_data, innings_index):
    running_total = 0
    cumulative_runs_by_over = []

    for over in match_data["innings"][innings_index]["overs"]:
        for delivery in over["deliveries"]:
            running_total += delivery["runs"]["total"]
        cumulative_runs_by_over.append(running_total)

    over_numbers = list(range(1, len(cumulative_runs_by_over) + 1))
    return cumulative_runs_by_over, over_numbers


def build_gauge_chart(chart_title, percentage_value, team_color, color_palette):
    gauge_figure = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage_value,
        title={"text": chart_title, "font": {"size": 16, "color": color_palette["WHITE"]}},
        number={"font": {"size": 22, "color": team_color}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "white", "tickwidth": 1},
            "bar": {"color": team_color},
            "bgcolor": "black",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40],   "color": "rgba(255,255,255,0.05)"},
                {"range": [40, 70],  "color": "rgba(255,255,255,0.08)"},
                {"range": [70, 100], "color": "rgba(255,255,255,0.12)"},
            ],
        },
    ))
    gauge_figure.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        margin=dict(t=40, b=0, l=0, r=0),
        height=220,
    )
    return gauge_figure


def build_stat_highlight_card(label, stat_value, background_color, text_color):
    return f"""
    <div style="background:{background_color};padding:16px 20px;border-radius:18px;
                margin-bottom:14px;box-shadow:0 6px 18px rgba(0,0,0,0.4);color:{text_color};">
        <div style="font-size:13px;letter-spacing:1px;opacity:0.85;">{label}</div>
        <div style="font-size:20px;font-weight:800;margin-top:6px;">{stat_value}</div>
    </div>"""


def get_batting_highlights_for_team(batting_players):
    display_name = lambda player: get_display_name(player["player_name"])

    top_run_scorer    = sorted(batting_players, key=lambda p: p["score"], reverse=True)[0]
    top_strike_rater  = sorted([p for p in batting_players if p["balls"] >= 5],
                                key=lambda p: p["strike_rate"], reverse=True)[0]
    most_fours_hitter = sorted(batting_players, key=lambda p: p["4s"],  reverse=True)[0]
    most_sixes_hitter = sorted(batting_players, key=lambda p: p["6s"],  reverse=True)[0]

    return (
        f"{display_name(top_run_scorer)} - {top_run_scorer['score']} Runs",
        f"{display_name(top_strike_rater)} - SR {top_strike_rater['strike_rate']}",
        f"{display_name(most_fours_hitter)} - {most_fours_hitter['4s']} fours",
        f"{display_name(most_sixes_hitter)} - {most_sixes_hitter['6s']} sixes",
    )


def get_bowling_highlights_for_team(bowling_players):
    display_name = lambda player: get_display_name(player["player_name"])

    most_economical_bowler = sorted(
        [p for p in bowling_players if int(float(p["overs"])) > 1],
        key=lambda p: p["runs"]
    )[0]
    most_wickets_bowler = sorted(bowling_players, key=lambda p: (-p["wickets"], p["runs"]))[0]

    wickets_highlight = (
        f"{display_name(most_wickets_bowler)} - {most_wickets_bowler['wickets']} Wickets"
        if most_wickets_bowler["wickets"] else ""
    )

    return (
        f"{display_name(most_economical_bowler)} - {most_economical_bowler['runs']} Runs ({most_economical_bowler['overs']} Overs)",
        wickets_highlight,
    )


def run_app():
    if "active_tab" not in st.session_state:
        st.session_state.active_tab = "Creative"

    match_schedule = pd.read_csv("data/datasets/schedule.csv")

    st.markdown(
        "<p style='font-size:15px;font-weight:600;margin-bottom:-20px;'>Select a match to get in depth analysis</p>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.write("")

    available_years = ["All"] + sorted(match_schedule["year"].unique().tolist(), reverse=True)
    year_column, match_column = st.columns([1, 3])

    with year_column:
        st.markdown("")
        selected_year = st.selectbox("Year", available_years)

    year_filtered_schedule = (
        match_schedule if selected_year == "All"
        else match_schedule[match_schedule["year"] == selected_year]
    )

    available_match_names = ["Select match"] + year_filtered_schedule["full_match_name"].unique().tolist()

    with match_column:
        st.markdown("")
        selected_match_name = st.selectbox("Match", available_match_names)

    if selected_match_name == "Select match":
        return

    match_file_number = match_schedule.loc[
    match_schedule["full_match_name"] == selected_match_name, "match_number"
    ].values[0]

    match_id = str(match_file_number).replace(".json", "")
    match_data = load_match_data(match_id)

    if not match_data:
        st.error("Match data not found in database.")
        return
    with open("data/colors.json") as f:
        team_color_config = json.load(f)

    batting_first_team = match_data["innings"][0]["team"]
    team_a, team_b = match_data["info"]["teams"]
    if team_a != batting_first_team:
        team_a, team_b = team_b, team_a

    toss_winning_team = match_data["info"]["toss"].get("winner", "")
    venue_name        = match_data["info"]["venue"]
    match_date        = match_data["info"]["dates"][0]
    match_format      = match_data["info"].get("match_type", "T20")

    event_info = match_data["info"]["event"]
    event_label = (
        f"Match No {event_info['match_number']}, {event_info['name']}"
        if "match_number" in event_info else event_info["name"]
    )

    match_outcome  = match_data["info"].get("outcome", {})
    outcome_result = match_outcome.get("result", "").lower()
    match_abandoned = outcome_result == "no result"

    if match_abandoned:
        _, center_column, _ = st.columns([0.5, 3, 0.5])
        with center_column:
            st.markdown(f"""
                <div style="border:1px solid #ccc;text-align:center;padding:10px;
                            border-radius:8px;background-color:#000000;">
                    Match between {team_a} vs {team_b} — Abandoned / No Result
                </div>""", unsafe_allow_html=True)
        return

    if "winner" in match_outcome:
        match_winner      = match_outcome["winner"]
        winning_margin_by = next(iter(match_outcome["by"]))
        winning_margin    = f"{match_outcome['by'][winning_margin_by]} {winning_margin_by.capitalize()}"
    else:
        match_winner   = match_outcome.get("eliminator", "")
        winning_margin = "Super Over"

    team_a_runs, team_a_deliveries, team_a_wicket_balls, team_a_retired = calculate_innings_totals(match_data, 0)
    team_b_runs, team_b_deliveries, team_b_wicket_balls, team_b_retired = calculate_innings_totals(match_data, 1)

    team_a_total_wickets = (
        (len(team_a_wicket_balls) + team_a_retired)
        if (len(team_a_wicket_balls) + team_a_retired) == 10
        else len(team_a_wicket_balls)
    )
    team_b_total_wickets = (
        (len(team_b_wicket_balls) + team_b_retired)
        if (len(team_b_wicket_balls) + team_b_retired) == 10
        else len(team_b_wicket_balls)
    )

    if "absent_hurt" in match_data["innings"][0]:
        team_a_total_wickets += 1
    if "absent_hurt" in match_data["innings"][1]:
        team_b_total_wickets += 1

    team_a_scorecard_display = f"{team_a_runs}/{team_a_total_wickets}"
    team_b_scorecard_display = f"{team_b_runs}/{team_b_total_wickets}"
    team_a_overs_display     = format_deliveries_as_overs(team_a_deliveries)
    team_b_overs_display     = format_deliveries_as_overs(team_b_deliveries)

    team_colors       = team_color_config["team"]
    team_a_bg_color   = team_colors[team_a]["bg-color"]
    team_a_text_color = team_colors[team_a]["text_color"]
    team_b_bg_color   = team_colors[team_b]["bg-color"]
    team_b_text_color = team_colors[team_b]["text_color"]

    team_a_safe_color = get_safe_team_color(team_a_bg_color)
    team_b_safe_color = get_safe_team_color(team_b_bg_color)

    color_palette = {
        "TEAM_A": team_a_bg_color, "TEAM_B": team_b_bg_color,
        "ACCENT": "#F1C40F", "VENUE": "#2ECC71",
        "BG1": "#5F0A87", "BG2": "#A4508B", "BG3": "#FEC260",
        "WHITE": "#FFFFFF", "BLACK": "#000000", "NAVY": "#FFBF00",
        "CHART_TITLE": "#FFD700", "X_AXIS": "#FF4C4C",
        "Y_AXIS": "#39FF14", "AXIS_TITLE": "#00FFFF",
        "BUTTON_RED": "#FF0000", "EVENT_BG1": "#111111",
        "EVENT_BG2": "#333333", "FORMAT_BG": "#192841",
    }

    team_a_logo_base64 = convert_image_to_base64("assets/team1_side_ball.jpg")
    team_b_logo_base64 = convert_image_to_base64("assets/team2_side_ball.jfif")

    st.markdown("""
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;800;900&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital@1&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

    box_data(
        color_palette, match_date, team_a, team_b,
        team_a_scorecard_display, team_b_scorecard_display,
        team_a_overs_display, team_b_overs_display,
        team_a_logo_base64, team_b_logo_base64,
        team_a_bg_color, team_b_bg_color,
        team_a_text_color, team_b_text_color,
        event_label,
    )

    player_of_match_name = match_data["info"]["player_of_match"][0]
    winner_bg_color   = team_a_bg_color   if match_winner == team_a else team_b_bg_color
    winner_text_color = team_a_text_color if match_winner == team_a else team_b_text_color

    player_of_match_in_team_a = player_of_match_name in match_data["info"]["players"][team_a]
    pom_bg_color   = team_a_bg_color   if player_of_match_in_team_a else team_b_bg_color
    pom_text_color = team_a_text_color if player_of_match_in_team_a else team_b_text_color

    st.markdown("")
    st.markdown(f"""
    <div class="result-row">
        <div class="result-left">
            <div class="result-pill" style="background:{winner_bg_color};color:{winner_text_color}">
                {match_winner} won by {winning_margin}
            </div>
        </div>
        <div style="width:140px;"></div>
        <div class="pom-right">
            <div class="pom-pill" style="background:{pom_bg_color};color:{pom_text_color}">
                Player of the Match: {get_display_name(player_of_match_name)}
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    toss_winner_bg_color   = team_a_bg_color   if toss_winning_team == team_a else team_b_bg_color
    toss_winner_text_color = team_a_text_color if toss_winning_team == team_a else team_b_text_color

    st.markdown("<div style='height:25px'></div>", unsafe_allow_html=True)

    venue_info_box = information_box("Venue", venue_name, "", "", "grass-box")
    toss_info_box  = information_box("Toss Winner", f"{toss_winning_team} won the toss",
                                     toss_winner_bg_color, toss_winner_text_color)

    left_info_box, right_info_box = (
        (toss_info_box, venue_info_box) if toss_winning_team == team_a
        else (venue_info_box, toss_info_box)
    )

    st.markdown(f"""
    <div class="toss-venue-container">
        <div style="flex:1;">{left_info_box}</div>
        <div class="format-box" style="background:#F1C40F;color:#000000;">
            <div class="small-text" style="color:#000000;">Type</div>
            <div class="big-text" style="color:#000000;">{match_format}</div>
        </div>
        <div style="flex:1;">{right_info_box}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(
        "<h3 style='text-align:center;'>Batting Scorecard (Click on player for detailed summary)</h3>",
        unsafe_allow_html=True,
    )

    def build_batting_lineup_with_absent(innings_index, final_score_display):
        batting_lineup = team_player_data(match_data, innings_index)
        if "absent_hurt" in match_data["innings"][innings_index]:
            absent_player_name = match_data["innings"][innings_index]["absent_hurt"][0]
            batting_lineup.append({
                "player_name": absent_player_name,
                "score": 0, "4s": 0, "6s": 0, "balls": 0,
                "strike_rate": 0.0, "FOW": final_score_display,
                "status": False, "wicket_type": "absent_hurt",
                "fielder": "NA", "Bowler": "NA",
            })
        return batting_lineup

    team_a_batting_lineup = build_batting_lineup_with_absent(0, team_a_scorecard_display)
    team_b_batting_lineup = build_batting_lineup_with_absent(1, team_b_scorecard_display)
    team_a_bowling_figures = bowler_stats(match_data, 1)
    team_b_bowling_figures = bowler_stats(match_data, 0)

    def render_batting_scorecard(batting_lineup, team_bg_color, team_txt_color):
        for player in batting_lineup:
            player_display_name  = get_display_name(player["player_name"])
            fielder_display_name = get_display_name(player["fielder"])
            bowler_display_name  = get_display_name(player["Bowler"])
            score_with_not_out   = f"{player['score']}*" if player["status"] else str(player["score"])

            st.markdown(
                custom_expander(
                    f"{player_display_name} — {score_with_not_out}",
                    dataa(
                        player_display_name, player["score"], player["balls"],
                        player["strike_rate"], player["4s"], player["6s"],
                        player["FOW"], player["wicket_type"],
                        fielder_display_name, bowler_display_name,
                    ),
                    team_bg_color, team_txt_color,
                ),
                unsafe_allow_html=True,
            )

    def render_bowling_scorecard(bowling_figures, team_bg_color, team_txt_color):
        for bowler in bowling_figures:
            bowler_display_name = get_display_name(bowler["player_name"])
            st.markdown(
                custom_expander1(
                    f"{bowler_display_name} — {bowler['wickets']} / {bowler['runs']}",
                    bowling_summary(
                        bowler["wickets"], bowler["economy"], bowler_display_name,
                        bowler["overs"], maidens=bowler["maidens"],
                        multi_wicket_overs=bowler["multi_wicket_overs"],
                    ),
                    team_bg_color, team_txt_color,
                ),
                unsafe_allow_html=True,
            )

    batting_col_a, batting_col_b = st.columns(2)
    with batting_col_a:
        render_batting_scorecard(team_a_batting_lineup, team_a_bg_color, team_a_text_color)
    with batting_col_b:
        render_batting_scorecard(team_b_batting_lineup, team_b_bg_color, team_b_text_color)

    st.markdown(
        "<h3 style='text-align:center;'>Bowling Scorecard (Click on player for detailed summary)</h3>",
        unsafe_allow_html=True,
    )
    bowling_col_a, bowling_col_b = st.columns(2)
    with bowling_col_a:
        render_bowling_scorecard(team_a_bowling_figures, team_a_bg_color, team_a_text_color)
    with bowling_col_b:
        render_bowling_scorecard(team_b_bowling_figures, team_b_bg_color, team_b_text_color)

    st.markdown("")
    if "show_details" not in st.session_state:
        st.session_state.show_details = False

    _, center_col, _ = st.columns([0.1, 4, 0.1])
    with center_col:
        st.markdown("""
            <style>
                div[data-testid="stButton"] button { width: 100%; }
            </style>
        """, unsafe_allow_html=True)
        if st.button("Click here for analysis", key="stadium_anas_btn", use_container_width=True):
            st.session_state.open_pill = not st.session_state.open_pill

    if not st.session_state.get("open_pill"):
        return

    st.markdown(
        "<h3 style='text-align:center;'>Run Progression</h3>",
        unsafe_allow_html=True,
    )

    team_a_over_cumulative_runs, team_a_over_numbers = get_cumulative_runs_per_over(match_data, 0)
    team_b_over_cumulative_runs, team_b_over_numbers = get_cumulative_runs_per_over(match_data, 1)

    def build_milestone_marker_trace(over_numbers, cumulative_runs, team_color):
        milestone_overs = list(range(5, max(over_numbers), 5))
        return go.Scatter(
            x=milestone_overs,
            y=[cumulative_runs[over - 1] for over in milestone_overs],
            mode="markers+text",
            text=[cumulative_runs[over - 1] for over in milestone_overs],
            textposition="top center",
            marker=dict(size=9, color=team_color),
            showlegend=False,
        )

    run_progression_figure = go.Figure([
        go.Scatter(
            x=team_a_over_numbers, y=team_a_over_cumulative_runs,
            mode="lines+markers", name=team_a,
            line=dict(color=team_a_safe_color, width=3, shape="spline"),
            marker=dict(size=6),
        ),
        go.Scatter(
            x=team_b_over_numbers, y=team_b_over_cumulative_runs,
            mode="lines+markers", name=team_b,
            line=dict(color=team_b_safe_color, width=3, shape="spline"),
            marker=dict(size=6),
        ),
        build_milestone_marker_trace(team_a_over_numbers, team_a_over_cumulative_runs, team_a_bg_color),
        build_milestone_marker_trace(team_b_over_numbers, team_b_over_cumulative_runs, team_b_bg_color),
    ])
    run_progression_figure.update_layout(
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(family="Poppins", color="white"),
        title=dict(
            text="Score Progression",
            x=0.5, xanchor="center",
            y=0.95, yanchor="top",
            font=dict(size=24, color=color_palette["CHART_TITLE"]),
        ),
        margin=dict(t=80),
        xaxis=dict(
            title=dict(text="Overs", font=dict(size=16, color=color_palette["AXIS_TITLE"])),
            tickfont=dict(size=14, color=color_palette["X_AXIS"]),
            showgrid=False, zeroline=False, showline=False, ticks="outside",
        ),
        yaxis=dict(
            title=dict(text="Runs", font=dict(size=16, color=color_palette["AXIS_TITLE"])),
            tickfont=dict(size=14, color=color_palette["Y_AXIS"]),
            showgrid=False, zeroline=False, showline=False, ticks="outside",
        ),
        legend=dict(
            font=dict(size=14, color=color_palette["CHART_TITLE"]),
            orientation="h", y=1.02, x=0.5, xanchor="center",
        ),
    )

    team_a_phase_run_rates, team_a_dot_balls, team_a_singles_to_threes, team_a_boundaries = calculate_run_rate_and_shot_breakdown(match_data, 0)
    team_b_phase_run_rates, team_b_dot_balls, team_b_singles_to_threes, team_b_boundaries = calculate_run_rate_and_shot_breakdown(match_data, 1)

    def as_percentage_of_total(count, total_deliveries):
        return round((count / total_deliveries) * 100)

    team_a_dot_ball_pct  = as_percentage_of_total(team_a_dot_balls,          team_a_deliveries)
    team_a_rotation_pct  = as_percentage_of_total(team_a_singles_to_threes,  team_a_deliveries)
    team_a_boundary_pct  = as_percentage_of_total(team_a_boundaries,         team_a_deliveries)

    team_b_dot_ball_pct  = as_percentage_of_total(team_b_dot_balls,          team_b_deliveries)
    team_b_rotation_pct  = as_percentage_of_total(team_b_singles_to_threes,  team_b_deliveries)
    team_b_boundary_pct  = as_percentage_of_total(team_b_boundaries,         team_b_deliveries)

    show_phase_section(match_data, st, run_progression_figure, team_a_bg_color, team_b_bg_color, color_palette)

    st.markdown(
        "<h2 style='text-align:center;'>Team Wise Analytics</h2>",
        unsafe_allow_html=True,
    )

    analytics_col_a, analytics_col_b = st.columns(2)
    with analytics_col_a:
        st.markdown(f"<h3 style='text-align:center;'>{team_a}</h3>", unsafe_allow_html=True)
        gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
        with gauge_col1:
            st.plotly_chart(
                build_gauge_chart("Dot Ball %", team_a_dot_ball_pct, team_a_safe_color, color_palette),
                use_container_width=True, config={"displayModeBar": False},
            )
        with gauge_col2:
            st.plotly_chart(
                build_gauge_chart("1-2-3 %", team_a_rotation_pct, team_a_safe_color, color_palette),
                use_container_width=True, config={"displayModeBar": False},
            )
        with gauge_col3:
            st.plotly_chart(
                build_gauge_chart("Boundary %", team_a_boundary_pct, team_a_safe_color, color_palette),
                use_container_width=True, config={"displayModeBar": False},
            )

    with analytics_col_b:
        st.markdown(f"<h3 style='text-align:center;'>{team_b}</h3>", unsafe_allow_html=True)
        gauge_col1, gauge_col2, gauge_col3 = st.columns(3)
        with gauge_col1:
            st.plotly_chart(
                build_gauge_chart("Dot Ball %", team_b_dot_ball_pct, team_b_safe_color, color_palette),
                use_container_width=True, config={"displayModeBar": False},
            )
        with gauge_col2:
            st.plotly_chart(
                build_gauge_chart("1-2-3 %", team_b_rotation_pct, team_b_safe_color, color_palette),
                use_container_width=True, config={"displayModeBar": False},
            )
        with gauge_col3:
            st.plotly_chart(
                build_gauge_chart("Boundary %", team_b_boundary_pct, team_b_safe_color, color_palette),
                use_container_width=True, config={"displayModeBar": False},
            )

    st.markdown(
        "<h2 style='text-align:center;'>Key Team Highlights</h2>",
        unsafe_allow_html=True,
    )

    highlight_labels = [
        "Most Runs", "Best Strike Rate", "Most 4s", "Most 6s",
        "Best Economical Bowler", "Most Wickets",
    ]

    highlights_col_a, highlights_col_b = st.columns(2)
    with highlights_col_a:
        st.markdown(f"<h3 style='text-align:center;'>{team_a}</h3>", unsafe_allow_html=True)
        team_a_all_highlights = (
            get_batting_highlights_for_team(team_a_batting_lineup)
            + get_bowling_highlights_for_team(team_a_bowling_figures)
        )
        for label, highlight_value in zip(highlight_labels, team_a_all_highlights):
            st.markdown(
                build_stat_highlight_card(label, highlight_value, team_a_bg_color, team_a_text_color),
                unsafe_allow_html=True,
            )

    with highlights_col_b:
        st.markdown(f"<h3 style='text-align:center;'>{team_b}</h3>", unsafe_allow_html=True)
        team_b_all_highlights = (
            get_batting_highlights_for_team(team_b_batting_lineup)
            + get_bowling_highlights_for_team(team_b_bowling_figures)
        )
        for label, highlight_value in zip(highlight_labels, team_b_all_highlights):
            st.markdown(
                build_stat_highlight_card(label, highlight_value, team_b_bg_color, team_b_text_color),
                unsafe_allow_html=True,
            )