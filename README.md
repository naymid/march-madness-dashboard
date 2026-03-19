# 2026 NCAA March Madness Dashboard

Live analytics dashboard for the 2026 NCAA Tournament Final Four.
Auto-updates probabilities, tracks live betting lines, flags +EV bets, and suggests parlays.

## Features

- **Win probabilities** — Log5 model using KenPom/EvanMiya ratings with injury adjustments and H2H factors
- **Live scores** — ESPN API (updates every 2 min)
- **Live betting lines** — The Odds API (moneylines, spreads, totals across DraftKings/FanDuel/BetMGM/Caesars)
- **+EV detector** — Compares model probabilities vs market implied odds, flags positive-EV bets
- **Parlay builder** — Auto-generates positive-EV parlay combinations
- **Injury tracker** — ESPN injury feed + hardcoded known injuries as fallback
- **Auto-refresh** — Backend updates every 2 minutes, frontend polls every 30 seconds

## Run Locally

```bash
cd march-madness-dashboard
pip install -r requirements.txt
python app.py
# Open http://localhost:8000
```

## Deploy to Railway

1. Push this folder to a GitHub repo
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select the repo
4. Add environment variable: `ODDS_API_KEY=your_key` (get free key at [the-odds-api.com](https://the-odds-api.com))
5. Railway auto-detects the Dockerfile and deploys

## Get Live Odds

Without an API key, the dashboard runs on demo odds from our pre-research.
To enable live lines:

1. Sign up free at https://the-odds-api.com (500 req/month free)
2. Set env var: `ODDS_API_KEY=your_key_here`
3. Restart the app

## Model Details

**Teams tracked:** Arizona, Michigan, Duke, Houston (Final Four)

**Factors:**
- KenPom Adjusted Efficiency Margin (AdjEM) as base rating
- EvanMiya consistency classification (Strong/Streaky/Suspect)
- Kill Shot % (ability to build 10+ point runs)
- Injury adjustment (Caleb Foster OUT = -2.5 pts for Duke)
- Head-to-head neutral site results
- Coaching tournament experience

**Key research findings encoded:**
- Duke beat Michigan 68-63 neutral site Feb 21 (boards 41-28)
- Arizona beat Houston 79-74 Big 12 Championship
- Houston beat Duke in 2025 Final Four from -14 with 8 min left
- Arizona 8-2 all-time vs Michigan
- Caleb Foster (Duke PG) OUT for season — Cayden Boozer (28% from 3) replacing

## Manual Injury Update

```bash
curl -X POST "http://localhost:8000/api/injury?team=Duke&player=Ngongba&description=OUT+foot&em_impact=-1.5"
```
