"""
2026 NCAA March Madness Dashboard — FastAPI backend
Full 64-team bracket, round-by-round predictions, live odds, +EV alerts.
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data_fetcher import fetch_all_data, get_known_injuries, get_demo_odds
from bracket_data import (
    TEAM_DATA, REGION_ORDER, ROUND_INFO, NOTABLE_UPSETS,
    get_r64_matchups, get_predicted_bracket_path, get_teams_by_region
)
from probability_engine import (
    win_probability, championship_probabilities,
    simulate_full_bracket, ev_calculation, parlay_ev, add_injury
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ─── In-Memory State ──────────────────────────────────────────────────────────
state = {
    "scores": {"games": []},
    "injuries": get_known_injuries(),
    "odds": get_demo_odds(),
    "probabilities": {},
    "bracket_sim": {},
    "ev_opportunities": [],
    "parlays": [],
    "last_updated": datetime.utcnow().isoformat(),
    "update_count": 0,
    "alerts": [],
    "results": {
        "East": {}, "South": {}, "West": {}, "Midwest": {},
        "Final Four": {}, "Championship": {}
    },
}

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await update_all_data()
    scheduler.add_job(update_all_data, "interval", minutes=2, id="data_refresh")
    scheduler.start()
    logger.info("Dashboard started. Refreshing every 2 minutes.")
    yield
    scheduler.shutdown()


app = FastAPI(title="2026 March Madness Dashboard", version="2.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# ─── Background Update ────────────────────────────────────────────────────────
async def update_all_data():
    global state
    try:
        logger.info("Updating data...")
        data = await fetch_all_data()
        state["scores"] = data["scores"]
        state["last_updated"] = data["fetched_at"]
        state["update_count"] += 1
        if data["injuries"]:
            state["injuries"] = data["injuries"]
        state["odds"] = data["odds"]
        state["bracket_sim"] = simulate_full_bracket()
        state["probabilities"] = championship_probabilities()
        state["ev_opportunities"] = calculate_ev_opportunities(data["odds"])
        state["parlays"] = generate_parlays(state["ev_opportunities"])
        state["alerts"] = generate_alerts(state["ev_opportunities"], state["injuries"])
        logger.info(f"Update #{state['update_count']} complete. EV opps: {len(state['ev_opportunities'])}")
    except Exception as e:
        logger.error(f"Update failed: {e}", exc_info=True)


# ─── Standard market ML lines for each R64 seed matchup ─────────────────────
# Based on historical NCAA Tournament opening lines (DraftKings/FanDuel typical)
# These represent where the market opens before sharp money and live injury news.
# Our model's injury/research adjustments are where the edge comes from.
_SEED_ML: dict[tuple[int, int], tuple[int, int]] = {
    (1, 16): (-4000, 2500),
    (2, 15): (-900,  600),
    (3, 14): (-580,  420),
    (4, 13): (-360,  285),
    (5, 12): (-235,  195),
    (6, 11): (-185,  155),
    (7, 10): (-155,  130),
    (8,  9): (-120,  100),
}


def _build_injury_note(team_a: str, team_b: str) -> str:
    notes = []
    for t in [team_a, team_b]:
        inj_adj = TEAM_DATA[t].get("injury_adjustment", 0)
        if inj_adj <= -2.0:
            notes.append(f"{t} injuries ({inj_adj:+.1f} EM impact)")
    return " | ".join(notes)


def calculate_ev_opportunities(odds_data: dict) -> list[dict]:
    """
    Scan every confirmed R64 matchup for +EV vs standard seed-based market lines.
    Only R64 games are used — these are the only 100% confirmed games.
    Model incorporates full injury/research adjustments; market uses seed baseline.
    Both sides of every game are evaluated.
    """
    opps = []

    for region in REGION_ORDER:
        for team_a, team_b in get_r64_matchups(region):
            wp = win_probability(team_a, team_b)
            seed_a, seed_b = wp["seed_a"], wp["seed_b"]

            # Identify favorite (lower seed number = stronger team)
            if seed_a <= seed_b:
                fav, dog = team_a, team_b
                fav_seed, dog_seed = seed_a, seed_b
                fav_prob, dog_prob = wp["win_prob_a"], wp["win_prob_b"]
            else:
                fav, dog = team_b, team_a
                fav_seed, dog_seed = seed_b, seed_a
                fav_prob, dog_prob = wp["win_prob_b"], wp["win_prob_a"]

            seed_key = (min(fav_seed, dog_seed), max(fav_seed, dog_seed))
            if seed_key not in _SEED_ML:
                continue
            fav_ml, dog_ml = _SEED_ML[seed_key]
            inj_note = _build_injury_note(team_a, team_b)

            for team, prob, ml in [(fav, fav_prob, fav_ml), (dog, dog_prob, dog_ml)]:
                opponent = dog if team == fav else fav
                ev = ev_calculation(prob, ml)
                if ev["is_positive_ev"] and ev["edge"] > 0.02:
                    opps.append({
                        "team": team,
                        "opponent": opponent,
                        "matchup": f"({seed_a}) {team_a} vs ({seed_b}) {team_b}",
                        "region": region,
                        "round": "Round of 64",
                        "bet_type": f"{team} ML",
                        "odds": ml,
                        "model_prob": round(prob, 4),
                        "implied_prob": ev["implied_prob"],
                        "edge": round(ev["edge"], 4),
                        "ev_per_dollar": ev["ev_per_dollar"],
                        "kelly_pct": ev["kelly_pct"],
                        "rating": "STRONG" if ev["edge"] > 0.10 else "MODERATE",
                        "projected_spread": wp["projected_spread"],
                        "injury_note": inj_note,
                        "effective_em": round(
                            wp["effective_em_a"] if team == team_a else wp["effective_em_b"], 1
                        ),
                    })

    opps.sort(key=lambda x: x["edge"], reverse=True)
    return opps[:20]


def generate_parlays(ev_opps: list[dict]) -> list[dict]:
    """
    Build parlays exclusively from confirmed R64 +EV opportunities.
    Groups top edges into 2-leg and 3-leg tickets.
    """
    # Only confirmed R64 games with meaningful edge
    r64 = [o for o in ev_opps if o["round"] == "Round of 64" and o["edge"] > 0.04]
    if len(r64) < 2:
        return []

    parlays = []

    # Best 2-leg: top 2 by edge
    top2 = r64[:2]
    p1 = parlay_ev([
        {"team": o["team"], "label": f"{o['team']} ML vs {o['opponent']} ({o['odds']:+d})", "odds": o["odds"], "win_prob": o["model_prob"]}
        for o in top2
    ])
    p1["name"] = "Top-2 Edge R64 Parlay"
    p1["rationale"] = " + ".join(
        f"{o['team']} model {o['model_prob']*100:.0f}% vs market {o['implied_prob']*100:.0f}% (edge +{o['edge']*100:.1f}%)"
        for o in top2
    )
    parlays.append(p1)

    # Best 3-leg: top 3 by edge (if available)
    if len(r64) >= 3:
        top3 = r64[:3]
        p2 = parlay_ev([
            {"team": o["team"], "label": f"{o['team']} ML vs {o['opponent']} ({o['odds']:+d})", "odds": o["odds"], "win_prob": o["model_prob"]}
            for o in top3
        ])
        p2["name"] = "Top-3 Edge R64 Parlay"
        p2["rationale"] = " + ".join(
            f"{o['team']} (+{o['edge']*100:.1f}% edge)"
            for o in top3
        )
        parlays.append(p2)

    # Underdog-focused 2-leg: top 2 dogs (odds > 0) by edge
    dogs = [o for o in r64 if o["odds"] > 0][:2]
    if len(dogs) >= 2:
        p3 = parlay_ev([
            {"team": o["team"], "label": f"{o['team']} ML vs {o['opponent']} ({o['odds']:+d})", "odds": o["odds"], "win_prob": o["model_prob"]}
            for o in dogs
        ])
        p3["name"] = "R64 Underdog Value Parlay"
        p3["rationale"] = "Two model-identified underdogs where injury/research gives us significant edge over market."
        parlays.append(p3)

    parlays = [p for p in parlays if p["is_positive_ev"]]
    parlays.sort(key=lambda x: x["ev_per_dollar"], reverse=True)
    return parlays


def generate_alerts(ev_opps: list[dict], injuries: list[dict]) -> list[dict]:
    alerts = []
    for opp in ev_opps[:5]:
        if opp["edge"] > 0.06:
            alerts.append({
                "type": "EV",
                "severity": "HIGH" if opp["edge"] > 0.12 else "MEDIUM",
                "message": f"+EV: {opp['team']} ML ({opp['odds']:+d}) in {opp.get('matchup', opp['team']+' vs '+opp['opponent'])} — Model {opp['model_prob']*100:.0f}% vs Market {opp['implied_prob']*100:.0f}% — Edge: +{opp['edge']*100:.1f}%",
                "team": opp["team"],
            })
    for inj in injuries:
        if inj.get("status", "").upper() in ("OUT", "QUESTIONABLE"):
            alerts.append({
                "type": "INJURY",
                "severity": "HIGH" if "OUT" in inj.get("status", "").upper() else "MEDIUM",
                "message": f"INJURY — {inj['team']}: {inj['player']} ({inj['position']}) {inj['status']}: {inj.get('detail','')[:80]}",
                "team": inj["team"],
            })
    return alerts


# ─── API Endpoints ────────────────────────────────────────────────────────────
@app.get("/api/state")
async def get_state():
    return JSONResponse(content={
        **{k: v for k, v in state.items() if k != "bracket_sim"},
        "probabilities": state.get("probabilities") or championship_probabilities(),
    })


@app.get("/api/bracket")
async def get_bracket():
    sim = state.get("bracket_sim") or simulate_full_bracket()
    return JSONResponse(content=sim)


@app.get("/api/bracket/region/{region}")
async def get_region(region: str):
    from probability_engine import simulate_region
    sim = state.get("bracket_sim", {})
    region_sim = sim.get("regions", {}).get(region) or simulate_region(region)
    teams = get_teams_by_region(region)
    return JSONResponse(content={"region": region, "teams": teams, "simulation": region_sim})


@app.get("/api/bracket/predicted-path")
async def get_predicted_path():
    return JSONResponse(content={
        "predicted_bracket": get_predicted_bracket_path(),
        "notable_upsets": NOTABLE_UPSETS,
        "round_schedule": ROUND_INFO,
    })


@app.get("/api/probabilities")
async def get_probabilities():
    return JSONResponse(content=state.get("probabilities") or championship_probabilities())


@app.get("/api/matchup/{team_a}/{team_b}")
async def get_matchup(team_a: str, team_b: str):
    return JSONResponse(content=win_probability(team_a, team_b))


@app.get("/api/ev")
async def get_ev():
    return JSONResponse(content={"opportunities": state.get("ev_opportunities", []), "updated_at": state.get("last_updated")})


@app.get("/api/parlays")
async def get_parlays_ep():
    return JSONResponse(content={"parlays": state.get("parlays", []), "updated_at": state.get("last_updated")})


@app.get("/api/odds")
async def get_odds():
    return JSONResponse(content=state.get("odds", get_demo_odds()))


@app.get("/api/injuries")
async def get_injuries():
    return JSONResponse(content={"injuries": state.get("injuries", get_known_injuries())})


@app.get("/api/scores")
async def get_scores():
    return JSONResponse(content=state.get("scores", {"games": []}))


@app.get("/api/teams")
async def get_teams():
    return JSONResponse(content={"teams": TEAM_DATA, "total": len(TEAM_DATA)})


@app.post("/api/result")
async def post_result(region: str, round_name: str, winner: str, loser: str, score: str = ""):
    state["results"][region][f"{round_name}_{winner}"] = {
        "winner": winner, "loser": loser, "score": score, "round": round_name
    }
    state["bracket_sim"] = simulate_full_bracket()
    state["probabilities"] = championship_probabilities()
    state["ev_opportunities"] = calculate_ev_opportunities(state["odds"])
    return JSONResponse(content={"status": "result recorded", "updated_probs": state["probabilities"]})


@app.post("/api/injury")
async def post_injury(team: str, player: str, description: str, em_impact: float = 0.0):
    add_injury(team, f"{player}: {description}", em_impact)
    state["bracket_sim"] = simulate_full_bracket()
    state["probabilities"] = championship_probabilities()
    return JSONResponse(content={"status": "injury added", "new_probs": state["probabilities"]})


@app.post("/api/force-update")
async def force_update(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_all_data)
    return JSONResponse(content={"status": "update triggered"})


@app.get("/api/health")
async def health():
    return {"status": "ok", "update_count": state["update_count"], "last_updated": state["last_updated"], "teams": len(TEAM_DATA)}


# ─── Static + Frontend ────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
