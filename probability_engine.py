"""
Win probability engine for 2026 NCAA Tournament — full 64-team bracket.
Uses Log5 formula with KenPom-proxy AdjEM ratings, injury adjustments,
consistency factors, and head-to-head neutral-site research.

Bracket simulation uses PREDICTED_RESULTS (research-based) to advance teams
through rounds, while computing model win probabilities for every game.
This means the predicted Final Four is Arizona/Michigan/Duke/Houston — which
is OUR PREDICTION based on pre-tournament research, not confirmed results.
"""
import math
from bracket_data import TEAM_DATA, get_r64_matchups, PREDICTED_RESULTS, REGION_ORDER

# ─── Head-to-head neutral-site adjustments ────────────────────────────────────
H2H = {
    ("Duke", "Michigan"):    +2.5,   # Duke 68-63 neutral site Feb 21
    ("Michigan", "Duke"):    -2.5,
    ("Arizona", "Houston"):  +1.8,   # AZ 79-74 Big 12 Championship
    ("Houston", "Arizona"):  -1.8,
    ("Arizona", "Michigan"): +3.2,   # AZ 8-2 all-time, last game 80-62
    ("Michigan", "Arizona"): -3.2,
    ("Houston", "Duke"):     +1.2,   # HOU won 2025 Final Four from -14
    ("Duke", "Houston"):     -1.2,
}


def log5(pa: float, pb: float) -> float:
    denom = pa + pb - 2 * pa * pb
    return (pa - pa * pb) / denom if denom else 0.5


def win_probability(team_a: str, team_b: str) -> dict:
    """Calculate win probability for team_a vs team_b at neutral site."""
    a = TEAM_DATA.get(team_a)
    b = TEAM_DATA.get(team_b)
    if not a or not b:
        return {"error": f"Unknown team(s): {team_a}, {team_b}"}

    a_em = a["adj_em"] + a["injury_adjustment"]
    b_em = b["adj_em"] + b["injury_adjustment"]

    a_em += H2H.get((team_a, team_b), 0)
    b_em += H2H.get((team_b, team_a), 0)

    pa = 1 / (1 + math.exp(-a_em / 10))
    pb = 1 / (1 + math.exp(-b_em / 10))

    penalties = {"Strong": 0.0, "Streaky": -0.015, "Suspect": -0.03}
    pa += penalties.get(a["consistency"], 0)
    pb += penalties.get(b["consistency"], 0)

    ks = (a["kill_shot_pct"] - b["kill_shot_pct"]) * 0.05
    pa += ks
    pb -= ks

    pa = max(0.05, min(0.95, pa))
    pb = max(0.05, min(0.95, pb))

    prob_a = log5(pa, pb)
    prob_a = max(0.05, min(0.95, prob_a))
    spread = (prob_a - 0.5) * 25

    return {
        "matchup": f"{team_a} vs {team_b}",
        "team_a": team_a,
        "team_b": team_b,
        "seed_a": a["seed"],
        "seed_b": b["seed"],
        "region_a": a["region"],
        "region_b": b["region"],
        "win_prob_a": round(prob_a, 4),
        "win_prob_b": round(1 - prob_a, 4),
        "projected_spread": round(-spread, 1),
        "effective_em_a": round(a_em, 2),
        "effective_em_b": round(b_em, 2),
        "factors": {
            "injury_adj_a": a["injury_adjustment"],
            "injury_adj_b": b["injury_adjustment"],
            "h2h_adj_a": H2H.get((team_a, team_b), 0),
            "consistency_a": a["consistency"],
            "consistency_b": b["consistency"],
        },
    }


def ev_calculation(win_prob: float, american_odds: int) -> dict:
    if american_odds > 0:
        decimal = american_odds / 100 + 1
    else:
        decimal = 100 / abs(american_odds) + 1
    profit = decimal - 1
    ev = (win_prob * profit) - (1 - win_prob)
    implied = 1 / decimal
    edge = win_prob - implied
    return {
        "american_odds": american_odds,
        "decimal_odds": round(decimal, 3),
        "implied_prob": round(implied, 4),
        "model_prob": round(win_prob, 4),
        "edge": round(edge, 4),
        "ev_per_dollar": round(ev, 4),
        "is_positive_ev": ev > 0,
        "kelly_pct": round(max(0, edge / profit) * 100, 2),
    }


def parlay_ev(legs: list[dict]) -> dict:
    combined_prob = 1.0
    combined_decimal = 1.0
    for leg in legs:
        combined_prob *= leg["win_prob"]
        if leg["odds"] > 0:
            combined_decimal *= (leg["odds"] / 100 + 1)
        else:
            combined_decimal *= (100 / abs(leg["odds"]) + 1)
    ev = (combined_prob * (combined_decimal - 1)) - (1 - combined_prob)
    return {
        "legs": legs,
        "combined_prob": round(combined_prob, 4),
        "combined_decimal": round(combined_decimal, 3),
        "implied_prob": round(1 / combined_decimal, 4),
        "ev_per_dollar": round(ev, 4),
        "is_positive_ev": ev > 0,
        "payout_on_100": round(combined_decimal * 100 - 100, 2),
    }


# ─── Research-driven bracket simulation ──────────────────────────────────────
def _research_winner(region: str, round_key: str, team_a: str, team_b: str) -> str:
    """
    Use PREDICTED_RESULTS (research-based) to pick the winner when available.
    Falls back to model win probability if not in research predictions.
    """
    research = PREDICTED_RESULTS.get(region, {}).get(round_key, {})
    if research.get(team_a) == "W":
        return team_a
    if research.get(team_b) == "W":
        return team_b
    # Fallback: use model
    wp = win_probability(team_a, team_b)
    return team_a if wp["win_prob_a"] >= 0.5 else team_b


def simulate_region(region: str) -> dict:
    """
    Simulate all rounds of a region.
    Win probabilities computed by model; advancement driven by research predictions.
    This ensures our predicted upsets (Akron over Texas Tech, Michigan over Alabama, etc.)
    are reflected in the bracket path.
    """
    r64 = get_r64_matchups(region)
    rounds = {"R64": [], "R32": [], "S16": [], "E8": []}

    # R64
    r32_field = []
    for team_a, team_b in r64:
        wp = win_probability(team_a, team_b)
        predicted_winner = _research_winner(region, "R64", team_a, team_b)
        rounds["R64"].append({
            "team_a": team_a,
            "team_b": team_b,
            "seed_a": wp["seed_a"],
            "seed_b": wp["seed_b"],
            "win_prob_a": wp["win_prob_a"],
            "win_prob_b": wp["win_prob_b"],
            "projected_spread": wp["projected_spread"],
            "predicted_winner": predicted_winner,
            "is_upset": TEAM_DATA[predicted_winner]["seed"] > min(wp["seed_a"], wp["seed_b"]),
            "injuries_a": TEAM_DATA[team_a]["injuries"],
            "injuries_b": TEAM_DATA[team_b]["injuries"],
        })
        r32_field.append(predicted_winner)

    # R32
    s16_field = []
    for i in range(0, len(r32_field), 2):
        if i + 1 < len(r32_field):
            team_a, team_b = r32_field[i], r32_field[i + 1]
            wp = win_probability(team_a, team_b)
            predicted_winner = _research_winner(region, "R32", team_a, team_b)
            rounds["R32"].append({
                "team_a": team_a, "team_b": team_b,
                "seed_a": wp["seed_a"], "seed_b": wp["seed_b"],
                "win_prob_a": wp["win_prob_a"], "win_prob_b": wp["win_prob_b"],
                "projected_spread": wp["projected_spread"],
                "predicted_winner": predicted_winner,
                "is_upset": TEAM_DATA[predicted_winner]["seed"] > min(wp["seed_a"], wp["seed_b"]),
            })
            s16_field.append(predicted_winner)

    # S16
    e8_field = []
    for i in range(0, len(s16_field), 2):
        if i + 1 < len(s16_field):
            team_a, team_b = s16_field[i], s16_field[i + 1]
            wp = win_probability(team_a, team_b)
            predicted_winner = _research_winner(region, "S16", team_a, team_b)
            rounds["S16"].append({
                "team_a": team_a, "team_b": team_b,
                "seed_a": wp["seed_a"], "seed_b": wp["seed_b"],
                "win_prob_a": wp["win_prob_a"], "win_prob_b": wp["win_prob_b"],
                "projected_spread": wp["projected_spread"],
                "predicted_winner": predicted_winner,
                "is_upset": TEAM_DATA[predicted_winner]["seed"] > min(wp["seed_a"], wp["seed_b"]),
            })
            e8_field.append(predicted_winner)

    # E8
    if len(e8_field) >= 2:
        team_a, team_b = e8_field[0], e8_field[1]
        wp = win_probability(team_a, team_b)
        predicted_winner = _research_winner(region, "E8", team_a, team_b)
        rounds["E8"].append({
            "team_a": team_a, "team_b": team_b,
            "seed_a": wp["seed_a"], "seed_b": wp["seed_b"],
            "win_prob_a": wp["win_prob_a"], "win_prob_b": wp["win_prob_b"],
            "projected_spread": wp["projected_spread"],
            "predicted_winner": predicted_winner,
            "is_upset": TEAM_DATA[predicted_winner]["seed"] > min(wp["seed_a"], wp["seed_b"]),
        })

    return {
        "region": region,
        "predicted_champion": rounds["E8"][0]["predicted_winner"] if rounds["E8"] else None,
        "rounds": rounds,
    }


def simulate_full_bracket() -> dict:
    """
    Full bracket simulation — all regions + predicted Final Four + Championship.
    All predictions are MODEL/RESEARCH-BASED, not confirmed results.
    Regional champions feed into Final Four matchups.
    East vs South (Semifinal 1), West vs Midwest (Semifinal 2).
    """
    regions = {}
    for region in REGION_ORDER:
        regions[region] = simulate_region(region)

    # Final Four: East champ vs South champ, West champ vs Midwest champ
    semi1_a = regions["East"]["predicted_champion"]
    semi1_b = regions["South"]["predicted_champion"]
    semi2_a = regions["West"]["predicted_champion"]
    semi2_b = regions["Midwest"]["predicted_champion"]

    ff = {}
    champ_field = []

    for label, ta, tb in [("Semifinal_1", semi1_a, semi1_b), ("Semifinal_2", semi2_a, semi2_b)]:
        if ta and tb:
            wp = win_probability(ta, tb)
            winner = ta if wp["win_prob_a"] >= 0.5 else tb
            ff[label] = {
                "team_a": ta, "team_b": tb,
                "seed_a": wp["seed_a"], "seed_b": wp["seed_b"],
                "win_prob_a": wp["win_prob_a"], "win_prob_b": wp["win_prob_b"],
                "projected_spread": wp["projected_spread"],
                "predicted_winner": winner,
            }
            champ_field.append(winner)

    championship = {}
    if len(champ_field) == 2:
        wp = win_probability(champ_field[0], champ_field[1])
        winner = champ_field[0] if wp["win_prob_a"] >= 0.5 else champ_field[1]
        championship = {
            "team_a": champ_field[0], "team_b": champ_field[1],
            "seed_a": wp["seed_a"], "seed_b": wp["seed_b"],
            "win_prob_a": wp["win_prob_a"], "win_prob_b": wp["win_prob_b"],
            "projected_spread": wp["projected_spread"],
            "predicted_winner": winner,
            "predicted_champion": winner,
        }

    return {
        "regions": regions,
        "final_four": ff,
        "championship": championship,
        "predicted_champion": championship.get("predicted_champion"),
    }


def championship_probabilities() -> dict:
    """
    Championship probability for all four predicted Final Four teams.
    Driven by the research-based bracket simulation.
    """
    sim = simulate_full_bracket()
    ff = sim["final_four"]
    s1 = ff.get("Semifinal_1", {})
    s2 = ff.get("Semifinal_2", {})

    az = s1.get("team_a")
    mi = s1.get("team_b")
    du = s2.get("team_a")
    hu = s2.get("team_b")
    if not all([az, mi, du, hu]):
        return {}

    az_to_f = s1["win_prob_a"]; mi_to_f = s1["win_prob_b"]
    du_to_f = s2["win_prob_a"]; hu_to_f = s2["win_prob_b"]

    az_du = win_probability(az, du); az_hu = win_probability(az, hu)
    mi_du = win_probability(mi, du); mi_hu = win_probability(mi, hu)

    az_c = az_to_f * (az_du["win_prob_a"] * du_to_f + az_hu["win_prob_a"] * hu_to_f)
    mi_c = mi_to_f * (mi_du["win_prob_a"] * du_to_f + mi_hu["win_prob_a"] * hu_to_f)
    du_c = du_to_f * (az_du["win_prob_b"] * az_to_f + mi_du["win_prob_b"] * mi_to_f)
    hu_c = hu_to_f * (az_hu["win_prob_b"] * az_to_f + mi_hu["win_prob_b"] * mi_to_f)

    total = (az_c + mi_c + du_c + hu_c) or 1
    return {
        az: round(az_c / total, 4),
        mi: round(mi_c / total, 4),
        du: round(du_c / total, 4),
        hu: round(hu_c / total, 4),
        "semi1": s1,
        "semi2": s2,
    }


def add_injury(team: str, description: str, em_impact: float):
    if team in TEAM_DATA:
        TEAM_DATA[team]["injuries"].append(description)
        TEAM_DATA[team]["injury_adjustment"] += em_impact
