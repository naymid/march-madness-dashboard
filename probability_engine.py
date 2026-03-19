"""
Win probability engine for 2026 NCAA Tournament.
Encodes pre-research team ratings and applies live adjustments.
Uses Log5 formula: P(A beats B) = (Pa - Pa*Pb) / (Pa + Pb - 2*Pa*Pb)
"""
from dataclasses import dataclass, field
from typing import Optional
import math


@dataclass
class TeamStats:
    name: str
    seed: int
    region: str
    adj_em: float          # KenPom Adjusted Efficiency Margin
    adj_o: float           # Adjusted Offensive Efficiency
    adj_d: float           # Adjusted Defensive Efficiency
    adj_t: float           # Adjusted Tempo
    evan_miya_rating: float
    consistency: str       # "Strong" | "Streaky" | "Suspect"
    kill_shot_pct: float   # % of games with 10+ unanswered run
    coach_tourney_wins: int
    coach_final_fours: int
    injuries: list = field(default_factory=list)
    injury_adjustment: float = 0.0  # negative = hurt, positive = healthy return

    @property
    def win_pct(self) -> float:
        """Convert AdjEM to approximate win percentage using sigmoid."""
        return 1 / (1 + math.exp(-self.adj_em / 10))


# ─── BASE TEAM RATINGS (encoded from KenPom/EvanMiya research) ───────────────
TEAMS: dict[str, TeamStats] = {
    "Arizona": TeamStats(
        name="Arizona",
        seed=1,
        region="East",
        adj_em=27.5,
        adj_o=122.4,
        adj_d=94.9,
        adj_t=69.8,
        evan_miya_rating=27.1,
        consistency="Strong",
        kill_shot_pct=0.71,
        coach_tourney_wins=8,
        coach_final_fours=1,
        injuries=["Jaden Bradley wrist (cleared, X-ray negative)"],
        injury_adjustment=0.0,
    ),
    "Michigan": TeamStats(
        name="Michigan",
        seed=5,
        region="East",
        adj_em=19.3,
        adj_o=116.2,
        adj_d=96.9,
        adj_t=67.2,
        evan_miya_rating=18.6,
        consistency="Streaky",
        kill_shot_pct=0.52,
        coach_tourney_wins=4,
        coach_final_fours=0,
        injuries=[],
        injury_adjustment=0.0,
    ),
    "Duke": TeamStats(
        name="Duke",
        seed=1,
        region="West",
        adj_em=25.8,
        adj_o=120.1,
        adj_d=94.3,
        adj_t=70.4,
        evan_miya_rating=25.3,
        consistency="Strong",
        kill_shot_pct=0.68,
        coach_tourney_wins=11,
        coach_final_fours=2,
        injuries=[
            "Caleb Foster PG OUT (foot fracture, season-ending surgery)",
            "Patrick Ngongba II C questionable (foot soreness)",
            "Cayden Boozer PG starter (28% from 3, defensive liability)",
        ],
        injury_adjustment=-2.8,
    ),
    "Houston": TeamStats(
        name="Houston",
        seed=2,
        region="West",
        adj_em=22.4,
        adj_o=114.8,
        adj_d=92.4,
        adj_t=65.1,
        evan_miya_rating=22.1,
        consistency="Strong",
        kill_shot_pct=0.74,
        coach_tourney_wins=21,
        coach_final_fours=3,
        injuries=[],
        injury_adjustment=0.0,
    ),
}

# ─── HEAD-TO-HEAD ADJUSTMENTS ─────────────────────────────────────────────────
# Based on recent neutral-site results
H2H_ADJUSTMENTS: dict[tuple[str, str], float] = {
    # format: (team_a, team_b): points added to team_a's effective EM
    ("Duke", "Michigan"):   +2.5,   # Duke won neutral site Feb 21 68-63
    ("Michigan", "Duke"):   -2.5,
    ("Arizona", "Houston"): +1.8,   # AZ beat HOU 79-74 in Big 12 Championship
    ("Houston", "Arizona"): -1.8,
    ("Arizona", "Michigan"): +3.2,  # AZ 8-2 all-time, last game AZ 80-62 in 2021
    ("Michigan", "Arizona"): -3.2,
    ("Houston", "Duke"):    +1.2,   # HOU beat Duke in 2025 Final Four
    ("Duke", "Houston"):    -1.2,
}


def log5(pa: float, pb: float) -> float:
    """Log5 win probability formula."""
    if pa + pb - 2 * pa * pb == 0:
        return 0.5
    return (pa - pa * pb) / (pa + pb - 2 * pa * pb)


def win_probability(team_a: str, team_b: str, context: str = "neutral") -> dict:
    """
    Calculate win probability for team_a vs team_b.
    Returns dict with win_prob, edge metrics, and breakdown.
    """
    a = TEAMS.get(team_a)
    b = TEAMS.get(team_b)
    if not a or not b:
        return {"error": f"Unknown team(s): {team_a}, {team_b}"}

    # Apply injury adjustments to effective EM
    a_em = a.adj_em + a.injury_adjustment
    b_em = b.adj_em + b.injury_adjustment

    # Apply head-to-head adjustment
    h2h_a = H2H_ADJUSTMENTS.get((team_a, team_b), 0.0)
    h2h_b = H2H_ADJUSTMENTS.get((team_b, team_a), 0.0)
    a_em += h2h_a
    b_em += h2h_b

    # Convert to win probabilities
    pa = 1 / (1 + math.exp(-a_em / 10))
    pb = 1 / (1 + math.exp(-b_em / 10))

    # Consistency factor (Streaky teams underperform in high-stakes)
    consistency_penalty = {"Strong": 0.0, "Streaky": -0.015, "Suspect": -0.03}
    pa += consistency_penalty.get(a.consistency, 0)
    pb += consistency_penalty.get(b.consistency, 0)

    # Kill Shot factor (ability to put games away)
    kill_shot_factor = (a.kill_shot_pct - b.kill_shot_pct) * 0.05
    pa += kill_shot_factor
    pb -= kill_shot_factor

    # Clamp
    pa = max(0.05, min(0.95, pa))
    pb = max(0.05, min(0.95, pb))

    win_prob_a = log5(pa, pb)
    win_prob_a = max(0.05, min(0.95, win_prob_a))

    # Projected spread (roughly 2.5 pts per 10% win prob away from 50%)
    spread = (win_prob_a - 0.5) * 25

    return {
        "matchup": f"{team_a} vs {team_b}",
        "team_a": team_a,
        "team_b": team_b,
        "win_prob_a": round(win_prob_a, 4),
        "win_prob_b": round(1 - win_prob_a, 4),
        "projected_spread": round(-spread, 1),  # negative = team_a favored
        "effective_em_a": round(a_em, 2),
        "effective_em_b": round(b_em, 2),
        "factors": {
            "injury_adj_a": a.injury_adjustment,
            "injury_adj_b": b.injury_adjustment,
            "h2h_adj_a": h2h_a,
            "consistency_a": a.consistency,
            "consistency_b": b.consistency,
        },
    }


def ev_calculation(win_prob: float, american_odds: int) -> dict:
    """
    Calculate Expected Value given win probability and American odds.
    EV = (prob * payout) - (1 - prob)
    Returns EV per $1 bet.
    """
    if american_odds > 0:
        decimal = american_odds / 100 + 1
    else:
        decimal = 100 / abs(american_odds) + 1

    profit = decimal - 1
    ev = (win_prob * profit) - ((1 - win_prob) * 1)
    implied_prob = (1 / decimal)
    edge = win_prob - implied_prob

    return {
        "american_odds": american_odds,
        "decimal_odds": round(decimal, 3),
        "implied_prob": round(implied_prob, 4),
        "model_prob": round(win_prob, 4),
        "edge": round(edge, 4),
        "ev_per_dollar": round(ev, 4),
        "is_positive_ev": ev > 0,
        "kelly_pct": round(max(0, edge / profit) * 100, 2),
    }


def championship_probabilities() -> dict:
    """
    Monte Carlo-style championship probability for Final Four teams.
    Calculates: P(win semi) * P(win final given semi win)
    """
    # Semis
    sf1 = win_probability("Arizona", "Michigan")
    sf2 = win_probability("Duke", "Houston")

    az_to_final = sf1["win_prob_a"]
    mi_to_final = sf1["win_prob_b"]
    du_to_final = sf2["win_prob_a"]
    hu_to_final = sf2["win_prob_b"]

    # Finals matchups (calculate all 4 combos)
    az_vs_du = win_probability("Arizona", "Duke")
    az_vs_hu = win_probability("Arizona", "Houston")
    mi_vs_du = win_probability("Michigan", "Duke")
    mi_vs_hu = win_probability("Michigan", "Houston")

    # Championship prob = P(make final) * P(win final vs each opponent) * P(that opp makes final)
    az_champ = az_to_final * (
        az_vs_du["win_prob_a"] * du_to_final +
        az_vs_hu["win_prob_a"] * hu_to_final
    )
    mi_champ = mi_to_final * (
        mi_vs_du["win_prob_a"] * du_to_final +
        mi_vs_hu["win_prob_a"] * hu_to_final
    )
    du_champ = du_to_final * (
        az_vs_du["win_prob_b"] * az_to_final +
        mi_vs_du["win_prob_b"] * mi_to_final
    )
    hu_champ = hu_to_final * (
        az_vs_hu["win_prob_b"] * az_to_final +
        mi_vs_hu["win_prob_b"] * mi_to_final
    )

    total = az_champ + mi_champ + du_champ + hu_champ
    # Normalize
    return {
        "Arizona":  round(az_champ / total, 4),
        "Michigan": round(mi_champ / total, 4),
        "Duke":     round(du_champ / total, 4),
        "Houston":  round(hu_champ / total, 4),
        "semi1": sf1,
        "semi2": sf2,
    }


def apply_result_update(winner: str, loser: str):
    """
    After a game result, update teams dict to reflect elimination.
    Adjusts remaining teams' ratings based on opponent faced.
    """
    if loser in TEAMS:
        TEAMS[loser].adj_em = -99  # Eliminated


def add_injury(team: str, description: str, em_impact: float):
    """Add or update injury for a team."""
    if team in TEAMS:
        TEAMS[team].injuries.append(description)
        TEAMS[team].injury_adjustment += em_impact


def parlay_ev(legs: list[dict]) -> dict:
    """
    Calculate combined parlay EV.
    legs: list of {"team": str, "odds": int, "win_prob": float}
    """
    combined_prob = 1.0
    combined_decimal = 1.0
    for leg in legs:
        combined_prob *= leg["win_prob"]
        if leg["odds"] > 0:
            combined_decimal *= (leg["odds"] / 100 + 1)
        else:
            combined_decimal *= (100 / abs(leg["odds"]) + 1)

    ev = (combined_prob * (combined_decimal - 1)) - (1 - combined_prob)
    implied = 1 / combined_decimal

    return {
        "legs": legs,
        "combined_prob": round(combined_prob, 4),
        "combined_decimal": round(combined_decimal, 3),
        "implied_prob": round(implied, 4),
        "ev_per_dollar": round(ev, 4),
        "is_positive_ev": ev > 0,
        "payout_on_100": round(combined_decimal * 100 - 100, 2),
    }
