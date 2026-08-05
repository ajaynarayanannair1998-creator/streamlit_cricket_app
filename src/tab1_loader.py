import sqlite3
import streamlit as st
import pandas as pd
import numpy as np

DB_PATH = "src/cricket.db"  

@st.cache_resource
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row   
    return conn


@st.cache_data
def load_match_data(match_id: str) -> dict:
    conn = get_connection()

    match_row = conn.execute(
        "SELECT * FROM matches WHERE match_id = ?", (match_id,)
    ).fetchone()

    if not match_row:
        return {}

    m = dict(match_row)

    squad_rows = conn.execute(
        "SELECT team, player FROM squads WHERE match_id = ?", (match_id,)
    ).fetchall()

    players_dict = {}
    for row in squad_rows:
        players_dict.setdefault(row["team"], []).append(row["player"])

    delivery_rows = conn.execute("""
        SELECT * FROM deliveries
        WHERE match_id = ?
        ORDER BY inning, over, ball
    """, (match_id,)).fetchall()


    info = {
        "dates":           [m["date"]],
        "season":          m["season"],
        "venue":           m["venue"],
        "teams":           [m["team1"], m["team2"]],
        "toss":            {"winner": m["toss_winner"], "decision": m["toss_decision"]},
        "outcome":         _build_outcome(m),
        "player_of_match": m["player_of_match"].split(", ") if m["player_of_match"] else [],
        "event":           {"name": m["event_name"], "stage": m["event_stage"]},
        "match_type":      m["match_type"],
        "players":         players_dict,   
    }


    innings_dict = {}
    for row in delivery_rows:
        d = dict(row)
        inning_num   = d["inning"]
        over_num     = d["over"]
        batting_team = d["batting_team"]

        if inning_num not in innings_dict:
            innings_dict[inning_num] = {
                "team":  batting_team,
                "overs": {}
            }

        if over_num not in innings_dict[inning_num]["overs"]:
            innings_dict[inning_num]["overs"][over_num] = []

        innings_dict[inning_num]["overs"][over_num].append(_build_delivery(d))


    innings_list = []
    for inning_num in sorted(innings_dict.keys()):
        inning_data  = innings_dict[inning_num]
        overs_list   = []
        for over_num in sorted(inning_data["overs"].keys()):
            overs_list.append({
                "over":       over_num,
                "deliveries": inning_data["overs"][over_num]
            })
        innings_list.append({
            "team":  inning_data["team"],
            "overs": overs_list,
        })

    return {
        "info":    info,
        "innings": innings_list,
    }


def _build_outcome(m: dict) -> dict:
    outcome = {}
    if m["winner"]:
        outcome["winner"] = m["winner"]
        if m["win_by_runs"]:
            outcome["by"] = {"runs": m["win_by_runs"]}
        elif m["win_by_wickets"]:
            outcome["by"] = {"wickets": m["win_by_wickets"]}
    else:
        outcome["result"] = "no result"
    return outcome


def _build_delivery(d: dict) -> dict:
    delivery = {
        "batter":      d["batter"],
        "non_striker": d["non_striker"],
        "bowler":      d["bowler"],
        "runs": {
            "batter": d["runs_batter"],
            "extras": d["runs_extras"],
            "total":  d["runs_total"],
        },
    }

    extras_map = {
        "wide":   "wides",
        "noball": "noballs",
        "bye":    "byes",
        "legbye": "legbyes",
    }
    if d["extras_type"] and d["extras_type"] in extras_map:
        delivery["extras"] = {extras_map[d["extras_type"]]: d["runs_extras"]}

    if d["wicket_player_out"]:
        wicket = {
            "player_out": d["wicket_player_out"],
            "kind":       d["wicket_kind"],
        }
        if d["wicket_fielder"]:
            wicket["fielders"] = [{"name": d["wicket_fielder"]}]
        delivery["wickets"] = [wicket]

    return delivery



@st.cache_data
def get_batter_scorecard(match_id: str):
    conn = get_connection()
    query = """
        SELECT
            inning,
            batting_team,
            batter,
            SUM(runs_batter)                              AS runs,
            SUM(CASE WHEN is_wide = 0 THEN 1 ELSE 0 END) AS balls,
            SUM(is_boundary)                              AS fours,
            SUM(is_six)                                   AS sixes,
            MAX(CASE WHEN wicket_player_out = batter THEN wicket_kind ELSE '' END) AS dismissal,
            CASE WHEN MAX(wicket_player_out = batter) THEN 0 ELSE 1 END AS not_out
        FROM deliveries
        WHERE match_id = ?
        GROUP BY inning, batter
        ORDER BY inning, runs DESC
    """
    import pandas as pd
    df = pd.read_sql_query(query, conn, params=(match_id,))
    df["strike_rate"] = (df["runs"] / df["balls"].replace(0, float("nan")) * 100).round(2)
    return df


@st.cache_data
def get_bowler_scorecard(match_id: str):
    conn = get_connection()
    query = """
        SELECT
            inning,
            bowling_team,
            bowler,
            COUNT(CASE WHEN is_wide = 0 AND is_noball = 0 THEN 1 END) AS balls,
            SUM(runs_total)                            AS runs_conceded,
            COUNT(CASE WHEN wicket_player_out != ''
                       AND wicket_kind NOT IN ('run out','retired hurt','obstructing the field')
                  THEN 1 END)                          AS wickets,
            SUM(is_wide)                               AS wides,
            SUM(is_noball)                             AS noballs
        FROM deliveries
        WHERE match_id = ?
        GROUP BY inning, bowler
        ORDER BY inning, wickets DESC
    """
    
    df = pd.read_sql_query(query, conn, params=(match_id,))
    df["overs"]   = (df["balls"] // 6).astype(str) + "." + (df["balls"] % 6).astype(str)
    df["economy"] = (df["runs_conceded"] / (df["balls"] / 6).replace(0, float("nan"))).round(2)
    return df


@st.cache_data
def get_over_by_over(match_id: str):
    conn = get_connection()
    query = """
        SELECT
            inning,
            batting_team,
            over,
            SUM(runs_total)  AS runs,
            SUM(CASE WHEN wicket_player_out != '' THEN 1 ELSE 0 END) AS wickets
        FROM deliveries
        WHERE match_id = ?
        GROUP BY inning, over
        ORDER BY inning, over
    """
    df = pd.read_sql_query(query, conn, params=(match_id,))
    df["cumulative_runs"] = df.groupby("inning")["runs"].cumsum()
    return df


@st.cache_data
def get_match_info(match_id: str) -> dict:
    conn = get_connection()
    row  = conn.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,)).fetchone()
    return dict(row) if row else {}