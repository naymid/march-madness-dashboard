"""
Full 2026 NCAA Tournament bracket — 64 teams, 4 regions, all rounds.
Encodes team ratings, seeds, injuries, and predicted paths from pre-tournament research.

Final Four: Arizona (East) vs Michigan (South), Duke (West) vs Houston (Midwest)
National bracket pairings: East/South play each other; West/Midwest play each other.
"""

# ─── Team Ratings (KenPom-proxy AdjEM, encoded from research) ─────────────────
# Format: name: {adj_em, adj_o, adj_d, adj_t, seed, region, consistency,
#                kill_shot_pct, injury_adjustment, injuries, coach_tourney_wins}

TEAM_DATA = {
    # ── EAST REGION ────────────────────────────────────────────────────────────
    "Arizona":          {"adj_em": 27.5, "adj_o": 122.4, "adj_d": 94.9, "adj_t": 69.8, "seed": 1,  "region": "East",    "consistency": "Strong",  "kill_shot_pct": 0.71, "injury_adjustment": 0.0,  "injuries": ["Jaden Bradley G: left wrist (cleared, X-ray negative)"], "coach": "Tommy Lloyd", "coach_wins": 8,  "coach_ffs": 1},
    "Tennessee":        {"adj_em": 25.1, "adj_o": 118.3, "adj_d": 93.2, "adj_t": 68.1, "seed": 2,  "region": "East",    "consistency": "Strong",  "kill_shot_pct": 0.68, "injury_adjustment": 0.0,  "injuries": [], "coach": "Rick Barnes",    "coach_wins": 18, "coach_ffs": 1},
    "Marquette":        {"adj_em": 23.1, "adj_o": 117.2, "adj_d": 94.1, "adj_t": 70.3, "seed": 3,  "region": "East",    "consistency": "Strong",  "kill_shot_pct": 0.65, "injury_adjustment": 0.0,  "injuries": [], "coach": "Shaka Smart",    "coach_wins": 12, "coach_ffs": 0},
    "Texas Tech":       {"adj_em": 20.1, "adj_o": 115.4, "adj_d": 95.3, "adj_t": 66.4, "seed": 4,  "region": "East",    "consistency": "Streaky", "kill_shot_pct": 0.53, "injury_adjustment": -3.5, "injuries": ["JT Toppin F: ACL tear Feb 17, OUT for season — All-Big 12 player gone"], "coach": "Grant McCasland", "coach_wins": 6, "coach_ffs": 0},
    "St. John's":       {"adj_em": 21.3, "adj_o": 116.8, "adj_d": 95.5, "adj_t": 68.9, "seed": 5,  "region": "East",    "consistency": "Strong",  "kill_shot_pct": 0.63, "injury_adjustment": 0.0,  "injuries": [], "coach": "Rick Pitino",    "coach_wins": 22, "coach_ffs": 2},
    "Creighton":        {"adj_em": 20.8, "adj_o": 116.1, "adj_d": 95.3, "adj_t": 71.2, "seed": 6,  "region": "East",    "consistency": "Strong",  "kill_shot_pct": 0.61, "injury_adjustment": 0.0,  "injuries": [], "coach": "Greg McDermott",  "coach_wins": 8,  "coach_ffs": 0},
    "Missouri":         {"adj_em": 18.5, "adj_o": 114.6, "adj_d": 96.1, "adj_t": 69.4, "seed": 7,  "region": "East",    "consistency": "Streaky", "kill_shot_pct": 0.55, "injury_adjustment": 0.0,  "injuries": [], "coach": "Dennis Gates",    "coach_wins": 4,  "coach_ffs": 0},
    "BYU":              {"adj_em": 18.2, "adj_o": 114.1, "adj_d": 95.9, "adj_t": 70.1, "seed": 8,  "region": "East",    "consistency": "Streaky", "kill_shot_pct": 0.52, "injury_adjustment": 0.0,  "injuries": [], "coach": "Kevin Young",     "coach_wins": 3,  "coach_ffs": 0},
    "Penn State":       {"adj_em": 17.1, "adj_o": 113.4, "adj_d": 96.3, "adj_t": 67.8, "seed": 9,  "region": "East",    "consistency": "Streaky", "kill_shot_pct": 0.49, "injury_adjustment": 0.0,  "injuries": [], "coach": "Mike Rhoades",    "coach_wins": 3,  "coach_ffs": 0},
    "Utah State":       {"adj_em": 16.9, "adj_o": 113.1, "adj_d": 96.2, "adj_t": 68.7, "seed": 10, "region": "East",    "consistency": "Streaky", "kill_shot_pct": 0.50, "injury_adjustment": 0.0,  "injuries": [], "coach": "Jerrod Calhoun",  "coach_wins": 2,  "coach_ffs": 0},
    "VCU":              {"adj_em": 14.9, "adj_o": 111.3, "adj_d": 96.4, "adj_t": 72.1, "seed": 11, "region": "East",    "consistency": "Streaky", "kill_shot_pct": 0.56, "injury_adjustment": 0.0,  "injuries": [], "coach": "Mike Rhoades",    "coach_wins": 5,  "coach_ffs": 0},
    "Akron":            {"adj_em": 15.8, "adj_o": 112.4, "adj_d": 96.6, "adj_t": 67.3, "seed": 12, "region": "East",    "consistency": "Streaky", "kill_shot_pct": 0.51, "injury_adjustment": 0.0,  "injuries": [], "coach": "John Groce",      "coach_wins": 2,  "coach_ffs": 0},
    "Colgate":          {"adj_em": 11.2, "adj_o": 108.7, "adj_d": 97.5, "adj_t": 69.9, "seed": 13, "region": "East",    "consistency": "Streaky", "kill_shot_pct": 0.43, "injury_adjustment": 0.0,  "injuries": [], "coach": "Matt Langel",     "coach_wins": 1,  "coach_ffs": 0},
    "N. Kentucky":      {"adj_em": 9.1,  "adj_o": 106.8, "adj_d": 97.7, "adj_t": 68.4, "seed": 14, "region": "East",    "consistency": "Suspect", "kill_shot_pct": 0.39, "injury_adjustment": 0.0,  "injuries": [], "coach": "Darrin Horn",     "coach_wins": 0,  "coach_ffs": 0},
    "Sacred Heart":     {"adj_em": 6.2,  "adj_o": 104.1, "adj_d": 97.9, "adj_t": 67.8, "seed": 15, "region": "East",    "consistency": "Suspect", "kill_shot_pct": 0.33, "injury_adjustment": 0.0,  "injuries": [], "coach": "Anthony Latina",  "coach_wins": 0,  "coach_ffs": 0},
    "Norfolk State":    {"adj_em": 2.1,  "adj_o": 100.4, "adj_d": 98.3, "adj_t": 66.2, "seed": 16, "region": "East",    "consistency": "Suspect", "kill_shot_pct": 0.28, "injury_adjustment": 0.0,  "injuries": [], "coach": "Robert Jones",    "coach_wins": 0,  "coach_ffs": 0},

    # ── SOUTH REGION ───────────────────────────────────────────────────────────
    "Alabama":          {"adj_em": 25.3, "adj_o": 119.1, "adj_d": 93.8, "adj_t": 71.4, "seed": 1,  "region": "South",   "consistency": "Strong",  "kill_shot_pct": 0.70, "injury_adjustment": 0.0,  "injuries": [], "coach": "Nate Oats",       "coach_wins": 9,  "coach_ffs": 1},
    "Kentucky":         {"adj_em": 24.1, "adj_o": 118.2, "adj_d": 94.1, "adj_t": 70.2, "seed": 2,  "region": "South",   "consistency": "Strong",  "kill_shot_pct": 0.67, "injury_adjustment": 0.0,  "injuries": [], "coach": "Mark Pope",       "coach_wins": 5,  "coach_ffs": 0},
    "Wisconsin":        {"adj_em": 22.4, "adj_o": 116.7, "adj_d": 94.3, "adj_t": 65.8, "seed": 3,  "region": "South",   "consistency": "Strong",  "kill_shot_pct": 0.62, "injury_adjustment": 0.0,  "injuries": [], "coach": "Greg Gard",       "coach_wins": 6,  "coach_ffs": 0},
    "Louisville":       {"adj_em": 20.5, "adj_o": 115.8, "adj_d": 95.3, "adj_t": 68.3, "seed": 4,  "region": "South",   "consistency": "Streaky", "kill_shot_pct": 0.55, "injury_adjustment": -1.5, "injuries": ["Mikel Brown Jr. PG: back injury, OUT for first two games"], "coach": "Pat Kelsey",      "coach_wins": 4,  "coach_ffs": 0},
    "Michigan":         {"adj_em": 19.3, "adj_o": 116.2, "adj_d": 96.9, "adj_t": 67.2, "seed": 5,  "region": "South",   "consistency": "Streaky", "kill_shot_pct": 0.52, "injury_adjustment": 0.0,  "injuries": [], "coach": "Dusty May",       "coach_wins": 4,  "coach_ffs": 0},
    "Gonzaga":          {"adj_em": 20.2, "adj_o": 115.9, "adj_d": 95.7, "adj_t": 69.8, "seed": 6,  "region": "South",   "consistency": "Streaky", "kill_shot_pct": 0.59, "injury_adjustment": 0.0,  "injuries": [], "coach": "Mark Few",        "coach_wins": 24, "coach_ffs": 1},
    "Kansas":           {"adj_em": 18.9, "adj_o": 114.8, "adj_d": 95.9, "adj_t": 70.1, "seed": 7,  "region": "South",   "consistency": "Streaky", "kill_shot_pct": 0.56, "injury_adjustment": 0.0,  "injuries": [], "coach": "Bill Self",        "coach_wins": 28, "coach_ffs": 5},
    "Northwestern":     {"adj_em": 17.1, "adj_o": 113.2, "adj_d": 96.1, "adj_t": 66.9, "seed": 8,  "region": "South",   "consistency": "Suspect", "kill_shot_pct": 0.47, "injury_adjustment": 0.0,  "injuries": [], "coach": "Chris Collins",    "coach_wins": 2,  "coach_ffs": 0},
    "Wake Forest":      {"adj_em": 16.8, "adj_o": 112.9, "adj_d": 96.1, "adj_t": 68.4, "seed": 9,  "region": "South",   "consistency": "Suspect", "kill_shot_pct": 0.46, "injury_adjustment": 0.0,  "injuries": [], "coach": "Steve Forbes",     "coach_wins": 2,  "coach_ffs": 0},
    "Colorado State":   {"adj_em": 16.7, "adj_o": 112.8, "adj_d": 96.1, "adj_t": 69.2, "seed": 10, "region": "South",   "consistency": "Streaky", "kill_shot_pct": 0.50, "injury_adjustment": 0.0,  "injuries": [], "coach": "Niko Medved",     "coach_wins": 2,  "coach_ffs": 0},
    "Virginia":         {"adj_em": 14.6, "adj_o": 110.9, "adj_d": 96.3, "adj_t": 62.1, "seed": 11, "region": "South",   "consistency": "Strong",  "kill_shot_pct": 0.44, "injury_adjustment": 0.0,  "injuries": [], "coach": "Tony Bennett",     "coach_wins": 12, "coach_ffs": 1},
    "UC San Diego":     {"adj_em": 14.1, "adj_o": 110.4, "adj_d": 96.3, "adj_t": 67.9, "seed": 12, "region": "South",   "consistency": "Streaky", "kill_shot_pct": 0.48, "injury_adjustment": 0.0,  "injuries": [], "coach": "Eric Olen",       "coach_wins": 0,  "coach_ffs": 0},
    "Vermont":          {"adj_em": 11.4, "adj_o": 108.9, "adj_d": 97.5, "adj_t": 67.1, "seed": 13, "region": "South",   "consistency": "Strong",  "kill_shot_pct": 0.41, "injury_adjustment": 0.0,  "injuries": [], "coach": "John Becker",     "coach_wins": 2,  "coach_ffs": 0},
    "Oakland":          {"adj_em": 9.8,  "adj_o": 107.1, "adj_d": 97.3, "adj_t": 70.2, "seed": 14, "region": "South",   "consistency": "Suspect", "kill_shot_pct": 0.38, "injury_adjustment": 0.0,  "injuries": [], "coach": "Greg Kampe",      "coach_wins": 1,  "coach_ffs": 0},
    "Longwood":         {"adj_em": 6.4,  "adj_o": 104.3, "adj_d": 97.9, "adj_t": 68.6, "seed": 15, "region": "South",   "consistency": "Suspect", "kill_shot_pct": 0.34, "injury_adjustment": 0.0,  "injuries": [], "coach": "Griff Aldrich",   "coach_wins": 0,  "coach_ffs": 0},
    "Hampton":          {"adj_em": 3.8,  "adj_o": 102.1, "adj_d": 98.3, "adj_t": 67.4, "seed": 16, "region": "South",   "consistency": "Suspect", "kill_shot_pct": 0.29, "injury_adjustment": 0.0,  "injuries": [], "coach": "Buck Joyner",     "coach_wins": 0,  "coach_ffs": 0},

    # ── WEST REGION ────────────────────────────────────────────────────────────
    "Duke":             {"adj_em": 25.8, "adj_o": 120.1, "adj_d": 94.3, "adj_t": 70.4, "seed": 1,  "region": "West",    "consistency": "Strong",  "kill_shot_pct": 0.68, "injury_adjustment": -2.8, "injuries": ["Caleb Foster PG: foot fracture, season-ending surgery. Boozer (28% from 3) starting.", "Patrick Ngongba II C: foot soreness, questionable"], "coach": "Jon Scheyer",     "coach_wins": 11, "coach_ffs": 2},
    "Iowa State":       {"adj_em": 24.4, "adj_o": 118.6, "adj_d": 94.2, "adj_t": 69.3, "seed": 2,  "region": "West",    "consistency": "Strong",  "kill_shot_pct": 0.66, "injury_adjustment": 0.0,  "injuries": [], "coach": "T.J. Otzelberger", "coach_wins": 7,  "coach_ffs": 0},
    "Illinois":         {"adj_em": 22.7, "adj_o": 117.1, "adj_d": 94.4, "adj_t": 70.8, "seed": 3,  "region": "West",    "consistency": "Strong",  "kill_shot_pct": 0.64, "injury_adjustment": 0.0,  "injuries": [], "coach": "Brad Underwood",  "coach_wins": 7,  "coach_ffs": 0},
    "Texas":            {"adj_em": 20.4, "adj_o": 115.7, "adj_d": 95.3, "adj_t": 68.7, "seed": 4,  "region": "West",    "consistency": "Streaky", "kill_shot_pct": 0.57, "injury_adjustment": 0.0,  "injuries": [], "coach": "Rodney Terry",    "coach_wins": 6,  "coach_ffs": 0},
    "Purdue":           {"adj_em": 20.9, "adj_o": 116.2, "adj_d": 95.3, "adj_t": 67.9, "seed": 5,  "region": "West",    "consistency": "Strong",  "kill_shot_pct": 0.60, "injury_adjustment": 0.0,  "injuries": [], "coach": "Matt Painter",    "coach_wins": 14, "coach_ffs": 0},
    "Michigan State":   {"adj_em": 19.8, "adj_o": 115.4, "adj_d": 95.6, "adj_t": 69.2, "seed": 6,  "region": "West",    "consistency": "Strong",  "kill_shot_pct": 0.62, "injury_adjustment": 0.0,  "injuries": [], "coach": "Tom Izzo",        "coach_wins": 34, "coach_ffs": 8},
    "Florida":          {"adj_em": 18.6, "adj_o": 114.3, "adj_d": 95.7, "adj_t": 70.4, "seed": 7,  "region": "West",    "consistency": "Streaky", "kill_shot_pct": 0.55, "injury_adjustment": 0.0,  "injuries": [], "coach": "Todd Golden",     "coach_wins": 3,  "coach_ffs": 0},
    "Oklahoma":         {"adj_em": 16.4, "adj_o": 112.7, "adj_d": 96.3, "adj_t": 68.8, "seed": 8,  "region": "West",    "consistency": "Streaky", "kill_shot_pct": 0.49, "injury_adjustment": 0.0,  "injuries": [], "coach": "Porter Moser",    "coach_wins": 6,  "coach_ffs": 0},
    "Indiana":          {"adj_em": 16.1, "adj_o": 112.4, "adj_d": 96.3, "adj_t": 68.1, "seed": 9,  "region": "West",    "consistency": "Streaky", "kill_shot_pct": 0.48, "injury_adjustment": 0.0,  "injuries": [], "coach": "Thad Matta",      "coach_wins": 10, "coach_ffs": 1},
    "Colorado":         {"adj_em": 16.2, "adj_o": 112.5, "adj_d": 96.3, "adj_t": 67.6, "seed": 10, "region": "West",    "consistency": "Streaky", "kill_shot_pct": 0.49, "injury_adjustment": 0.0,  "injuries": [], "coach": "Tad Boyle",       "coach_wins": 4,  "coach_ffs": 0},
    "New Mexico":       {"adj_em": 14.3, "adj_o": 110.8, "adj_d": 96.5, "adj_t": 69.7, "seed": 11, "region": "West",    "consistency": "Streaky", "kill_shot_pct": 0.47, "injury_adjustment": 0.0,  "injuries": [], "coach": "Richard Pitino",   "coach_wins": 5,  "coach_ffs": 0},
    "Duquesne":         {"adj_em": 13.7, "adj_o": 110.1, "adj_d": 96.4, "adj_t": 68.3, "seed": 12, "region": "West",    "consistency": "Suspect", "kill_shot_pct": 0.44, "injury_adjustment": 0.0,  "injuries": [], "coach": "Keith Dambrot",   "coach_wins": 2,  "coach_ffs": 0},
    "High Point":       {"adj_em": 10.2, "adj_o": 107.6, "adj_d": 97.4, "adj_t": 70.2, "seed": 13, "region": "West",    "consistency": "Suspect", "kill_shot_pct": 0.40, "injury_adjustment": 0.0,  "injuries": [], "coach": "Tubby Smith",     "coach_wins": 8,  "coach_ffs": 0},
    "Winthrop":         {"adj_em": 8.9,  "adj_o": 106.4, "adj_d": 97.5, "adj_t": 69.1, "seed": 14, "region": "West",    "consistency": "Suspect", "kill_shot_pct": 0.37, "injury_adjustment": 0.0,  "injuries": [], "coach": "Mark Prosser",    "coach_wins": 1,  "coach_ffs": 0},
    "Liberty":          {"adj_em": 6.8,  "adj_o": 104.5, "adj_d": 97.7, "adj_t": 67.9, "seed": 15, "region": "West",    "consistency": "Suspect", "kill_shot_pct": 0.34, "injury_adjustment": 0.0,  "injuries": [], "coach": "Ritchie McKay",   "coach_wins": 2,  "coach_ffs": 0},
    "Montana":          {"adj_em": 2.8,  "adj_o": 101.2, "adj_d": 98.4, "adj_t": 66.8, "seed": 16, "region": "West",    "consistency": "Suspect", "kill_shot_pct": 0.27, "injury_adjustment": 0.0,  "injuries": [], "coach": "Travis DeCuire",  "coach_wins": 1,  "coach_ffs": 0},

    # ── MIDWEST REGION ─────────────────────────────────────────────────────────
    "Auburn":           {"adj_em": 26.2, "adj_o": 121.3, "adj_d": 95.1, "adj_t": 71.2, "seed": 1,  "region": "Midwest", "consistency": "Strong",  "kill_shot_pct": 0.72, "injury_adjustment": 0.0,  "injuries": [], "coach": "Bruce Pearl",     "coach_wins": 19, "coach_ffs": 2},
    "Houston":          {"adj_em": 22.4, "adj_o": 114.8, "adj_d": 92.4, "adj_t": 65.1, "seed": 2,  "region": "Midwest", "consistency": "Strong",  "kill_shot_pct": 0.74, "injury_adjustment": 0.0,  "injuries": [], "coach": "Kelvin Sampson",  "coach_wins": 21, "coach_ffs": 3},
    "Ole Miss":         {"adj_em": 22.1, "adj_o": 116.8, "adj_d": 94.7, "adj_t": 70.6, "seed": 3,  "region": "Midwest", "consistency": "Streaky", "kill_shot_pct": 0.61, "injury_adjustment": 0.0,  "injuries": [], "coach": "Chris Beard",     "coach_wins": 11, "coach_ffs": 0},
    "Kansas State":     {"adj_em": 20.1, "adj_o": 115.4, "adj_d": 95.3, "adj_t": 68.9, "seed": 4,  "region": "Midwest", "consistency": "Streaky", "kill_shot_pct": 0.56, "injury_adjustment": 0.0,  "injuries": [], "coach": "Jerome Tang",     "coach_wins": 4,  "coach_ffs": 0},
    "Baylor":           {"adj_em": 20.7, "adj_o": 116.1, "adj_d": 95.4, "adj_t": 69.7, "seed": 5,  "region": "Midwest", "consistency": "Streaky", "kill_shot_pct": 0.59, "injury_adjustment": 0.0,  "injuries": [], "coach": "Scott Drew",      "coach_wins": 16, "coach_ffs": 1},
    "UCF":              {"adj_em": 18.1, "adj_o": 114.2, "adj_d": 96.1, "adj_t": 68.4, "seed": 6,  "region": "Midwest", "consistency": "Streaky", "kill_shot_pct": 0.52, "injury_adjustment": 0.0,  "injuries": [], "coach": "Johnny Dawkins",  "coach_wins": 5,  "coach_ffs": 0},
    "Memphis":          {"adj_em": 17.8, "adj_o": 113.9, "adj_d": 96.1, "adj_t": 71.3, "seed": 7,  "region": "Midwest", "consistency": "Streaky", "kill_shot_pct": 0.55, "injury_adjustment": 0.0,  "injuries": [], "coach": "Penny Hardaway",  "coach_wins": 3,  "coach_ffs": 0},
    "Texas A&M":        {"adj_em": 17.3, "adj_o": 113.6, "adj_d": 96.3, "adj_t": 68.1, "seed": 8,  "region": "Midwest", "consistency": "Streaky", "kill_shot_pct": 0.51, "injury_adjustment": 0.0,  "injuries": [], "coach": "Buzz Williams",   "coach_wins": 8,  "coach_ffs": 0},
    "Oregon":           {"adj_em": 16.9, "adj_o": 113.1, "adj_d": 96.2, "adj_t": 68.8, "seed": 9,  "region": "Midwest", "consistency": "Streaky", "kill_shot_pct": 0.50, "injury_adjustment": 0.0,  "injuries": [], "coach": "Dana Altman",    "coach_wins": 15, "coach_ffs": 0},
    "Drake":            {"adj_em": 15.9, "adj_o": 112.2, "adj_d": 96.3, "adj_t": 68.4, "seed": 10, "region": "Midwest", "consistency": "Strong",  "kill_shot_pct": 0.52, "injury_adjustment": 0.0,  "injuries": [], "coach": "Darian DeVries",  "coach_wins": 3,  "coach_ffs": 0},
    "San Diego State":  {"adj_em": 15.4, "adj_o": 111.7, "adj_d": 96.3, "adj_t": 65.4, "seed": 11, "region": "Midwest", "consistency": "Strong",  "kill_shot_pct": 0.58, "injury_adjustment": 0.0,  "injuries": [], "coach": "Brian Dutcher",   "coach_wins": 10, "coach_ffs": 1},
    "James Madison":    {"adj_em": 13.4, "adj_o": 110.0, "adj_d": 96.6, "adj_t": 69.1, "seed": 12, "region": "Midwest", "consistency": "Streaky", "kill_shot_pct": 0.46, "injury_adjustment": 0.0,  "injuries": [], "coach": "Mark Byington",   "coach_wins": 1,  "coach_ffs": 0},
    "Northeast":        {"adj_em": 8.6,  "adj_o": 106.2, "adj_d": 97.6, "adj_t": 67.8, "seed": 13, "region": "Midwest", "consistency": "Suspect", "kill_shot_pct": 0.37, "injury_adjustment": 0.0,  "injuries": [], "coach": "Kyle Roper",      "coach_wins": 0,  "coach_ffs": 0},
    "Gardner-Webb":     {"adj_em": 7.3,  "adj_o": 105.1, "adj_d": 97.8, "adj_t": 68.3, "seed": 14, "region": "Midwest", "consistency": "Suspect", "kill_shot_pct": 0.35, "injury_adjustment": 0.0,  "injuries": [], "coach": "Tim Craft",       "coach_wins": 0,  "coach_ffs": 0},
    "Monmouth":         {"adj_em": 5.8,  "adj_o": 103.5, "adj_d": 97.7, "adj_t": 68.1, "seed": 15, "region": "Midwest", "consistency": "Suspect", "kill_shot_pct": 0.31, "injury_adjustment": 0.0,  "injuries": [], "coach": "King Rice",       "coach_wins": 1,  "coach_ffs": 0},
    "MVSU":             {"adj_em": 1.9,  "adj_o": 99.8,  "adj_d": 97.9, "adj_t": 66.4, "seed": 16, "region": "Midwest", "consistency": "Suspect", "kill_shot_pct": 0.25, "injury_adjustment": 0.0,  "injuries": [], "coach": "Donte' Jackson",  "coach_wins": 0,  "coach_ffs": 0},
}

# ─── Bracket structure: seed matchups per region ──────────────────────────────
# Standard R64 pairings: (higher_seed, lower_seed)
R64_SEEDS = [(1, 16), (8, 9), (5, 12), (4, 13), (6, 11), (3, 14), (7, 10), (2, 15)]

# Which bracket quadrant each game is in (determines R32 matchups)
# Top half: games 1, 2, 3, 4 (seeds 1,16,8,9,5,12,4,13)
# Bottom half: games 5, 6, 7, 8 (seeds 6,11,3,14,7,10,2,15)
R64_GAME_ORDER = [
    (1, 16), (8, 9),   # top-top → winners meet in R32
    (5, 12), (4, 13),  # top-bottom → winners meet in R32
    (6, 11), (3, 14),  # bottom-top → winners meet in R32
    (7, 10), (2, 15),  # bottom-bottom → winners meet in R32
]

# Regions map to halves of the national bracket
# East/South → one side of Final Four
# West/Midwest → other side of Final Four
NATIONAL_FF_PAIRINGS = [
    ("East", "South"),    # East champ vs South champ in Semifinal 1
    ("West", "Midwest"),  # West champ vs Midwest champ in Semifinal 2
]

REGION_ORDER = ["East", "South", "West", "Midwest"]

# ─── Pre-research predicted paths ─────────────────────────────────────────────
# Based on KenPom/EvanMiya/injury analysis from pre-tournament research
PREDICTED_RESULTS = {
    "East": {
        "R64": {
            "Arizona": "W", "Norfolk State": "L",
            "BYU": "W", "Penn State": "L",
            "St. John's": "W", "Akron": "L",   # St. John's slight fav
            "Texas Tech": "L", "Akron": "W",    # Akron UPSET — Toppin OUT
            "Creighton": "W", "VCU": "L",
            "Marquette": "W", "N. Kentucky": "L",
            "Missouri": "W", "Utah State": "L",
            "Tennessee": "W", "Sacred Heart": "L",
        },
        "R32": {
            "Arizona": "W", "BYU": "L",
            "Akron": "W", "St. John's": "L",    # Akron continues run
            "Creighton": "W", "Marquette": "L",  # toss-up, slight Creighton edge
            "Tennessee": "W", "Missouri": "L",
        },
        "S16": {
            "Arizona": "W", "Akron": "L",       # Arizona smothers Cinderella
            "Tennessee": "W", "Creighton": "L",
        },
        "E8": {
            "Arizona": "W", "Tennessee": "L",   # Arizona to Final Four
        },
        "FF_seed": 1,
        "FF_team": "Arizona",
    },
    "South": {
        "R64": {
            "Alabama": "W", "Hampton": "L",
            "Northwestern": "W", "Wake Forest": "L",
            "Michigan": "W", "UC San Diego": "L",
            "Louisville": "L", "Vermont": "W",  # Vermont UPSET — Brown Jr. OUT
            "Gonzaga": "W", "Virginia": "L",
            "Wisconsin": "W", "Oakland": "L",
            "Kansas": "W", "Colorado State": "L",
            "Kentucky": "W", "Longwood": "L",
        },
        "R32": {
            "Alabama": "W", "Northwestern": "L",
            "Michigan": "W", "Vermont": "L",    # Michigan survives scare
            "Wisconsin": "W", "Gonzaga": "L",
            "Kentucky": "W", "Kansas": "L",
        },
        "S16": {
            "Michigan": "W", "Alabama": "L",    # MICHIGAN UPSETS ALABAMA — Streaky/Izzo-killer
            "Kentucky": "W", "Wisconsin": "L",
        },
        "E8": {
            "Michigan": "W", "Kentucky": "L",   # Michigan to Final Four — Dusty May magic
        },
        "FF_seed": 5,
        "FF_team": "Michigan",
    },
    "West": {
        "R64": {
            "Duke": "W", "Montana": "L",
            "Indiana": "W", "Oklahoma": "L",   # Indiana slight edge
            "Purdue": "W", "Duquesne": "L",
            "Texas": "W", "High Point": "L",
            "Michigan State": "W", "New Mexico": "L",
            "Illinois": "W", "Winthrop": "L",
            "Florida": "W", "Colorado": "L",
            "Iowa State": "W", "Liberty": "L",
        },
        "R32": {
            "Duke": "W", "Indiana": "L",
            "Purdue": "W", "Texas": "L",
            "Illinois": "W", "Michigan State": "L",
            "Iowa State": "W", "Florida": "L",
        },
        "S16": {
            "Duke": "W", "Purdue": "L",
            "Iowa State": "W", "Illinois": "L",
        },
        "E8": {
            "Duke": "W", "Iowa State": "L",    # Duke to Final Four
        },
        "FF_seed": 1,
        "FF_team": "Duke",
    },
    "Midwest": {
        "R64": {
            "Auburn": "W", "MVSU": "L",
            "Texas A&M": "W", "Oregon": "L",
            "Baylor": "W", "James Madison": "L",
            "Kansas State": "W", "Northeast": "L",
            "UCF": "W", "San Diego State": "L",
            "Ole Miss": "W", "Gardner-Webb": "L",
            "Memphis": "W", "Drake": "L",
            "Houston": "W", "Monmouth": "L",
        },
        "R32": {
            "Auburn": "W", "Texas A&M": "L",
            "Baylor": "W", "Kansas State": "L",
            "Ole Miss": "W", "UCF": "L",
            "Houston": "W", "Memphis": "L",
        },
        "S16": {
            "Auburn": "W", "Baylor": "L",
            "Houston": "W", "Ole Miss": "L",
        },
        "E8": {
            "Houston": "W", "Auburn": "L",     # Houston over Auburn — defensive identity
        },
        "FF_seed": 2,
        "FF_team": "Houston",
    },
}

# ─── Notable upsets from research ─────────────────────────────────────────────
NOTABLE_UPSETS = [
    {"upset": "Akron over Texas Tech", "seed_line": "12 over 4", "reason": "JT Toppin (All-Big 12 F) ACL tear Feb 17, season-ending"},
    {"upset": "Vermont over Louisville", "seed_line": "13 over 4", "reason": "Mikel Brown Jr. (PG) back injury, OUT for first two games"},
    {"upset": "Michigan over Alabama", "seed_line": "5 over 1", "reason": "Dusty May system, Alabama Streaky classification vs Michigan's tournament edge"},
    {"upset": "Michigan over Kentucky", "seed_line": "5 over 2", "reason": "Michigan's Hot Hand tournament run, Kentucky inconsistent in big moments"},
    {"upset": "Houston over Auburn", "seed_line": "2 over 1", "reason": "Houston defensive identity smothers Auburn pace; Sampson outcoaches Pearl"},
]

# ─── Round schedule ───────────────────────────────────────────────────────────
ROUND_INFO = {
    "First Four": {"dates": "Mar 18-19, 2026", "location": "Dayton, OH"},
    "R64":        {"dates": "Mar 19-20, 2026", "location": "Various (8 sites)"},
    "R32":        {"dates": "Mar 21-22, 2026", "location": "Various (8 sites)"},
    "S16":        {"dates": "Mar 27-28, 2026", "location": "Various (4 sites)"},
    "E8":         {"dates": "Mar 29-30, 2026", "location": "Various (4 sites)"},
    "FF":         {"dates": "Apr 4-5, 2026",   "location": "San Antonio, TX"},
    "Championship": {"dates": "Apr 7, 2026",   "location": "San Antonio, TX"},
}

def get_teams_by_region(region: str) -> list[dict]:
    """Return all teams in a region, sorted by seed."""
    teams = [
        {"name": name, **data}
        for name, data in TEAM_DATA.items()
        if data["region"] == region
    ]
    return sorted(teams, key=lambda t: t["seed"])


def get_team(name: str) -> dict | None:
    return TEAM_DATA.get(name)


def get_r64_matchups(region: str) -> list[tuple[str, str]]:
    """Return R64 matchups for a region as (higher_seed_team, lower_seed_team)."""
    teams_by_seed = {t["seed"]: t["name"] for t in get_teams_by_region(region)}
    matchups = []
    for s1, s2 in R64_GAME_ORDER:
        if s1 in teams_by_seed and s2 in teams_by_seed:
            matchups.append((teams_by_seed[s1], teams_by_seed[s2]))
    return matchups


# ─── Confirmed Final Four (user-validated from tournament play) ───────────────
CONFIRMED_FINAL_FOUR = {
    "Semifinal_1": {"team_a": "Arizona", "team_b": "Michigan", "region_a": "East", "region_b": "South"},
    "Semifinal_2": {"team_a": "Duke",    "team_b": "Houston",  "region_a": "West",  "region_b": "Midwest"},
}


def get_predicted_bracket_path() -> dict:
    """Return the full predicted tournament bracket from pre-research."""
    result = {}
    for region, data in PREDICTED_RESULTS.items():
        result[region] = {
            "rounds": {k: v for k, v in data.items() if k not in ("FF_seed", "FF_team")},
            "ff_team": data["FF_team"],
            "ff_seed": data["FF_seed"],
        }
    result["Final Four"] = {
        "Semifinal 1": {"East": "Arizona", "South": "Michigan", "predicted_winner": "Arizona"},
        "Semifinal 2": {"West": "Duke", "Midwest": "Houston", "predicted_winner": "Houston"},
        "Championship": {"predicted_winner": "Arizona"},
    }
    return result
