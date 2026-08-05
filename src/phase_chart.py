import plotly.graph_objects as go
import json

PHASES = [
    {"label": "Powerplay",    "name": "pp",    "start": 0,  "end": 5},
    {"label": "Middle Overs", "name": "mid",   "start": 6,  "end": 14},
    {"label": "Death Overs",  "name": "death", "start": 15, "end": 19},
]
with open("data/player_aliases.json.txt") as f:
    player_name_aliases = json.load(f)

def resolve_color(color, fallback="#006C67"):
    return fallback if color == "#050301" else color

def clean_layout(title, COLORS):
    return dict(
        plot_bgcolor="black", paper_bgcolor="black",
        font=dict(family="Poppins", color="white"),
        title=dict(text=title, x=0.5, xanchor="center", y=0.95, yanchor="top", font=dict(size=20, color=COLORS["CHART_TITLE"])),
        margin=dict(t=70, b=100, l=20, r=30), height=400, barmode="group",
        hovermode="closest",
        xaxis=dict(
            title=dict(text="Run Rate", font=dict(size=14, color=COLORS["AXIS_TITLE"])),
            tickfont=dict(size=12, color=COLORS["X_AXIS"]),
            showgrid=False, zeroline=False, showline=False, ticks="",
            showspikes=False,
        ),
        yaxis=dict(
            tickfont=dict(size=13, color=COLORS["Y_AXIS"]),
            showgrid=False, zeroline=False, showline=False, ticks="",
            autorange="reversed",
            showspikes=False,
        ),
        legend=dict(font=dict(size=12, color=COLORS["CHART_TITLE"]), orientation="h", y=-0.22, x=0.5, xanchor="center"),
    )

def get_batting_teams(match_data):
    info = match_data.get("info", {})
    fallback = info.get("teams", ["Team A", "Team B"])
    innings = match_data.get("innings", [])
    bat1 = innings[0].get("team", fallback[0]) if len(innings) > 0 else fallback[0]
    bat2 = innings[1].get("team", fallback[1]) if len(innings) > 1 else fallback[1]
    return bat1, bat2


def get_match_overs(match_data):
    return match_data.get("info", {}).get("overs", 20)


def format_overs_and_balls(overs_count):
    if isinstance(overs_count, int) or overs_count.is_integer():
        return f"{int(overs_count)}.0"
    completed_overs = int(overs_count)
    fractional_part = round(overs_count - completed_overs, 2)
    balls = round(fractional_part * 6)
    if balls >= 6:
        completed_overs += 1
        balls = 0
    return f"{completed_overs}.{balls}"

def get_phase_stats(overs_data, match_overs=20):
    if not overs_data:
        return {
            phase["name"]: {
                "runs": 0, "wickets": 0, "rr": 0.0,
                "was_played": False, "ended_here": False, "final_stamp": "0"
            } for phase in PHASES
        }
    stats = {}
    last_over_obj = overs_data[-1]
    final_stamp = f"{last_over_obj['over_num'] + 1}"
    for phase in PHASES:
        effective_phase_end = min(phase["end"], match_overs - 1)
        phase_overs = [
            o for o in overs_data
            if phase["start"] <= o["over_num"] <= effective_phase_end
        ]
        was_played = len(phase_overs) > 0
        if was_played:
            runs = sum(o["over_runs"] for o in phase_overs)
            wickets = sum(o["wicket_count"] for o in phase_overs)
            overs_count = len(phase_overs)
            is_termination_phase = (phase["start"] <= last_over_obj["over_num"] <= effective_phase_end)
            stats[phase["name"]] = {
                "runs": runs,
                "wickets": wickets,
                "rr": round(runs / overs_count, 2) if overs_count > 0 else 0.0,
                "was_played": True,
                "ended_here": is_termination_phase,
                "final_stamp": final_stamp
            }
        else:
            stats[phase["name"]] = {
                "runs": 0, "wickets": 0, "rr": 0.0,
                "was_played": False, "ended_here": False, "final_stamp": final_stamp
            }
    return stats

def get_peak_cumulative_rr(overs_data):
    if not overs_data: return None
    return max(overs_data, key=lambda o: o["cumulative_rr"])

def get_highest_scoring_overs(overs_data, top_n=2):
    if not overs_data: return []
    return sorted(overs_data, key=lambda o: o["over_runs"], reverse=True)[:top_n]

def get_sudden_changes(overs_data, threshold=4):
    return [
        {
            "type": "spike" if overs_data[i]["over_runs"] - overs_data[i-1]["over_runs"] > 0 else "drop",
            "diff": overs_data[i]["over_runs"] - overs_data[i-1]["over_runs"],
            "over": overs_data[i]["over_label"],
            "runs": overs_data[i]["runs"] if "runs" in overs_data[i] else overs_data[i]["over_runs"],
        }
        for i in range(1, len(overs_data))
        if abs(overs_data[i]["over_runs"] - overs_data[i-1]["over_runs"]) >= threshold
    ]

def analyze_downfall_overs(overs_data):
    if not overs_data: return {}
    collapse_over = None
    for o in reversed(overs_data):
        if o["wicket_count"] > 1:
            collapse_over = o
            break
    valid_low_overs = [o for o in overs_data if o["over_num"] > 0 or o["over_runs"] == 0]
    slowest_over = min(valid_low_overs, key=lambda o: o["over_runs"]) if valid_low_overs else overs_data[0]
    econ_over = min(overs_data, key=lambda o: o["over_runs"])
    return {"collapse": collapse_over, "slowest": slowest_over, "economical": econ_over}

def build_team1_chart(overs_data, team_name, COLOR_A, COLORS, match_overs=20):
    color = resolve_color(COLOR_A)
    phase_stats = get_phase_stats(overs_data, match_overs)
    phase_labels = [p["label"] for p in PHASES]
    rr_vals = [phase_stats[p["name"]]["rr"] for p in PHASES]
    w_vals  = [phase_stats[p["name"]]["wickets"] for p in PHASES]
    r_vals  = [phase_stats[p["name"]]["runs"] for p in PHASES]
    bar_text = [f"RR: {rr}  |  W: {w}  |  {r} runs" for rr, w, r in zip(rr_vals, w_vals, r_vals)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=phase_labels, x=rr_vals, orientation="h", name=team_name, marker_color=color,
        text=bar_text, textposition="inside", insidetextanchor="middle",
        textfont=dict(size=12, color="white", family="Poppins"),
        hovertemplate="<b>%{y}</b><br>RR: %{x}<extra></extra>",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode="markers",
        name=team_name,
        marker=dict(color=color, size=12, symbol="square"),
        showlegend=True,
    ))
    fig.update_layout(**clean_layout(f"{team_name} — Phase Run Rate", COLORS))
    return fig

def build_team2_chart(overs_data, bat1_name, bat2_name, target, COLOR_A, COLOR_B, COLORS, match_overs=20):
    color2, color1 = resolve_color(COLOR_B), resolve_color(COLOR_A)
    phase_stats = get_phase_stats(overs_data, match_overs)

    TOTAL_CHASE_OVERS = match_overs

    cumulative_by_over = {o["over_num"]: o["cumulative_runs"] for o in overs_data}

    def runs_scored_before_phase(phase_start):
        if phase_start == 0:
            return 0
        prev_over = phase_start - 1
        while prev_over >= 0:
            if prev_over in cumulative_by_over:
                return cumulative_by_over[prev_over]
            prev_over -= 1
        return 0

    phase_labels = [p["label"] for p in PHASES]
    rr_vals = [phase_stats[p["name"]]["rr"] for p in PHASES]
    w_vals  = [phase_stats[p["name"]]["wickets"] for p in PHASES]
    r_vals  = [phase_stats[p["name"]]["runs"] for p in PHASES]
    played_phases = [p for p in PHASES if phase_stats[p["name"]]["was_played"]]

    bar_text = []
    for i, phase in enumerate(PHASES):
        rr = rr_vals[i]
        w  = w_vals[i]
        r  = r_vals[i]
        s  = phase_stats[phase["name"]]

        if not s["was_played"]:
            bar_text.append("")
            continue

        runs_before = runs_scored_before_phase(phase["start"])
        runs_needed_at_phase_start = target - runs_before

        overs_remaining_at_phase_start = TOTAL_CHASE_OVERS - phase["start"]
        rrr_at_phase_start = (
            round(runs_needed_at_phase_start / overs_remaining_at_phase_start, 2)
            if overs_remaining_at_phase_start > 0 else 0
        )

        is_last_played_phase = (phase["name"] == played_phases[-1]["name"])

        if is_last_played_phase:
            runs_still_needed = max(runs_needed_at_phase_start, 0)
            label = f"Need {runs_still_needed} runs  |  CRR: {rr}  |  W: {w}  |  {r} scored"
        else:
            phase_actual_end = min(phase["end"], TOTAL_CHASE_OVERS - 1)
            phase_over_count = max(phase_actual_end - phase["start"] + 1, 1)
            expected = round(rrr_at_phase_start * phase_over_count)
            label = f"RRR pace {expected} runs.  |  CRR: {rr}  |  W: {w}  |  {r} scored"

        bar_text.append(label)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=phase_labels, x=rr_vals, orientation="h",
        name=f"{bat2_name} (CRR)", marker_color=color2,
        text=bar_text, textposition="inside", insidetextanchor="middle",
        textfont=dict(size=12, color="white", family="Poppins"),
        hovertemplate="<b>%{y}</b><br>CRR: %{x}<extra></extra>",
        showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        name=f"{bat2_name} (CRR)",
        marker=dict(color=color2, size=12, symbol="square"),
        showlegend=True,
    ))

    fig.add_annotation(
        text="* 'At least X exp.' = Required Run Rate at phase start × phase overs remaining",
        xref="paper", x=0.5, xanchor="center",
        yref="y",    y=-0.5, yanchor="middle",
        showarrow=False,
        font=dict(size=10, color="rgba(255,255,255,0.45)", family="Poppins"),
        align="center",
    )

    fig.update_layout(**clean_layout(f"{bat2_name} — Phase CRR vs RRR", COLORS))
    return fig

def render_aligned_metrics(st, phase_stats_t1, phase_stats_t2, bat1, bat2, match_data):
    st.markdown("### Inning Progression by Phase")

    phase_mapping = [
        {"name": "pp",    "label": "Powerplay (Overs 1-6)"},
        {"name": "mid",   "label": "Middle Overs (Overs 7-15)"},
        {"name": "death", "label": "Death Overs (Overs 16-20)"}
    ]

    match_info = match_data.get("info", {}) if match_data else {}
    winner = match_info.get("outcome", {}).get("winner", None)

    clean_winner = str(winner).strip().lower() if winner else ""
    clean_bat2   = str(bat2).strip().lower()

    total_wkts_t1 = sum(phase_stats_t1[p["name"]].get("wickets", 0) for p in phase_mapping if p["name"] in phase_stats_t1)
    total_wkts_t2 = sum(phase_stats_t2[p["name"]].get("wickets", 0) for p in phase_mapping if p["name"] in phase_stats_t2) if phase_stats_t2 else 0

    for p in phase_mapping:
        s1 = phase_stats_t1.get(p["name"], {})
        s2 = phase_stats_t2.get(p["name"], {}) if phase_stats_t2 else None

        if s1.get("was_played") or (s2 and s2.get("was_played")):
            with st.container(border=True):
                st.markdown(f"#### {p['label']}")

                if s1.get("was_played"):
                    t1_status = ""
                    if s1.get("ended_here"):
                        t1_status = " (All Out)" if int(total_wkts_t1) >= 10 else f" (Innings Closed at {s1['final_stamp']} Ov)"
                    st.markdown(
                        f"**{bat1}** &nbsp;&nbsp;•&nbsp;&nbsp; "
                        f"`{s1['rr']} RPO` &nbsp;&nbsp;•&nbsp;&nbsp; "
                        f"**{s1['runs']}** runs &nbsp;&nbsp;•&nbsp;&nbsp; "
                        f"**{s1['wickets']}** W{t1_status}"
                    )

                if s1.get("was_played") and s2 and s2.get("was_played"):
                    st.markdown("<div style='margin: 4px 0; border-top: 1px dashed rgba(255,255,255,0.1);'></div>", unsafe_allow_html=True)

                if s2 and s2.get("was_played"):
                    t2_status = ""
                    if s2.get("ended_here"):
                        if int(total_wkts_t2) >= 10:
                            t2_status = " (All Out)"
                        elif clean_winner == clean_bat2:
                            t2_status = f" (Target Chased in {s2['final_stamp']} Ov)"
                        else:
                            t2_status = f" (Innings Stopped at {s2['final_stamp']} Ov)"
                    st.markdown(
                        f"**{bat2}** &nbsp;&nbsp;•&nbsp;&nbsp; "
                        f"`{s2['rr']} RPO` &nbsp;&nbsp;•&nbsp;&nbsp; "
                        f"**{s2['runs']}** runs &nbsp;&nbsp;•&nbsp;&nbsp; "
                        f"**{s2['wickets']}** W{t2_status}"
                    )


def render_dynamic_match_story(st, overs1, overs2, bat1, bat2, winner, outcome):
    result_type = outcome.get("result", "").lower()
    if result_type == "tie":
        st.warning("Match Tied! Scores were level at the end of the regular innings. Deep narrative summary is skipped for tied outcomes.")
        return

    team1_total = overs1[-1]["cumulative_runs"] if overs1 else 0
    initial_rrr = round(team1_total / 20, 2)

    total_wkts_t2 = overs2[-1]["wicket_count"] if overs2 else 0
    final_over_t2 = overs2[-1]["over_num"] if overs2 else 0

    if winner == bat1:
        winning_team, losing_team = bat1, bat2
        winning_overs, losing_overs = overs1, overs2
        team1_lost = False
        loser_phrase = "Run Chase"
    else:
        winning_team, losing_team = bat2, bat1
        winning_overs, losing_overs = overs2, overs1
        team1_lost = True
        loser_phrase = "First Innings"

    header_col1, header_col2 = st.columns(2)
    with header_col1:
        st.markdown(f"<div style='margin:0; padding:0; font-size:15px; font-weight:bold; font-family:Poppins;'>Winning Momentum: {winning_team}</div>", unsafe_allow_html=True)
    with header_col2:
        st.markdown(f"<div style='margin:0; padding:0; font-size:15px; font-weight:bold; font-family:Poppins;'>Pressure Points: {losing_team}</div>", unsafe_allow_html=True)

    body_col1, body_col2 = st.columns(2)

    with body_col1:
        peak_moment = get_peak_cumulative_rr(winning_overs)
        top_overs = get_highest_scoring_overs(winning_overs, top_n=2)
        changes_win = get_sudden_changes(winning_overs)

        st.write("#### **Where They Capitalized & Accelerated:**")
        if peak_moment:
            st.write(f"Peak Momentum Point: At **{peak_moment['over_label']}**, they achieved their highest cumulative run-rate of **{peak_moment['cumulative_rr']} RPO** ({peak_moment['cumulative_runs']} runs on the board).")

        if top_overs:
            st.write("Highest Scoring Inning Explosions:")
            for o in top_overs:
                st.write(f"• **{o['over_label']}** yielded **{o['over_runs']} runs** (Bowled by *{player_name_aliases.get(o['bowler'], o['bowler'])[0]}*)")

    with body_col2:
        if losing_overs:
            downfall = analyze_downfall_overs(losing_overs)
            changes_lose = get_sudden_changes(losing_overs)

            st.write(f"#### **{loser_phrase} Turning Points & Stall Out Factors:**")

            if downfall.get("collapse"):
                dc = downfall["collapse"]
                st.write(f"Wicket Damage Over: Momentum completely broke during **{dc['over_label']}**, dropping **{dc['wicket_count']} critical wickets**. Damage inflicted by **{player_name_aliases.get(dc['bowler'], dc['bowler'])[0]}**.")

            if downfall.get("slowest"):
                ds = downfall["slowest"]
                st.write(f"Stagnant Run-Rate Trap: Dot balls built heavy pressure during **{ds['over_label']}**, where they were strangled to just **{ds['over_runs']} runs**.")

            if downfall.get("economical"):
                de = downfall["economical"]
                dc = downfall.get("collapse") or {}
                if de['over_num'] != downfall.get("slowest", {}).get("over_num"):
                    bowler_key = dc.get("bowler", de.get("bowler", ""))
                    st.write(f"Defensive Containment: Tight bowling during **{de['over_label']}** yielded only **{de['over_runs']} runs**, locked down by **{player_name_aliases.get(bowler_key, bowler_key)[0] if bowler_key else 'Unknown'}**.")

            if team1_total < 100:
                if not team1_lost and (total_wkts_t2 >= 8 or final_over_t2 >= 18):
                    st.write(f"Low Score Scare: Even though they defended a minor sub-100 score, they triggered panic in the chase; stalling the opponent until **Over {final_over_t2 + 1}** or picking up **{total_wkts_t2} wickets** before letting it slip.")
            else:
                if team1_lost:
                    for o in overs1:
                        if 5 <= o["over_num"] <= 17:
                            projected_total = o["cumulative_rr"] * 20
                            if projected_total >= (team1_total + 20):
                                st.write(f"Pacing Deficit Factor: During **{o['over_label']}** their trajectory pointed towards a total of **{int(projected_total)} runs**. Slowing down late cost them at least **{int(projected_total - team1_total)} extra runs**.")
                                break
                else:
                    chase_failure_flag = False
                    for o in overs2:
                        if 5 <= o["over_num"] <= 17:
                            overs_left = 20 - (o["over_num"] + 1)
                            runs_needed = (team1_total + 1) - o["cumulative_runs"]
                            if overs_left > 0:
                                current_rrr = runs_needed / overs_left
                                if (initial_rrr - current_rrr) >= 2.0:
                                    st.write(f"Uncapitalized Advantage: They put themselves into a commanding position by dropping the required run rate from an initial **{initial_rrr}** down to **{round(current_rrr, 2)} RPO** around **{o['over_label']}**, but failed to anchor the finish.")
                                    chase_failure_flag = True
                                    break

                    if not chase_failure_flag and overs1:
                        for o in overs1:
                            if 5 <= o["over_num"] <= 14:
                                mid_projection = o["cumulative_rr"] * 20
                                if (team1_total - mid_projection) >= 20:
                                    st.write(f"Opponent Growth Impact: They allowed the game to slide late; opponent was restricted to a lower scoring projection at **{o['over_label']}**, but added an extra **{int(team1_total - mid_projection)} runs** in a late-innings surge.")
                                    break
        else:
            st.info("No data available to track losing performance details.")

    swings_col1, swings_col2 = st.columns(2)

    with swings_col1:
        if winning_overs and changes_win:
            st.caption("NOTABLE INNINGS SWINGS")
            for c in changes_win[:3]:
                st.write(f"**{c['over']}** — Variation of {c['diff']} runs ({c['runs']} runs scored)")

    with swings_col2:
        if losing_overs and changes_lose:
            st.caption("NOTABLE INNINGS SWINGS")
            for c in changes_lose[:3]:
                st.write(f"**{c['over']}** — Variation of {c['diff']} runs ({c['runs']} runs scored)")


def _extract_overs_context(match_data):
    def extract_inning(inn_idx):
        try: inning = match_data["innings"][inn_idx]
        except IndexError: return []
        overs_data, cumulative_runs = [], 0
        for over_obj in inning.get("overs", []):
            over_num = over_obj.get("over", 0)
            over_runs, wickets = 0, []
            deliveries = over_obj.get("deliveries", [])
            bowler_name = deliveries[0].get("bowler", "Unknown Bowler") if deliveries else "Unknown Bowler"

            for delivery in deliveries:
                over_runs += delivery.get("runs", {}).get("total", 0)
                for w in delivery.get("wickets", []):
                    if w.get("kind") != "retired hurt":
                        wickets.append(w.get("player_out", ""))
            cumulative_runs += over_runs
            overs_data.append({
                "over_num": over_num,
                "over_label": f"Over {over_num + 1}",
                "over_runs": over_runs,
                "bowler": bowler_name,
                "cumulative_runs": cumulative_runs,
                "cumulative_rr": round(cumulative_runs / (over_num + 1), 2),
                "wicket_count": len(wickets),
                "wicket_players": ", ".join(wickets),
            })
        return overs_data

    overs1 = extract_inning(0)
    overs2 = extract_inning(1)
    target = 1
    if overs1: target = overs1[-1]["cumulative_runs"] + 1
    return overs1, overs2, target


def show_phase_chart(match_data, st, prog_fig, COLOR_A, COLOR_B, COLORS):
    bat1, bat2 = get_batting_teams(match_data)
    overs1, overs2, target = _extract_overs_context(match_data)
    match_overs = get_match_overs(match_data)

    prog_fig.update_layout(height=475)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(prog_fig, use_container_width=True, config={"displayModeBar": False})
    with col2:
        tab1, tab2 = st.tabs([bat1, bat2])
        with tab1:
            if overs1:
                st.plotly_chart(
                    build_team1_chart(overs1, bat1, COLOR_A, COLORS, match_overs),
                    use_container_width=True, config={"displayModeBar": False}
                )
        with tab2:
            if overs2:
                st.plotly_chart(
                    build_team2_chart(overs2, bat1, bat2, target, COLOR_A, COLOR_B, COLORS, match_overs),
                    use_container_width=True, config={"displayModeBar": False}
                )

def show_phase_summary(match_data, st, COLOR_A, COLOR_B):
    bat1, bat2 = get_batting_teams(match_data)
    info = match_data.get("info", {})
    winner = info.get("outcome", {}).get("winner", "")
    outcome = info.get("outcome", {})
    overs1, overs2, target = _extract_overs_context(match_data)
    match_overs = get_match_overs(match_data)
    phase_stats_t1 = get_phase_stats(overs1, match_overs)
    phase_stats_t2 = get_phase_stats(overs2, match_overs) if overs2 else None

    st.write("")

    with st.popover("Click here to view side-by-side match summary report", use_container_width=True):
        st.markdown(f"## **{bat1} vs {bat2}** — Comparative Phase Summary")
        st.write("---")

        if phase_stats_t1:
            render_aligned_metrics(st, phase_stats_t1, phase_stats_t2, bat1, bat2, match_data)

        st.write("---")

        if overs1:
            render_dynamic_match_story(st, overs1, overs2, bat1, bat2, winner, outcome)

def show_phase_section(match_data, st, prog_fig, COLOR_A, COLOR_B, COLORS):
    show_phase_chart(match_data, st, prog_fig, COLOR_A, COLOR_B, COLORS)
    show_phase_summary(match_data, st, COLOR_A, COLOR_B)