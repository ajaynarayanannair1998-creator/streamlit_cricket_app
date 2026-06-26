import random

def _default_player():
    return {"score": 0, "4s": 0, "6s": 0, "deliveries": 0,
            "FOW": "Not out", "Bowler": "NA", "wicket_type": "NA",
            "fielder": "NA", "status": True}

def _get_fielder(wicket):
    return wicket["fielders"][0]["name"] if wicket.get("fielders") else "NA"

def _apply_wicket(players, batter, wicket, bowler, fow_str, is_striker):
    if batter not in players:
        players[batter] = _default_player()
    p = players[batter]
    kind = wicket["kind"]
    p["wicket_type"] = kind
    p["Bowler"] = bowler
    p["FOW"] = fow_str
    p["status"] = False
    if kind in ("caught", "stumped") or (kind == "run out" and is_striker):
        p["fielder"] = _get_fielder(wicket)
    elif kind == "run out":
        p["fielder"] = _get_fielder(wicket)

def _to_batter_row(name, p):
    balls = p["deliveries"]
    return {
        "player_name": name, "score": p["score"],
        "4s": p["4s"], "6s": p["6s"], "balls": balls,
        "strike_rate": round(p["score"] / balls * 100, 2) if balls else 0,
        "FOW": p["FOW"], "status": p["status"],
        "wicket_type": p["wicket_type"],
        "fielder": p["fielder"], "Bowler": p["Bowler"],
    }

def team_player_data(match_data, innings):
    players, fow_runs, fow_wkts = {}, 0, 0
    for over in match_data["innings"][innings]["overs"]:
        for d in over["deliveries"]:
            batter, bowler = d["batter"], d["bowler"]
            extras = d.get("extras", {})
            wickets = d.get("wickets", [])
            fow_runs += d["runs"]["total"]

            if batter not in players:
                players[batter] = _default_player()
            p = players[batter]
            p["score"] += d["runs"]["batter"]
            if d["runs"]["batter"] == 4: p["4s"] += 1
            elif d["runs"]["batter"] == 6: p["6s"] += 1
            if not extras or "legbyes" in extras or "noballs" in extras:
                p["deliveries"] += 1

            if wickets:
                fow_wkts += 1
                fow_str = f"{fow_runs}/{fow_wkts}"
                player_out = wickets[0].get("player_out")
                _apply_wicket(players, player_out, wickets[0], bowler, fow_str,
                              is_striker=(player_out == batter))

    return [_to_batter_row(n, p) for n, p in players.items()]


def bowler_stats(match_data, innings):
    """
    Returns per-bowler stats including maiden overs and
    a list of overs in which the bowler took 2+ wickets.
    """
    bowlers = {}

    for over in match_data["innings"][innings]["overs"]:
        over_wickets_per_bowler = {}   # bowler -> wicket count in this over
        over_runs_per_bowler    = {}   # bowler -> legal runs conceded in this over

        for d in over["deliveries"]:
            bowler = d["bowler"]
            extras = d.get("extras", {})
            wickets = d.get("wickets", [])

            if bowler not in bowlers:
                bowlers[bowler] = {
                    "runs": 0, "wickets": 0, "deliveries": 0,
                    "overs": 0, "economy": 0,
                    "maidens": 0, "multi_wicket_overs": [],
                }

            b = bowlers[bowler]
            over_wickets_per_bowler.setdefault(bowler, 0)
            over_runs_per_bowler.setdefault(bowler, 0)

            # Runs conceded (exclude leg-byes and byes)
            if not extras or not ({"legbyes", "byes"} & extras.keys()):
                run_val = d["runs"]["total"]
                b["runs"] += run_val
                over_runs_per_bowler[bowler] += run_val

            # Wickets (exclude run-outs)
            if wickets and wickets[0]["kind"] != "run out":
                b["wickets"] += 1
                over_wickets_per_bowler[bowler] += 1

            # Legal deliveries
            if not ({"wides", "noballs"} & extras.keys()):
                b["deliveries"] += 1

        # Collect all bowlers who appeared in this over
        all_bowlers_this_over = set(over_wickets_per_bowler) | set(over_runs_per_bowler)

        # Post-over calculations for each bowler who bowled in this over
        for bowler in all_bowlers_this_over:
            b = bowlers[bowler]
            # Maiden: zero runs conceded in a complete over (6 legal balls)
            legal_this_over = sum(
                1 for d in over["deliveries"]
                if d["bowler"] == bowler and
                   not ({"wides", "noballs"} & d.get("extras", {}).keys())
            )
            if legal_this_over == 6 and over_runs_per_bowler.get(bowler, 0) == 0:
                b["maidens"] += 1

            # Multi-wicket over
            if over_wickets_per_bowler.get(bowler, 0) >= 2:
                b["multi_wicket_overs"].append(over_wickets_per_bowler[bowler])

        # Recompute overs/economy after every over (last write wins; safe)
        for bowler, b in bowlers.items():
            b["overs"] = f"{b['deliveries'] // 6}.{b['deliveries'] % 6}"
            b["economy"] = (
                round(b["runs"] / b["deliveries"] * 6, 2)
                if b["deliveries"] else 0
            )

    return [{"player_name": n, **{k: v for k, v in b.items()}}
            for n, b in bowlers.items()]


# ---------------------------------------------------------------------------
# Bowling commentary
# ---------------------------------------------------------------------------

def _five_wicket_haul_line(name, wickets, economy, overs):
    """Special opener for a five-wicket (or better) haul."""
    wkt_s = "wickets" if wickets > 1 else "wicket"
    if wickets >= 6:
        options = [
            (f"An absolutely stunning performance by {name}! "
             f"{wickets} {wkt_s} in {overs} overs — the batters had no answer today."),
            (f"Phenomenal! {name} wreaked havoc with {wickets} {wkt_s}, "
             f"finishing with a memorable economy of {economy}."),
        ]
    else:
        options = [
            (f"What a spell! {name} bags a five-wicket haul — "
             f"{wickets} {wkt_s} in {overs} overs at an economy of {economy}. "
             f"A career-defining performance!"),
            (f"Five-for {name}! One of the great individual bowling displays, "
             f"taking {wickets} {wkt_s} and rocking the batting line-up."),
        ]
    return random.choice(options)


def _maiden_line(name, maiden_count):
    """Commentary snippet for maiden overs."""
    if maiden_count == 0:
        return ""
    if maiden_count == 1:
        options = [
            f"Notably, {name} bowled a maiden over, keeping the pressure tight.",
            f"{name} also kept one over completely dot-ball clean — a maiden to remember.",
            f"A maiden over from {name} underlined the control on display today.",
        ]
    else:
        options = [
            (f"Remarkably, {name} bowled {maiden_count} maiden overs, "
             f"strangling the batters and leaving them scoreless across those spells."),
            (f"{maiden_count} maidens from {name} — a masterclass in line, length, and pressure."),
        ]
    return " " + random.choice(options)


def _multi_wicket_over_line(name, multi_wicket_overs):
    """Commentary snippet for overs in which the bowler took 2+ wickets."""
    if not multi_wicket_overs:
        return ""
    parts = []
    for wkts in multi_wicket_overs:
        if wkts >= 3:
            parts.append(
                random.choice([
                    f"In one devastating over {name} picked up {wkts} wickets, sending shockwaves through the innings.",
                    f"A hat-trick threat! {name} struck {wkts} times in a single over.",
                ])
            )
        else:  # exactly 2
            parts.append(
                random.choice([
                    f"{name} struck twice in the same over, turning the game on its head.",
                    f"A double-wicket over from {name} shifted all the momentum.",
                    f"Two in two! {name} removed a pair of batters in one electric over.",
                ])
            )
    return " " + " ".join(parts)


def bowling_summary(wickets, economy, bowler_name, overs,
                    maidens=0, multi_wicket_overs=None):
    """
    Generate rich bowling commentary.

    Parameters
    ----------
    wickets            : int   – total wickets taken
    economy            : float – economy rate
    bowler_name        : str
    overs              : str   – e.g. "4.2"
    maidens            : int   – maiden overs (default 0)
    multi_wicket_overs : list  – list of per-over wicket counts where count >= 2
                                 (default None → treated as empty)
    """
    if multi_wicket_overs is None:
        multi_wicket_overs = []

    wkt_s = "wicket" if wickets == 1 else "wickets"

    # --- Opening sentence based on wickets + economy ---
    if wickets >= 5:
        base = _five_wicket_haul_line(bowler_name, wickets, economy, overs)

    elif wickets >= 4 and economy < 6:
        base = random.choice([
            (f"Outstanding spell by {bowler_name}! Dominating with {wickets} {wkt_s} "
             f"and a miserly economy of {economy} in {overs} overs."),
            (f"{bowler_name} was virtually unplayable — {wickets} {wkt_s} at just "
             f"{economy} an over. The batting side had no respite."),
        ])

    elif wickets >= 4 and economy < 8:
        base = random.choice([
            (f"A very strong showing from {bowler_name} — {wickets} {wkt_s} in "
             f"{overs} overs with a decent economy of {economy}."),
            (f"{bowler_name} delivered the goods with the ball, finishing with "
             f"{wickets} {wkt_s} and an economy of {economy}."),
        ])

    elif wickets >= 3 and economy < 7:
        base = random.choice([
            (f"Great performance by {bowler_name}! Picked up {wickets} crucial {wkt_s} "
             f"while keeping a tight economy of {economy} over {overs} overs."),
            (f"{bowler_name} was at the heart of the attack — {wickets} {wkt_s} "
             f"and only {economy} runs per over."),
        ])

    elif wickets >= 2 and economy < 8:
        base = random.choice([
            (f"Good effort by {bowler_name}. Contributed with {wickets} {wkt_s} "
             f"and kept things fairly economical at {economy} an over."),
            (f"{bowler_name} chipped in with {wickets} important {wkt_s}, "
             f"conceding at {economy} per over across {overs} overs."),
        ])

    elif wickets == 1 and economy < 7:
        base = random.choice([
            (f"A disciplined spell from {bowler_name} — picked up {wickets} {wkt_s} "
             f"and gave nothing away, finishing at an economy of {economy}."),
            (f"{bowler_name} kept it tight and was rewarded with the prized {wkt_s}, "
             f"conceding just {economy} an over."),
        ])

    elif wickets == 1:
        base = random.choice([
            f"Decent performance by {bowler_name} — grabbed a {wkt_s} in his {overs} overs.",
            (f"{bowler_name} got a {wkt_s} to show for his efforts, "
             f"though the economy of {economy} will be something to improve on."),
        ])

    elif wickets == 0 and economy > 10:
        base = random.choice([
            (f"A tough outing for {bowler_name}. Went for {economy} an over "
             f"without a wicket — the batters took full advantage in his {overs} overs."),
            (f"{bowler_name} struggled today, conceding at {economy} per over "
             f"with nothing to show for his effort."),
        ])

    elif wickets == 0 and economy > 8:
        base = random.choice([
            (f"An expensive spell for {bowler_name} — no {wkt_s} and "
             f"an economy of {economy} over {overs} overs."),
            f"{bowler_name} will be looking to come back stronger after a costly {overs}-over spell.",
        ])

    elif economy < 6:
        tail = (f"Took {wickets} {wkt_s} in his {overs} overs spell."
                if wickets else "")
        base = random.choice([
            f"Very economical bowling by {bowler_name}. {tail}".strip(),
            (f"{bowler_name} was a model of control, giving away just {economy} "
             f"per over. {tail}").strip(),
        ])

    else:
        base = f"Decent performance by {bowler_name} in his {overs} overs."

    # --- Append maiden / multi-wicket-over notes ---
    base += _maiden_line(bowler_name, maidens)

    # Skip multi-wicket-over note when it would be redundant: i.e. the bowler
    # took exactly 2 wickets total AND both came in the same single over —
    # the base commentary already captured that story fully.
    all_in_one_over = (
        len(multi_wicket_overs) == 1 and
        multi_wicket_overs[0] == wickets == 2
    )
    if not all_in_one_over:
        base += _multi_wicket_over_line(bowler_name, multi_wicket_overs)

    return base


# ---------------------------------------------------------------------------
# Batter helpers (unchanged from original)
# ---------------------------------------------------------------------------

def _score_line(name, score, balls, sr, fours, sixes, fow):
    out = fow != "Not out"
    if score >= 100:
        adj = "blazing" if sr > 150 else "well crafted"
        mood = "at an unbelievable strike rate" if sr > 150 else "with patience and control at a strike rate"
        return (f"What a {adj} century by {name}! Scored {mood} of {sr}, "
                f"smashing {fours} boundaries and {sixes} sixes.")
    if score > 50:
        if sr > 200: return (f"{name} smashed an outstanding half-century, scoring {score} "
                             f"in just {balls} balls at a massive strike rate of {sr}.<br>")
        if sr > 150: return (f"{name} unleashed an explosive innings, smashing {score} "
                             f"runs in just {balls} balls at a remarkable strike rate of {sr}.<br>")
        return (f"{name} registered a solid half-century, scoring {score} runs "
                f"from {balls} balls with a strike rate of {sr}.<br>")
    if out and score == 0:
        return (f"{name} is out for a golden duck, dismissed on the very first ball!<br>"
                if balls == 1 else
                f"{name} departs for a duck after facing {balls} deliveries.<br>")
    if score >= 30:
        return (f"{name} played an aggressive cameo, scoring {score} runs in {balls} balls "
                f"at a strike rate of {sr}.<br>" if sr > 150 else
                f"{name} made a steady contribution of {score} runs from {balls} balls.<br>")
    if balls > 10:
        if sr >= 200: return f"{name} went on the attack, scoring rapidly with a strike rate above 200.<br>"
        if sr >= 150: return f"{name} maintained a brisk scoring rate during the innings.<br>"
        return f"{name} struggled to accelerate, scoring {score} runs from {balls} balls.<br>"
    if balls > 5:
        if sr > 200 and score<=10:
            return f"{name} provided a quick burst, smashing runs at a strike rate over 200.<br>"
        elif sr < 200  and score<10:
            return f"{name} was unable to score well.<br>"
        elif sr < 200  and score<5:
            return f"{name} had a very low score.<br>"
    if 0 < balls <= 5:
        if sr > 200 and score <= 10 and out and (fours or sixes):
            return f"{name} tried to accelerate at the start but did not manage to convert.<br>"
        if balls > 2 and sr > 200 and 10 < score <= 30 and out and (fours or sixes):
            return f"{name} played a small innings but kept the scoreboard ticking at a good speed.<br>"
        if balls > 2 and sr > 200 and fow == "Not out":
            return (f"{name} played a cameo hitting {score} off {balls} deliveries.<br>"
                    if fours or sixes else
                    f"{name} added some runs, scoring {score} off {balls} deliveries.<br>")
    if balls <= 10:
        return f"{name} had a short stay at the crease, scoring {score} from {balls} balls.<br>"
    return f"{name} played an innings of {score} runs in {balls} balls with {sr} strike rate.<br>"


def _boundary_line(name, fours, sixes):
    if fours > 5 and sixes > 5:
        return f"{name} entertained the crowd with {fours} fours and {sixes} sixes."
    if fours > 5:
        return f"{name} relied heavily on timing, striking {fours} fours along with {sixes} sixes."
    if fours > 1 or sixes > 1:
        if sixes > 5 and fours > 1:
            return f"{name} preferred the aerial route, smashing {sixes} sixes along with {fours} fours."
        return f"In his knock, {name} found the boundaries with {fours} fours and {sixes} sixes."
    if fours == 1 and sixes == 1:
        return f"The innings included a boundary and a maximum from {name}."
    if fours == 1:
        return (f"In his brief stay, {name} managed to find the boundary once."
                if (score := 0) == 0 else f"During his innings, {name} found the fence once.")
    if sixes == 1:
        return f"During the innings, {name} struck a solitary six."
    if fours > 1:
        return f"{name} struck {fours} well-timed fours during the innings."
    if sixes > 1:
        return f"{name} cleared the ropes {sixes} times with powerful hitting."
    return ""


def _dismissal_line(name, wicket_type, bowler, fielder):
    choices = {
        "bowled":        [f"His innings ended when he was bowled by {bowler}. "],
        "lbw":           [f"He was trapped lbw by {bowler}. ",
                          f"{name} was given out LBW to {bowler}. "],
        "caught":        [f"He was caught by {fielder} off {bowler}. ",
                          f"{name} was caught by {fielder} off {bowler}. "],
        "stumped":       [f"He was stumped by {fielder} off a delivery from {bowler}. "],
        "run out":       ([f"He was run out by a brilliant fielding effort from {fielder}. "]
                          if fielder != "NA" else ["He was run out. "]),
        "retired hurt":  [f"Unfortunately {name} retired hurt. "],
        "absent_hurt":   [f"Unfortunately {name} was absent hurt. "],
    }
    options = choices.get(wicket_type, [])
    return random.choice(options) if options else ""


def dataa(name, score, balls, strike_rate, fours, sixes, fow, wicket_type, fielder, bowler):
    summary = _score_line(name, score, balls, strike_rate, fours, sixes, fow)
    summary += _boundary_line(name, fours, sixes)
    summary += _dismissal_line(name, wicket_type, bowler, fielder)
    summary += ("He stood not out till the end of the innings."
                if fow == "Not out" else f"He departs as team reaches {fow}.")
    return summary