"""
Data fetching module for NCAA Tournament dashboard.
Pulls live data from ESPN API (public), The Odds API (requires key), and ESPN injury feed.
"""
import os
import asyncio
import logging
from datetime import datetime
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

ESPN_SCOREBOARD = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
ESPN_TOURNAMENT = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/tournament/bracket"
ESPN_INJURIES = "https://site.api.espn.com/apis/v2/sports/basketball/mens-college-basketball/injuries"
ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# Tracked teams for Final Four
TRACKED_TEAMS = {"Arizona Wildcats", "Michigan Wolverines", "Duke Blue Devils", "Houston Cougars",
                 "Arizona", "Michigan", "Duke", "Houston"}

# Short name mapping
SHORT_NAMES = {
    "Arizona Wildcats": "Arizona",
    "Michigan Wolverines": "Michigan",
    "Duke Blue Devils": "Duke",
    "Houston Cougars": "Houston",
}


async def fetch_espn_scores() -> dict:
    """Fetch live/recent scores from ESPN API."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(ESPN_SCOREBOARD, params={"groups": "50", "limit": 100})
            resp.raise_for_status()
            data = resp.json()
            games = []
            for event in data.get("events", []):
                comps = event.get("competitions", [])
                if not comps:
                    continue
                comp = comps[0]
                competitors = comp.get("competitors", [])
                if len(competitors) < 2:
                    continue
                home = competitors[0]
                away = competitors[1]
                home_name = home.get("team", {}).get("displayName", "")
                away_name = away.get("team", {}).get("displayName", "")

                # Only include tracked teams or tournament games
                if not any(n in TRACKED_TEAMS for n in [home_name, away_name]):
                    # Check if it's a tournament game by name
                    if "NCAA" not in event.get("name", "") and "Tournament" not in event.get("name", ""):
                        continue

                status = comp.get("status", {})
                game = {
                    "id": event.get("id"),
                    "name": event.get("name"),
                    "date": event.get("date"),
                    "home": SHORT_NAMES.get(home_name, home_name),
                    "away": SHORT_NAMES.get(away_name, away_name),
                    "home_score": int(home.get("score", 0) or 0),
                    "away_score": int(away.get("score", 0) or 0),
                    "home_winner": home.get("winner", False),
                    "away_winner": away.get("winner", False),
                    "status": status.get("type", {}).get("name", ""),
                    "status_detail": status.get("type", {}).get("description", ""),
                    "period": status.get("period", 0),
                    "clock": status.get("displayClock", ""),
                    "venue": comp.get("venue", {}).get("fullName", ""),
                    "neutral": comp.get("neutralSite", False),
                }
                games.append(game)
            return {"games": games, "updated_at": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"ESPN scores fetch error: {e}")
            return {"games": [], "updated_at": datetime.utcnow().isoformat(), "error": str(e)}


async def fetch_espn_tournament_bracket() -> dict:
    """Fetch NCAA Tournament bracket data from ESPN."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(ESPN_TOURNAMENT)
            resp.raise_for_status()
            data = resp.json()
            return {"bracket": data, "updated_at": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.error(f"ESPN bracket fetch error: {e}")
            return {"bracket": {}, "updated_at": datetime.utcnow().isoformat(), "error": str(e)}


async def fetch_espn_injuries() -> list[dict]:
    """Fetch injury reports from ESPN fantasy injury feed."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(ESPN_INJURIES)
            resp.raise_for_status()
            data = resp.json()
            injuries = []
            for item in data.get("items", []):
                athlete = item.get("athlete", {})
                team_name = athlete.get("team", {}).get("displayName", "")
                short_name = SHORT_NAMES.get(team_name, team_name)
                if not any(short_name == t for t in ["Arizona", "Michigan", "Duke", "Houston"]):
                    continue
                injuries.append({
                    "team": short_name,
                    "player": athlete.get("displayName", ""),
                    "position": athlete.get("position", {}).get("abbreviation", ""),
                    "status": item.get("type", {}).get("description", ""),
                    "detail": item.get("headline", ""),
                    "updated": item.get("date", ""),
                })
            return injuries
        except Exception as e:
            logger.error(f"ESPN injuries fetch error: {e}")
            # Return hardcoded known injuries as fallback
            return get_known_injuries()


def get_known_injuries() -> list[dict]:
    """Hardcoded known injuries from research (fallback)."""
    return [
        {
            "team": "Duke",
            "player": "Caleb Foster",
            "position": "PG",
            "status": "OUT",
            "detail": "Foot fracture, season-ending surgery. Cayden Boozer (28% from 3) is primary backup.",
            "updated": "2026-02-01",
            "impact": -2.5,
        },
        {
            "team": "Duke",
            "player": "Patrick Ngongba II",
            "position": "C",
            "status": "Questionable",
            "detail": "Foot soreness, possible return for Final Four. Being evaluated daily.",
            "updated": "2026-03-15",
            "impact": -0.5,
        },
        {
            "team": "Arizona",
            "player": "Jaden Bradley",
            "position": "G",
            "status": "Active",
            "detail": "Left wrist injury in Big 12 final, X-ray negative. Cleared to play.",
            "updated": "2026-03-14",
            "impact": 0.0,
        },
    ]


async def fetch_odds(sport_key: str = "basketball_ncaab", api_key: Optional[str] = None) -> dict:
    """
    Fetch betting odds from The Odds API.
    Requires ODDS_API_KEY environment variable.
    Free tier: 500 requests/month.
    Sign up at https://the-odds-api.com
    """
    key = api_key or os.environ.get("ODDS_API_KEY")
    if not key:
        logger.warning("No ODDS_API_KEY set — returning demo odds data")
        return get_demo_odds()

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(
                f"{ODDS_API_BASE}/sports/{sport_key}/odds",
                params={
                    "apiKey": key,
                    "regions": "us",
                    "markets": "h2h,spreads,totals",
                    "oddsFormat": "american",
                    "bookmakers": "draftkings,fanduel,betmgm,caesars",
                },
            )
            resp.raise_for_status()
            events = resp.json()
            processed = []
            for event in events:
                home = event.get("home_team", "")
                away = event.get("away_team", "")
                # Filter for tracked teams
                if not any(t in [home, away] for t in TRACKED_TEAMS):
                    continue
                books = {}
                for bm in event.get("bookmakers", []):
                    for market in bm.get("markets", []):
                        market_key = market.get("key")
                        outcomes = {}
                        for outcome in market.get("outcomes", []):
                            outcomes[outcome["name"]] = outcome.get("price")
                        books.setdefault(bm["key"], {})[market_key] = outcomes

                processed.append({
                    "home": SHORT_NAMES.get(home, home),
                    "away": SHORT_NAMES.get(away, away),
                    "commence_time": event.get("commence_time"),
                    "books": books,
                    "best_lines": _get_best_lines(books, home, away),
                })

            return {
                "events": processed,
                "updated_at": datetime.utcnow().isoformat(),
                "requests_remaining": resp.headers.get("x-requests-remaining", "unknown"),
            }
        except Exception as e:
            logger.error(f"Odds API fetch error: {e}")
            return get_demo_odds()


def _get_best_lines(books: dict, home: str, away: str) -> dict:
    """Extract best available lines across bookmakers."""
    best = {"h2h": {}, "spread": {}, "total": {}}
    for bm, markets in books.items():
        for market_key, outcomes in markets.items():
            if market_key == "h2h":
                for team, odds in outcomes.items():
                    if odds is not None:
                        short = SHORT_NAMES.get(team, team)
                        if short not in best["h2h"] or odds > best["h2h"][short]:
                            best["h2h"][short] = odds
            elif market_key == "spreads":
                for team, odds in outcomes.items():
                    short = SHORT_NAMES.get(team, team)
                    best["spread"][short] = odds
            elif market_key == "totals":
                best["total"] = outcomes
    return best


def get_demo_odds() -> dict:
    """
    Demo odds based on pre-research market lines.
    These are approximate lines from DraftKings/FanDuel circa tournament open.
    Update with live lines once ODDS_API_KEY is configured.
    """
    return {
        "events": [
            {
                "home": "Arizona",
                "away": "Michigan",
                "commence_time": "2026-04-05T18:00:00Z",
                "note": "DEMO ODDS — configure ODDS_API_KEY for live lines",
                "best_lines": {
                    "h2h": {"Arizona": -300, "Michigan": +240},
                    "spread": {"Arizona": -6.5, "Michigan": +6.5},
                    "total": {"Over": -110, "Under": -110, "line": 152.5},
                },
                "books": {
                    "draftkings": {
                        "h2h": {"Arizona": -295, "Michigan": +235},
                        "spreads": {"Arizona": -6.5, "Michigan": +6.5},
                        "totals": {"Over": -110, "Under": -110},
                    }
                },
            },
            {
                "home": "Duke",
                "away": "Houston",
                "commence_time": "2026-04-05T21:00:00Z",
                "note": "DEMO ODDS — configure ODDS_API_KEY for live lines",
                "best_lines": {
                    "h2h": {"Duke": -180, "Houston": +155},
                    "spread": {"Duke": -4.0, "Houston": +4.0},
                    "total": {"Over": -110, "Under": -110, "line": 138.5},
                },
                "books": {
                    "draftkings": {
                        "h2h": {"Duke": -175, "Houston": +150},
                        "spreads": {"Duke": -4.0, "Houston": +4.0},
                        "totals": {"Over": -110, "Under": -110},
                    }
                },
            },
            {
                "home": "TBD",
                "away": "TBD",
                "commence_time": "2026-04-07T21:00:00Z",
                "note": "Championship game — lines post after semis",
                "best_lines": {
                    "h2h": {"Arizona": -150, "Houston": +380},
                    "total": {"line": 145.0},
                },
                "books": {},
                "championship": True,
            },
        ],
        "updated_at": datetime.utcnow().isoformat(),
        "is_demo": True,
    }


async def fetch_all_data() -> dict:
    """Fetch all data sources in parallel."""
    scores_task = fetch_espn_scores()
    injuries_task = fetch_espn_injuries()
    odds_task = fetch_odds()

    scores, injuries, odds = await asyncio.gather(
        scores_task, injuries_task, odds_task, return_exceptions=True
    )

    return {
        "scores": scores if not isinstance(scores, Exception) else {"games": [], "error": str(scores)},
        "injuries": injuries if not isinstance(injuries, Exception) else get_known_injuries(),
        "odds": odds if not isinstance(odds, Exception) else get_demo_odds(),
        "fetched_at": datetime.utcnow().isoformat(),
    }
