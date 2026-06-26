import os
import json
import sqlite3
from pathlib import Path

FOLDER  = r"IPL"
DB_PATH = "cricket.db"


conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

cur.executescript("""
    CREATE TABLE IF NOT EXISTS matches (
        match_id            TEXT PRIMARY KEY,
        date                TEXT,
        season              TEXT,
        venue               TEXT,
        team1               TEXT,
        team2               TEXT,
        toss_winner         TEXT,
        toss_decision       TEXT,
        winner              TEXT,
        win_by_runs         INTEGER,
        win_by_wickets      INTEGER,
        player_of_match     TEXT,
        event_name          TEXT,
        event_stage         TEXT,
        is_knockout         INTEGER,
        match_type          TEXT
    );

    CREATE TABLE IF NOT EXISTS deliveries (
        id                  INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id            TEXT,
        inning              INTEGER,
        batting_team        TEXT,
        bowling_team        TEXT,
        over                INTEGER,
        ball                INTEGER,
        batter              TEXT,
        non_striker         TEXT,
        bowler              TEXT,
        runs_batter         INTEGER,
        runs_extras         INTEGER,
        runs_total          INTEGER,
        extras_type         TEXT,
        is_wide             INTEGER,
        is_noball           INTEGER,
        is_boundary         INTEGER,
        is_six              INTEGER,
        wicket_player_out   TEXT,
        wicket_kind         TEXT,
        wicket_fielder      TEXT,
        FOREIGN KEY (match_id) REFERENCES matches(match_id)
    );

    CREATE TABLE IF NOT EXISTS squads (
        match_id    TEXT,
        team        TEXT,
        player      TEXT,
        FOREIGN KEY (match_id) REFERENCES matches(match_id)
    );

    CREATE INDEX IF NOT EXISTS idx_deliveries_match  ON deliveries(match_id);
    CREATE INDEX IF NOT EXISTS idx_deliveries_batter ON deliveries(batter);
    CREATE INDEX IF NOT EXISTS idx_deliveries_bowler ON deliveries(bowler);
    CREATE INDEX IF NOT EXISTS idx_squads_match      ON squads(match_id);
""")
conn.commit()



all_files = list(Path(FOLDER).glob("*.json"))


existing_ids = set(
    row[0] for row in cur.execute("SELECT match_id FROM matches").fetchall()
)

new_files = [fp for fp in all_files if fp.stem not in existing_ids]

print(f"Total files    : {len(all_files)}")
print(f"Already in DB  : {len(existing_ids)}")
print(f"New to process : {len(new_files)}")

if not new_files:
    print("\n DB is already up to date — nothing to add!")
    conn.close()
    exit()

print(f"\nProcessing {len(new_files)} new files …")



skipped  = []
inserted = 0

for fp in new_files:
    match_id = fp.stem

    try:
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)

        info   = data.get("info", {})
        teams  = info.get("teams", [])
        dates  = info.get("dates", [""])
        event  = info.get("event", {})

      
        event_name  = event.get("name",  "") if isinstance(event, dict) else str(event)
        event_stage = event.get("stage", "") if isinstance(event, dict) else ""
        is_knockout = int(any(k in event_stage.lower()
                              for k in ["final", "semi", "playoff", "eliminator", "qualifier"]))

        outcome  = info.get("outcome", {})
        winner   = outcome.get("winner", "")
        by       = outcome.get("by", {})
        win_runs = by.get("runs",    None)
        win_wkts = by.get("wickets", None)
        toss     = info.get("toss", {})
        pom_list = info.get("player_of_match", [])
        pom      = ", ".join(pom_list) if isinstance(pom_list, list) else str(pom_list)

        cur.execute("""
            INSERT OR IGNORE INTO matches VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            match_id,
            dates[0] if dates else "",
            str(info.get("season", "")),
            info.get("venue", ""),
            teams[0] if len(teams) > 0 else "",
            teams[1] if len(teams) > 1 else "",
            toss.get("winner", ""),
            toss.get("decision", ""),
            winner,
            win_runs,
            win_wkts,
            pom,
            event_name,
            event_stage,
            is_knockout,
            info.get("match_type", "T20"),
        ))

        
        squad_rows = []
        for team, players in info.get("players", {}).items():
            for player in players:
                squad_rows.append((match_id, team, player))

        cur.executemany("""
            INSERT INTO squads (match_id, team, player) VALUES (?,?,?)
        """, squad_rows)

        
        rows = []
        for inning_idx, inning in enumerate(data.get("innings", []), start=1):
            batting_team = inning.get("team", "")
            bowling_team = next((t for t in teams if t != batting_team), "")

            for over_obj in inning.get("overs", []):
                over_num = over_obj.get("over", 0)

                for ball_idx, delivery in enumerate(over_obj.get("deliveries", [])):
                    runs    = delivery.get("runs", {})
                    extras  = delivery.get("extras", {})
                    wickets = delivery.get("wickets", [])

                    if   "wides"   in extras: extras_type = "wide"
                    elif "noballs" in extras: extras_type = "noball"
                    elif "byes"    in extras: extras_type = "bye"
                    elif "legbyes" in extras: extras_type = "legbye"
                    else:                     extras_type = ""

                    w_out = w_kind = w_fielder = ""
                    if wickets:
                        w         = wickets[0]
                        w_out     = w.get("player_out", "")
                        w_kind    = w.get("kind", "")
                        fielders  = w.get("fielders", [])
                        w_fielder = fielders[0].get("name", "") if fielders else ""

                    runs_batter = runs.get("batter", 0)

                    rows.append((
                        match_id, inning_idx, batting_team, bowling_team,
                        over_num, ball_idx,
                        delivery.get("batter",      ""),
                        delivery.get("non_striker", ""),
                        delivery.get("bowler",      ""),
                        runs_batter,
                        runs.get("extras", 0),
                        runs.get("total",  0),
                        extras_type,
                        int("wides"   in extras),
                        int("noballs" in extras),
                        int(runs_batter == 4),
                        int(runs_batter == 6),
                        w_out, w_kind, w_fielder,
                    ))

        cur.executemany("""
            INSERT INTO deliveries
            (match_id, inning, batting_team, bowling_team, over, ball,
             batter, non_striker, bowler,
             runs_batter, runs_extras, runs_total, extras_type,
             is_wide, is_noball, is_boundary, is_six,
             wicket_player_out, wicket_kind, wicket_fielder)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, rows)

        inserted += 1

    except Exception as e:
        skipped.append((fp.name, str(e)))

conn.commit()
conn.close()


size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)

print(f"\n Done!")
print(f"   Newly inserted : {inserted}")
print(f"   Skipped        : {len(skipped)}")
print(f"   DB size        : {size_mb:.1f} MB → {DB_PATH}")
if skipped:
    print("\n  Skipped files:")
    for name, err in skipped:
        print(f"   {name}: {err}")