import os
import json
import glob
from collections import defaultdict

FOLDER_PATH = "IPL" 
ALIAS_FILE_PATH = "player_aliases.json.txt"

TEAM_MAPPING = {
    "Royal Challengers Bangalore":"Royal Challengers Bengaluru",
    "Delhi Daredevils": "Delhi Capitals",
    "Kings XI Punjab": "Punjab Kings",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Deccan Chargers": "Sunrisers Hyderabad"
}

def clean_team(team_name):
    return TEAM_MAPPING.get(team_name, team_name)

def load_player_aliases(filepath):
    if not os.path.exists(filepath):
        print(f"Warning: Alias file '{filepath}' not found. Skipping alias logic.")
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            aliases = json.load(f)
            return {k: v[0] if isinstance(v, list) and v else k for k, v in aliases.items()}
    except Exception as e:
        print(f"Error loading alias configuration file: {e}")
        return {}

def process_cricsheet_data(folder_path):
    file_pattern = os.path.join(folder_path, "*.json")
    all_files = glob.glob(file_pattern)
    
    if not all_files:
        print(f"No JSON files found in {folder_path}.")
        return {}

    player_aliases = load_player_aliases(ALIAS_FILE_PATH)
    
    def clean_player(name):
        return player_aliases.get(name, name)

    matches_by_season = defaultdict(list)
    
    for filepath in all_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                match_data = json.load(f)
            except Exception:
                continue
            
            info = match_data.get('info', {})
            if info.get('competition') == 'Indian Premier League' or info.get('event', {}).get('name') == 'Indian Premier League':
                season = str(info.get('season'))
                if '/' in season:
                    season = season.split('/')[0]
                
                match_date = info.get('dates', ['0000-00-00'])[0]
                matches_by_season[season].append((match_date, match_data))

    raw_stats = defaultdict(lambda: {
        "overall": {
            "total_matches": 0, "wins": 0, "seasons_played": set(),
            "runs_tracker": defaultdict(int), "wickets_tracker": defaultdict(int),
            "best_team_score": 0
        },
        "seasons": defaultdict(lambda: {
            "wins": 0, "total_matches": 0
        })
    })

    season_champions = {}
    season_runners_up = {}
    season_teams_progression = defaultdict(lambda: defaultdict(set))

    for season in sorted(matches_by_season.keys()):
        sorted_matches = sorted(matches_by_season[season], key=lambda x: x[0])
        
        if sorted_matches:
            final_match_data = sorted_matches[-1][1]
            final_info = final_match_data.get('info', {})
            final_teams = [clean_team(t) for t in final_info.get('teams', [])]
            outcome = final_info.get('outcome', {})
            
            if 'winner' in outcome and len(final_teams) == 2:
                winner_team = clean_team(outcome['winner'])
                season_champions[season] = winner_team
                runner_team = final_teams[1] if final_teams[0] == winner_team else final_teams[0]
                season_runners_up[season] = runner_team

        for idx, (date, match) in enumerate(sorted_matches):
            info = match.get('info', {})
            teams = [clean_team(t) for t in info.get('teams', [])]
            if len(teams) < 2:
                continue
                
            outcome = info.get('outcome', {})
            winner = clean_team(outcome.get('winner')) if 'winner' in outcome else None
            stage = info.get('stage')
            
            if not stage:
                match_num = info.get('event', {}).get('match_number')
                if match_num is None:
                    is_playoff = (len(sorted_matches) - idx) <= 4
                    stage = "Playoff Match" if is_playoff else "League stage"
                else:
                    stage = "League stage"

            innings = match.get('innings', [])
            standard_innings_count = 0
            
            for inning in innings:
                inning_name = str(inning.get('name', '')).lower()
                if "super over" in inning_name or "eliminator" in inning_name or standard_innings_count >= 2:
                    continue
                
                team_batting = clean_team(inning.get('team'))
                if team_batting not in teams:
                    continue
                
                team_bowling = teams[1] if teams[0] == team_batting else teams[0]
                standard_innings_count += 1
                
                total_runs = 0
                for over in inning.get('overs', []):
                    for delivery in over.get('deliveries', []):
                        runs_dict = delivery.get('runs', {})
                        total_runs += runs_dict.get('total', 0)
                        
                        batter = clean_player(delivery.get('batter'))
                        raw_stats[team_batting]["overall"]["runs_tracker"][batter] += runs_dict.get('batter', 0)
                        
                        bowler = clean_player(delivery.get('bowler'))
                        if 'wickets' in delivery:
                            for wicket in delivery.get('wickets', []):
                                w_type = str(wicket.get('kind', '')).lower()
                                if w_type in ['bowled', 'caught', 'caught and bowled', 'lbw', 'stumped', 'hit wicket']:
                                    raw_stats[team_bowling]["overall"]["wickets_tracker"][bowler] += 1

                if total_runs > raw_stats[team_batting]["overall"]["best_team_score"]:
                    raw_stats[team_batting]["overall"]["best_team_score"] = total_runs

            for team in teams:
                raw_stats[team]["overall"]["total_matches"] += 1
                raw_stats[team]["overall"]["seasons_played"].add(season)
                raw_stats[team]["seasons"][season]["total_matches"] += 1
                
                if winner == team:
                    raw_stats[team]["overall"]["wins"] += 1
                    raw_stats[team]["seasons"][season]["wins"] += 1
                
                if stage.lower() in ["league stage", "group stage"]:
                    season_teams_progression[season][team].add("League stage")
                else:
                    season_teams_progression[season][team].add(stage)

    def format_run_milestone(runs):
        if runs >= 100:
            return f"{(runs // 100) * 100}+ runs"
        return f"{runs} runs"

    def format_wicket_milestone(wickets):
        if wickets >= 10:
            return f"{(wickets // 10) * 10}+ wickets"
        return f"{wickets} wickets"

    formatted_output = {}
    for team, data in raw_stats.items():
        sorted_seasons = sorted(list(data["overall"]["seasons_played"]))
        if not sorted_seasons:
            continue
            
        run_scores = data["overall"]["runs_tracker"]
        if run_scores:
            top_batsman = max(run_scores, key=run_scores.get)
            most_runs_str = f"{top_batsman} ({format_run_milestone(run_scores[top_batsman])})"
        else:
            most_runs_str = "NA"
        
        wicket_counts = data["overall"]["wickets_tracker"]
        if wicket_counts:
            top_bowler = max(wicket_counts, key=wicket_counts.get)
            most_wickets_str = f"{top_bowler} ({format_wicket_milestone(wicket_counts[top_bowler])})"
        else:
            most_wickets_str = "NA"
            
        best_season = "NA"
        max_season_wins = -1
        for yr in sorted_seasons:
            s_wins = data["seasons"][yr]["wins"]
            if s_wins > max_season_wins:
                max_season_wins = s_wins
                best_season = yr

        tot_m = data["overall"]["total_matches"]
        tot_w = data["overall"]["wins"]
        win_pct = round((tot_w / tot_m) * 100, 2) if tot_m > 0 else 0.0

        team_dict = {
            "overall": {
                "total_wins": tot_w,
                "total_matches": tot_m,
                "win_%": win_pct,
                "first_year": sorted_seasons[0],
                "last_year": sorted_seasons[-1],
                "best_season": best_season,
                "champions": [yr for yr, champ in season_champions.items() if champ == team],
                "most_runs_player": most_runs_str,
                "best_team_score": data["overall"]["best_team_score"],
                "most_wickets_player": most_wickets_str
            },
            "season_wise": []
        }
        
        for yr in sorted_seasons:
            s_data = data["seasons"][yr]
            s_matches = s_data["total_matches"]
            s_wins = s_data["wins"]
            s_win_pct = round((s_wins / s_matches) * 100, 2) if s_matches > 0 else 0.0
            
            if season_champions.get(yr) == team:
                result_stage = "Champions"
            elif season_runners_up.get(yr) == team:
                result_stage = "Runner-up"
            else:
                stages_visited = season_teams_progression[yr][team]
                if "Qualifier 2" in stages_visited: result_stage = "Qualifier 2"
                elif "Eliminator" in stages_visited: result_stage = "Eliminator"
                elif "Qualifier 1" in stages_visited: result_stage = "Qualifier 1"
                elif "Playoff Match" in stages_visited: result_stage = "Playoffs"
                else: result_stage = "League stage"
                
            team_dict["season_wise"].append({
                "year": yr,
                "wins": s_wins,
                "matches": s_matches,
                "win%": s_win_pct,
                "result": result_stage
            })
            
        formatted_output[team] = team_dict

    return {"team": formatted_output}

if __name__ == "__main__":
    final_json_structure = process_cricsheet_data(FOLDER_PATH)
    output_filename = "ipl_franchise_perfect_analytics.json"
    with open(output_filename, 'w', encoding='utf-8') as out_f:
        json.dump(final_json_structure, out_f, indent=4)
    print(f"Data mapping accurate! Filtered results saved to '{output_filename}'")