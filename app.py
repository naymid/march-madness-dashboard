"""
2026 NCAA March Madness Dashboard — FastAPI backend
Serves REST API + static frontend dashboard
Auto-updates via APScheduler background jobs
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
from probability_engine import (
    TEAMS,
    win_probability,
    championship_probabilities,
    ev_calculation,
    parlay_ev,
    apply_result_update,
    add_injury,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await update_all_data()
    scheduler.add_job(update_all_data, "interval", minutes=2, id="data_refresh")
    scheduler.start()
    logger.info("Dashboard started. Refreshing every 2 minutes.")
    yield
    scheduler.shutdown()


app = FastAPI(title="March Madness 2026 Dashboard", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-Memory State ──────────────────────────────────────────────────────────
state = {
    "scores": {"games": []},
    "injuries": get_known_injuries(),
    "odds": get_demo_odds(),
    "probabilities": {},
    "ev_opportunities": [],
    "parlays": [],
    "last_updated": datetime.utcnow().isoformat(),
    "update_count": 0,
    "alerts": [],
}

scheduler = AsyncIOScheduler()


# ─── Background Update Job ────────────────────────────────────────────────────
async def update_all_data():
    """Scheduled job: refresh all data and recalculate model."""
    global state
    try:
        logger.info("Updating data...")
        data = await fetch_all_data()

        state["scores"] = data["scores"]
        state["last_updated"] = data["fetched_at"]
        state["update_count"] += 1

        # Update injuries from live feed
        if data["injuries"]:
            state["injuries"] = data["injuries"]

        # Update odds
        state["odds"] = data["odds"]

        # Recalculate probabilities
        state["probabilities"] = championship_probabilities()

        # Recalculate EV opportunities
        state["ev_opportunities"] = calculate_ev_opportunities(data["odds"])

        # Generate parlay suggestions
        state["parlays"] = generate_parlays(state["ev_opportunities"])

        # Check for new results and update model
        check_for_upsets(data["scores"])

        # Generate alerts
        state["alerts"] = generate_alerts(state["ev_opportunities"], state["injuries"])

        logger.info(f"Update #{state['update_count']} complete. EV opps: {len(state['ev_opportunities'])}")
    except Exception as e:
        logger.error(f"Update failed: {e}", exc_info=True)


def calculate_ev_opportunities(odds_data: dict) -> list[dict]:
    """Compare model probabilities against market odds to find +EV bets."""
    opportunities = []
    probs = championship_probabilities()

    semifinal_probs = {
        "Arizona": probs["semi1"]["win_prob_a"],
        "Michigan": probs["semi1"]["win_prob_b"],
        "Duke": probs["semi2"]["win_prob_a"],
        "Houston": probs["semi2"]["win_prob_b"],
    }
    champ_probs = {k: v for k, v in probs.items() if k not in ("semi1", "semi2")}

    for event in odds_data.get("events", []):
        home = event.get("home", "")
        away = event.get("away", "")
        best = event.get("best_lines", {})
        is_champ = event.get("championship", False)

        for team in [home, away]:
            if team in ("TBD",):
                continue
            # Moneyline
            ml_odds = best.get("h2h", {}).get(team)
            if ml_odds is not None:
                # Semi final prob
                if is_champ:
                    model_prob = champ_probs.get(team, 0)
                    bet_type = "Championship ML"
                else:
                    model_prob = semifinal_probs.get(team, 0)
                    bet_type = "Semifinal ML"

                if model_prob > 0:
                    ev = ev_calculation(model_prob, ml_odds)
                    if ev["is_positive_ev"]:
                        opportunities.append({
                            "team": team,
                            "opponent": away if team == home else home,
                            "bet_type": bet_type,
                            "odds": ml_odds,
                            "model_prob": round(model_prob, 4),
                            "implied_prob": ev["implied_prob"],
                            "edge": round(ev["edge"], 4),
                            "ev_per_dollar": ev["ev_per_dollar"],
                            "kelly_pct": ev["kelly_pct"],
                            "rating": "STRONG" if ev["edge"] > 0.10 else "MODERATE",
                        })

            # Spread
            spread_odds = best.get("spread", {}).get(team)
            if spread_odds and not is_champ:
                spread_val = spread_odds if isinstance(spread_odds, (int, float)) else -110
                model_spread = win_probability(home, away)["projected_spread"] if team == home else -win_probability(home, away)["projected_spread"]
                market_spread = event.get("best_lines", {}).get("spread", {})
                # Get the line value (not the juice)
                line_val = None
                for k, v in market_spread.items():
                    if k == team:
                        line_val = v

                if line_val is not None and isinstance(line_val, (int, float)):
                    # Favorable spread if model thinks team covers by margin
                    if (team == home and model_spread < line_val - 1.5) or \
                       (team == away and model_spread > line_val + 1.5):
                        ev = ev_calculation(0.54, -110)  # Slight edge on spread
                        opportunities.append({
                            "team": team,
                            "opponent": away if team == home else home,
                            "bet_type": f"Spread ({'+' if line_val > 0 else ''}{line_val})",
                            "odds": -110,
                            "model_prob": 0.54,
                            "implied_prob": 0.524,
                            "edge": 0.016,
                            "ev_per_dollar": ev["ev_per_dollar"],
                            "kelly_pct": ev["kelly_pct"],
                            "rating": "MODERATE",
                        })

    # Sort by edge descending
    opportunities.sort(key=lambda x: x["edge"], reverse=True)
    return opportunities


def generate_parlays(ev_opps: list[dict]) -> list[dict]:
    """Generate suggested parlays from positive-EV legs."""
    probs = championship_probabilities()

    # Pre-built research parlays
    parlays = []

    # Parlay 1: Arizona Final Four win + Houston Final Four win
    az_sf_prob = probs["semi1"]["win_prob_a"]
    hu_sf_prob = probs["semi2"]["win_prob_b"]

    p1 = parlay_ev([
        {"team": "Arizona", "label": "Arizona beats Michigan (SF)", "odds": -300, "win_prob": az_sf_prob},
        {"team": "Houston", "label": "Houston beats Duke (SF)", "odds": 155, "win_prob": hu_sf_prob},
    ])
    p1["name"] = "Value Parlay: AZ + HOU Final Four"
    p1["rationale"] = "Arizona strong favorite; Houston +EV underdog. If both advance, AZ-HOU final is wild."
    parlays.append(p1)

    # Parlay 2: Houston ML + Under (Houston slows pace vs Duke)
    p2 = parlay_ev([
        {"team": "Houston", "label": "Houston ML (+155)", "odds": 155, "win_prob": hu_sf_prob},
        {"team": "Under", "label": "Duke vs Houston Under 138.5", "odds": -110, "win_prob": 0.58},
    ])
    p2["name"] = "Houston Game Parlay"
    p2["rationale"] = "Houston defensive identity slows Duke's pace. Under + Houston ML both +EV."
    parlays.append(p2)

    # Parlay 3: Arizona -6.5 + Championship
    az_champ = probs["Arizona"]
    p3 = parlay_ev([
        {"team": "Arizona", "label": "Arizona -6.5 vs Michigan", "odds": -110, "win_prob": 0.61},
        {"team": "Arizona", "label": "Arizona Championship", "odds": -150, "win_prob": az_champ},
    ])
    p3["name"] = "Arizona Two-Leg Parlay"
    p3["rationale"] = "Arizona covers comfortably vs Michigan then rides to championship. Model prob > implied."
    parlays.append(p3)

    # Filter to only +EV parlays
    parlays = [p for p in parlays if p["is_positive_ev"]]
    parlays.sort(key=lambda x: x["ev_per_dollar"], reverse=True)
    return parlays


def check_for_upsets(scores_data: dict):
    """Detect completed games and update model if upsets occurred."""
    for game in scores_data.get("games", []):
        if game.get("status") == "STATUS_FINAL":
            home = game.get("home")
            away = game.get("away")
            if game.get("home_winner"):
                winner, loser = home, away
            elif game.get("away_winner"):
                winner, loser = away, home
            else:
                continue

            # Check if this was a tracked team losing
            if loser in TEAMS and TEAMS[loser].adj_em > -90:
                apply_result_update(winner, loser)
                logger.info(f"Result recorded: {winner} over {loser}")


def generate_alerts(ev_opps: list[dict], injuries: list[dict]) -> list[dict]:
    """Generate dashboard alerts for noteworthy situations."""
    alerts = []

    # Strong EV alerts
    for opp in ev_opps:
        if opp["edge"] > 0.08:
            alerts.append({
                "type": "EV",
                "severity": "HIGH" if opp["edge"] > 0.12 else "MEDIUM",
                "message": f"+EV: {opp['team']} {opp['bet_type']} at {opp['odds']:+d} — Edge: {opp['edge']*100:.1f}%",
                "team": opp["team"],
            })

    # Injury alerts
    for inj in injuries:
        if inj.get("status", "").upper() in ("OUT", "QUESTIONABLE"):
            alerts.append({
                "type": "INJURY",
                "severity": "HIGH" if inj.get("status", "").upper() == "OUT" else "MEDIUM",
                "message": f"{inj['team']} — {inj['player']} ({inj['position']}): {inj['status']} — {inj.get('detail', '')[:80]}",
                "team": inj["team"],
            })

    return alerts


# ─── API Endpoints ────────────────────────────────────────────────────────────
@app.get("/api/state")
async def get_state():
    """Full dashboard state."""
    return JSONResponse(content={
        **state,
        "probabilities": state.get("probabilities") or championship_probabilities(),
    })


@app.get("/api/probabilities")
async def get_probabilities():
    """Current win probabilities for all matchups."""
    probs = championship_probabilities()
    return JSONResponse(content=probs)


@app.get("/api/matchup/{team_a}/{team_b}")
async def get_matchup(team_a: str, team_b: str):
    """Head-to-head probability for a specific matchup."""
    return JSONResponse(content=win_probability(team_a, team_b))


@app.get("/api/ev")
async def get_ev_opportunities():
    """Current +EV betting opportunities."""
    return JSONResponse(content={
        "opportunities": state.get("ev_opportunities", []),
        "updated_at": state.get("last_updated"),
    })


@app.get("/api/parlays")
async def get_parlays():
    """Suggested positive-EV parlays."""
    return JSONResponse(content={
        "parlays": state.get("parlays", []),
        "updated_at": state.get("last_updated"),
    })


@app.get("/api/odds")
async def get_odds():
    """Current betting lines."""
    return JSONResponse(content=state.get("odds", get_demo_odds()))


@app.get("/api/injuries")
async def get_injuries():
    """Current injury report."""
    return JSONResponse(content={"injuries": state.get("injuries", get_known_injuries())})


@app.get("/api/scores")
async def get_scores():
    """Live/recent game scores."""
    return JSONResponse(content=state.get("scores", {"games": []}))


@app.post("/api/force-update")
async def force_update(background_tasks: BackgroundTasks):
    """Manually trigger a data refresh."""
    background_tasks.add_task(update_all_data)
    return JSONResponse(content={"status": "update triggered"})


@app.post("/api/injury")
async def add_injury_endpoint(team: str, player: str, description: str, em_impact: float = 0.0):
    """Manually add an injury to the model."""
    add_injury(team, f"{player}: {description}", em_impact)
    state["probabilities"] = championship_probabilities()
    return JSONResponse(content={"status": "injury added", "new_probs": state["probabilities"]})


@app.get("/api/health")
async def health():
    return {"status": "ok", "update_count": state["update_count"], "last_updated": state["last_updated"]}



# ─── Serve Frontend ───────────────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main dashboard HTML."""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
