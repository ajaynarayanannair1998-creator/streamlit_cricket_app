import pandas as pd
import streamlit as st
import numpy as np
import json
import plotly.express as px
from assets.styles import apply_styles, custom_expander1, custom_expander, team_box_html, pill, info_box

TEAM_ALIASES = {
    "Royal Challengers Bangalore": "Royal Challengers Bengaluru",
    "Delhi Daredevils": "Delhi Capitals",
    "Rising Pune Supergiant": "Rising Pune Supergiants",
    "Deccan Chargers": "Sunrisers Hyderabad",
    "Kings XI Punjab": "Punjab Kings",
}

CHART_STYLE = dict(
    paper_bgcolor="black", plot_bgcolor="black", height=500,
    font=dict(color="red"), title_font=dict(size=18, color="red"),
    legend=dict(font=dict(color="white", size=12)),
)

RED_AXIS = dict(title_font=dict(color="red"), tickfont=dict(color="red"), showgrid=False)


def pct(n, total):
    return round(n / total * 100, 2) if total > 0 else 0

def safe_range(df, col, lo=0.5, hi=0.8):
    low, high = df[col].quantile(lo), df[col].quantile(hi)
    return (round(low) if not np.isnan(low) else "-", round(high) if not np.isnan(high) else "-")

def avg_200_per_year(df):
    if df.empty:
        return 0
    return df.groupby("year")[["team1score", "team2score"]].apply(lambda x: (x >= 200).sum().sum()).mean()

def nrmh(v):
    return f"{v}%" if v != 0 else "NRMH"


def stadium_data():
    apply_styles()

    df = pd.read_csv("data/datasets/fixtures.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    df["margin"] = df["team1score"] - df["team2score"]

    stadium_stats = df.groupby("city").agg(
        match_count=("city", "count"), year_count=("year", "nunique")
    ).reset_index()
    valid_stadiums = stadium_stats[
        (stadium_stats["match_count"] >= 5) & (stadium_stats["year_count"] > 1)
    ]["city"].sort_values().tolist()

    selected_stadium = st.selectbox("Select Stadium", ["All stadiums"] + valid_stadiums)
    data = df.copy() if selected_stadium == "All stadiums" else df[df["city"] == selected_stadium].copy()

    if data.empty:
        st.warning("No data available for this stadium")
        st.stop()

    data = data.dropna(subset=["powerplay_score_teama", "powerplay_score_teamb"])
    data["pp_diff"] = data["powerplay_score_teama"] - data["powerplay_score_teamb"]

    total = len(data)
    old_df, new_df = data[data["year"] < 2025], data[data["year"] >= 2025]
    n_new = len(new_df)

    defended_pct   = pct((data["team1"] == data["winner"]).sum(), total)
    chased_pct     = 100 - defended_pct
    toss_field_pct = pct((data["toss_decision"] == "field").sum(), total)
    toss_bat_pct   = 100 - toss_field_pct
    toss_win_pct   = pct((data["toss_winner"] == data["winner"]).sum(), total)
    preferred      = "Field" if toss_field_pct > toss_bat_pct else "Bat"

    avg_1st   = data["team1score"].mean()
    avg_2nd   = data["team2score"].mean()
    median_1st = data["team1score"].median()
    p25, p75  = data["team1score"].quantile(0.25), data["team1score"].quantile(0.75)
    safe_lo, safe_hi = safe_range(data[data["team1"] == data["winner"]], "team1score")

    pp_win_pct = pct(len(data[
        ((data["pp_diff"] > 0) & (data["team1"] == data["winner"])) |
        ((data["pp_diff"] < 0) & (data["team2"] == data["winner"]))
    ]), total)

    pre200 = avg_200_per_year(old_df)

    if n_new > 0:
        recent_defended_pct  = pct((new_df["team1"] == new_df["winner"]).sum(), n_new)
        recent_chased_pct    = 100 - recent_defended_pct
        recent_toss_win_pct  = pct((new_df["toss_winner"] == new_df["winner"]).sum(), n_new)
        post200              = avg_200_per_year(new_df)
        post200pct           = pct(post200, n_new)
        success200           = new_df[(new_df["team1score"] >= 200) & (new_df["team1"] != new_df["winner"])].shape[0]
        avg_1st_recent       = new_df["team1score"].mean()
        recent_safe_lo, recent_safe_hi = safe_range(new_df[new_df["team1"] == new_df["winner"]], "team1score")
        trend_text = "Chasing has become easier in recent years" if recent_chased_pct > chased_pct else "Defending has become stronger recently"
    else:
        recent_defended_pct = recent_chased_pct = recent_toss_win_pct = 0
        post200 = post200pct = success200 = avg_1st_recent = 0
        recent_safe_lo = recent_safe_hi = 0
        trend_text = "No recent data to analyze trend"

    st.title("Stadium Intelligence Dashboard")
    st.markdown("_Recent analysis indicates matches since 2025. NRMH = No Recent Matches Held._")

    c1, c2, c3 = st.columns(3)
    with c1:
        pill("Total Matches", total)
        pill("Typical 1st Inn Score", round(median_1st))
        pill("Typical Score Range", f"{round(p25)}-{round(p75)}")
    with c2:
        pill("Start Year", data.iloc[0]["year"])
        pill("Typical 1st Inn Score (2025+)", round(avg_1st_recent))
        pill("Overall Safe Score", f"{safe_lo}-{safe_hi}")
    with c3:
        pill("Recent Year", data.iloc[-1]["year"])
        pill("2nd Innings Avg", round(avg_2nd) if not np.isnan(avg_2nd) else 0)
        pill("Recent Safe Score (2025+)", f"{recent_safe_lo}-{recent_safe_hi}")

    safe_msg = (f"Safe score is above {safe_hi}" if recent_safe_lo == 0
                else f"Earlier above {safe_hi} was safe; now above {recent_safe_hi} is the benchmark")
    st.write(safe_msg)

    st.markdown("### Toss and Impact")
    c1, c2, c3 = st.columns(3)
    with c1:
        pill("Bat First Decision",        f"{round(toss_bat_pct, 2)}%")
        pill("Defending Win %",           f"{defended_pct}%")
        pill("Recent Defending Win %",    nrmh(round(recent_defended_pct, 2)))
        pill("Avg 200+ Scores (pre-2025)", round(pre200, 2))
    with c2:
        pill("Bowl First Decision",       f"{toss_field_pct}%")
        pill("Chasing Win %",             f"{chased_pct}%")
        pill("Recent Chasing Win %",      nrmh(round(recent_chased_pct, 2)))
        pill("Avg 200+ Scores (2025+)",   round(post200, 2))
    with c3:
        pill("Captain's Preference",      f"{preferred} first")
        pill("Toss Winner Win %",         f"{toss_win_pct}%")
        pill("Recent Toss Winner Win %",  nrmh(round(recent_toss_win_pct, 2)))
        pill("Recent 200+ Chase Wins",    success200)

    if n_new == 0:
        st.markdown("""
            <div style="background-color: #FF4B4B; color: #FFFFFF; 
                        padding: 12px 20px; border-radius: 8px; 
                        font-size: 15px; font-weight: 600; 
                        text-align: center; margin: 10px 0;
                        box-shadow: 0 2px 8px rgba(255,75,75,0.4);">
                Recent t20 data is unavailable so can't comment on recent t20 data.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("## How T20 Has Evolved")

        st.markdown(f"""
            <div style="background-color: #1a1a1a; color: #FFFFFF; 
                        padding: 12px 20px; border-radius: 8px; 
                        font-size: 15px; font-weight: 600; 
                        text-align: center; margin: 10px 0;
                        box-shadow: 0 2px 8px rgba(255,75,75,0.3); border-left: 4px solid #FF4B4B;">
                📊 Recent Avg Score: <span style="color:#FF4B4B">{round(avg_1st_recent)}</span>
                &nbsp;|&nbsp;
                Earlier Avg Score: <span style="color:#aaa">{round(avg_1st)}</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background-color: #1a1a1a; color: #FFFFFF; 
                        padding: 12px 20px; border-radius: 8px; 
                        font-size: 15px; font-weight: 600; 
                        text-align: center; margin: 10px 0;
                        box-shadow: 0 2px 8px rgba(255,75,75,0.3); border-left: 4px solid #FF4B4B;">
                🏆 Modern Safe Score: <span style="color:#FF4B4B">{recent_safe_lo}–{recent_safe_hi}</span>
                &nbsp;|&nbsp;
                Earlier Safe Score: <span style="color:#aaa">{safe_lo}–{safe_hi}</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div style="background-color: #1a1a1a; color: #FFFFFF; 
                        padding: 12px 20px; border-radius: 8px; 
                        font-size: 15px; font-weight: 600; 
                        text-align: center; margin: 10px 0;
                        box-shadow: 0 2px 8px rgba(255,75,75,0.3); border-left: 4px solid #FF4B4B;">
                🏃 Recent Chasing Win %: <span style="color:#FF4B4B">{recent_chased_pct:.1f}%</span>
                &nbsp;|&nbsp;
                {trend_text}
            </div>
        """, unsafe_allow_html=True)

#     st.caption(f"Analysing {total} matches")
    st.caption(f"Analysing {total} matches")

    st.markdown("## Visuals")
    st.markdown('<style>div[data-testid="stRadio"] * { color: white !important; }</style>', unsafe_allow_html=True)

    choice = st.radio("Select mode", ["Overall", "Recent"], horizontal=True)
    view = data if choice == "Overall" else new_df

    if view.empty:
        st.markdown("""
        <div style="background-color: #FF4B4B; color: #FFFFFF; 
                    padding: 12px 20px; border-radius: 8px; 
                    font-size: 15px; font-weight: 600; 
                    text-align: center; margin: 10px 0;
                    box-shadow: 0 2px 8px rgba(255,75,75,0.4);">
            No recent matches held at this venue. Use overall analytics.
        </div>
        """, unsafe_allow_html=True)
        st.write("")
    else:
        n = len(view)
        bins = 5 if n < 20 else (8 if n < 50 else (12 if n < 200 else 20))

        fig_hist = px.histogram(view, x="team1score", nbins=bins, title="1st Innings Score Distribution", opacity=0.85)
        fig_hist.update_traces(marker=dict(color="red", line=dict(color="darkred", width=0.2)))
        fig_hist.update_xaxes(**RED_AXIS)
        fig_hist.update_yaxes(**RED_AXIS)
        fig_hist.update_layout(**CHART_STYLE, bargap=0.01,
                               xaxis=dict(showgrid=False, zeroline=False),
                               yaxis=dict(showgrid=False, zeroline=False))

        view = view.copy()
        view["winner"] = view["winner"].replace(TEAM_ALIASES)
        counts = view["winner"].value_counts().reset_index()
        counts.columns = ["winner", "count"]

        with open("data/colors.json") as f:
            team_colors = json.load(f)
        color_map = {t: v["bg-color"] for t, v in team_colors["team"].items()}

        fig_pie = px.pie(counts, names="winner", values="count", hole=0.3,
                         color="winner", color_discrete_map=color_map)
        fig_pie.update_layout(**CHART_STYLE, title=dict(text="Team Win %", font=dict(color="red", size=18)))

        c1, c2 = st.columns(2)
        c1.plotly_chart(fig_hist, use_container_width=True)
        c2.plotly_chart(fig_pie, use_container_width=True)

    trend_df = data.groupby("year")["team1score"].mean().reset_index()
    fig_line = px.line(trend_df, x="year", y="team1score",
                       labels={"team1score": "Avg Runs", "year": "Year"},
                       title="Average Runs Over the Years")
    fig_line.update_traces(line_color="red")
    fig_line.update_xaxes(**RED_AXIS)
    fig_line.update_yaxes(**RED_AXIS)
    fig_line.update_layout(**CHART_STYLE)
    st.plotly_chart(fig_line, use_container_width=True)