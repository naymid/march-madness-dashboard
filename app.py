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


# ─── EV / Parlay Logic ───────────────────────────────────────────────────────
def _get_ml_for_team(odds_data: dict, team: str) -> Optional[int]:
    for event in odds_data.get("events", []):
        h2h = event.get("best_lines", {}).get("h2h", {})
        if team in h2h:
            return h2h[team]
    return None


def calculate_ev_opportunities(odds_data: dict) -> list[dict]:
    opps = []
    sim = state.get("bracket_sim", {})
    ff = sim.get("final_four", {})
    champ = sim.get("championship", {})

    # Final Four lines from odds feed
    for semi_key, game in ff.items():
        for team, prob, opp in [
            (game["team_a"], game["win_prob_a"], game["team_b"]),
            (game["team_b"], game["win_prob_b"], game["team_a"]),
        ]:
            ml = _get_ml_for_team(odds_data, team)
            if ml is not None:
                ev = ev_calculation(prob, ml)
                if ev["is_positive_ev"]:
                    opps.append({
                        "team": team, "opponent": opp,
                        "bet_type": f"{semi_key.replace('_', ' ')} ML",
                        "round": "Final Four", "odds": ml,
                        "model_prob": round(prob, 4),
                        "implied_prob": ev["implied_prob"],
                        "edge": round(ev["edge"], 4),
                        "ev_per_dollar": ev["ev_per_dollar"],
                        "kelly_pct": ev["kelly_pct"],
                        "rating": "STRONG" if ev["edge"] > 0.10 else "MODERATE",
                    })

    # Championship lines
    if champ and champ.get("team_a"):
        for team, prob, opp in [
            (champ["team_a"], champ.get("win_prob_a", 0), champ["team_b"]),
            (champ["team_b"], champ.get("win_prob_b", 0), champ["team_a"]),
        ]:
            ml = _get_ml_for_team(odds_data, team)
            if ml is not None:
                ev = ev_calculation(prob, ml)
                if ev["is_positive_ev"]:
                    opps.append({
                        "team": team, "opponent": opp,
                        "bet_type": "Championship ML",
                        "round": "Championship", "odds": ml,
                        "model_prob": round(prob, 4),
                        "implied_prob": ev["implied_prob"],
                        "edge": round(ev["edge"], 4),
                        "ev_per_dollar": ev["ev_per_dollar"],
                        "kelly_pct": ev["kelly_pct"],
                        "rating": "STRONG" if ev["edge"] > 0.10 else "MODERATE",
                    })

    # R64 — scan all matchups for significant line value
    for region in REGION_ORDER:
        for team_a, team_b in get_r64_matchups(region):
            wp = win_probability(team_a, team_b)
            spread = wp.get("projected_spread", 0)
            if abs(spread) > 8:
                fav = team_a if wp["win_prob_a"] > 0.5 else team_b
                fav_prob = max(wp["win_prob_a"], wp["win_prob_b"])
                dog_prob = 1 - fav_prob
                dog = team_b if fav == team_a else team_a
                # Check dog value — heavy favs often slightly over-priced
                approx_dog_odds = int((1 - dog_prob) / dog_prob * 100)
                ev = ev_calculation(dog_prob, approx_dog_odds)
                if ev["is_positive_ev"] and ev["edge"] > 0.03:
                    opps.append({
                        "team": dog, "opponent": fav,
                        "bet_type": f"R64 Upset ML (proj {fav} -{abs(spread):.0f})",
                        "round": "Round of 64", "odds": approx_dog_odds,
                        "model_prob": round(dog_prob, 4),
                        "implied_prob": ev["implied_prob"],
                        "edge": round(ev["edge"], 4),
                        "ev_per_dollar": ev["ev_per_dollar"],
                        "kelly_pct": ev["kelly_pct"],
                        "rating": "MODERATE",
                    })

    opps.sort(key=lambda x: x["edge"], reverse=True)
    return opps[:20]


def generate_parlays(ev_opps: list[dict]) -> list[dict]:
    sim = state.get("bracket_sim", {})
    ff = sim.get("final_four", {})
    if not ff:
        return []

    s1 = ff.get("Semifinal_1", {})
    s2 = ff.get("Semifinal_2", {})
    parlays = []

    az = s1.get("team_a", "Arizona")
    mi = s1.get("team_b", "Michigan")
    du = s2.get("team_a", "Duke")
    hu = s2.get("team_b", "Houston")
    az_prob = s1.get("win_prob_a", 0.82)
    hu_prob = s2.get("win_prob_b", 0.56)
    az_champ = state.get("probabilities", {}).get(az, 0.54)

    p1 = parlay_ev([
        {"team": hu, "label": f"{hu} ML (+155 demo)", "odds": 155, "win_prob": hu_prob},
        {"team": "Under", "label": f"{du} vs {hu} Under 138.5", "odds": -110, "win_prob": 0.58},
    ])
    p1["name"] = f"{hu} Game Parlay"
    p1["rationale"] = f"{hu} defensive identity slows {du}'s pace. Under + {hu} ML both +EV vs market."
    parlays.append(p1)

    p2 = parlay_ev([
        {"team": az, "label": f"{az} -6.5 vs {mi}", "odds": -110, "win_prob": az_prob * 0.82},
        {"team": az, "label": f"{az} Championship", "odds": -150, "win_prob": az_champ},
    ])
    p2["name"] = f"{az} Two-Leg Parlay"
    p2["rationale"] = f"{az} covers big vs {mi}, rides to title. Model 54.2% vs market 40% implied."
    parlays.append(p2)

    p3 = parlay_ev([
        {"team": az, "label": f"{az} beats {mi} (SF)", "odds": -300, "win_prob": az_prob},
        {"team": hu, "label": f"{hu} beats {du} (SF)", "odds": 155, "win_prob": hu_prob},
    ])
    p3["name"] = "Final Four Value Parlay"
    p3["rationale"] = f"Best of both semis. {az} dominant favorite + {hu} underdog edge in one ticket."
    parlays.append(p3)

    upset_opps = [o for o in ev_opps if o["round"] == "Round of 64" and o.get("edge", 0) > 0.05][:2]
    if len(upset_opps) >= 2:
        p4 = parlay_ev([
            {"team": l["team"], "label": f"{l['team']} R64 upset", "odds": l["odds"], "win_prob": l["model_prob"]}
            for l in upset_opps
        ])
        p4["name"] = "R64 Upset Double"
        p4["rationale"] = "Two model-identified R64 upsets with positive EV each."
        parlays.append(p4)

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
                "message": f"+EV: {opp['team']} {opp['bet_type']} ({opp['odds']:+d}) — Edge: +{opp['edge']*100:.1f}%",
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
