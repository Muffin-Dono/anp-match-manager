# Tournament settings
INFO = {
    "full_name": "Winter Warzone 2025",
    "start_date": "2025-01-13",
    "equal_bans": True, # equal number of map bans per team
    "maps_per_match": 3, # number of maps in a single match
    "max_bans": 1, # maximum number of maps banned per team
    "max_picks": 1, # maximum number of maps picked per team
    "map_pools": ["Standard"] # list of available map pools
}

# List of available maps with base names, aliases, and map pool types
MAP_POOL = {
    "nt_ballistremade_ctg_a16": {
        "base_name": ["Ballistremade"],
        "aliases": ["Ballistrade", "Balli"],
        "map_pool": "Standard"
    },
    "nt_dew_ctg_b1": {
        "base_name": ["Dew"],
        "aliases": [],
        "map_pool": "Standard"
    },
    "nt_grid_ctg_b1comp": {
        "base_name": ["Grid"],
        "aliases": [],
        "map_pool": "Standard"
    },
    "nt_saitama_redux_ctg_a5": {
        "base_name": ["Saitama"],
        "aliases": ["Tietama"],
        "map_pool": "Standard"
    },
    "nt_snowfall_ctg_b12": {
        "base_name": ["Snowfall"],
        "aliases": [],
        "map_pool": "Standard"
    },
    "nt_tetsu_ctg_b6": {
        "base_name": ["Tetsu"],
        "aliases": ["Testu"],
        "map_pool": "Standard"
    },
    "nt_threadplate_ctg": {
        "base_name": ["Threadplate"],
        "aliases": ["Thread"],
        "map_pool": "Standard"
    }
}

# List of team Discord roles with role IDs, clan tags, and team names
TEAM_ROLES = {
    "[ASCI] Anti-Shaving Club I": {
        "id": 1319293536591413298,
        "tag": "ASCI",
        "name": "Anti-Shaving Club I",
    },
    "[ASCI] Anti-Shaving Club II": {
        "id": 1325535639260889209,
        "tag": "ASCII",
        "name": "Anti-Shaving Club II",
    },
    "[BLVD] Blood and Thunder": {
        "id": 1325533278513401919,
        "tag": "BLVD",
        "name": "Blood and Thunder"
    },
    "[BONK] Bonkurazu": {
        "id": 915003320081473576,
        "tag": "BONK",
        "name": "Bonkurazu"
    },
    "[GB] Ghost Brigade": {
        "id": 915291950893129788,
        "tag": "GB",
        "name": "Ghost Brigade"
    },
    "[HOP] Hopgoblins": {
        "id": 1319364385415630940,
        "tag": "HOP",
        "name": "Hopgoblins"
    },
    "[Ikko] Ikko Ikki": {
        "id": 915001460373225502,
        "tag": "Ikko",
        "name": "Ikko Ikki"
    },
    "[KOBA] KOBAYASHI CLAN": {
        "id": 1135193320155525171,
        "tag": "KOBA",
        "name": "KOBAYASHI CLAN"
    },
    "[MNHR] Menhera": {
        "id": 1139703753130389514,
        "tag": "MNHR",
        "name": "Menhera"
    },
    "[OSHA] Only Some Hammers Allowed": {
        "id": 1319292531078594592,
        "tag": "OSHA",
        "name": "Only Some Hammers Allowed"
    }
}
