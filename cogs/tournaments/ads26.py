# Tournament settings
INFO = {
    "full_name": "Autumn Draft Showdown 2026",
    "short_name": "ADS26",
    "start_date": "2026-09-07",
    "stream_url": "https://www.twitch.tv/activeneotokyoplayers",
    "bracket_url": "https://neotokyo.challonge.com/ads26",
    "vods_url": "https://www.youtube.com/@ActiveNeotokyo",
    "equal_bans": True, # equal number of map bans per team
    "maps_per_match": 3, # number of maps in a single match
    "max_bans": 1, # maximum number of maps banned per team
    "max_picks": 1, # maximum number of maps picked per team
    "map_pools": ["Standard"] # list of available map pools
}

# List of available maps with versions, aliases, and map pool types
MAPS = {
    "Dew": {
        "version": "nt_dew_ctg_b1f",
        "aliases": [],
        "pool": "Standard",
    },
    "Ghost": {
        "version": "ntre_ghost_ctg",
        "aliases": [],
        "pool": "Standard",
    },
    "Grid": {
        "version": "ntre_grid_ctg_b3",
        "aliases": [],
        "pool": "Standard",
    },
    "Hebi": {
        "version": "ntre_hebi_ctg_b2_zwia",
        "aliases": [],
        "pool": "Standard",
    },
    "Saitama": {
        "version": "ntre_saitama_ctg",
        "aliases": ["Tietama"],
        "pool": "Standard",
    },
    "Shinkansen": {
        "version": "nt_shinkansen_ctg",
        "aliases": [],
        "pool": "Standard",
    },
    "Tetsu": {
        "version": "ntre_tetsu_ctg_b6f3",
        "aliases": ["Testu"],
        "pool": "Standard",
    },
}

# List of teams with role names, clan tags, and role IDs
TEAMS = {
    "Boltronics": {
        "role": "[pug?] Boltronics",
        "tag": "pug?",
        "id": 1536849991581302937
    },
    "Disconnected and Confused": {
        "role": "[DAC] Disconnected and Confused",
        "tag": "DAC",
        "id": 1536850744542629948
    },
    "Exodisma": {
        "role": "[EXO] Exodisma",
        "tag": "EXO",
        "id": 1536847705454940402
    },
    "Large Larry Model": {
        "role": "[LLM] Large Larry Model",
        "tag": "LLM",
        "id": 1536849786488094740
    },
    "Lucky Strike": {
        "role": "[STRIKE] Lucky Strike",
        "tag": "STRIKE",
        "id": 1536851025917382766
    },
    "Road to Deepfrog": {
        "role": "dF. Road to Deepfrog",
        "tag": "dF.",
        "id": 1536848301410746388
    },
    "Zero Recons Surviving": {
        "role": "[ZRS] Zero Recons Surviving",
        "tag": "ZRS",
        "id": 1536849293661700246
    }
}
