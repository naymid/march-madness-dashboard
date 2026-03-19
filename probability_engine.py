"""
Win probability engine for 2026 NCAA Tournament — full 64-team bracket.
Uses Log5 formula with KenPom-proxy AdjEM ratings, injury adjustments,
consistency factors, and head-to-head neutral-site research.
"""
import math
from bracket_data import TEAM_DATA, get_r64_matchups, PREDICTED_RESULTS, REGION_ORDER, CONFIRMED_FINAL_FOUR

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

# ─── Core math ────────────────────────────────────────────────────────────────
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

    # Consistency penalty for high-stakes games
    penalties = {"Strong": 0.0, "Streaky": -0.015, "Suspect": -0.03}
    pa += penalties.get(a["consistency"], 0)
    pb += penalties.get(b["consistency"], 0)

    # Kill Shot factor
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


# ─── Full bracket simulation ──────────────────────────────────────────────────
def simulate_region(region: str) -> dict:
    """
    Simulate all rounds of a region using model win probabilities.
    Returns round-by-round matchups with win probabilities and predicted winners.
    """
    r64 = get_r64_matchups(region)
    rounds = {"R64": [], "R32": [], "S16": [], "E8": []}

    # R64
    r32_field = []
    for team_a, team_b in r64:
        wp = win_probability(team_a, team_b)
        predicted_winner = team_a if wp["win_prob_a"] >= 0.5 else team_b
        predicted_loser = team_b if wp["win_prob_a"] >= 0.5 else team_a
        win_prob = max(wp["win_prob_a"], wp["win_prob_b"])
        rounds["R64"].append({
            "team_a": team_a,
            "team_b": team_b,
            "seed_a": wp["seed_a"],
            "seed_b": wp["seed_b"],
            "win_prob_a": wp["win_prob_a"],
            "win_prob_b": wp["win_prob_b"],
            "projected_spread": wp["projected_spread"],
            "predicted_winner": predicted_winner,
            "win_prob_winner": round(win_prob, 4),
            "injuries_a": TEAM_DATA[team_a]["injuries"],
            "injuries_b": TEAM_DATA[team_b]["injuries"],
        })
        r32_field.append(predicted_winner)

    # R32 — winners of adjacent R64 games meet
    s16_field = []
    for i in range(0, len(r32_field), 2):
        if i + 1 < len(r32_field):
            team_a, team_b = r32_field[i], r32_field[i + 1]
            wp = win_probability(team_a, team_b)
            predicted_winner = team_a if wp["win_prob_a"] >= 0.5 else team_b
            win_prob = max(wp["win_prob_a"], wp["win_prob_b"])
            rounds["R32"].append({
                "team_a": team_a,
                "team_b": team_b,
                "seed_a": wp["seed_a"],
                "seed_b": wp["seed_b"],
                "win_prob_a": wp["win_prob_a"],
                "win_prob_b": wp["win_prob_b"],
                "projected_spread": wp["projected_spread"],
                "predicted_winner": predicted_winner,
                "win_prob_winner": round(win_prob, 4),
            })
            s16_field.append(predicted_winner)

    # S16
    e8_field = []
    for i in range(0, len(s16_field), 2):
        if i + 1 < len(s16_field):
            team_a, team_b = s16_field[i], s16_field[i + 1]
            wp = win_probability(team_a, team_b)
            predicted_winner = team_a if wp["win_prob_a"] >= 0.5 else team_b
            win_prob = max(wp["win_prob_a"], wp["win_prob_b"])
            rounds["S16"].append({
                "team_a": team_a,
                "team_b": team_b,
                "seed_a": wp["seed_a"],
                "seed_b": wp["seed_b"],
                "win_prob_a": wp["win_prob_a"],
                "win_prob_b": wp["win_prob_b"],
                "projected_spread": wp["projected_spread"],
                "predicted_winner": predicted_winner,
                "win_prob_winner": round(win_prob, 4),
            })
            e8_field.append(predicted_winner)

    # E8
    if len(e8_field) >= 2:
        team_a, team_b = e8_field[0], e8_field[1]
        wp = win_probability(team_a, team_b)
        predicted_winner = team_a if wp["win_prob_a"] >= 0.5 else team_b
        win_prob = max(wp["win_prob_a"], wp["win_prob_b"])
        rounds["E8"].append({
            "team_a": team_a,
            "team_b": team_b,
            "seed_a": wp["seed_a"],
            "seed_b": wp["seed_b"],
            "win_prob_a": wp["win_prob_a"],
            "win_prob_b": wp["win_prob_b"],
            "projected_spread": wp["projected_spread"],
            "predicted_winner": predicted_winner,
            "win_prob_winner": round(win_prob, 4),
        })

    return {
        "region": region,
        "predicted_champion": rounds["E8"][0]["predicted_winner"] if rounds["E8"] else None,
        "rounds": rounds,
    }


def simulate_full_bracket() -> dict:
    """
    Run full bracket simulation — all regions + confirmed Final Four + Championship.
    Regions simulate from R64 using the model.
    Final Four uses CONFIRMED teams (Arizona/Michigan, Duke/Houston).
    """
    regions = {}

    for region in REGION_ORDER:
        sim = simulate_region(region)
        regions[region] = sim

    # Use confirmed Final Four teams, not simulated (model may differ due to upsets)
    cf = CONFIRMED_FINAL_FOUR
    semi1_a = cf["Semifinal_1"]["team_a"]
    semi1_b = cf["Semifinal_1"]["team_b"]
    semi2_a = cf["Semifinal_2"]["team_a"]
    semi2_b = cf["Semifinal_2"]["team_b"]

    ff = {}
    champ_field = []

    if semi1_a and semi1_b:
        wp = win_probability(semi1_a, semi1_b)
        winner = semi1_a if wp["win_prob_a"] >= 0.5 else semi1_b
        ff["Semifinal_1"] = {
            "team_a": semi1_a, "team_b": semi1_b,
            "seed_a": wp["seed_a"], "seed_b": wp["seed_b"],
            "win_prob_a": wp["win_prob_a"], "win_prob_b": wp["win_prob_b"],
            "projected_spread": wp["projected_spread"],
            "predicted_winner": winner,
        }
        champ_field.append(winner)

    if semi2_a and semi2_b:
        wp = win_probability(semi2_a, semi2_b)
        winner = semi2_a if wp["win_prob_a"] >= 0.5 else semi2_b
        ff["Semifinal_2"] = {
            "team_a": semi2_a, "team_b": semi2_b,
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
    Championship probability using CONFIRMED Final Four teams.
    Overrides pure simulation with user-validated bracket results.
    """
    # Use confirmed Final Four, not simulated one
    cf = CONFIRMED_FINAL_FOUR
    s1_a = cf["Semifinal_1"]["team_a"]
    s1_b = cf["Semifinal_1"]["team_b"]
    s2_a = cf["Semifinal_2"]["team_a"]
    s2_b = cf["Semifinal_2"]["team_b"]

    wp1 = win_probability(s1_a, s1_b)
    wp2 = win_probability(s2_a, s2_b)

    # Build s1, s2 dicts matching simulate_full_bracket format
    s1 = {**wp1, "team_a": s1_a, "team_b": s1_b,
          "seed_a": TEAM_DATA[s1_a]["seed"], "seed_b": TEAM_DATA[s1_b]["seed"]}
    s2 = {**wp2, "team_a": s2_a, "team_b": s2_b,
          "seed_a": TEAM_DATA[s2_a]["seed"], "seed_b": TEAM_DATA[s2_b]["seed"]}

    # Legacy path uses s1/s2
    ff = {"Semifinal_1": s1, "Semifinal_2": s2}
    sim = {"final_four": ff}

    # Get FF teams — now using confirmed teams
    s1 = ff.get("Semifinal_1", {})
    s2 = ff.get("Semifinal_2", {})

    az = s1.get("team_a")
    mi = s1.get("team_b")
    du = s2.get("team_a")
    hu = s2.get("team_b")

    if not all([az, mi, du, hu]):
        return {}

    az_to_final = s1["win_prob_a"]
    mi_to_final = s1["win_prob_b"]
    du_to_final = s2["win_prob_a"]
    hu_to_final = s2["win_prob_b"]

    # All championship matchups
    az_du = win_probability(az, du)
    az_hu = win_probability(az, hu)
    mi_du = win_probability(mi, du)
    mi_hu = win_probability(mi, hu)

    az_champ = az_to_final * (az_du["win_prob_a"] * du_to_final + az_hu["win_prob_a"] * hu_to_final)
    mi_champ = mi_to_final * (mi_du["win_prob_a"] * du_to_final + mi_hu["win_prob_a"] * hu_to_final)
    du_champ = du_to_final * (az_du["win_prob_b"] * az_to_final + mi_du["win_prob_b"] * mi_to_final)
    hu_champ = hu_to_final * (az_hu["win_prob_b"] * az_to_final + mi_hu["win_prob_b"] * mi_to_final)

    total = az_champ + mi_champ + du_champ + hu_champ or 1

    return {
        az: round(az_champ / total, 4),
        mi: round(mi_champ / total, 4),
        du: round(du_champ / total, 4),
        hu: round(hu_champ / total, 4),
        "semi1": s1,
        "semi2": s2,
    }


def add_injury(team: str, description: str, em_impact: float):
    if team in TEAM_DATA:
        TEAM_DATA[team]["injuries"].append(description)
        TEAM_DATA[team]["injury_adjustment"] += em_impact
