import os
import subprocess
import sys
import re
import threading
import queue
from pathlib import Path

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox, scrolledtext
except ImportError:
    print("Error: tkinter module not found. Please ensure you are running a standard Python installation.")
    sys.exit(1)


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
    "Voice Lines": {
        "CRE": "Cream the Rabbit",
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

# Placeholder for Cream's voice lines.
# This will be populated with the list of 230 names.
VOICE_CRE_TRACKS = {
    "1: approach_rival": "00000_streaming",
    "2: boost_high_1": "00001_streaming",
    "3: boost_high_2": "00002_streaming",
    "4: boost_low": "00003_streaming",
    "5: boost_mid_1": "00004_streaming",
    "6: boost_mid_2": "00005_streaming",
    "7: break_object": "00006_streaming",
    "8: ceremony_1": "00007_streaming",
    "9: ceremony_2": "00008_streaming",
    "10: characterselect": "00009_streaming",
    "11: checkpoint": "00010_streaming",
    "12: common_discontent": "00011_streaming",
    "13: common_elated": "00012_streaming",
    "14: common_happy": "00013_streaming",
    "15: common_incite": "00014_streaming",
    "16: common_regretable": "00015_streaming",
    "17: countdown_1": "00016_streaming",
    "18: countdown_2": "00017_streaming",
    "19: countdown_festa_1": "00018_streaming",
    "20: countdown_festa_2": "00019_streaming",
    "21: countdown_finalround_1": "00020_streaming",
    "22: countdown_finalround_2": "00021_streaming",
    "23: countdown_firstround": "00022_streaming",
    "24: countdown_rankup": "00023_streaming",
    "25: coursecomment_cold": "00024_streaming",
    "26: coursecomment_fear": "00025_streaming",
    "27: coursecomment_fun": "00026_streaming",
    "28: coursecomment_hot": "00027_streaming",
    "29: coursecomment_like": "00028_streaming",
    "30: coursecomment_nostalgic": "00029_streaming",
    "31: coursecomment_stg1020": "00030_streaming",
    "32: coursecomment_stg1030": "00031_streaming",
    "33: coursecomment_stg2001": "00032_streaming",
    "34: coursecomment_surprise": "00033_streaming",
    "35: courseout_1": "00034_streaming",
    "36: courseout_2": "00035_streaming",
    "37: dodge_item_1": "00036_streaming",
    "38: dodge_item_2": "00037_streaming",
    "39: dropout": "00038_streaming",
    "40: enter_gate_1": "00039_streaming",
    "41: enter_gate_2": "00040_streaming",
    "42: enter_shortcut": "00041_streaming",
    "43: fail_damage_1": "00042_streaming",
    "44: fail_damage_2": "00043_streaming",
    "45: fail_item_bodycut": "00044_streaming",
    "46: fail_item_damage_1": "00045_streaming",
    "47: fail_item_damage_2": "00046_streaming",
    "48: fail_item_monster": "00047_streaming",
    "49: fail_item_to_amy": "00048_streaming",
    "50: fail_item_to_big": "00049_streaming",
    "51: fail_item_to_bla": "00050_streaming",
    "52: fail_item_to_cha": "00051_streaming",
    "53: fail_item_to_egg": "00052_streaming",
    "54: fail_item_to_egp": "00053_streaming",
    "55: fail_item_to_esp": "00054_streaming",
    "56: fail_item_to_jet": "00055_streaming",
    "57: fail_item_to_knu": "00056_streaming",
    "58: fail_item_to_met": "00057_streaming",
    "59: fail_item_to_ome": "00058_streaming",
    "60: fail_item_to_rou": "00059_streaming",
    "61: fail_item_to_sag": "00060_streaming",
    "62: fail_item_to_sha": "00061_streaming",
    "63: fail_item_to_sil": "00062_streaming",
    "64: fail_item_to_son": "00063_streaming",
    "65: fail_item_to_sto": "00064_streaming",
    "66: fail_item_to_tai": "00065_streaming",
    "67: fail_item_to_vec": "00066_streaming",
    "68: fail_item_to_wav": "00067_streaming",
    "69: fail_item_to_zav": "00068_streaming",
    "70: fail_item_to_zaz": "00069_streaming",
    "71: fail_push_1": "00070_streaming",
    "72: fail_push_2": "00071_streaming",
    "73: fail_spin_1": "00072_streaming",
    "74: fail_spin_2": "00073_streaming",
    "75: fail_wall_1": "00074_streaming",
    "76: fail_wall_2": "00075_streaming",
    "77: first_race_movie_lose_rival": "00076_streaming",
    "78: first_race_movie_win_rival": "00077_streaming",
    "79: get_item": "00078_streaming",
    "80: get_item_common": "00079_streaming",
    "81: get_machineparts": "00080_streaming",
    "82: ghost_lose": "00081_streaming",
    "83: ghost_win": "00082_streaming",
    "84: goal_common": "00083_streaming",
    "85: goal_high_1": "00084_streaming",
    "86: goal_high_2": "00085_streaming",
    "87: goal_low_1": "00086_streaming",
    "88: goal_low_2": "00087_streaming",
    "89: goal_middle_1": "00088_streaming",
    "90: goal_middle_2": "00089_streaming",
    "91: goal_top_1": "00090_streaming",
    "92: goal_top_2": "00091_streaming",
    "93: hit_item_1": "00092_streaming",
    "94: hit_item_2": "00093_streaming",
    "95: hit_item_to_amy": "00094_streaming",
    "96: hit_item_to_big": "00095_streaming",
    "97: hit_item_to_bla": "00096_streaming",
    "98: hit_item_to_cha": "00097_streaming",
    "99: hit_item_to_egg": "00098_streaming",
    "100: hit_item_to_egp": "00099_streaming",
    "101: hit_item_to_esp": "00100_streaming",
    "102: hit_item_to_jet": "00101_streaming",
    "103: hit_item_to_knu": "00102_streaming",
    "104: hit_item_to_met": "00103_streaming",
    "105: hit_item_to_ome": "00104_streaming",
    "106: hit_item_to_rou": "00105_streaming",
    "107: hit_item_to_sag": "00106_streaming",
    "108: hit_item_to_sha": "00107_streaming",
    "109: hit_item_to_sil": "00108_streaming",
    "110: hit_item_to_son": "00109_streaming",
    "111: hit_item_to_sto": "00110_streaming",
    "112: hit_item_to_tai": "00111_streaming",
    "113: hit_item_to_vec": "00112_streaming",
    "114: hit_item_to_wav": "00113_streaming",
    "115: hit_item_to_zav": "00114_streaming",
    "116: hit_item_to_zaz": "00115_streaming",
    "117: introduce": "00116_streaming",
    "118: is_approached_rival": "00117_streaming",
    "119: is_overtaken_rival": "00118_streaming",
    "120: keep_item": "00119_streaming",
    "121: last_race_movie_lose_rival": "00120_streaming",
    "122: last_race_movie_win_rival": "00121_streaming",
    "123: left_1": "00122_streaming",
    "124: left_2": "00123_streaming",
    "125: max_ring": "00124_streaming",
    "126: newrecord": "00125_streaming",
    "127: overtake_1": "00126_streaming",
    "128: overtake_2": "00127_streaming",
    "129: overtake_rival": "00128_streaming",
    "130: playerlevel_up": "00129_streaming",
    "131: push_1": "00130_streaming",
    "132: push_2": "00131_streaming",
    "133: rankdown": "00132_streaming",
    "134: rankup_a": "00133_streaming",
    "135: rankup_b": "00134_streaming",
    "136: rankup_c": "00135_streaming",
    "137: rankup_common_1": "00136_streaming",
    "138: rankup_common_2": "00137_streaming",
    "139: rankup_d": "00138_streaming",
    "140: rankup_highest_1": "00139_streaming",
    "141: rankup_highest_2": "00140_streaming",
    "142: rankup_legend": "00141_streaming",
    "143: rankup_special": "00142_streaming",
    "144: reaction_behind_player_rival": "00143_streaming",
    "145: reaction_select_gate_rival": "00144_streaming",
    "146: reaction_top_player_rival": "00145_streaming",
    "147: ready_movie_first_to_amy_rival": "00146_streaming",
    "148: ready_movie_first_to_big_rival": "00147_streaming",
    "149: ready_movie_first_to_bla_rival": "00148_streaming",
    "150: ready_movie_first_to_cha_rival": "00149_streaming",
    "151: ready_movie_first_to_egg_rival": "00150_streaming",
    "152: ready_movie_first_to_egp_rival": "00151_streaming",
    "153: ready_movie_first_to_esp_rival": "00152_streaming",
    "154: ready_movie_first_to_jet_rival": "00153_streaming",
    "155: ready_movie_first_to_knu_rival": "00154_streaming",
    "156: ready_movie_first_to_met_rival": "00155_streaming",
    "157: ready_movie_first_to_ome_rival": "00156_streaming",
    "158: ready_movie_first_to_rou_rival": "00157_streaming",
    "159: ready_movie_first_to_sag_rival": "00158_streaming",
    "160: ready_movie_first_to_sha_rival": "00159_streaming",
    "161: ready_movie_first_to_sil_rival": "00160_streaming",
    "162: ready_movie_first_to_son_rival": "00161_streaming",
    "163: ready_movie_first_to_sto_rival": "00162_streaming",
    "164: ready_movie_first_to_tai_rival": "00163_streaming",
    "165: ready_movie_first_to_vec_rival": "00164_streaming",
    "166: ready_movie_first_to_wav_rival": "00165_streaming",
    "167: ready_movie_first_to_zav_rival": "00166_streaming",
    "168: ready_movie_first_to_zaz_rival": "00167_streaming",
    "169: ready_movie_last_to_amy_rival": "00168_streaming",
    "170: ready_movie_last_to_big_rival": "00169_streaming",
    "171: ready_movie_last_to_bla_rival": "00170_streaming",
    "172: ready_movie_last_to_cha_rival": "00171_streaming",
    "173: ready_movie_last_to_egg_rival": "00172_streaming",
    "174: ready_movie_last_to_egp_rival": "00173_streaming",
    "175: ready_movie_last_to_esp_rival": "00174_streaming",
    "176: ready_movie_last_to_jet_rival": "00175_streaming",
    "177: ready_movie_last_to_knu_rival": "00176_streaming",
    "178: ready_movie_last_to_met_rival": "00177_streaming",
    "179: ready_movie_last_to_ome_rival": "00178_streaming",
    "180: ready_movie_last_to_rou_rival": "00179_streaming",
    "181: ready_movie_last_to_sag_rival": "00180_streaming",
    "182: ready_movie_last_to_sha_rival": "00181_streaming",
    "183: ready_movie_last_to_sil_rival": "00182_streaming",
    "184: ready_movie_last_to_son_rival": "00183_streaming",
    "185: ready_movie_last_to_sto_rival": "00184_streaming",
    "186: ready_movie_last_to_tai_rival": "00185_streaming",
    "187: ready_movie_last_to_vec_rival": "00186_streaming",
    "188: ready_movie_last_to_wav_rival": "00187_streaming",
    "189: ready_movie_last_to_zav_rival": "00188_streaming",
    "190: ready_movie_last_to_zaz_rival": "00189_streaming",
    "191: ready_movie_rival": "00190_streaming",
    "192: result_movie_draw_rival": "00191_streaming",
    "193: result_movie_lose_rival": "00192_streaming",
    "194: result_movie_win_rival": "00193_streaming",
    "195: reverse": "00194_streaming",
    "196: select_gate_1": "00195_streaming",
    "197: select_gate_2": "00196_streaming",
    "198: select_gate_rival": "00197_streaming",
    "199: slipstream": "00198_streaming",
    "200: stamp_1": "00199_streaming",
    "201: stamp_2": "00200_streaming",
    "202: stamp_3": "00201_streaming",
    "203: stamp_4": "00202_streaming",
    "204: stamp_5": "00203_streaming",
    "205: stamp_7": "00204_streaming",
    "206: stamp_6; stamp_8": "00205_streaming",
    "207: startboost_1": "00206_streaming",
    "208: startboost_2": "00207_streaming",
    "209: startboost_3": "00208_streaming",
    "210: startboost_4": "00209_streaming",
    "211: stunt_first": "00210_streaming",
    "212: stunt_second": "00211_streaming",
    "213: stunt_third_1": "00212_streaming",
    "214: stunt_third_2": "00213_streaming",
    "215: timetrial_highrank": "00214_streaming",
    "216: timetrial_lowrank": "00215_streaming",
    "217: use_item_attack_1": "00216_streaming",
    "218: use_item_attack_2": "00217_streaming",
    "219: use_item_bodycut": "00218_streaming",
    "220: use_item_bomb_max": "00219_streaming",
    "221: use_item_boost_1": "00220_streaming",
    "222: use_item_boost_2": "00221_streaming",
    "223: use_item_darkchao": "00222_streaming",
    "224: use_item_king": "00223_streaming",
    "225: use_item_monster": "00224_streaming",
    "226: use_item_put_1": "00225_streaming",
    "227: use_item_put_2": "00226_streaming",
    "228: use_item_ring": "00227_streaming",
    "229: use_item_violetvoid": "00228_streaming",
    "230: use_item_warp": "00229_streaming",
}
class BGMSelectorWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Select Common BGM")
        self.geometry("600x600")
        self.transient(parent)
        self.grab_set()
        self.result = None

        tree = ttk.Treeview(self, columns=("filename",), show="tree headings")
        tree.heading("#0", text="Name")
        tree.heading("filename", text="Filename")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for category, tracks in BGM_DATA.items():
            category_node = tree.insert("", "end", text=category, open=True)
            for id_num, name in tracks.items():
                if category == "Menu & System":
                    filename = "BGM.acb"
                elif category == "Voice Lines":
                    filename = f"VOICE_{id_num}.acb"
                else:
                    filename = f"BGM_STG{id_num}.acb"
                display_text = f"{id_num}: {name}" if category != "Menu & System" else name
                tree.insert(category_node, "end", text=display_text, values=(filename,))
        def on_select():
            selected_item = tree.focus()
            if selected_item and tree.parent(selected_item): # Ensure a child item is selected
                self.result = tree.item(selected_item, "values")[0]
                self.destroy()

        tree.bind("<Double-1>", lambda e: on_select())
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Select", command=on_select).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

# --- Configuration ---
# Set the paths to your tools relative to this script.
TOOLS_DIR = Path("tools")
ACB_EDITOR = TOOLS_DIR / "AcbEditor.exe"
CONVERT_BAT = TOOLS_DIR / "Convert2UNION.bat"
UNREAL_PAK = TOOLS_DIR / "UnrealPak.bat"
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

class ThreadedTask(threading.Thread):
    def __init__(self, queue, function, *args, **kwargs):
        super().__init__()
        self.queue = queue
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.function(*self.args, **self.kwargs)
            self.queue.put(('success', result))
        except Exception as e:
            self.queue.put(('error', e))

class ModBuilderGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CrossWorlds Music Mod Builder")
        self.geometry("800x750")

        # --- Menu Bar ---
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        # Create a "Help" menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Credits", command=self.show_credits)

        # --- State Variables ---
        self.acb_file = tk.StringVar()
        self.unpacked_folder = tk.StringVar()
        self.mod_name = tk.StringVar(value="MyAwesomeMusicMod")
        self.original_files = []
        self.new_files = []
        # StringVars for the new replacement comboboxes
        self.intro_var = tk.StringVar()
        self.lap1_var = tk.StringVar()
        self.final_lap_var = tk.StringVar()

        # --- New state vars for direct file selection ---
        self.intro_wav_path = tk.StringVar()
        self.lap1_wav_path = tk.StringVar()
        self.final_lap_wav_path = tk.StringVar()

        self.intro_loops_var = tk.BooleanVar()
        self.intro_loop_start_var = tk.StringVar()
        self.intro_loop_end_var = tk.StringVar()

        self.lap1_loops_var = tk.BooleanVar()
        self.lap1_loop_start_var = tk.StringVar()
        self.lap1_loop_end_var = tk.StringVar()

        self.final_lap_loops_var = tk.BooleanVar()
        self.final_lap_loop_start_var = tk.StringVar()
        self.final_lap_loop_end_var = tk.StringVar()
        
        self.status_var = tk.StringVar(value="Ready.")
        # --- New state vars for menu music ---
        self.menu_track_vars = {}
        self.voice_cre_track_vars = {}

        self.replacement_map = {}

        # --- Main Layout ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Create Widgets ---
        self._create_widgets(main_frame)

        # --- Check for tools on startup ---
        self.check_tools()

        # --- Status Bar ---
        status_bar = ttk.Label(self, textvariable=self.status_var, anchor=tk.W, relief=tk.SUNKEN, padding="2 5")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _create_widgets(self, parent):
        # --- Step 1: Unpack ---
        unpack_frame = ttk.LabelFrame(parent, text="Step 1: Select & Unpack ACB", padding="10")
        unpack_frame.pack(fill=tk.X, pady=5)

        ttk.Label(unpack_frame, text="ACB File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(unpack_frame, textvariable=self.acb_file, state='readonly').grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5)
        
        ttk.Button(unpack_frame, text="Select BGM...", command=self.select_common_bgm).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.unpack_button = ttk.Button(unpack_frame, text="Unpack", command=self.unpack_acb, state=tk.DISABLED)
        self.unpack_button.grid(row=1, column=2, sticky=tk.E, padx=5, pady=5)
        unpack_frame.columnconfigure(1, weight=1)

        # --- Step 2: Convert ---
        convert_outer_frame = ttk.LabelFrame(parent, text="Step 2: Convert Audio", padding="10")
        convert_outer_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Add a placeholder label
        self.unpack_first_label = ttk.Label(convert_outer_frame, text="Please select and unpack an ACB file in Step 1 to see conversion options.", justify=tk.CENTER)
        self.unpack_first_label.pack(expand=True)

        # Create a canvas and a scrollbar for the scrollable area
        self.canvas = tk.Canvas(convert_outer_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(convert_outer_frame, orient="vertical", command=self.canvas.yview)
        scrollable_frame = ttk.Frame(self.canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Widgets are created but not packed yet. They will be shown after unpacking.
        # self.canvas.pack(side="left", fill="both", expand=True)
        # self.scrollbar.pack(side="right", fill="y")

        # --- Mouse Wheel Scrolling ---
        def _on_mousewheel(event):
            # Determine scroll direction and magnitude
            if sys.platform == "win32":
                delta = -1 * (event.delta // 120)
            elif sys.platform == "darwin": # macOS
                delta = event.delta
            else: # Linux
                if event.num == 4:
                    delta = -1
                else:
                    delta = 1
            self.canvas.yview_scroll(delta, "units")

        self.canvas.bind_all("<MouseWheel>", _on_mousewheel) # Windows/macOS
        self.canvas.bind_all("<Button-4>", _on_mousewheel)   # Linux scroll up
        self.canvas.bind_all("<Button-5>", _on_mousewheel)   # Linux scroll down

        # Create track selection widgets
        self.stage_music_frame = ttk.Frame(scrollable_frame)
        self.stage_music_frame.pack(fill=tk.X)

        self.intro_frame, self.intro_widgets = self._create_track_selector(self.stage_music_frame, "Intro Music", self.intro_wav_path, self.select_intro_wav, self.intro_loops_var, self.intro_loop_start_var, self.intro_loop_end_var)
        ttk.Separator(self.stage_music_frame, orient='horizontal').pack(fill='x', pady=10)
        self.lap1_frame, self.lap1_widgets = self._create_track_selector(self.stage_music_frame, "Lap 1 Music", self.lap1_wav_path, self.select_lap1_wav, self.lap1_loops_var, self.lap1_loop_start_var, self.lap1_loop_end_var)
        ttk.Separator(self.stage_music_frame, orient='horizontal').pack(fill='x', pady=10)
        self.final_lap_frame, self.final_lap_widgets = self._create_track_selector(self.stage_music_frame, "Final Lap Music", self.final_lap_wav_path, self.select_final_lap_wav, self.final_lap_loops_var, self.final_lap_loop_start_var, self.final_lap_loop_end_var)

        # --- New Menu Music Frame ---
        self.menu_music_frame = ttk.Frame(scrollable_frame)
        # Don't pack it yet, will be managed in set_acb_file

        for label, hca_name in MENU_BGM_TRACKS.items():
            path_var = tk.StringVar()
            loop_var = tk.BooleanVar()
            start_var = tk.StringVar()
            end_var = tk.StringVar()
            self.menu_track_vars[hca_name] = {'path': path_var, 'loop': loop_var, 'start': start_var, 'end': end_var}
            frame, _ = self._create_track_selector(self.menu_music_frame, label, path_var, lambda p=path_var: self._select_wav_file(p), loop_var, start_var, end_var)
            ttk.Separator(self.menu_music_frame, orient='horizontal').pack(fill='x', pady=5, after=frame)

        # --- New Voice Line Frame (for VOICE_CRE) ---
        self.voice_cre_frame = ttk.Frame(scrollable_frame)
        # Don't pack it yet, will be managed in set_acb_file

        for label, hca_name in VOICE_CRE_TRACKS.items():
            path_var = tk.StringVar()
            loop_var = tk.BooleanVar()
            start_var = tk.StringVar()
            end_var = tk.StringVar()
            self.voice_cre_track_vars[hca_name] = {'path': path_var, 'loop': loop_var, 'start': start_var, 'end': end_var}
            frame, _ = self._create_track_selector(self.voice_cre_frame, label, path_var, lambda p=path_var: self._select_wav_file(p), loop_var, start_var, end_var)
            ttk.Separator(self.voice_cre_frame, orient='horizontal').pack(fill='x', pady=5, after=frame)
        # Convert button is outside the scrollable area
        self.convert_button = ttk.Button(convert_outer_frame, text="Convert Selected Audio", command=self.convert_audio, state=tk.DISABLED)
        # self.convert_button.pack(pady=10) # Packed later

        # --- Step 3: Repack (formerly Step 4) ---
        repack_frame = ttk.LabelFrame(parent, text="Step 3: Repack & Create Mod", padding="10")
        repack_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        repack_frame.columnconfigure(1, weight=1)

        self.repack_button = ttk.Button(repack_frame, text="Repack ACB", command=self.repack_acb, state=tk.DISABLED)
        self.repack_button.grid(row=0, column=0, padx=5, pady=5)

        ttk.Label(repack_frame, text="Mod Name:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(repack_frame, textvariable=self.mod_name).grid(row=1, column=1, sticky=tk.EW, padx=5)
        self.pak_button = ttk.Button(repack_frame, text="Create .pak", command=self.create_pak, state=tk.DISABLED)
        self.pak_button.grid(row=1, column=2, padx=(5,0))

        self.show_pak_button = ttk.Button(repack_frame, text="Show Pak Output", command=self.show_pak_output)
        self.show_pak_button.grid(row=1, column=3, padx=(5,5))
    def _create_track_selector(self, parent, label_text, path_var, command, loop_var, loop_start_var, loop_end_var):
        """Helper to create a file selection and loop point widget group."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, padx=5, pady=5)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text=label_text).grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(frame, textvariable=path_var, state='readonly').grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Button(frame, text="Browse...", command=command).grid(row=0, column=2)

        loop_frame = ttk.Frame(frame)
        loop_frame.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=5)
        loop_frame.columnconfigure(1, weight=1)
        loop_frame.columnconfigure(3, weight=1)

        ttk.Checkbutton(loop_frame, text="Add Loop Points (samples)", variable=loop_var, command=lambda: self._toggle_loop_widgets(loop_frame, loop_var)).grid(row=0, column=0, columnspan=4, sticky=tk.W)
        ttk.Label(loop_frame, text="Start:").grid(row=1, column=0, sticky=tk.W, padx=(15, 0))
        ttk.Entry(loop_frame, textvariable=loop_start_var).grid(row=1, column=1, sticky=tk.EW, padx=5)
        ttk.Label(loop_frame, text="End:").grid(row=1, column=2, sticky=tk.W)
        ttk.Entry(loop_frame, textvariable=loop_end_var).grid(row=1, column=3, sticky=tk.EW, padx=5)
        return frame, loop_frame

    def _toggle_loop_widgets(self, loop_frame, loop_var):
        state = tk.NORMAL if loop_var.get() else tk.DISABLED
        for widget in loop_frame.winfo_children():
            if not isinstance(widget, ttk.Checkbutton):
                widget.config(state=state)

    def check_tools(self):
        missing_tools = []
        for tool in [ACB_EDITOR, CONVERT_BAT, UNREAL_PAK]:
            if not tool.exists():
                missing_tools.append(str(tool))
        
        if missing_tools:
            messagebox.showerror("Tools Missing", f"The following tools were not found:\n\n" + "\n".join(missing_tools) + "\n\nPlease ensure the 'tools' folder is correctly set up next to the script.")
            self.destroy()
        
        # Hide loop widgets on startup
        self.intro_loops_var.set(False); self._toggle_loop_widgets(self.intro_widgets, self.intro_loops_var)
        self.lap1_loops_var.set(False); self._toggle_loop_widgets(self.lap1_widgets, self.lap1_loops_var)
        self.final_lap_loops_var.set(False); self._toggle_loop_widgets(self.final_lap_widgets, self.final_lap_loops_var)
        
        # This is tricky. The widgets are already created. We need to find them again to disable them.
        # We'll rely on the order they were created in the menu_music_frame.
        # The children are [frame, separator, frame, separator, ...]. We want the frames.
        menu_frames = [child for child in self.menu_music_frame.winfo_children() if isinstance(child, ttk.Frame)]
        for hca_name, var_dict in self.menu_track_vars.items():
            # Find the corresponding loop_frame inside the main frame for this track
            # This is fragile, but it's the simplest way without a big refactor.
            loop_frame = [child for child in menu_frames.pop(0).winfo_children() if isinstance(child, ttk.Frame)][0]
            var_dict['loop'].set(False)
            self._toggle_loop_widgets(loop_frame, var_dict['loop'])
        voice_frames = [child for child in self.voice_cre_frame.winfo_children() if isinstance(child, ttk.Frame)]
        for hca_name, var_dict in self.voice_cre_track_vars.items():
            loop_frame = [child for child in voice_frames.pop(0).winfo_children() if isinstance(child, ttk.Frame)][0]
            var_dict['loop'].set(False)
            self._toggle_loop_widgets(loop_frame, var_dict['loop'])


    def run_command_threaded(self, target_func, on_complete, args=(), kwargs=None):
        """Runs a command in a separate thread to avoid freezing the GUI."""
        self.queue = queue.Queue()
        if kwargs is None:
            kwargs = {}
        task = ThreadedTask(self.queue, target_func, *args, **kwargs)
        task.start()
        self.after(100, self.process_queue, on_complete)

    def _execute_command(self, command, shell, cwd):
        """The actual command execution logic for the thread."""
        try:
            # For GUI apps or console apps where we don't need output,
            if not shell:
                # For GUI apps or non-interactive console tools, we don't want to capture output.
                # Doing so can cause "invalid handle" errors.
                # To prevent a console window from appearing with the GUI, we use CREATE_NO_WINDOW.
                # This is the most direct way to run an external tool without interaction.
                # However, for VGAudioCli, we want to see the output in the console, so we don't hide it.
                creation_flags = 0
                subprocess.run(command, check=True, cwd=cwd, creationflags=creation_flags)
                # We don't need to return any output, just confirm it ran.
                return "Process completed."
            else:
                # For non-interactive batch files like UnrealPak.bat
                # The command is passed as a list, and shell=True handles execution.
                subprocess.run(command, shell=True, check=True, cwd=cwd)
                return "Process completed."

        except FileNotFoundError:
            raise FileNotFoundError(f"Command not found: {command[0]}")
        except subprocess.CalledProcessError as e:
            error_message = f"An error occurred while running:\n{' '.join(command)}\n\nThe tool may have failed. Exit code: {e.returncode}"
            raise RuntimeError(error_message) from e

    def process_queue(self, on_complete):
        """Checks the queue for results from the thread."""
        try:
            msg_type, message = self.queue.get_nowait()
            if msg_type == 'error':
                self.status_var.set(f"Error! Check console for details.")
                messagebox.showerror("Execution Error", str(message))
                self.reset_ui_state()
            elif msg_type == 'success':
                on_complete(message)
        except queue.Empty:
            self.after(100, self.process_queue, on_complete)

    def reset_ui_state(self):
        """Resets buttons to an interactive state after an operation."""
        self.status_var.set("Ready.")
        self.unpack_button.config(state=tk.NORMAL if self.acb_file.get() else tk.DISABLED)
        self.convert_button.config(state=tk.NORMAL if self.unpacked_folder.get() else tk.DISABLED)
        self.repack_button.config(state=tk.NORMAL if self.unpacked_folder.get() else tk.DISABLED)
        self.pak_button.config(state=tk.NORMAL if self.unpacked_folder.get() else tk.DISABLED)

    def _select_wav_file(self, path_var):
        filepath = filedialog.askopenfilename(
            title="Select WAV file",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        if filepath:
            path_var.set(filepath)

    def select_intro_wav(self): self._select_wav_file(self.intro_wav_path)
    def select_lap1_wav(self): self._select_wav_file(self.lap1_wav_path)
    def select_final_lap_wav(self): self._select_wav_file(self.final_lap_wav_path)

    def select_common_bgm(self):
        selector = BGMSelectorWindow(self)
        self.wait_window(selector) # Wait for the BGM selector to close
        
        acb_filename = selector.result
        if not acb_filename:
            return

        # Instruct the user to find the file they extracted.
        filepath = filedialog.askopenfilename(
            title=f"Locate {acb_filename} (extracted with FModel)",
            initialfile=acb_filename,
            filetypes=[("ACB files", f"*{acb_filename}"), ("All files", "*.*")]
        )

        if filepath:
            self.set_acb_file(filepath)


    def select_acb_manual(self):
        filepath = filedialog.askopenfilename(
            title="Select .acb file",
            filetypes=[("ACB files", "*.acb"), ("All files", "*.*")]
        )
        if filepath:
            self.set_acb_file(filepath)

    def set_acb_file(self, filepath):
        """Central function to set the ACB file and reset the UI state."""
        self.acb_file.set(filepath)
        self.unpack_button.config(state=tk.NORMAL)
        
        # Reset subsequent steps
        self.unpacked_folder.set("")
        self.convert_button.config(state=tk.DISABLED) # Will be enabled on unpack
        self.intro_wav_path.set('')
        self.lap1_wav_path.set('')
        self.final_lap_wav_path.set('')
        self.intro_loops_var.set(False); self.lap1_loops_var.set(False); self.final_lap_loops_var.set(False)

        # Hide conversion options and show the placeholder text
        self.stage_music_frame.pack_forget()
        self.menu_music_frame.pack_forget()
        self.voice_cre_frame.pack_forget()
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        self.convert_button.pack_forget()
        self.unpack_first_label.pack(expand=True)

        self._toggle_loop_widgets(self.intro_widgets, self.intro_loops_var)
        self._toggle_loop_widgets(self.lap1_widgets, self.lap1_loops_var)
        self._toggle_loop_widgets(self.final_lap_widgets, self.final_lap_loops_var)
        for var_dict in self.menu_track_vars.values():
            var_dict['path'].set('')
            var_dict['loop'].set(False)
            # Loop widgets are toggled off during check_tools init
        for var_dict in self.voice_cre_track_vars.values():
            var_dict['path'].set('')
            var_dict['loop'].set(False)

        self.repack_button.config(state=tk.DISABLED)
        self.pak_button.config(state=tk.DISABLED)

        # Show/hide widgets based on filename
        acb_path = Path(filepath)
        if acb_path.stem == "BGM":
            self.menu_music_frame.pack(fill=tk.X)
        elif acb_path.stem == "VOICE_CRE":
            self.voice_cre_frame.pack(fill=tk.X)
        else:
            self.stage_music_frame.pack(fill=tk.X)
            if acb_path.stem.startswith("BGM_STG2"):
                self.intro_frame.pack_forget()
            else:
                self.intro_frame.pack(fill=tk.X, padx=5, pady=5)

    def unpack_acb(self):
        acb_path = Path(self.acb_file.get())
        unpacked_path = acb_path.parent / acb_path.stem
        self.unpacked_folder.set(str(unpacked_path))
        print(f"--- Step 1: Unpacking '{acb_path.name}' ---")
        self.status_var.set(f"Unpacking '{acb_path.name}'...")
        self.unpack_button.config(state=tk.DISABLED)
        self.run_command_threaded(self._execute_command, self.on_unpack_complete, args=([str(ACB_EDITOR), str(acb_path)], False), kwargs={'cwd': None})

    def on_unpack_complete(self, result):
        print("Unpacking complete.")
        self.status_var.set("Unpacking complete. Ready for audio conversion.")
        unpacked_path = Path(self.unpacked_folder.get())
        if not unpacked_path.exists():
            messagebox.showerror("Error", f"Failed to unpack. Folder '{unpacked_path.name}' was not created.")
            self.reset_ui_state()
            return
        
        # Show the conversion options now that unpacking is done
        self.unpack_first_label.pack_forget()
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.convert_button.pack(pady=10)

        messagebox.showinfo("Success", f"Unpacked to '{unpacked_path.name}'")
        self.convert_button.config(state=tk.NORMAL)
        self.repack_button.config(state=tk.NORMAL)
        self.pak_button.config(state=tk.NORMAL)
        self.populate_orig_listbox()

    def convert_audio(self):
        """New fully automated conversion process."""
        acb_path = Path(self.acb_file.get())
        acb_name = acb_path.stem
        print(f"\n--- Step 2: Starting Conversion for '{acb_name}' ---")
        self.status_var.set(f"Preparing to convert audio for '{acb_name}'...")
        
        if OUTPUT_DIR.exists():
            import shutil
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR)
        
        # --- Parse Convert2UNION.bat to find the command ---
        try:
            with open(CONVERT_BAT, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find '{CONVERT_BAT}'.")
            return

        print("Parsing Convert2UNION.bat...")
        command_line = None
        target_label = f":option-{acb_name}"
        for i, line in enumerate(lines):
            if line.strip().lower() == target_label.lower():
                if i + 1 < len(lines):
                    command_line = lines[i+1].strip()
                    break
        
        if not command_line or not command_line.lower().startswith("vgaudiocli.exe"):
            messagebox.showerror("Error", f"Could not find a valid VGAudioCli command for '{acb_name}' in '{CONVERT_BAT}'.")
            return

        # --- Prepare list of conversions to run ---
        tasks = []
        is_menu_bgm = acb_path.stem == "BGM"
        is_voice_cre = acb_path.stem == "VOICE_CRE"

        if is_menu_bgm:
            for hca_name, var_dict in self.menu_track_vars.items():
                if var_dict['path'].get():
                    tasks.append((hca_name, var_dict['path'], var_dict['loop'], var_dict['start'], var_dict['end']))
        elif is_voice_cre:
            for hca_name, var_dict in self.voice_cre_track_vars.items():
                if var_dict['path'].get():
                    tasks.append((hca_name, var_dict['path'], var_dict['loop'], var_dict['start'], var_dict['end']))
        else: # Stage music
            if self.intro_wav_path.get():
                tasks.append(("intro", self.intro_wav_path, self.intro_loops_var, self.intro_loop_start_var, self.intro_loop_end_var))
            if self.lap1_wav_path.get():
                tasks.append(("lap1", self.lap1_wav_path, self.lap1_loops_var, self.lap1_loop_start_var, self.lap1_loop_end_var))
            if self.final_lap_wav_path.get():
                tasks.append(("final_lap", self.final_lap_wav_path, self.final_lap_loops_var, self.final_lap_loop_start_var, self.final_lap_loop_end_var))
        
        print("The following files will be converted:")
        for name, path_var, _, _, _ in tasks:
            wav_path = Path(path_var.get())
            print(f"  - Source: '{wav_path.name}' -> Target: {name}.hca")

        if not tasks:
            messagebox.showinfo("Nothing to Convert", "No WAV files were selected for conversion.")
            return

        # --- Run conversions in a thread ---
        self.convert_button.config(state=tk.DISABLED)
        self.status_var.set("Converting audio files... this may take a moment.")
        self.run_command_threaded(self._run_conversion_tasks, self.on_convert_complete, args=(tasks, command_line, str(TOOLS_DIR)))

    def _run_conversion_tasks(self, tasks, base_command_line, cwd):
        """The actual conversion logic that runs in a thread."""
        import shlex, shutil

        # Create temporary input/output dirs inside the tools folder, as the batch script expects
        temp_input_dir = Path(cwd) / "input"
        temp_output_dir = Path(cwd) / "output"

        for name, path_var, loop_var, start_var, end_var in tasks:
            wav_path = Path(path_var.get())
            print(f"Converting '{wav_path.name}' for {name}...")

            # 1. Prepare temp directories
            if temp_input_dir.exists(): shutil.rmtree(temp_input_dir)
            if temp_output_dir.exists(): shutil.rmtree(temp_output_dir)
            os.makedirs(temp_input_dir)
            os.makedirs(temp_output_dir)

            # 2. Copy user's WAV to the temp input dir
            shutil.copy2(wav_path, temp_input_dir)

            # 3. Build the command, but do NOT replace input/output placeholders
            command_parts = shlex.split(base_command_line)

            if loop_var.get():
                start, end = start_var.get().strip(), end_var.get().strip()
                if start and end:
                    command_parts.extend(['-l', f'{start}-{end}'])
                    print(f"  - with loop points: {start}-{end}")
            
            vgaudio_cli_path = Path(cwd) / command_parts[0]
            command_parts[0] = str(vgaudio_cli_path)
            
            print(f"  - Command: {' '.join(shlex.quote(p) for p in command_parts)}")
            # 4. Run the command. It will read from tools/input and write to tools/output
            subprocess.run(command_parts, check=True, cwd=cwd)

            # 5. Move the result from temp output to the main output folder
            converted_files = list(temp_output_dir.glob('*'))
            if converted_files:
                shutil.move(str(converted_files[0]), str(OUTPUT_DIR / f"{name}.hca"))

        # 6. Clean up temp directories
        if temp_input_dir.exists(): shutil.rmtree(temp_input_dir)
        if temp_output_dir.exists(): shutil.rmtree(temp_output_dir)

    def on_convert_complete(self, result):
        print("All conversions complete.")
        self.status_var.set("Audio conversion complete. Ready to repack.")
        messagebox.showinfo("Success", "Audio conversion complete!")
        self.reset_ui_state()

    def populate_orig_listbox(self):
        """This function now just validates the original file structure."""
        self.original_files = []
        unpacked_path = Path(self.unpacked_folder.get())
        try:
            self.original_files = sorted([f.name for f in unpacked_path.iterdir() if f.suffix.lower() in ['.hca', '.adx']])
            if Path(self.acb_file.get()).stem != "BGM" and len(self.original_files) < 5:
                messagebox.showwarning("Unexpected File Structure", 
                    f"Warning: Found {len(self.original_files)} audio files, but expected at least 5.\n\n"
                    "The automatic replacement for Intro/Lap1/Final Lap might not work correctly.")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find unpacked folder: {unpacked_path}")
            self.original_files = []

    def populate_new_listbox(self):
        # This function is no longer needed as dropdowns are removed.
        pass

    def apply_replacements(self):
        unpacked_path = Path(self.unpacked_folder.get())
        if len(self.original_files) < 5:
            messagebox.showerror("Error", "Cannot apply replacements: Not enough original files found in the unpacked folder.")
            return False

        # Build the replacement map based on combobox selections
        if self.lap1_var.get():
            self.replacement_map[self.original_files[0]] = self.lap1_var.get() # Lap 1
            self.replacement_map[self.original_files[1]] = "lap1.hca" # Lap 1 intro
        if self.final_lap_var.get():
            self.replacement_map[self.original_files[2]] = self.final_lap_var.get() # Final Lap
            self.replacement_map[self.original_files[3]] = "final_lap.hca" # Final Lap intro
        if self.intro_var.get():
            self.replacement_map[self.original_files[4]] = "intro.hca" # Intro

        if not self.replacement_map:
            messagebox.showinfo("No Changes", "No replacement tracks were selected. Nothing to apply.")
            return True # This is not an error

        files_replaced = 0
        for original_file, new_file in self.replacement_map.items():
            source_path = OUTPUT_DIR / new_file
            dest_path = unpacked_path / original_file
            if not source_path.exists():
                messagebox.showerror("File Not Found", f"Could not find replacement file: {source_path}")
                return False
            import shutil
            shutil.copy2(source_path, dest_path)
            files_replaced += 1
        
        messagebox.showinfo("Success", f"{files_replaced} file(s) replaced successfully in the unpacked folder.")
        return True

    def repack_acb(self):
        print("\n--- Applying Replacements ---")
        self.status_var.set("Applying replacement audio files...")
        unpacked_path = Path(self.unpacked_folder.get())
        self.replacement_map = {}

        acb_stem = Path(self.acb_file.get()).stem
        is_menu_bgm = acb_stem == "BGM"
        is_voice_cre = acb_stem == "VOICE_CRE"
        is_crossworlds = acb_stem.startswith("BGM_STG2")

        # --- Define Special Track Structures ---
        special_structures = {
            # Dodonpa Factory
            "BGM_STG1026": {"lap1": 0, "lap1_intro": 1, "final_lap": 5, "final_lap_intro": None, "intro": 3},
            # Mystic Jungle, Kronos Island
            "BGM_STG1025": {"intro": 0, "lap1": 1, "lap1_intro": 2, "final_lap": 3, "final_lap_intro": 4},
            "BGM_STG1035": {"intro": 0, "lap1": 1, "lap1_intro": 2, "final_lap": 3, "final_lap_intro": 4},
            # Colorful Mall
            "BGM_STG1030": {"lap1": 0, "lap1_intro": 1, "intro": 2, "final_lap": 3, "final_lap_intro": None},
            # Sand Road, Market Street, Chao Park, Radical Highway, Egg Expo, Apotos
            "BGM_STG1003": {"lap1": 0, "lap1_intro": 1, "intro": 2, "final_lap": 3, "final_lap_intro": 4},
            "BGM_STG1005": {"lap1": 0, "lap1_intro": 1, "intro": 2, "final_lap": 3, "final_lap_intro": 4},
            "BGM_STG1020": {"lap1": 0, "lap1_intro": 1, "intro": 2, "final_lap": 3, "final_lap_intro": 4},
            "BGM_STG1021": {"lap1": 0, "lap1_intro": 1, "intro": 2, "final_lap": 3, "final_lap_intro": 4},
            "BGM_STG1031": {"lap1": 0, "lap1_intro": 1, "intro": 2, "final_lap": 3, "final_lap_intro": 4},
            "BGM_STG1032": {"lap1": 0, "lap1_intro": 1, "intro": 2, "final_lap": 3, "final_lap_intro": 4},
            # Golden Temple (Crossworlds)
            "BGM_STG2004": {"lap1": 0, "lap1_intro": 1, "final_lap": 2, "final_lap_intro": None, "intro": None},
        }

        # Build the replacement map based on converted files
        if is_menu_bgm:
            for hca_name, var_dict in self.menu_track_vars.items():
                converted_file = OUTPUT_DIR / f"{hca_name}.hca"
                if converted_file.exists():
                    self.replacement_map[hca_name + ".hca"] = hca_name + ".hca"
        elif is_voice_cre:
            for hca_name, var_dict in self.voice_cre_track_vars.items():
                converted_file = OUTPUT_DIR / f"{hca_name}.hca"
                if converted_file.exists():
                    self.replacement_map[hca_name + ".hca"] = hca_name + ".hca"
        elif acb_stem in special_structures:
            print(f"Applying special structure for {acb_stem}...")
            structure = special_structures[acb_stem]
            
            if (OUTPUT_DIR / "lap1.hca").exists():
                if structure["lap1"] is not None: self.replacement_map[self.original_files[structure["lap1"]]] = "lap1.hca"
                if structure["lap1_intro"] is not None: self.replacement_map[self.original_files[structure["lap1_intro"]]] = "lap1.hca"
            
            if (OUTPUT_DIR / "final_lap.hca").exists():
                if structure["final_lap"] is not None: self.replacement_map[self.original_files[structure["final_lap"]]] = "final_lap.hca"
                if structure["final_lap_intro"] is not None: self.replacement_map[self.original_files[structure["final_lap_intro"]]] = "final_lap.hca"
            
            if not is_crossworlds and (OUTPUT_DIR / "intro.hca").exists():
                if structure["intro"] is not None: self.replacement_map[self.original_files[structure["intro"]]] = "intro.hca"

        else: # Default logic for other stage tracks
            if len(self.original_files) < 5:
                messagebox.showerror("Error", "Cannot apply replacements: Not enough original files found in the unpacked folder.")
                return

            if (OUTPUT_DIR / "lap1.hca").exists():
                self.replacement_map[self.original_files[0]] = "lap1.hca" # Lap 1
                # Check to avoid index out of bounds if there's only 1 file
                if len(self.original_files) > 1:
                    self.replacement_map[self.original_files[1]] = "lap1.hca" # Lap 1 intro
            if (OUTPUT_DIR / "final_lap.hca").exists():
                if len(self.original_files) > 2:
                    self.replacement_map[self.original_files[2]] = "final_lap.hca" # Final Lap
                if len(self.original_files) > 3:
                    self.replacement_map[self.original_files[3]] = "final_lap.hca" # Final Lap intro
            if not is_crossworlds and (OUTPUT_DIR / "intro.hca").exists():
                if len(self.original_files) > 4:
                    self.replacement_map[self.original_files[4]] = "intro.hca" # Intro

        if not self.replacement_map:
            messagebox.showinfo("No Changes", "No converted tracks found in 'output' folder. Nothing to apply.")
            return

        import shutil
        for original_file, new_file in self.replacement_map.items():
            source_path = OUTPUT_DIR / new_file
            dest_path = unpacked_path / original_file
            print(f"Copying '{source_path}' to '{dest_path}'...")
            shutil.copy2(source_path, dest_path)
        
        print("All replacements applied.")
        messagebox.showinfo("Success", f"{len(self.replacement_map)} file(s) replaced successfully in the unpacked folder.")

        print("\n--- Step 3: Repacking ACB ---")
        self.status_var.set(f"Repacking '{unpacked_path.name}'...")
        self.repack_button.config(state=tk.DISABLED)
        self.run_command_threaded(self._execute_command, self.on_repack_complete, args=([str(ACB_EDITOR), str(unpacked_path)], False), kwargs={'cwd': None})

    def on_repack_complete(self, result):
        print("Repacking complete.")
        self.status_var.set("ACB repacked successfully. Ready to create .pak file.")
        messagebox.showinfo("Success", "ACB folder has been repacked!")
        self.reset_ui_state()

    def create_pak(self):
        mod_name_str = self.mod_name.get().strip()
        if not mod_name_str:
            messagebox.showerror("Error", "Mod Name cannot be empty.")
            return

        print(f"\n--- Step 4: Creating Mod Pak '{mod_name_str}.pak' ---")
        self.status_var.set(f"Creating mod package '{mod_name_str}.pak'...")
        mod_root_folder = Path(mod_name_str)
        criware_folder = mod_root_folder / "UNION" / "Content" / "CriWareData"

        try:
            os.makedirs(criware_folder, exist_ok=True)

            import shutil
            acb_path = Path(self.acb_file.get())
            print(f"Copying '{acb_path.name}' to mod folder...")
            shutil.copy2(acb_path, criware_folder)

            awb_file = acb_path.with_suffix('.awb')
            if awb_file.exists():
                print(f"Copying '{awb_file.name}' to mod folder...")
                shutil.copy2(awb_file, criware_folder)
        except Exception as e:
            messagebox.showerror("File Error", f"Error preparing files for packing: {e}")
            return

        self.pak_button.config(state=tk.DISABLED)
        self.run_command_threaded(self._execute_command, self.on_pak_complete, args=([str(UNREAL_PAK), str(mod_root_folder.resolve())], True), kwargs={'cwd': None})

    def on_pak_complete(self, result):
        mod_name_str = self.mod_name.get().strip()
        print(f"Pak file creation complete.")
        self.status_var.set(f"Mod '{mod_name_str}.pak' created successfully!")
        pak_file = Path(mod_name_str).with_suffix('.pak')
        messagebox.showinfo("Mod Creation Complete!", f"Successfully created mod package:\n{pak_file.resolve()}")
        self.reset_ui_state()

    def show_pak_output(self):
        """Opens the script's directory where the .pak file is created."""
        output_dir = Path.cwd()
        try:
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin": # macOS
                subprocess.run(["open", output_dir], check=True)
            else: # Linux
                subprocess.run(["xdg-open", output_dir], check=True)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open output directory:\n{e}")

    def show_credits(self):
        """Displays the credits window."""
        credits_text = (
            "CrossWorlds Music Mod Builder\n\n"
            "Created by: RED1\n\n"
            "A tool to simplify the process of creating music mods for\n"
            "Sonic Racing: Crossworlds.\n\n"
            "Special Thanks:\n"
            "Lycus - For Testing and Feedback\n"
        )
        messagebox.showinfo("Credits", credits_text)
if __name__ == "__main__":
    app = ModBuilderGUI()
    app.mainloop()
