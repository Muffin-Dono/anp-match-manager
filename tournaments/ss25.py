# Tournament settings
INFO = {
    "full_name": "Summer Skirmish 2025",
    "start_date": "2025-07-21",
    "equal_bans": True, # equal number of map bans per team
    "maps_per_match": 3, # number of maps in a single match
    "max_bans": 1, # maximum number of maps banned per team
    "max_picks": 1, # maximum number of maps picked per team
    "map_pools": ["Standard", "Wildcard"] # list of available map pools
}

# List of available maps with base names, aliases, and map pool types
MAP_POOL = {
    "nt_envoy_ctg": {
        "base_name": ["Envoy"],
        "aliases": [],
        "map_pool": "Standard"
    },
    "nt_oilstain_ctg": {
        "base_name": ["Oilstain"],
        "aliases": ["Oil"],
        "map_pool": "Standard",
    },
    "nt_rogue_ctg_b4": {
        "base_name": ["Rogue"],
        "aliases": ["Rouge"],
        "map_pool": "Standard",
    },
    "nt_scrapmetal_ctg_a7f": {
        "base_name": ["Scrapmetal"],
        "aliases": ["Scrap"],
        "map_pool": "Standard",
    },
    "nt_tetsu_ctg_b6f": {
        "base_name": ["Tetsu"],
        "aliases": ["Testu"],
        "map_pool": "Standard",
    },
    "nt_dawnlife_ctg_b1": {
        "base_name": ["Dawnlife"],
        "aliases": ["Dawn"],
        "map_pool": "Wildcard",
    },
    "nt_tetsujin_ctg": {
        "base_name": ["Tetsujin"],
        "aliases": ["Jin"],
        "map_pool": "Wildcard",
    },
    "nt_turmuk_ctg_beta3": {
        "base_name": ["Turmuk"],
        "aliases": ["Tarmac"],
        "map_pool": "Wildcard",
    }
}

# List of team Discord roles with role IDs, clan tags, and team names
TEAM_ROLES = {
    "[BONK] Bonkurazu": {
        "id": 915003320081473576,
        "tag": "BONK",
        "name": "Bonkurazu"
    },
    "._o< | DuctTales": {
        "id": 1386762664990212166,
        "tag": "._o<",
        "name": "DuctTales",
    },
    "[EQ] Equinox": {
        "id": 1386760980029112520,
        "tag": "EQ",
        "name": "Equinox"
    },
    "[KOBA] KOBAYASHI CLAN": {
        "id": 1135193320155525171,
        "tag": "KOBA",
        "name": "KOBAYASHI CLAN"
    },
    "[SAA] SHOCK AND AWE": {
        "id": 1386763196496609451,
        "tag": "SAA",
        "name": "SHOCK AND AWE"
    },
    "=-SLI-= Slightly Less Incompetent": {
        "id": 1396589635936849920,
        "tag": "SLI",
        "name": "Slightly Less Incompetent"
    },
    "[11:59] They Will Eat Earl's Dust": {
        "id": 1396589916695040093,
        "tag": "11:59",
        "name": "They Will Eat Earl's Dust"
    }
}
