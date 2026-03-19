"""
2026 NCAA Men's Basketball Tournament — Real bracket data.
All 68 teams with actual seeds, regions, real KenPom rankings,
real injuries, venue advantages, and coach tournament history.

Sources: ESPN, CBS Sports, KenPom, SportsBettingDime, Yahoo Sports (March 2026)

First Four results (Dayton, OH — March 17-18):
  - Texas 68, NC State 66 (Tramon Mark buzzer beater) → Texas plays #6 BYU (West)
  - Howard 86, UMBC 83 → Howard plays #1 Michigan (Midwest)
  - Prairie View A&M 67, Lehigh 55 → Prairie View plays #1 Florida (South)
  - Miami (OH) beat SMU → Miami(OH) plays #6 Tennessee (Midwest)

Final Four location: Lucas Oil Stadium, Indianapolis, IN (April 4 & 6)
National bracket pairings: East/South on one side, West/Midwest on the other.
→ Final Four: Duke (East) vs Houston (South), Arizona (West) vs Michigan (Midwest)
"""

# ─── Full 64+4 team data ──────────────────────────────────────────────────────
# adj_em: KenPom Adjusted Efficiency Margin (estimated from rank + O/D ranks)
# adj_o / adj_d: per-100-possession efficiency (offense higher = better; defense lower = better)
# consistency: Strong | Streaky | Suspect (EvanMiya-proxy classification)
# kill_shot_pct: frequency of 10+ unanswered runs (proxy from scoring burst data)
# injury_adjustment: negative EM penalty from injuries (OUT/Q players)
# venue_region: which region they play Sweet 16/E8 in (crowd factor)

TEAM_DATA = {

    # ════════════════════════════════════════════════════════════
    # EAST REGION  (R64/R32: Buffalo NY + Philadelphia PA | S16/E8: Washington DC)
    # East champ plays South champ in Final Four
    # ════════════════════════════════════════════════════════════

    "Duke": {
        "adj_em": 37.4, "adj_o": 125.2, "adj_d": 87.8, "adj_t": 71.3,
        "kenpom_rank": 1, "seed": 1, "region": "East",
        "consistency": "Strong", "kill_shot_pct": 0.74,
        "injury_adjustment": -1.8,  # Foster OUT (8.5 PPG), Ngongba Q (10.7 PPG)
        "injuries": [
            "Caleb Foster PG: broken right foot (regular-season finale), OUT — likely out until Final Four if Duke advances",
            "Patrick Ngongba II C: foot soreness, QUESTIONABLE (10.7 PPG, 6.2 RPG)",
        ],
        "record": "32-2", "coach": "Jon Scheyer", "coach_wins": 11, "coach_ffs": 2,
        "stars": "Cameron Boozer (22.7/10.2, 1st Team AA), Isaiah Evans (14.5 PPG)",
        "notes": "No. 1 overall seed. Highest offensive rating in KenPom history. AdjO rank #4, AdjD rank #2.",
        "venue_home_factor": 0.0,
    },
    "UConn": {
        "adj_em": 26.8, "adj_o": 116.4, "adj_d": 89.6, "adj_t": 69.1,
        "kenpom_rank": 11, "seed": 2, "region": "East",
        "consistency": "Strong", "kill_shot_pct": 0.66,
        "injury_adjustment": -0.8,  # Demary Jr Q (10.9), Stewart Q (4.5)
        "injuries": [
            "Silas Demary Jr G: ankle, QUESTIONABLE (10.9 PPG)",
            "Jaylin Stewart F: knee, QUESTIONABLE (4.5 PPG)",
        ],
        "record": "29-5", "coach": "Dan Hurley", "coach_wins": 18, "coach_ffs": 2,
        "stars": "Solo Ball (13.9 PPG), Alex Karaban (12.9 PPG), Tarris Reed Jr. (13.8 PPG)",
        "notes": "Seeking 3rd national title in 4 years. Won 18 straight. Lost Big East final to St. John's.",
        "venue_home_factor": 0.0,
    },
    "Michigan State": {
        "adj_em": 28.2, "adj_o": 113.8, "adj_d": 85.6, "adj_t": 68.4,
        "kenpom_rank": 9, "seed": 3, "region": "East",
        "consistency": "Strong", "kill_shot_pct": 0.68,
        "injury_adjustment": -0.3,  # Divine Ugochukwu foot OUT (5.1 PPG, minor)
        "injuries": ["Divine Ugochukwu G: foot, OUT (5.1 PPG — limited impact)"],
        "record": "25-7", "coach": "Tom Izzo", "coach_wins": 34, "coach_ffs": 8,
        "stars": "Jeremy Fears Jr. (15.5 PPG, 9.1 APG)",
        "notes": "Top-10 defense. Izzo: 8 Final Fours, ruthless tournament coach.",
        "venue_home_factor": 0.0,
    },
    "Kansas": {
        "adj_em": 20.4, "adj_o": 117.2, "adj_d": 96.8, "adj_t": 70.6,
        "kenpom_rank": 21, "seed": 4, "region": "East",
        "consistency": "Streaky", "kill_shot_pct": 0.55,
        "injury_adjustment": -1.2,  # Peterson missed 11 games
        "injuries": ["Darryn Peterson G: missed 11 games with undisclosed injury, NOW playing (19.9 PPG — projected #1 NBA pick)"],
        "record": "23-10", "coach": "Bill Self", "coach_wins": 28, "coach_ffs": 5,
        "stars": "Darryn Peterson (19.9 PPG — projected #1 NBA Draft pick)",
        "notes": "Overseeded by analytics (~10 lines per KenPom). 3-4 in final 7 games. KenPom #21.",
        "venue_home_factor": 0.0,
    },
    "St. John's": {
        "adj_em": 22.6, "adj_o": 111.8, "adj_d": 89.2, "adj_t": 68.9,
        "kenpom_rank": 16, "seed": 5, "region": "East",
        "consistency": "Strong", "kill_shot_pct": 0.64,
        "injury_adjustment": 0.0,
        "injuries": ["Casper Pohto F: hip, OUT (0.3 PPG — negligible)"],
        "record": "28-6", "coach": "Rick Pitino", "coach_wins": 22, "coach_ffs": 2,
        "stars": "Zuby Ejiofor (16.0 PPG, 7.1 RPG)",
        "notes": "Back-to-back Big East regular season titles. Won Big East Tournament (beat UConn in final). KenPom #16.",
        "venue_home_factor": 0.0,
    },
    "Louisville": {
        "adj_em": 19.8, "adj_o": 113.6, "adj_d": 93.8, "adj_t": 67.4,
        "kenpom_rank": 19, "seed": 6, "region": "East",
        "consistency": "Streaky", "kill_shot_pct": 0.54,
        "injury_adjustment": -2.1,  # Brown Jr. OUT for opening weekend
        "injuries": ["Mikel Brown Jr. PG: back injury, OUT for first two tournament games (starting PG — major loss)"],
        "record": "23-10", "coach": "Pat Kelsey", "coach_wins": 4, "coach_ffs": 0,
        "stars": "Team effort — Brown Jr. absence elevates other guards",
        "notes": "KenPom #19. WITHOUT starting PG for R64 and R32. Massive vulnerability.",
        "venue_home_factor": 0.0,
    },
    "UCLA": {
        "adj_em": 18.2, "adj_o": 113.1, "adj_d": 94.9, "adj_t": 69.7,
        "kenpom_rank": 28, "seed": 7, "region": "East",
        "consistency": "Streaky", "kill_shot_pct": 0.52,
        "injury_adjustment": -3.2,  # Bilodeau Q (17.6) + Dent Q (13.5) — both stars questionable
        "injuries": [
            "Tyler Bilodeau F: knee, QUESTIONABLE (17.6 PPG — leading scorer)",
            "Donovan Dent G: calf, QUESTIONABLE (13.5 PPG — #2 scorer)",
        ],
        "record": "22-11", "coach": "Mick Cronin", "coach_wins": 9, "coach_ffs": 0,
        "stars": "Tyler Bilodeau (17.6 PPG), Donovan Dent (13.5 PPG) — both questionable",
        "notes": "Two top scorers questionable. Major injury cloud. Dangerous upset candidate for UCF.",
        "venue_home_factor": 0.0,
    },
    "Ohio State": {
        "adj_em": 20.8, "adj_o": 114.2, "adj_d": 93.4, "adj_t": 70.1,
        "kenpom_rank": 26, "seed": 8, "region": "East",
        "consistency": "Streaky", "kill_shot_pct": 0.56,
        "injury_adjustment": -0.4,  # Chatman Q (4.5 — minor)
        "injuries": ["Taison Chatman G: groin, QUESTIONABLE (4.5 PPG — minimal impact)"],
        "record": "21-12", "coach": "Jake Diebler", "coach_wins": 3, "coach_ffs": 0,
        "stars": "Bruce Thornton, Devin Royal",
        "notes": "Analytics say underseeded — KenPom #26, Torvik #23. Should be ~1-2 seed higher.",
        "venue_home_factor": 0.0,
    },
    "TCU": {
        "adj_em": 16.4, "adj_o": 111.8, "adj_d": 95.4, "adj_t": 68.8,
        "kenpom_rank": 33, "seed": 9, "region": "East",
        "consistency": "Suspect", "kill_shot_pct": 0.48,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "20-13", "coach": "Jamie Dixon", "coach_wins": 11, "coach_ffs": 0,
        "stars": "Emanuel Miller",
        "notes": "KenPom #23 defense. Path through Ohio State difficult — Ohio State underseeded.",
        "venue_home_factor": 0.0,
    },
    "UCF": {
        "adj_em": 15.8, "adj_o": 111.2, "adj_d": 95.4, "adj_t": 69.4,
        "kenpom_rank": 36, "seed": 10, "region": "East",
        "consistency": "Suspect", "kill_shot_pct": 0.47,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "21-12", "coach": "Johnny Dawkins", "coach_wins": 5, "coach_ffs": 0,
        "stars": "Jaylin Marshall",
        "notes": "Faces UCLA — both Bilodeau and Dent questionable. Real upset opportunity.",
        "venue_home_factor": 0.0,
    },
    "South Florida": {
        "adj_em": 14.2, "adj_o": 110.4, "adj_d": 96.2, "adj_t": 67.8,
        "kenpom_rank": 44, "seed": 11, "region": "East",
        "consistency": "Streaky", "kill_shot_pct": 0.52,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "23-10", "coach": "Amir Abdur-Rahim", "coach_wins": 2, "coach_ffs": 0,
        "stars": "JJ Mandaquit (14.8 PPG)",
        "notes": "Won 11 straight games entering tournament. Faces Louisville WITHOUT Brown Jr. — live upset.",
        "venue_home_factor": 0.0,
    },
    "Northern Iowa": {
        "adj_em": 13.8, "adj_o": 109.8, "adj_d": 96.0, "adj_t": 66.4,
        "kenpom_rank": 42, "seed": 12, "region": "East",
        "consistency": "Strong", "kill_shot_pct": 0.49,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "24-9", "coach": "Ben Jacobson", "coach_wins": 4, "coach_ffs": 0,
        "stars": "Bowen Born",
        "notes": "Top-25 KenPom defense. Slow-tempo style can bother St. John's.",
        "venue_home_factor": 0.0,
    },
    "Cal Baptist": {
        "adj_em": 10.4, "adj_o": 107.2, "adj_d": 96.8, "adj_t": 68.1,
        "kenpom_rank": 68, "seed": 13, "region": "East",
        "consistency": "Suspect", "kill_shot_pct": 0.41,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "26-7", "coach": "Rick Croy", "coach_wins": 1, "coach_ffs": 0,
        "stars": "Shawn Holiday", "notes": "WAC champion.",
        "venue_home_factor": 0.0,
    },
    "North Dakota State": {
        "adj_em": 8.8, "adj_o": 106.1, "adj_d": 97.3, "adj_t": 67.6,
        "kenpom_rank": 82, "seed": 14, "region": "East",
        "consistency": "Suspect", "kill_shot_pct": 0.38,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "25-9", "coach": "Saul Phillips", "coach_wins": 2, "coach_ffs": 0,
        "stars": "Boden Skunberg", "notes": "Summit League champion.",
        "venue_home_factor": 0.0,
    },
    "Furman": {
        "adj_em": 6.4, "adj_o": 104.2, "adj_d": 97.8, "adj_t": 68.4,
        "kenpom_rank": 110, "seed": 15, "region": "East",
        "consistency": "Suspect", "kill_shot_pct": 0.34,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "23-11", "coach": "Bob Richey", "coach_wins": 1, "coach_ffs": 0,
        "stars": "JP Pegues", "notes": "SoCon champion.",
        "venue_home_factor": 0.0,
    },
    "Siena": {
        "adj_em": 3.2, "adj_o": 101.6, "adj_d": 98.4, "adj_t": 67.2,
        "kenpom_rank": 155, "seed": 16, "region": "East",
        "consistency": "Suspect", "kill_shot_pct": 0.28,
        "injury_adjustment": -1.4,  # Goodrick OUT + Chandler Q
        "injuries": [
            "Tasman Goodrick G: knee, OUT (9.7 PPG)",
            "Antonio Chandler G: non-injury related concern (7.3 PPG)",
        ],
        "record": "22-12", "coach": "Jamion Christian", "coach_wins": 1, "coach_ffs": 0,
        "stars": "Jackson Stormo", "notes": "MAAC champion. Two key players unavailable.",
        "venue_home_factor": 0.0,
    },

    # ════════════════════════════════════════════════════════════
    # WEST REGION  (R64/R32: San Diego CA + Portland OR | S16/E8: San Jose CA)
    # West champ plays Midwest champ in Final Four
    # ════════════════════════════════════════════════════════════

    "Arizona": {
        "adj_em": 34.8, "adj_o": 124.1, "adj_d": 89.3, "adj_t": 70.2,
        "kenpom_rank": 3, "seed": 1, "region": "West",
        "consistency": "Strong", "kill_shot_pct": 0.72,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "32-2", "coach": "Tommy Lloyd", "coach_wins": 8, "coach_ffs": 1,
        "stars": "Brayden Burries (16.0 PPG), Koa Peat (13.8 PPG), Jaden Bradley (13.4 PPG)",
        "notes": "Won first 23 games. Top-5 offense + top-3 defense per KenPom. AdjO #5, AdjD #3.",
        "venue_home_factor": 0.8,  # West coast games in San Diego/Portland — slight home feel
    },
    "Purdue": {
        "adj_em": 23.6, "adj_o": 124.8, "adj_d": 101.2, "adj_t": 68.2,
        "kenpom_rank": 8, "seed": 2, "region": "West",
        "consistency": "Streaky", "kill_shot_pct": 0.58,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "27-8", "coach": "Matt Painter", "coach_wins": 14, "coach_ffs": 0,
        "stars": "Braden Smith (14.9 PPG, 8.7 APG), Fletcher Loyer (13.6 PPG)",
        "notes": "Nation's #2 offense. BUT: went 6-7 in final 13 games. Started 17-1 then collapsed. Major late-season form concern. AdjO #2, AdjD #36.",
        "venue_home_factor": 0.0,
    },
    "Gonzaga": {
        "adj_em": 27.2, "adj_o": 118.4, "adj_d": 91.2, "adj_t": 70.8,
        "kenpom_rank": 10, "seed": 3, "region": "West",
        "consistency": "Strong", "kill_shot_pct": 0.65,
        "injury_adjustment": -3.6,  # Huff OUT since Jan 15 (17.8 PPG — massive loss)
        "injuries": ["Braden Huff C: dislocated kneecap (OUT since January 15), 17.8 PPG, 7.2 RPG — season-altering absence"],
        "record": "30-3", "coach": "Mark Few", "coach_wins": 24, "coach_ffs": 1,
        "stars": "Graham Ike (19.7 PPG) carries load without Huff",
        "notes": "WITHOUT star big man Huff for 2+ months. Gonzaga has adjusted but Ike faces major double-team pressure.",
        "venue_home_factor": 1.2,  # Portland is close to Gonzaga's Spokane home base
    },
    "Arkansas": {
        "adj_em": 19.4, "adj_o": 119.8, "adj_d": 100.4, "adj_t": 72.1,
        "kenpom_rank": 18, "seed": 4, "region": "West",
        "consistency": "Streaky", "kill_shot_pct": 0.58,
        "injury_adjustment": -0.6,  # Karter Knox Q (knee, 8.1)
        "injuries": ["Karter Knox F: knee, QUESTIONABLE (8.1 PPG)"],
        "record": "26-8", "coach": "John Calipari", "coach_wins": 39, "coach_ffs": 4,
        "stars": "Darius Acuff Jr. (22.2 PPG, 6.4 APG) — 'best under Calipari'",
        "notes": "Calipari says this is his best team at Arkansas. AdjO rank #6 — elite offense. Acuff is a potential lottery pick.",
        "venue_home_factor": 0.0,
    },
    "Wisconsin": {
        "adj_em": 17.8, "adj_o": 112.4, "adj_d": 94.6, "adj_t": 65.8,
        "kenpom_rank": 24, "seed": 5, "region": "West",
        "consistency": "Strong", "kill_shot_pct": 0.54,
        "injury_adjustment": -2.2,  # Winter Q (13.3), Janicki Q (2.2)
        "injuries": [
            "Nolan Winter C: ankle, QUESTIONABLE (13.3 PPG, 7.4 RPG — key post player)",
            "Jack Janicki F: wrist, QUESTIONABLE (2.2 PPG — minor)",
        ],
        "record": "24-10", "coach": "Greg Gard", "coach_wins": 6, "coach_ffs": 0,
        "stars": "John Blackwell (18.3 PPG)",
        "notes": "KenPom #24. Slow pace Wisconsin system. Nolan Winter injury significant for interior defense.",
        "venue_home_factor": 0.0,
    },
    "BYU": {
        "adj_em": 16.2, "adj_o": 113.8, "adj_d": 97.6, "adj_t": 69.4,
        "kenpom_rank": 38, "seed": 6, "region": "West",
        "consistency": "Streaky", "kill_shot_pct": 0.50,
        "injury_adjustment": -5.8,  # BOTH star players OUT — Saunders (18.0) + Baker (7.5) — catastrophic
        "injuries": [
            "Richie Saunders G: knee, OUT FOR SEASON (18.0 PPG — leading scorer, season-ending)",
            "Dawson Baker G: knee, OUT FOR SEASON (7.5 PPG — #3 scorer)",
        ],
        "record": "23-11", "coach": "Kevin Young", "coach_wins": 3, "coach_ffs": 0,
        "stars": "DEPLETED — lost two of top three scorers to injuries",
        "notes": "CATASTROPHIC injury situation. Saunders (18.0 PPG) + Baker both OUT. Faces Texas (11-seed) in R64. Major upset risk.",
        "venue_home_factor": 0.0,
    },
    "Miami (FL)": {
        "adj_em": 17.4, "adj_o": 112.8, "adj_d": 95.4, "adj_t": 70.2,
        "kenpom_rank": 31, "seed": 7, "region": "West",
        "consistency": "Streaky", "kill_shot_pct": 0.52,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "21-11", "coach": "Jim Larrañaga", "coach_wins": 16, "coach_ffs": 1,
        "stars": "Matthew Cleveland (15.2 PPG)",
        "notes": "Experienced ACC tournament team. Faces Missouri in R64.",
        "venue_home_factor": 0.0,
    },
    "Villanova": {
        "adj_em": 16.8, "adj_o": 112.1, "adj_d": 95.3, "adj_t": 68.8,
        "kenpom_rank": 29, "seed": 8, "region": "West",
        "consistency": "Streaky", "kill_shot_pct": 0.51,
        "injury_adjustment": -1.4,  # Hodge OUT (9.2)
        "injuries": ["Matthew Hodge G: knee, OUT (9.2 PPG — significant contributor)"],
        "record": "22-12", "coach": "Kyle Neptune", "coach_wins": 4, "coach_ffs": 0,
        "stars": "Eric Dixon (16.8 PPG)",
        "notes": "WITHOUT Hodge. Faces Utah State — analytics say Utah State underseeded.",
        "venue_home_factor": 0.0,
    },
    "Utah State": {
        "adj_em": 17.6, "adj_o": 113.4, "adj_d": 95.8, "adj_t": 67.9,
        "kenpom_rank": 32, "seed": 9, "region": "West",
        "consistency": "Strong", "kill_shot_pct": 0.54,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "24-9", "coach": "Jerrod Calhoun", "coach_wins": 2, "coach_ffs": 0,
        "stars": "Great Osobor (18.4 PPG, 9.2 RPG)",
        "notes": "Analysts call this 'best 8/9 matchup in bracket.' Utah State rated higher than Villanova by multiple systems. KenPom #32.",
        "venue_home_factor": 0.0,
    },
    "Missouri": {
        "adj_em": 12.8, "adj_o": 110.4, "adj_d": 97.6, "adj_t": 69.1,
        "kenpom_rank": 51, "seed": 10, "region": "West",
        "consistency": "Suspect", "kill_shot_pct": 0.46,
        "injury_adjustment": -2.1,  # Boateng OUT + Porter Q
        "injuries": [
            "Annor Boateng F: leg, OUT (2.7 PPG — minor)",
            "Jevon Porter G: lower leg, QUESTIONABLE (6.2 PPG)",
        ],
        "record": "19-14", "coach": "Dennis Gates", "coach_wins": 4, "coach_ffs": 0,
        "stars": "Sean East II (15.1 PPG)",
        "notes": "KenPom #51 — notably overseeded. Two players unavailable.",
        "venue_home_factor": 0.0,
    },
    "Texas": {
        "adj_em": 16.4, "adj_o": 112.2, "adj_d": 95.8, "adj_t": 69.6,
        "kenpom_rank": 34, "seed": 11, "region": "West",
        "consistency": "Streaky", "kill_shot_pct": 0.53,
        "injury_adjustment": -0.4,  # Traore Q (knee, 3.4 — minor)
        "injuries": ["Lassina Traore F: knee, QUESTIONABLE (3.4 PPG — minor)"],
        "record": "18-15", "coach": "Rodney Terry", "coach_wins": 6, "coach_ffs": 0,
        "stars": "Tramon Mark (19.4 PPG — buzzer beater vs NC State in First Four)",
        "notes": "First Four winner. Tramon Mark hit buzzer-beater to beat NC State 68-66. Faces DEPLETED BYU (both star guards OUT). Major upset opportunity already delivered.",
        "venue_home_factor": 0.0,
    },
    "High Point": {
        "adj_em": 11.2, "adj_o": 108.4, "adj_d": 97.2, "adj_t": 70.4,
        "kenpom_rank": 66, "seed": 12, "region": "West",
        "consistency": "Suspect", "kill_shot_pct": 0.43,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "26-7", "coach": "Tubby Smith", "coach_wins": 8, "coach_ffs": 0,
        "stars": "John-Michael Wright (16.2 PPG)", "notes": "Big South champion.",
        "venue_home_factor": 0.0,
    },
    "Hawaii": {
        "adj_em": 9.6, "adj_o": 107.1, "adj_d": 97.5, "adj_t": 68.8,
        "kenpom_rank": 78, "seed": 13, "region": "West",
        "consistency": "Suspect", "kill_shot_pct": 0.40,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "23-9", "coach": "Eran Ganot", "coach_wins": 1, "coach_ffs": 0,
        "stars": "JoVon McClanahan (16.8 PPG)", "notes": "Big West champion.",
        "venue_home_factor": 1.5,  # San Diego — Pacific time zone, slight home comfort
    },
    "Kennesaw State": {
        "adj_em": 7.8, "adj_o": 105.8, "adj_d": 98.0, "adj_t": 69.2,
        "kenpom_rank": 94, "seed": 14, "region": "West",
        "consistency": "Suspect", "kill_shot_pct": 0.36,
        "injury_adjustment": -4.8,  # Cottle SUSPENDED — leading scorer gone
        "injuries": ["Simeon Cottle G: SUSPENDED (20.2 PPG — leading scorer by far, gone for tournament)"],
        "record": "24-10", "coach": "Amir Abdur-Rahim", "coach_wins": 1, "coach_ffs": 0,
        "stars": "DEPLETED — Cottle (20.2 PPG) suspended, faces Gonzaga",
        "notes": "Faces Gonzaga WITHOUT leading scorer. Already problematic matchup made worse.",
        "venue_home_factor": 0.0,
    },
    "Queens (NC)": {
        "adj_em": 5.8, "adj_o": 103.4, "adj_d": 97.6, "adj_t": 68.4,
        "kenpom_rank": 118, "seed": 15, "region": "West",
        "consistency": "Suspect", "kill_shot_pct": 0.33,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "24-9", "coach": "Bart Lundy", "coach_wins": 0, "coach_ffs": 0,
        "stars": "First NCAA Tournament appearance", "notes": "SAC champion. Historic first bid.",
        "venue_home_factor": 0.0,
    },
    "LIU": {
        "adj_em": 1.8, "adj_o": 99.4, "adj_d": 97.6, "adj_t": 66.8,
        "kenpom_rank": 168, "seed": 16, "region": "West",
        "consistency": "Suspect", "kill_shot_pct": 0.26,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "19-15", "coach": "Granby Jeter", "coach_wins": 0, "coach_ffs": 0,
        "stars": "NEC champion",
        "notes": "KenPom #168. Faces Arizona — expected blowout.",
        "venue_home_factor": 0.0,
    },

    # ════════════════════════════════════════════════════════════
    # MIDWEST REGION  (R64/R32: St. Louis MO + Oklahoma City OK | S16/E8: Chicago IL)
    # Midwest champ plays West champ in Final Four
    # ════════════════════════════════════════════════════════════

    "Michigan": {
        "adj_em": 35.6, "adj_o": 120.8, "adj_d": 85.2, "adj_t": 68.1,
        "kenpom_rank": 2, "seed": 1, "region": "Midwest",
        "consistency": "Strong", "kill_shot_pct": 0.71,
        "injury_adjustment": -0.6,  # Cason OUT (8.4 — limited role player)
        "injuries": ["LJ Cason G: knee, OUT (8.4 PPG — rotation player, not starter)"],
        "record": "31-3", "coach": "Dusty May", "coach_wins": 4, "coach_ffs": 0,
        "stars": "Yaxel Lendeborg (14.3 PPG, 7.3 RPG)",
        "notes": "Nation's #1 DEFENSE (AdjD rank #1, KenPom #2 overall). Dusty May's second year. AdjO rank #8.",
        "venue_home_factor": 0.4,  # Chicago Sweet 16/E8 is close to Michigan
    },
    "Iowa State": {
        "adj_em": 28.4, "adj_o": 112.6, "adj_d": 84.2, "adj_t": 67.4,
        "kenpom_rank": 6, "seed": 2, "region": "Midwest",
        "consistency": "Strong", "kill_shot_pct": 0.68,
        "injury_adjustment": -0.2,  # Mitchell Q (1.0 — negligible)
        "injuries": ["Xzavion Mitchell G: undisclosed, QUESTIONABLE (1.0 PPG — negligible)"],
        "record": "27-7", "coach": "T.J. Otzelberger", "coach_wins": 7, "coach_ffs": 0,
        "stars": "Milan Momcilovic (17.0 PPG), Joshua Jefferson (16.6 PPG), Tamin Lipsey (13.3 PPG)",
        "notes": "AdjO rank #21, AdjD rank #4. Deep, balanced roster. No obvious weakness.",
        "venue_home_factor": 0.3,  # Oklahoma City is near Iowa State territory
    },
    "Virginia": {
        "adj_em": 24.4, "adj_o": 111.8, "adj_d": 87.4, "adj_t": 62.8,
        "kenpom_rank": 13, "seed": 3, "region": "Midwest",
        "consistency": "Strong", "kill_shot_pct": 0.54,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "29-5", "coach": "Ron Odom", "coach_wins": 2, "coach_ffs": 0,
        "stars": "Strong team defense (Bennett system preserved under Odom)",
        "notes": "Coach Odom's first year. 46.8% of shots from three — dangerous shooting team. KenPom #13.",
        "venue_home_factor": 0.0,
    },
    "Alabama": {
        "adj_em": 21.2, "adj_o": 119.4, "adj_d": 98.2, "adj_t": 74.8,
        "kenpom_rank": 17, "seed": 4, "region": "Midwest",
        "consistency": "Streaky", "kill_shot_pct": 0.62,
        "injury_adjustment": -4.2,  # Holloway SUSPENDED (16.8 PPG) + Bristow Q + Hannah Q
        "injuries": [
            "Aden Holloway G: SUSPENDED (felony arrest), OUT — 16.8 PPG (2nd leading scorer gone)",
            "Keitenn Bristow F: ankle, QUESTIONABLE (3.6 PPG)",
            "Davion Hannah G: undisclosed, QUESTIONABLE (3.3 PPG)",
        ],
        "record": "23-9", "coach": "Nate Oats", "coach_wins": 9, "coach_ffs": 1,
        "stars": "Labaron Philon Jr. (21.5 PPG — leads depleted team)",
        "notes": "Nation's leading offense (91.7 PPG) but BOTTOM-THIRD defense. Holloway suspended (felony) — 16.8 PPG gone. KenPom #3 offense, KenPom #67 defense. Vulnerable.",
        "venue_home_factor": 0.0,
    },
    "Texas Tech": {
        "adj_em": 20.8, "adj_o": 113.8, "adj_d": 93.0, "adj_t": 66.4,
        "kenpom_rank": 20, "seed": 5, "region": "Midwest",
        "consistency": "Streaky", "kill_shot_pct": 0.55,
        "injury_adjustment": -6.2,  # Toppin OUT (21.8/10.8) + Watts Q (11.5) — devastating
        "injuries": [
            "JT Toppin F: TORN ACL (February 17 vs Arizona State), OUT FOR SEASON — 21.8 PPG, 10.8 RPG, 43 blocks (55% FG) — the team's identity and best player gone",
            "LeJuan Watts G: foot/ankle, QUESTIONABLE (11.5 PPG — #3 scorer also uncertain)",
        ],
        "record": "22-10", "coach": "Grant McCasland", "coach_wins": 6, "coach_ffs": 0,
        "stars": "DEPLETED — Toppin was the entire team's identity",
        "notes": "Faces Akron in R64. Without Toppin (21.8/10.8 + 43 blocks), this team is fundamentally different. PRIME UPSET ALERT. Akron has 3 senior guards and 3 straight NCAA bids.",
        "venue_home_factor": 0.0,
    },
    "Tennessee": {
        "adj_em": 22.8, "adj_o": 112.4, "adj_d": 89.6, "adj_t": 68.2,
        "kenpom_rank": 15, "seed": 6, "region": "Midwest",
        "consistency": "Strong", "kill_shot_pct": 0.64,
        "injury_adjustment": -0.4,  # Phillips OUT (3.8 — minor)
        "injuries": ["Cade Phillips G: shoulder, OUT (3.8 PPG — minimal impact)"],
        "record": "21-11", "coach": "Rick Barnes", "coach_wins": 18, "coach_ffs": 1,
        "stars": "Jahmai Mashack, JP Estrella",
        "notes": "KenPom #15. Faces Miami(OH) in R64. AdjD rank #14.",
        "venue_home_factor": 0.0,
    },
    "Kentucky": {
        "adj_em": 18.6, "adj_o": 114.2, "adj_d": 95.6, "adj_t": 69.4,
        "kenpom_rank": 27, "seed": 7, "region": "Midwest",
        "consistency": "Streaky", "kill_shot_pct": 0.54,
        "injury_adjustment": -1.4,  # Lowe OUT (8.0 PPG)
        "injuries": ["Jaland Lowe G: shoulder, OUT (8.0 PPG — rotation guard)"],
        "record": "21-13", "coach": "Mark Pope", "coach_wins": 5, "coach_ffs": 0,
        "stars": "Otega Oweh (17.8 PPG)",
        "notes": "Pope's second year. Without Lowe. Faces Santa Clara (underseeded KenPom #35). Upset risk.",
        "venue_home_factor": 0.0,
    },
    "Georgia": {
        "adj_em": 17.2, "adj_o": 112.8, "adj_d": 95.6, "adj_t": 70.2,
        "kenpom_rank": 30, "seed": 8, "region": "Midwest",
        "consistency": "Streaky", "kill_shot_pct": 0.51,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "21-12", "coach": "Mike White", "coach_wins": 8, "coach_ffs": 0,
        "stars": "Blue Cain (16.4 PPG)",
        "notes": "SEC at-large. Faces Saint Louis in R64.",
        "venue_home_factor": 0.0,
    },
    "Saint Louis": {
        "adj_em": 16.8, "adj_o": 112.2, "adj_d": 95.4, "adj_t": 67.8,
        "kenpom_rank": 37, "seed": 9, "region": "Midwest",
        "consistency": "Streaky", "kill_shot_pct": 0.50,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "22-11", "coach": "Josh Schertz", "coach_wins": 3, "coach_ffs": 0,
        "stars": "Gibson Jimerson (18.2 PPG)",
        "notes": "A-10 regular season champion. Playing in St. Louis — NEAR HOME CROWD ADVANTAGE.",
        "venue_home_factor": 2.8,  # St. Louis is Saint Louis's HOME city — massive crowd factor
    },
    "Santa Clara": {
        "adj_em": 17.4, "adj_o": 113.1, "adj_d": 95.7, "adj_t": 68.6,
        "kenpom_rank": 35, "seed": 10, "region": "Midwest",
        "consistency": "Strong", "kill_shot_pct": 0.54,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "25-8", "coach": "Herb Sendek", "coach_wins": 12, "coach_ffs": 0,
        "stars": "Carlos Stewart (17.6 PPG)",
        "notes": "Massively underseeded — KenPom #35, Torvik #29. Faces Kentucky WITHOUT Jaland Lowe. PRIME UPSET candidate.",
        "venue_home_factor": 0.8,  # West coast school in Oklahoma City — minimal advantage
    },
    "Miami (OH)": {
        "adj_em": 13.4, "adj_o": 110.8, "adj_d": 97.4, "adj_t": 68.4,
        "kenpom_rank": 93, "seed": 11, "region": "Midwest",
        "consistency": "Streaky", "kill_shot_pct": 0.48,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "32-2", "coach": "Travis Steele", "coach_wins": 3, "coach_ffs": 0,
        "stars": "Micah Parrish (16.8 PPG)",
        "notes": "First Four winner (beat SMU). 31-1 regular season record but KenPom #93 — very soft schedule. Faces Tennessee in R64.",
        "venue_home_factor": 0.0,
    },
    "Akron": {
        "adj_em": 14.8, "adj_o": 111.4, "adj_d": 96.6, "adj_t": 67.4,
        "kenpom_rank": 45, "seed": 12, "region": "Midwest",
        "consistency": "Strong", "kill_shot_pct": 0.56,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "24-9", "coach": "John Groce", "coach_wins": 2, "coach_ffs": 0,
        "stars": "3 senior guards — experienced tournament team",
        "notes": "3 straight NCAA Tournament bids. 3 experienced senior guards. Faces Texas Tech WITHOUT JT Toppin (ACL). PRIME UPSET PICK — this is our signature R64 call.",
        "venue_home_factor": 0.0,
    },
    "Hofstra": {
        "adj_em": 11.4, "adj_o": 108.8, "adj_d": 97.4, "adj_t": 69.2,
        "kenpom_rank": 64, "seed": 13, "region": "Midwest",
        "consistency": "Suspect", "kill_shot_pct": 0.43,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "25-8", "coach": "Speedy Claxton", "coach_wins": 1, "coach_ffs": 0,
        "stars": "Tyler Thomas (15.8 PPG)", "notes": "CAA champion.",
        "venue_home_factor": 0.0,
    },
    "Wright State": {
        "adj_em": 8.4, "adj_o": 106.2, "adj_d": 97.8, "adj_t": 67.6,
        "kenpom_rank": 88, "seed": 14, "region": "Midwest",
        "consistency": "Suspect", "kill_shot_pct": 0.38,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "24-9", "coach": "Scott Nagy", "coach_wins": 2, "coach_ffs": 0,
        "stars": "Trey Calvin (17.4 PPG)", "notes": "Horizon League champion.",
        "venue_home_factor": 0.0,
    },
    "Tennessee State": {
        "adj_em": 2.8, "adj_o": 100.8, "adj_d": 98.0, "adj_t": 66.8,
        "kenpom_rank": 162, "seed": 15, "region": "Midwest",
        "consistency": "Suspect", "kill_shot_pct": 0.28,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "20-13", "coach": "Penny Collins", "coach_wins": 0, "coach_ffs": 0,
        "stars": "OVC champion",
        "notes": "KenPom gap vs Iowa State is 158 spots — among largest in bracket.",
        "venue_home_factor": 0.0,
    },
    "Howard": {
        "adj_em": 3.6, "adj_o": 101.8, "adj_d": 98.2, "adj_t": 67.2,
        "kenpom_rank": 148, "seed": 16, "region": "Midwest",
        "consistency": "Suspect", "kill_shot_pct": 0.30,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "22-14", "coach": "Kenneth Blakeney", "coach_wins": 1, "coach_ffs": 0,
        "stars": "First-ever NCAA Tournament WIN (beat UMBC 86-83 in First Four)",
        "notes": "Historic First Four win. MEAC champion. First-ever NCAA Tournament victory. Now faces #1 Michigan.",
        "venue_home_factor": 0.0,
    },

    # ════════════════════════════════════════════════════════════
    # SOUTH REGION  (R64/R32: Tampa FL + Greenville SC | S16/E8: Houston TX)
    # South champ plays East champ in Final Four
    # ════════════════════════════════════════════════════════════

    "Florida": {
        "adj_em": 29.8, "adj_o": 118.4, "adj_d": 88.6, "adj_t": 69.2,
        "kenpom_rank": 4, "seed": 1, "region": "South",
        "consistency": "Strong", "kill_shot_pct": 0.70,
        "injury_adjustment": -0.4,  # Connor Essegian Q (ankle, 4.8 — minor)
        "injuries": ["Connor Essegian G: ankle, QUESTIONABLE (4.8 PPG — limited role)"],
        "record": "26-7", "coach": "Todd Golden", "coach_wins": 3, "coach_ffs": 0,
        "stars": "Thomas Haugh (17.2 PPG), Alex Condon (14.8 PPG), Rueben Chinyelu (11.4 PPG)",
        "notes": "DEFENDING NATIONAL CHAMPIONS. 11-game winning streak. AdjO rank #9, AdjD rank #6.",
        "venue_home_factor": 1.2,  # Tampa is in Florida — strong home fan support
    },
    "Houston": {
        "adj_em": 27.4, "adj_o": 114.2, "adj_d": 86.8, "adj_t": 65.2,
        "kenpom_rank": 5, "seed": 2, "region": "South",
        "consistency": "Strong", "kill_shot_pct": 0.76,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "28-6", "coach": "Kelvin Sampson", "coach_wins": 21, "coach_ffs": 3,
        "stars": "Kingston Flemings (16.5 PPG, 5.4 APG — set school freshman scoring record 42pts), Emanuel Sharp (15.8 PPG)",
        "notes": "PLAYS SWEET 16 AND ELITE 8 IN HOUSTON TX — effectively home court for S16/E8. Elite defense (AdjD rank #4-5). Sampson: Hall of Fame-caliber. KenPom #5.",
        "venue_home_factor": 4.2,  # Sweet 16/E8 at Toyota Center IN HOUSTON — practically home game
    },
    "Illinois": {
        "adj_em": 27.6, "adj_o": 129.4, "adj_d": 101.8, "adj_t": 72.4,
        "kenpom_rank": 7, "seed": 3, "region": "South",
        "consistency": "Streaky", "kill_shot_pct": 0.62,
        "injury_adjustment": -0.2,  # Jakstys OUT (1.3 — negligible)
        "injuries": ["Jason Jakstys G: shoulder, OUT (1.3 PPG — negligible)"],
        "record": "24-8", "coach": "Brad Underwood", "coach_wins": 7, "coach_ffs": 0,
        "stars": "Keaton Wagler (17.9 PPG), Kylan Boswell (13.3 PPG)",
        "notes": "NATION'S #1 OFFENSE (KenPom AdjO rank #1, AdjO ~129). But AdjD rank only ~#28. Can they score fast enough to beat elite defenses?",
        "venue_home_factor": 0.0,
    },
    "Nebraska": {
        "adj_em": 19.6, "adj_o": 110.4, "adj_d": 90.8, "adj_t": 66.8,
        "kenpom_rank": 14, "seed": 4, "region": "South",
        "consistency": "Strong", "kill_shot_pct": 0.56,
        "injury_adjustment": -0.4,  # Essegian Q (4.8 — minor)
        "injuries": ["Connor Essegian G: ankle, QUESTIONABLE (4.8 PPG)"],
        "record": "26-6", "coach": "Fred Hoiberg", "coach_wins": 14, "coach_ffs": 0,
        "stars": "Pryce Sandfort (17.9 PPG)",
        "notes": "Best Big Ten defense (KenPom #7 AdjD). BUT: NEVER won an NCAA Tournament game in program history — massive psychological factor. KenPom #14.",
        "venue_home_factor": 0.0,
    },
    "Vanderbilt": {
        "adj_em": 25.8, "adj_o": 117.8, "adj_d": 92.0, "adj_t": 70.2,
        "kenpom_rank": 12, "seed": 5, "region": "South",
        "consistency": "Streaky", "kill_shot_pct": 0.60,
        "injury_adjustment": -1.4,  # Collins OUT knee (7.8)
        "injuries": ["Frankie Collins G: knee, OUT (7.8 PPG — backup guard)"],
        "record": "26-8", "coach": "Mark Byington", "coach_wins": 5, "coach_ffs": 0,
        "stars": "A.J. Hoggard (17.8 PPG), Tyler Nickel (15.2 PPG)",
        "notes": "MASSIVELY underseeded. KenPom #12, Torvik #10 — should be a 3 or 4 seed. Elite offense (AdjO rank #7). Analysts predict big run.",
        "venue_home_factor": 0.0,
    },
    "North Carolina": {
        "adj_em": 18.4, "adj_o": 114.8, "adj_d": 96.4, "adj_t": 71.4,
        "kenpom_rank": 23, "seed": 6, "region": "South",
        "consistency": "Streaky", "kill_shot_pct": 0.56,
        "injury_adjustment": -5.2,  # Wilson OUT (19.8 PPG — season-ending, #1 scorer and top-5 NBA pick)
        "injuries": [
            "Caleb Wilson G: FRACTURED THUMB (surgery March 5), OUT FOR SEASON — 19.8 PPG, top-5 projected NBA pick",
            "James Brown G: foot, OUT (1.2 PPG — negligible)",
        ],
        "record": "21-12", "coach": "Hubert Davis", "coach_wins": 8, "coach_ffs": 1,
        "stars": "RJ Davis (16.8 PPG) must carry massive load without Wilson",
        "notes": "WITHOUT Caleb Wilson (19.8 PPG, projected top-5 NBA pick, surgery March 5). This team lost its best player and face of the program. PRIME UPSET ALERT vs VCU.",
        "venue_home_factor": 0.0,
    },
    "Saint Mary's": {
        "adj_em": 20.2, "adj_o": 111.4, "adj_d": 91.2, "adj_t": 64.8,
        "kenpom_rank": 22, "seed": 7, "region": "South",
        "consistency": "Strong", "kill_shot_pct": 0.58,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "27-5", "coach": "Randy Bennett", "coach_wins": 16, "coach_ffs": 0,
        "stars": "Augustas Marciulionis (16.4 PPG)",
        "notes": "Top-10 scoring defense nationally (64.6 PPG allowed) for 5th straight year. WCC champion. Faces Texas A&M (Mgbako OUT).",
        "venue_home_factor": 0.4,  # West coast school, Greenville SC slightly unfamiliar
    },
    "Clemson": {
        "adj_em": 15.6, "adj_o": 111.8, "adj_d": 96.2, "adj_t": 68.8,
        "kenpom_rank": 39, "seed": 8, "region": "South",
        "consistency": "Streaky", "kill_shot_pct": 0.50,
        "injury_adjustment": -3.4,  # Welling OUT (ACL, 10.2/5.4) + Foster OUT (6.9)
        "injuries": [
            "Carter Welling F: torn ACL vs Wake Forest, OUT FOR SEASON (10.2 PPG, 5.4 RPG)",
            "Zac Foster G: knee, OUT (6.9 PPG)",
        ],
        "record": "21-12", "coach": "Brad Brownell", "coach_wins": 7, "coach_ffs": 0,
        "stars": "Chase Hunter (18.4 PPG) must compensate for losses",
        "notes": "BOTH starting big man (ACL) and wing OUT. Faces Iowa (underseeded KenPom #25). Major upset risk.",
        "venue_home_factor": 0.8,  # Greenville SC — Clemson fans nearby
    },
    "Iowa": {
        "adj_em": 18.6, "adj_o": 114.4, "adj_d": 95.8, "adj_t": 70.8,
        "kenpom_rank": 25, "seed": 9, "region": "South",
        "consistency": "Streaky", "kill_shot_pct": 0.54,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "20-13", "coach": "Fran McCaffery", "coach_wins": 9, "coach_ffs": 0,
        "stars": "Payton Sandfort (18.8 PPG), Josh Dix (16.2 PPG)",
        "notes": "UNDERSEEDED — KenPom #25, Torvik #26. Faces DEPLETED Clemson (Welling ACL + Foster OUT). Live upset pick.",
        "venue_home_factor": 0.0,
    },
    "Texas A&M": {
        "adj_em": 15.2, "adj_o": 110.8, "adj_d": 95.6, "adj_t": 68.4,
        "kenpom_rank": 40, "seed": 10, "region": "South",
        "consistency": "Streaky", "kill_shot_pct": 0.49,
        "injury_adjustment": -2.1,  # Mgbako OUT foot (10.4)
        "injuries": ["Mackenzie Mgbako F: foot, OUT (10.4 PPG — 2nd leading scorer)"],
        "record": "19-14", "coach": "Buzz Williams", "coach_wins": 8, "coach_ffs": 0,
        "stars": "Wade Taylor IV (17.4 PPG)",
        "notes": "Without Mgbako (10.4 PPG). Faces elite defensive Saint Mary's team.",
        "venue_home_factor": 0.6,  # Tampa — near their Texas fan base slightly
    },
    "VCU": {
        "adj_em": 14.6, "adj_o": 110.2, "adj_d": 95.6, "adj_t": 69.8,
        "kenpom_rank": 47, "seed": 11, "region": "South",
        "consistency": "Streaky", "kill_shot_pct": 0.55,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "24-10", "coach": "Mike Rhoades", "coach_wins": 5, "coach_ffs": 0,
        "stars": "Adrian Baldwin Jr. (15.4 PPG)",
        "notes": "Won A-10 Championship. Faces NORTH CAROLINA WITHOUT Caleb Wilson (19.8 PPG, top-5 NBA pick, season-ending surgery). PRIME UPSET PICK.",
        "venue_home_factor": 0.0,
    },
    "McNeese": {
        "adj_em": 11.8, "adj_o": 108.6, "adj_d": 96.8, "adj_t": 68.6,
        "kenpom_rank": 62, "seed": 12, "region": "South",
        "consistency": "Streaky", "kill_shot_pct": 0.46,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "26-7", "coach": "Will Wade", "coach_wins": 7, "coach_ffs": 0,
        "stars": "Shahada Wells (18.2 PPG)",
        "notes": "Southland champion. Will Wade reunion — former LSU/VCU coach.",
        "venue_home_factor": 0.0,
    },
    "Troy": {
        "adj_em": 9.2, "adj_o": 107.2, "adj_d": 98.0, "adj_t": 69.4,
        "kenpom_rank": 80, "seed": 13, "region": "South",
        "consistency": "Suspect", "kill_shot_pct": 0.40,
        "injury_adjustment": -1.8,  # Seng Q (12.9)
        "injuries": ["Theo Seng F: knee, QUESTIONABLE (12.9 PPG — leading scorer uncertain)"],
        "record": "24-9", "coach": "Scott Cross", "coach_wins": 2, "coach_ffs": 0,
        "stars": "Theo Seng (12.9 PPG) — questionable",
        "notes": "Sun Belt champion. Key player questionable.",
        "venue_home_factor": 0.0,
    },
    "Penn": {
        "adj_em": 7.2, "adj_o": 105.4, "adj_d": 98.2, "adj_t": 67.8,
        "kenpom_rank": 102, "seed": 14, "region": "South",
        "consistency": "Suspect", "kill_shot_pct": 0.36,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "22-8", "coach": "Steve Donahue", "coach_wins": 4, "coach_ffs": 0,
        "stars": "Clark Slajchert (15.8 PPG)", "notes": "Ivy League champion.",
        "venue_home_factor": 0.0,
    },
    "Idaho": {
        "adj_em": 5.4, "adj_o": 103.2, "adj_d": 97.8, "adj_t": 67.2,
        "kenpom_rank": 124, "seed": 15, "region": "South",
        "consistency": "Suspect", "kill_shot_pct": 0.32,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "23-10", "coach": "Zac Claus", "coach_wins": 0, "coach_ffs": 0,
        "stars": "Big Sky champion", "notes": "First NCAA Tournament bid in years.",
        "venue_home_factor": 0.0,
    },
    "Prairie View A&M": {
        "adj_em": 2.4, "adj_o": 100.2, "adj_d": 97.8, "adj_t": 66.4,
        "kenpom_rank": 145, "seed": 16, "region": "South",
        "consistency": "Suspect", "kill_shot_pct": 0.27,
        "injury_adjustment": 0.0, "injuries": [],
        "record": "21-13", "coach": "Byron Smith", "coach_wins": 1, "coach_ffs": 0,
        "stars": "Dontae Horne (25 pts, 7 reb, 4 stl in First Four win)",
        "notes": "First-ever NCAA Tournament WIN (beat Lehigh 67-55). SWAC champion. Historic moment.",
        "venue_home_factor": 0.6,  # Texas school, playing in Tampa
    },
}

# ─── Bracket structure ────────────────────────────────────────────────────────
R64_GAME_ORDER = [
    (1, 16), (8, 9),
    (5, 12), (4, 13),
    (6, 11), (3, 14),
    (7, 10), (2, 15),
]

REGION_ORDER = ["East", "South", "West", "Midwest"]

# National bracket pairings for Final Four
# East champion plays South champion | West champion plays Midwest champion
NATIONAL_FF_PAIRINGS = [
    ("East", "South"),
    ("West", "Midwest"),
]

ROUND_INFO = {
    "First Four": {"dates": "March 17-18, 2026", "location": "UD Arena, Dayton OH"},
    "R64":  {"dates": "March 19-20, 2026", "location": "Buffalo/Philadelphia (East) | Tampa/Greenville (South) | San Diego/Portland (West) | St. Louis/OKC (Midwest)"},
    "R32":  {"dates": "March 21-22, 2026", "location": "Same 8 sites"},
    "S16":  {"dates": "March 26-27, 2026", "location": "Washington DC (East) | Houston TX (South) | San Jose CA (West) | Chicago IL (Midwest)"},
    "E8":   {"dates": "March 28-29, 2026", "location": "Same 4 regional sites"},
    "FF":   {"dates": "April 4, 2026",     "location": "Lucas Oil Stadium, Indianapolis IN"},
    "Championship": {"dates": "April 6, 2026", "location": "Lucas Oil Stadium, Indianapolis IN"},
}

FIRST_FOUR_RESULTS = [
    {"winner": "Texas", "loser": "NC State", "score": "68-66", "note": "Tramon Mark buzzer-beater. Texas (11) plays BYU (6) in R64 West."},
    {"winner": "Howard", "loser": "UMBC", "score": "86-83", "note": "First-ever NCAA Tournament win for Howard. Plays Michigan (1) in R64 Midwest."},
    {"winner": "Prairie View A&M", "loser": "Lehigh", "score": "67-55", "note": "First-ever NCAA Tournament win for PVA&M. Dontae Horne: 25/7/4stl. Plays Florida (1) in R64 South."},
    {"winner": "Miami (OH)", "loser": "SMU", "score": "Final pending", "note": "Miami (OH) led 43-34 at half. Plays Tennessee (6) in R64 Midwest."},
]

# ─── Research-based predicted results ────────────────────────────────────────
# Based on KenPom ratings + injury analysis + venue factors + historical patterns
PREDICTED_RESULTS = {
    "East": {
        "R64": {
            "Duke": "W", "Siena": "L",
            "Ohio State": "W", "TCU": "L",          # Ohio State underseeded, wins 8v9
            "St. John's": "W", "Northern Iowa": "L",
            "Kansas": "W", "Cal Baptist": "L",
            "South Florida": "W", "Louisville": "L", # UPSET: SF 11-win streak, Louisville WITHOUT Brown Jr.
            "Michigan State": "W", "North Dakota State": "L",
            "UCF": "W", "UCLA": "L",                # UPSET: UCLA both stars questionable
            "UConn": "W", "Furman": "L",
        },
        "R32": {
            "Duke": "W", "Ohio State": "L",
            "St. John's": "W", "Kansas": "L",        # Zuby Ejiofor dominates
            "Michigan State": "W", "South Florida": "L",
            "UConn": "W", "UCF": "L",
        },
        "S16": {
            "Duke": "W", "St. John's": "L",
            "UConn": "W", "Michigan State": "L",
        },
        "E8": {
            "Duke": "W", "UConn": "L",              # Duke to Final Four
        },
    },
    "South": {
        "R64": {
            "Florida": "W", "Prairie View A&M": "L",
            "Iowa": "W", "Clemson": "L",             # UPSET: Iowa underseeded, Clemson missing Welling (ACL) + Foster
            "Vanderbilt": "W", "McNeese": "L",       # Vanderbilt massively underseeded (KenPom #12)
            "Nebraska": "W", "Troy": "L",
            "VCU": "W", "North Carolina": "L",       # UPSET: UNC without Wilson (19.8 PPG, season-ending surgery)
            "Illinois": "W", "Penn": "L",
            "Saint Mary's": "W", "Texas A&M": "L",   # Elite defense + Mgbako OUT for TAMU
            "Houston": "W", "Idaho": "L",
        },
        "R32": {
            "Florida": "W", "Iowa": "L",
            "Vanderbilt": "W", "Nebraska": "L",      # Vanderbilt (KenPom #12) vs Nebraska first-time winner
            "Illinois": "W", "VCU": "L",
            "Houston": "W", "Saint Mary's": "L",
        },
        "S16": {
            "Florida": "W", "Vanderbilt": "L",
            "Houston": "W", "Illinois": "L",         # Houston D (#4-5) vs Illinois O (#1) — defense wins; HOUSTON HOME CROWD
        },
        "E8": {
            "Houston": "W", "Florida": "L",          # Houston at home (Toyota Center) + Sampson experience
        },
    },
    "West": {
        "R64": {
            "Arizona": "W", "LIU": "L",
            "Utah State": "W", "Villanova": "L",     # Utah State underseeded, Villanova missing Hodge
            "Wisconsin": "W", "High Point": "L",
            "Arkansas": "W", "Hawaii": "L",
            "Texas": "W", "BYU": "L",                # UPSET: BYU missing BOTH star guards (Saunders + Baker OUT)
            "Gonzaga": "W", "Kennesaw State": "L",   # Cottle suspended — Gonzaga handles easily
            "Miami (FL)": "W", "Missouri": "L",      # Missouri missing Boateng + Porter Q
            "Purdue": "W", "Queens": "L",
        },
        "R32": {
            "Arizona": "W", "Utah State": "L",
            "Arkansas": "W", "Wisconsin": "L",       # Acuff (22.2/6.4) + Calipari experience
            "Gonzaga": "W", "Texas": "L",
            "Purdue": "W", "Miami (FL)": "L",
        },
        "S16": {
            "Arizona": "W", "Arkansas": "L",
            "Purdue": "W", "Gonzaga": "L",           # Purdue #2 offense vs Gonzaga missing Huff since Jan 15
        },
        "E8": {
            "Arizona": "W", "Purdue": "L",           # Arizona elite D smothers Purdue's offensive-only identity
        },
    },
    "Midwest": {
        "R64": {
            "Michigan": "W", "Howard": "L",
            "Georgia": "W", "Saint Louis": "L",      # Saint Louis home crowd won't help vs Georgia talent
            "Akron": "W", "Texas Tech": "L",         # UPSET: Toppin OUT (ACL) — our signature call
            "Alabama": "W", "Hofstra": "L",          # Philon (21.5) carries depleted Alabama
            "Tennessee": "W", "Miami (OH)": "L",
            "Virginia": "W", "Wright State": "L",
            "Santa Clara": "W", "Kentucky": "L",     # UPSET: Santa Clara KenPom #35 vs Kentucky without Lowe
            "Iowa State": "W", "Tennessee State": "L",
        },
        "R32": {
            "Michigan": "W", "Georgia": "L",
            "Alabama": "W", "Akron": "L",            # Philon 21.5 too much even without Holloway
            "Virginia": "W", "Tennessee": "L",       # Virginia's system + D edge
            "Iowa State": "W", "Santa Clara": "L",
        },
        "S16": {
            "Michigan": "W", "Alabama": "L",         # Michigan #1 DEF vs Alabama #67 DEF — Michigan elite D wins
            "Iowa State": "W", "Virginia": "L",
        },
        "E8": {
            "Michigan": "W", "Iowa State": "L",      # Michigan to Final Four — Dusty May system
        },
    },
}

# ─── Notable predicted upsets ─────────────────────────────────────────────────
NOTABLE_UPSETS = [
    {"upset": "Akron over Texas Tech", "seed_line": "12 over 5", "region": "Midwest", "round": "R64",
     "reason": "JT Toppin (21.8 PPG, 10.8 RPG, 43 BLK) tore ACL Feb 17. Texas Tech is a fundamentally different team without him. Akron has 3 senior guards and 3 straight NCAA bids."},
    {"upset": "VCU over North Carolina", "seed_line": "11 over 6", "region": "South", "round": "R64",
     "reason": "Caleb Wilson (19.8 PPG, top-5 NBA pick) had season-ending thumb surgery March 5. UNC loses their entire identity. VCU won A-10 Championship."},
    {"upset": "Iowa over Clemson", "seed_line": "9 over 8", "region": "South", "round": "R64",
     "reason": "Clemson missing Carter Welling (ACL, 10.2/5.4) AND Zac Foster. Iowa underseeded at KenPom #25 (given 9-seed). Straightforward upset."},
    {"upset": "Texas over BYU", "seed_line": "11 over 6", "region": "West", "round": "R64",
     "reason": "BYU lost BOTH star guards to knee injuries: Richie Saunders (18.0 PPG, season-ending) and Dawson Baker (season-ending). Texas just beat NC State on buzzer-beater and has momentum."},
    {"upset": "UCF over UCLA", "seed_line": "10 over 7", "region": "East", "round": "R64",
     "reason": "UCLA's top two scorers (Bilodeau 17.6 PPG, Dent 13.5 PPG) BOTH questionable. UCF is healthy and capable."},
    {"upset": "South Florida over Louisville", "seed_line": "11 over 6", "region": "East", "round": "R64",
     "reason": "Louisville WITHOUT starting PG Mikel Brown Jr. for first two games (back injury). South Florida on 11-game win streak."},
    {"upset": "Santa Clara over Kentucky", "seed_line": "10 over 7", "region": "Midwest", "round": "R64",
     "reason": "Santa Clara massively underseeded (KenPom #35, Torvik #29). Kentucky missing Jaland Lowe and has only 21-13 record."},
    {"upset": "Vanderbilt deep run", "seed_line": "5 seed running as effective 3/4", "region": "South", "round": "Multiple",
     "reason": "Vanderbilt KenPom #12, Torvik #10 — should be 3 or 4 seed. Elite offense (AdjO rank #7). Major bracket value as a 5-seed."},
    {"upset": "Houston Home Court S16/E8", "seed_line": "2 seed with home advantage", "region": "South", "round": "S16/E8",
     "reason": "Houston plays Sweet 16 and Elite 8 at Toyota Center IN HOUSTON TX. Practically a home game for the #2 seed. Massive crowd advantage."},
    {"upset": "Michigan over Iowa State (E8)", "seed_line": "1 over 2", "region": "Midwest", "round": "E8",
     "reason": "Nation's #1 defense (AdjD rank #1) vs Iowa State's balanced attack. Michigan's system under Dusty May suffocates opponents."},
]


# ─── Helper functions ────────────────────────────────────────────────────────
def get_teams_by_region(region: str) -> list[dict]:
    return sorted(
        [{"name": n, **d} for n, d in TEAM_DATA.items() if d["region"] == region],
        key=lambda t: t["seed"]
    )


def get_team(name: str) -> dict | None:
    return TEAM_DATA.get(name)


def get_r64_matchups(region: str) -> list[tuple[str, str]]:
    by_seed = {t["seed"]: t["name"] for t in get_teams_by_region(region)}
    return [(by_seed[s1], by_seed[s2]) for s1, s2 in R64_GAME_ORDER if s1 in by_seed and s2 in by_seed]


def get_predicted_bracket_path() -> dict:
    result = {}
    for region, data in PREDICTED_RESULTS.items():
        winners = {k: v for k, v in data.items()}
        ff_team = list(data.get("E8", {}).keys())[0] if data.get("E8") else "?"
        result[region] = {"rounds": winners, "ff_team": ff_team}
    result["Final Four"] = {
        "Semifinal_1": {"East": "Duke", "South": "Houston", "predicted_winner": "Duke"},
        "Semifinal_2": {"West": "Arizona", "Midwest": "Michigan", "predicted_winner": "Arizona"},
        "Championship": {"predicted_winner": "Arizona"},
    }
    return result
