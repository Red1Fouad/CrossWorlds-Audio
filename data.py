# --- Data for BGM Selector ---
BGM_DATA = {
    "Menu & System": {
        "BGM": "Menu & System Tracks",
    },
    "Track Themes": {
        # Ordered based on user request
        "1016": "E-Stadium", "1017": "Rainbow Garden", "1018": "Water Palace",
        "1022": "Metal Harbor", "1003": "Sand Road", "1030": "Colorful Mall",
        "1025": "Mystic Jungle", "1032": "Apotos", "1024": "Wonder Museum",
        "1029": "Crystal Mine", "1001": "Ocean View", "1033": "Pumpkin Mansion",
        "1034": "Urban Canyon", "1005": "Market Street", "1027": "Coral Town",
        "1023": "Blizzard Valley", "1021": "Radical Highway", "1020": "Chao Park",
        "1026": "Donpa Factory", "1028": "Aqua Forest", "1031": "Eggman Expo",
        "1035": "Kronos Island", "1036": "Northstar Islands", "1037": "White Space"
    },
    "Crossworlds": {
        "2001": "Sky Road", "2002": "Roulette Road", "2003": "Kraken Bay",
        "2004": "Golden Temple", "2005": "Magma Planet", "2007": "Hidden World",
        "2009": "Steampunk City", "2010": "Dragon Road", "2011": "Holoska",
        "2012": "Galactic Parade", "2014": "Dinosaur Jungle", "2015": "Sweet Mountain",
        "2016": "White Cave", "2017": "Cyber Space", "2019": "Digital Circuit",
    },
    "DLC Tracks": {
        "EXTND04": "Minecraft World",
        "EXTND05": "BiKiNi Bottom",
    },
    "Voice Lines": {
        "SON": "Sonic the Hedgehog",
        "TAI": "Miles 'Tails' Prower",
        "KNU": "Knuckles the Echidna",
        "AMY": "Amy Rose",
        "CRE": "Cream the Rabbit",
        "BIG": "Big the Cat",
        "SHA": "Shadow the Hedgehog",
        "ROU": "Rouge the Bat",
        "OME": "E-123 Omega",
        "SIL": "Silver the Hedgehog",
        "BLA": "Blaze the Cat",
        "VEC": "Vector the Crocodile",
        "ESP": "Espio the Chameleon",
        "CHA": "Charmy Bee",
        "ZAV": "Zavok",
        "ZAZ": "Zazz",
        "EGG": "Dr. Eggman",
        "MET": "Metal Sonic",
        "EGP": "Egg Pawn",
        "SAG": "Sage",
        "JET": "Jet the Hawk",
        "WAV": "Wave the Swallow",
        "STO": "Storm the Albatross",
    }
}

MENU_BGM_TRACKS = {
    # Label: (target .hca filename)
    "Title 1": "00054_streaming",
    "Title 2": "00055_streaming",
    "Race Park": "00041_streaming",
    "Garage": "00029_streaming",
    "Character Select": "00056_streaming",
    "Time Trial": "00052_streaming",
    "Friendship": "00028_streaming",
    "Lobby (World Match)": "00036_streaming",
    "Lobby (Friend Match)": "00038_streaming",
    "Lobby (Festival)": "00037_streaming",
    "CrossWorld Time Trial Intro": "00053_streaming",
    "Monster Truck": "00040_streaming",
}

DLC_SPONGEBOB_TRACKS = {
    "Intro": "00026_streaming",
    "Lap 1": "00023_streaming",
    "Final Lap": "00024_streaming",
    "Character Select": "00022_streaming",
    "Results": "00027_streaming",
    "Finish Jingle": "00028_streaming",
}

# Minecraft is handled separately now as a special case in the UI/repacking logic
DLC_MINECRAFT_TRACKS = {
    "Intro": "00034_streaming",
    "Overworld (Lap 1)": "00024_streaming",
    "Overworld (Out of Nether - Lap 1)": "00026_streaming",
    "The Nether (Lap 1)": "00027_streaming",
    "Overworld (Final Lap)": "00029_streaming",
    "Overworld (Out of The End - Final Lap)": "00031_streaming",
    "The End (Final Lap)": "00032_streaming",
    "Character Select": "00035_streaming",
    "Results": "00036_streaming",
    "Finish Jingle": "00042_streaming",
}

# A map to easily get the correct dictionary for a given ACB stem
SPECIAL_TRACK_MAP = {
    "BGM": MENU_BGM_TRACKS,
    "BGM_EXTND05": DLC_SPONGEBOB_TRACKS,
}

VOICE_CRE_TRACKS = {
    "1: Approach Rival": "00000_streaming",
    "2: Boost High 1": "00001_streaming",
    "3: Boost High 2": "00002_streaming",
    "4: Boost Low": "00003_streaming",
    "5: Boost Mid 1": "00004_streaming",
    "6: Boost Mid 2": "00005_streaming",
    "7: Break Object": "00006_streaming",
    "8: Ceremony 1": "00007_streaming",
    "9: Ceremony 2": "00008_streaming",
    "10: Character Select": "00009_streaming",
    "11: Checkpoint": "00010_streaming",
    "12: Common Discontent": "00011_streaming",
    "13: Common Elated": "00012_streaming",
    "14: Common Happy": "00013_streaming",
    "15: Common Incite": "00014_streaming",
    "16: Common Regretable": "00015_streaming",
    "17: Countdown 1": "00016_streaming",
    "18: Countdown 2": "00017_streaming",
    "19: Countdown Festa 1": "00018_streaming",
    "20: Countdown Festa 2": "00019_streaming",
    "21: Countdown Finalround 1": "00020_streaming",
    "22: Countdown Finalround 2": "00021_streaming",
    "23: Countdown Firstround": "00022_streaming",
    "24: Countdown Rankup": "00023_streaming",
    "25: Course Comment Cold": "00024_streaming",
    "26: Course Comment Fear": "00025_streaming",
    "27: Course Comment Fun": "00026_streaming",
    "28: Course Comment Hot": "00027_streaming",
    "29: Course Comment Like": "00028_streaming",
    "30: Course Comment Nostalgic": "00029_streaming",
    "31: Course Comment (Chao Park)": "00030_streaming",
    "32: Course Comment (Colorful Mall)": "00031_streaming",
    "33: Course Comment (Sky Road)": "00032_streaming",
    "34: Course Comment Surprise": "00033_streaming",
    "35: Courseout 1": "00034_streaming",
    "36: Courseout 2": "00035_streaming",
    "37: Dodge Item 1": "00036_streaming",
    "38: Dodge Item 2": "00037_streaming",
    "39: Dropout": "00038_streaming",
    "40: Enter Gate 1": "00039_streaming",
    "41: Enter Gate 2": "00040_streaming",
    "42: Enter Shortcut": "00041_streaming",
    "43: Fail Damage 1": "00042_streaming",
    "44: Fail Damage 2": "00043_streaming",
    "45: Fail Item Bodycut": "00044_streaming",
    "46: Fail Item Damage 1": "00045_streaming",
    "47: Fail Item Damage 2": "00046_streaming",
    "48: Fail Item Monster": "00047_streaming",
    "49: Fail Item To Amy": "00048_streaming",
    "50: Fail Item To Big": "00049_streaming",
    "51: Fail Item To Blaze": "00050_streaming",
    "52: Fail Item To Charmy": "00051_streaming",
    "53: Fail Item To Eggman": "00052_streaming",
    "54: Fail Item To Egpawn": "00053_streaming",
    "55: Fail Item To Espio": "00054_streaming",
    "56: Fail Item To Jet": "00055_streaming",
    "57: Fail Item To Knuckles": "00056_streaming",
    "58: Fail Item To Metal Sonic": "00057_streaming",
    "59: Fail Item To Omega": "00058_streaming",
    "60: Fail Item To Rouge": "00059_streaming",
    "61: Fail Item To Sage": "00060_streaming",
    "62: Fail Item To Shadow": "00061_streaming",
    "63: Fail Item To Silver": "00062_streaming",
    "64: Fail Item To Sonic": "00063_streaming",
    "65: Fail Item To Storm": "00064_streaming",
    "66: Fail Item To Tails": "00065_streaming",
    "67: Fail Item To Vector": "00066_streaming",
    "68: Fail Item To Wave": "00067_streaming",
    "69: Fail Item To Zavok": "00068_streaming",
    "70: Fail Item To Zazz": "00069_streaming",
    "71: Fail Push 1": "00070_streaming",
    "72: Fail Push 2": "00071_streaming",
    "73: Fail Spin 1": "00072_streaming",
    "74: Fail Spin 2": "00073_streaming",
    "75: Fail Wall 1": "00074_streaming",
    "76: Fail Wall 2": "00075_streaming",
    "77: First Race Movie Lose Rival": "00076_streaming",
    "78: First Race Movie Win Rival": "00077_streaming",
    "79: Get Item": "00078_streaming",
    "80: Get Item Common": "00079_streaming",
    "81: Get Machineparts": "00080_streaming",
    "82: Ghost Lose": "00081_streaming",
    "83: Ghost Win": "00082_streaming",
    "84: Goal Common": "00083_streaming",
    "85: Goal High 1": "00084_streaming",
    "86: Goal High 2": "00085_streaming",
    "87: Goal Low 1": "00086_streaming",
    "88: Goal Low 2": "00087_streaming",
    "89: Goal Middle 1": "00088_streaming",
    "90: Goal Middle 2": "00089_streaming",
    "91: Goal Top 1": "00090_streaming",
    "92: Goal Top 2": "00091_streaming",
    "93: Hit Item 1": "00092_streaming",
    "94: Hit Item 2": "00093_streaming",
    "95: Hit Item To Amy": "00094_streaming",
    "96: Hit Item To Big": "00095_streaming",
    "97: Hit Item To Blaze": "00096_streaming",
    "98: Hit Item To Charmy": "00097_streaming",
    "99: Hit Item To Eggman": "00098_streaming",
    "100: Hit Item To Egpawn": "00099_streaming",
    "101: Hit Item To Espio": "00100_streaming",
    "102: Hit Item To Jet": "00101_streaming",
    "103: Hit Item To Knuckles": "00102_streaming",
    "104: Hit Item To Metal Sonic": "00103_streaming",
    "105: Hit Item To Omega": "00104_streaming",
    "106: Hit Item To Rouge": "00105_streaming",
    "107: Hit Item To Sage": "00106_streaming",
    "108: Hit Item To Shadow": "00107_streaming",
    "109: Hit Item To Silver": "00108_streaming",
    "110: Hit Item To Sonic": "00109_streaming",
    "111: Hit Item To Storm": "00110_streaming",
    "112: Hit Item To Tails": "00111_streaming",
    "113: Hit Item To Vector": "00112_streaming",
    "114: Hit Item To Wave": "00113_streaming",
    "115: Hit Item To Zavok": "00114_streaming",
    "116: Hit Item To Zazz": "00115_streaming",
    "117: Introduce": "00116_streaming",
    "118: Is Approached Rival": "00117_streaming",
    "119: Is Overtaken Rival": "00118_streaming",
    "120: Keep Item": "00119_streaming",
    "121: Last Race Movie Lose Rival": "00120_streaming",
    "122: Last Race Movie Win Rival": "00121_streaming",
    "123: Left 1": "00122_streaming",
    "124: Left 2": "00123_streaming",
    "125: Max Ring": "00124_streaming",
    "126: Newrecord": "00125_streaming",
    "127: Overtake 1": "00126_streaming",
    "128: Overtake 2": "00127_streaming",
    "129: Overtake Rival": "00128_streaming",
    "130: Playerlevel Up": "00129_streaming",
    "131: Push 1": "00130_streaming",
    "132: Push 2": "00131_streaming",
    "133: Rankdown": "00132_streaming",
    "134: Rankup A": "00133_streaming",
    "135: Rankup B": "00134_streaming",
    "136: Rankup C": "00135_streaming",
    "137: Rankup Common 1": "00136_streaming",
    "138: Rankup Common 2": "00137_streaming",
    "139: Rankup D": "00138_streaming",
    "140: Rankup Highest 1": "00139_streaming",
    "141: Rankup Highest 2": "00140_streaming",
    "142: Rankup Legend": "00141_streaming",
    "143: Rankup Special": "00142_streaming",
    "144: Reaction Behind Player Rival": "00143_streaming",
    "145: Reaction Select Gate Rival": "00144_streaming",
    "146: Reaction Top Player Rival": "00145_streaming",
    "147: Ready Movie First To Amy Rival": "00146_streaming",
    "148: Ready Movie First To Big Rival": "00147_streaming",
    "149: Ready Movie First To Bla Rival": "00148_streaming",
    "150: Ready Movie First To Cha Rival": "00149_streaming",
    "151: Ready Movie First To Egg Rival": "00150_streaming",
    "152: Ready Movie First To Egp Rival": "00151_streaming",
    "153: Ready Movie First To Esp Rival": "00152_streaming",
    "154: Ready Movie First To Jet Rival": "00153_streaming",
    "155: Ready Movie First To Knu Rival": "00154_streaming",
    "156: Ready Movie First To Met Rival": "00155_streaming",
    "157: Ready Movie First To Ome Rival": "00156_streaming",
    "158: Ready Movie First To Rou Rival": "00157_streaming",
    "159: Ready Movie First To Sag Rival": "00158_streaming",
    "160: Ready Movie First To Sha Rival": "00159_streaming",
    "161: Ready Movie First To Sil Rival": "00160_streaming",
    "162: Ready Movie First To Son Rival": "00161_streaming",
    "163: Ready Movie First To Sto Rival": "00162_streaming",
    "164: Ready Movie First To Tai Rival": "00163_streaming",
    "165: Ready Movie First To Vec Rival": "00164_streaming",
    "166: Ready Movie First To Wav Rival": "00165_streaming",
    "167: Ready Movie First To Zav Rival": "00166_streaming",
    "168: Ready Movie First To Zaz Rival": "00167_streaming",
    "169: Ready Movie Last To Amy Rival": "00168_streaming",
    "170: Ready Movie Last To Big Rival": "00169_streaming",
    "171: Ready Movie Last To Bla Rival": "00170_streaming",
    "172: Ready Movie Last To Cha Rival": "00171_streaming",
    "173: Ready Movie Last To Egg Rival": "00172_streaming",
    "174: Ready Movie Last To Egp Rival": "00173_streaming",
    "175: Ready Movie Last To Esp Rival": "00174_streaming",
    "176: Ready Movie Last To Jet Rival": "00175_streaming",
    "177: Ready Movie Last To Knu Rival": "00176_streaming",
    "178: Ready Movie Last To Met Rival": "00177_streaming",
    "179: Ready Movie Last To Ome Rival": "00178_streaming",
    "180: Ready Movie Last To Rou Rival": "00179_streaming",
    "181: Ready Movie Last To Sag Rival": "00180_streaming",
    "182: Ready Movie Last To Sha Rival": "00181_streaming",
    "183: Ready Movie Last To Sil Rival": "00182_streaming",
    "184: Ready Movie Last To Son Rival": "00183_streaming",
    "185: Ready Movie Last To Sto Rival": "00184_streaming",
    "186: Ready Movie Last To Tai Rival": "00185_streaming",
    "187: Ready Movie Last To Vec Rival": "00186_streaming",
    "188: Ready Movie Last To Wav Rival": "00187_streaming",
    "189: Ready Movie Last To Zav Rival": "00188_streaming",
    "190: Ready Movie Last To Zaz Rival": "00189_streaming",
    "191: Ready Movie Rival": "00190_streaming",
    "192: Result Movie Draw Rival": "00191_streaming",
    "193: Result Movie Lose Rival": "00192_streaming",
    "194: Result Movie Win Rival": "00193_streaming",
    "195: Reverse": "00194_streaming",
    "196: Select Gate 1": "00195_streaming",
    "197: Select Gate 2": "00196_streaming",
    "198: Select Gate Rival": "00197_streaming",
    "199: Slipstream": "00198_streaming",
    "200: Stamp 1": "00199_streaming",
    "201: Stamp 2": "00200_streaming",
    "202: Stamp 3": "00201_streaming",
    "203: Stamp 4": "00202_streaming",
    "204: Stamp 5": "00203_streaming",
    "205: Stamp 7": "00204_streaming",
    "206: Stamp 6; Stamp 8": "00205_streaming",
    "207: Startboost 1": "00206_streaming",
    "208: Startboost 2": "00207_streaming",
    "209: Startboost 3": "00208_streaming",
    "210: Startboost 4": "00209_streaming",
    "211: Stunt First": "00210_streaming",
    "212: Stunt Second": "00211_streaming",
    "213: Stunt Third 1": "00212_streaming",
    "214: Stunt Third 2": "00213_streaming",
    "215: Timetrial Highrank": "00214_streaming",
    "216: Timetrial Lowrank": "00215_streaming",
    "217: Use Item Attack 1": "00216_streaming",
    "218: Use Item Attack 2": "00217_streaming",
    "219: Use Item Bodycut": "00218_streaming",
    "220: Use Item Bomb Max": "00219_streaming",
    "221: Use Item Boost 1": "00220_streaming",
    "222: Use Item Boost 2": "00221_streaming",
    "223: Use Item Darkchao": "00222_streaming",
    "224: Use Item King": "00223_streaming",
    "225: Use Item Monster": "00224_streaming",
    "226: Use Item Put 1": "00225_streaming",
    "227: Use Item Put 2": "00226_streaming",
    "228: Use Item Ring": "00227_streaming",
    "229: Use Item Violetvoid": "00228_streaming",
    "230: Use Item Warp": "00229_streaming",
}

def _generate_voice_lines(speaker_code, stage_ids=[]):
    """
    Generates a dictionary of voice lines with a variable number of course comments.
    The order of character interaction lines is generated dynamically based on the speaker.
    """
    # Create a combined map of all stage IDs to names for comments
    stage_name_map = {**BGM_DATA["Track Themes"], **BGM_DATA["Crossworlds"]}

    # Full list of characters for interactions
    all_characters = {
        "AMY": "Amy", "BIG": "Big", "BLA": "Blaze", "CHA": "Charmy", "CRE": "Cream",
        "EGG": "Eggman", "EGP": "Egg Pawn", "ESP": "Espio", "JET": "Jet", "KNU": "Knuckles",
        "MET": "Metal Sonic", "OME": "Omega", "ROU": "Rouge", "SAG": "Sage", "SHA": "Shadow",
        "SIL": "Silver", "SON": "Sonic", "STO": "Storm", "TAI": "Tails", "VEC": "Vector",
        "WAV": "Wave", "ZAV": "Zavok", "ZAZ": "Zazz"
    }

    # Filter out the speaker from the interaction list and sort alphabetically by name
    interaction_characters = {code: name for code, name in all_characters.items() if code != speaker_code}
    sorted_interaction_chars = dict(sorted(interaction_characters.items(), key=lambda item: item[1]))

    lines = {}
    i = 0

    # --- Section 1: Pre-Interaction Lines ---
    pre_comment_labels = [
        "Approach Rival", "Boost High 1", "Boost High 2", "Boost Low", "Boost Mid 1", "Boost Mid 2",
        "Break Object", "Ceremony 1", "Ceremony 2", "Character Select", "Checkpoint", "Common Discontent",
        "Common Elated", "Common Happy", "Common Incite", "Common Regretable", "Countdown 1", "Countdown 2",
        "Countdown Festa 1", "Countdown Festa 2", "Countdown Finalround 1", "Countdown Finalround 2",
        "Countdown Firstround", "Countdown Rankup"
    ]
    for label in pre_comment_labels:
        lines[f"{i+1}: {label}"] = f"{i:05d}_streaming" # 5-digit padding for file names
        i += 1

    # --- Section 2: Course Comments ---
    generic_comment_labels_1 = ["Cold", "Fear", "Fun", "Hot", "Like", "Nostalgic"]
    for label in generic_comment_labels_1:
        lines[f"{i+1}: Course Comment {label}"] = f"{i:05d}_streaming"
        i += 1

    for stage_id in stage_ids:
        stage_name = stage_name_map.get(stage_id, stage_id) # Fallback to ID if name not found (for "Unused")
        lines[f"{i+1}: Course Comment ({stage_name})"] = f"{i:05d}_streaming"
        i += 1

    lines[f"{i+1}: Course Comment Surprise"] = f"{i:05d}_streaming"
    i += 1

    # --- Section 3: Mid-section before character interactions ---
    mid_section_labels = [
        "Courseout 1", "Courseout 2", "Dodge Item 1", "Dodge Item 2", "Dropout", "Enter Gate 1", "Enter Gate 2",
        "Enter Shortcut", "Fail Damage 1", "Fail Damage 2", "Fail Item Bodycut", "Fail Item Damage 1",
        "Fail Item Damage 2", "Fail Item Monster"
    ]
    for label in mid_section_labels:
        lines[f"{i+1}: {label}"] = f"{i:05d}_streaming"
        i += 1

    # --- Section 4: Dynamic Character Interactions ---
    interaction_prefixes = [
        "Fail Item To", "Hit Item To", "Ready Movie First To", "Ready Movie Last To"
    ]
    for prefix in interaction_prefixes:
        for char_code, char_name in sorted_interaction_chars.items():
            # Handle special cases for label generation
            label_suffix = "Rival" if "Ready Movie" in prefix else ""
            label_char_name = "Egg Pawn" if char_name == "Egg Pawn" else char_name
            
            label = f"{prefix} {label_char_name} {label_suffix}".strip()
            lines[f"{i+1}: {label}"] = f"{i:05d}_streaming"
            i += 1

    # --- Section 5: Post-Interaction Lines ---
    post_interaction_labels = [
        "Fail Push 1", "Fail Push 2", "Fail Spin 1", "Fail Spin 2", "Fail Wall 1", "Fail Wall 2",
        "First Race Movie Lose Rival", "First Race Movie Win Rival", "Get Item", "Get Item Common", "Get Machineparts",
        "Ghost Lose", "Ghost Win", "Goal Common", "Goal High 1", "Goal High 2", "Goal Low 1", "Goal Low 2",
        "Goal Middle 1", "Goal Middle 2", "Goal Top 1", "Goal Top 2", "Hit Item 1", "Hit Item 2",
        "Introduce", "Is Approached Rival", "Is Overtaken Rival", "Keep Item",
        "Last Race Movie Lose Rival", "Last Race Movie Win Rival", "Left 1", "Left 2", "Max Ring", "Newrecord",
        "Overtake 1", "Overtake 2", "Overtake Rival", "Playerlevel Up", "Push 1", "Push 2", "Rankdown", "Rankup A",
        "Rankup B", "Rankup C", "Rankup Common 1", "Rankup Common 2", "Rankup D", "Rankup Highest 1",
        "Rankup Highest 2", "Rankup Legend", "Rankup Special", "Reaction Behind Player Rival",
        "Reaction Select Gate Rival", "Reaction Top Player Rival", "Ready Movie Rival", "Result Movie Draw Rival", "Result Movie Lose Rival",
        "Result Movie Win Rival", "Reverse", "Select Gate 1", "Select Gate 2", "Select Gate Rival", "Slipstream",
        "Stamp 1", "Stamp 2", "Stamp 3", "Stamp 4", "Stamp 5", "Stamp 7", "Stamp 6; Stamp 8", "Startboost 1",
        "Startboost 2", "Startboost 3", "Startboost 4", "Stunt First", "Stunt Second", "Stunt Third 1",
        "Stunt Third 2", "Timetrial Highrank", "Timetrial Lowrank", "Use Item Attack 1", "Use Item Attack 2",
        "Use Item Bodycut", "Use Item Bomb Max", "Use Item Boost 1", "Use Item Boost 2", "Use Item Darkchao",
        "Use Item King", "Use Item Monster", "Use Item Put 1", "Use Item Put 2", "Use Item Ring", "Use Item Violetvoid",
        "Use Item Warp"
    ]
    for label in post_interaction_labels:
        lines[f"{i+1}: {label}"] = f"{i:05d}_streaming"
        i += 1

    return lines

# --- Voice Line Dictionaries for All Characters ---

VOICE_SON_TRACKS = _generate_voice_lines('SON', stage_ids=['1032', '1035', '1037', '2003', '2014', '2017'])
VOICE_TAI_TRACKS = _generate_voice_lines('TAI', stage_ids=['1017', '1026', '1032', '1035', '2007', '2017'])
VOICE_KNU_TRACKS = _generate_voice_lines('KNU', stage_ids=['1003', '1018', '1029', '1033', '2004', '2012'])
VOICE_AMY_TRACKS = _generate_voice_lines('AMY', stage_ids=['1005', '1020', '1035', '1036', '2002', '2015'])
VOICE_BIG_TRACKS = _generate_voice_lines('BIG', stage_ids=['1020', '1030', '2011'])
VOICE_SHA_TRACKS = _generate_voice_lines('SHA', stage_ids=['1016', '1022', '1031', '1033', '1037', '2019'])
VOICE_ROU_TRACKS = _generate_voice_lines('ROU', stage_ids=['1030', '2002', '2004'])
VOICE_OME_TRACKS = _generate_voice_lines('OME', stage_ids=['1025', '1031', '2012'])
VOICE_SIL_TRACKS = _generate_voice_lines('SIL', stage_ids=['1018', '1024', '2015'])
VOICE_BLA_TRACKS = _generate_voice_lines('BLA', stage_ids=['1020', '1027', '2001'])
VOICE_VEC_TRACKS = _generate_voice_lines('VEC', stage_ids=['1001', '1033', '2015'])
VOICE_ESP_TRACKS = _generate_voice_lines('ESP', stage_ids=['1001', '1027', '1036'])
VOICE_CHA_TRACKS = _generate_voice_lines('CHA', stage_ids=['1001', '1017', '2015'])
VOICE_ZAV_TRACKS = _generate_voice_lines('ZAV', stage_ids=['2001', '2007', '2010'])
VOICE_ZAZ_TRACKS = _generate_voice_lines('ZAZ', stage_ids=['2005', '2007', '2009'])
VOICE_EGG_TRACKS = _generate_voice_lines('EGG', stage_ids=['1022', '1025', '1026', '1031', '2009', '2019'])
VOICE_SAG_TRACKS = _generate_voice_lines('SAG', stage_ids=['1025', '1031', '2017'])
VOICE_JET_TRACKS = _generate_voice_lines('JET', stage_ids=['1016', '1034', '2016'])
VOICE_WAV_TRACKS = _generate_voice_lines('WAV', stage_ids=['1024', '1028', '2004'])
VOICE_STO_TRACKS = _generate_voice_lines('STO', stage_ids=['1023', '2004', '2015'])
VOICE_MET_TRACKS = _generate_voice_lines('MET', stage_ids=['Unused 1', 'Unused 2', 'Unused 3'])
VOICE_EGP_TRACKS = _generate_voice_lines('EGP', stage_ids=['Unused 1', 'Unused 2', 'Unused 3'])
VOICE_CRE_TRACKS = _generate_voice_lines('CRE', stage_ids=['1020', '1030', '2001'])
