import os
import subprocess
import sys
import re
import threading
import queue
import shlex
from pathlib import Path

try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
                                   QLineEdit, QPushButton, QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem,
                                   QScrollArea, QCheckBox, QFrame, QMenuBar, QStatusBar, QDialog,
                                   QDialogButtonBox)
    from PySide6.QtCore import Qt, QThread, Signal, QObject
except ImportError:
    print("Error: PySide6 module not found. Please install it using 'pip install PySide6'")
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
class BGMSelectorWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Common BGM")
        self.resize(500, 600)
        self.result = None

        layout = QVBoxLayout(self)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Filename"])
        self.tree.setColumnWidth(0, 350)
        layout.addWidget(self.tree)

        for category, tracks in BGM_DATA.items():
            category_node = QTreeWidgetItem(self.tree, [category])
            category_node.setExpanded(True)
            for id_num, name in tracks.items():
                filename = ""
                if category == "Menu & System":
                    filename = "BGM.acb"
                elif category == "Voice Lines":
                    filename = f"VOICE_{id_num}.acb"
                else:
                    filename = f"BGM_STG{id_num}.acb"
                
                display_text = f"{id_num}: {name}" if category not in ["Menu & System", "Voice Lines"] else name
                QTreeWidgetItem(category_node, [display_text, filename])

        self.tree.itemDoubleClicked.connect(self.on_select)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_select(self, item, column):
        if item and item.childCount() == 0: # It's a selectable item, not a category
            self.on_accept()

    def on_accept(self):
        """Handles the logic for when the 'OK' or 'Select' button is clicked."""
        try:
            selected_items = self.tree.selectedItems()
            if selected_items and selected_items[0].childCount() == 0:
                self.result = selected_items[0].text(1)
                self.accept()
            else:
                QMessageBox.warning(self, "Selection Error", "Please select a specific track, not a category.")
        except IndexError:
             QMessageBox.warning(self, "Selection Error", "Please select a track.")

# --- Configuration ---
# Set the paths to your tools relative to this script.
TOOLS_DIR = Path("tools")
ACB_EDITOR = TOOLS_DIR / "AcbEditor.exe"
CONVERT_BAT = TOOLS_DIR / "Convert2UNION.bat"
UNREAL_PAK = TOOLS_DIR / "UnrealPak.bat"
INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

class Worker(QObject):
    """Worker for running tasks in a separate thread."""
    finished = Signal(object)
    error = Signal(Exception)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.function(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(e)

class ModBuilderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CrossWorlds Music Mod Builder")
        self.resize(800, 750)

        self.thread = None
        self.worker = None

        # --- Menu Bar ---
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        credits_action = help_menu.addAction("Credits")
        credits_action.triggered.connect(self.show_credits)

        # --- State Variables ---
        self._acb_file = ""
        self._unpacked_folder = ""
        self._mod_name = "MyAwesomeMusicMod"
        self.original_files = []
        self.new_files = []

        # --- New state vars for direct file selection ---
        self.intro_track_vars = {}
        self.lap1_track_vars = {}
        self.final_lap_track_vars = {}

        # --- New state vars for menu music ---
        self.menu_track_vars = {}
        self.voice_cre_track_vars = {}

        self.replacement_map = {}

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # --- Create Widgets ---
        self._create_widgets(main_layout)

        # --- Check for tools on startup ---
        self.check_tools()

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready.")

    def _create_widgets(self, main_layout):
        # --- Step 1: Unpack ---
        unpack_group = QGroupBox("Step 1: Select & Unpack ACB")
        main_layout.addWidget(unpack_group)
        unpack_layout = QVBoxLayout(unpack_group)
        
        acb_layout = QHBoxLayout()
        acb_layout.addWidget(QLabel("ACB File:"))
        self.acb_file_edit = QLineEdit()
        self.acb_file_edit.setReadOnly(True)
        acb_layout.addWidget(self.acb_file_edit)
        unpack_layout.addLayout(acb_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        select_bgm_button = QPushButton("Select BGM...")
        select_bgm_button.clicked.connect(self.select_common_bgm)
        btn_layout.addWidget(select_bgm_button)
        self.unpack_button = QPushButton("Unpack")
        self.unpack_button.clicked.connect(self.unpack_acb)
        self.unpack_button.setEnabled(False)
        btn_layout.addWidget(self.unpack_button)
        unpack_layout.addLayout(btn_layout)

        # --- Step 2: Convert ---
        convert_group = QGroupBox("Step 2: Convert Audio")
        main_layout.addWidget(convert_group)
        convert_outer_layout = QVBoxLayout(convert_group)

        # Add a placeholder label
        self.unpack_first_label = QLabel("Please select and unpack an ACB file in Step 1 to see conversion options.")
        self.unpack_first_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        convert_outer_layout.addWidget(self.unpack_first_label)

        # Create a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVisible(False)
        scroll_widget = QWidget()
        self.scroll_area.setWidget(scroll_widget)
        self.scroll_layout = QVBoxLayout(scroll_widget)
        convert_outer_layout.addWidget(self.scroll_area)

        # Create track selection widgets
        self.stage_music_frame = QWidget()
        stage_layout = QVBoxLayout(self.stage_music_frame)
        stage_layout.setContentsMargins(0,0,0,0)
        self.scroll_layout.addWidget(self.stage_music_frame)

        self.intro_track_vars = self._create_track_selector(stage_layout, "Intro Music")
        stage_layout.addWidget(self._create_separator())
        self.lap1_track_vars = self._create_track_selector(stage_layout, "Lap 1 Music")
        stage_layout.addWidget(self._create_separator())
        self.final_lap_track_vars = self._create_track_selector(stage_layout, "Final Lap Music")

        # --- New Menu Music Frame ---
        self.menu_music_frame = QWidget()
        menu_layout = QVBoxLayout(self.menu_music_frame)
        menu_layout.setContentsMargins(0,0,0,0)
        self.scroll_layout.addWidget(self.menu_music_frame)

        for label, hca_name in MENU_BGM_TRACKS.items():
            self.menu_track_vars[hca_name] = self._create_track_selector(menu_layout, label)
            if hca_name != list(MENU_BGM_TRACKS.values())[-1]:
                menu_layout.addWidget(self._create_separator())

        # --- New Voice Line Frame (for VOICE_CRE) ---
        self.voice_cre_frame = QWidget()
        voice_layout = QVBoxLayout(self.voice_cre_frame)
        voice_layout.setContentsMargins(0,0,0,0)
        self.scroll_layout.addWidget(self.voice_cre_frame)

        for label, hca_name in VOICE_CRE_TRACKS.items():
            self.voice_cre_track_vars[hca_name] = self._create_track_selector(voice_layout, label)
            if hca_name != list(VOICE_CRE_TRACKS.values())[-1]:
                voice_layout.addWidget(self._create_separator())

        self.scroll_layout.addStretch()

        # Convert button is outside the scrollable area
        self.convert_button = QPushButton("Convert Selected Audio")
        self.convert_button.clicked.connect(self.convert_audio)
        self.convert_button.setEnabled(False)
        self.convert_button.setVisible(False)
        convert_outer_layout.addWidget(self.convert_button, 0, Qt.AlignmentFlag.AlignCenter)

        # --- Step 3: Repack (formerly Step 4) ---
        repack_group = QGroupBox("Step 3: Repack & Create Mod")
        main_layout.addWidget(repack_group)
        repack_layout = QVBoxLayout(repack_group)

        self.repack_button = QPushButton("Repack ACB")
        self.repack_button.clicked.connect(self.repack_acb)
        self.repack_button.setEnabled(False)
        repack_layout.addWidget(self.repack_button)

        mod_name_layout = QHBoxLayout()
        mod_name_layout.addWidget(QLabel("Mod Name:"))
        self.mod_name_edit = QLineEdit(self._mod_name)
        self.mod_name_edit.textChanged.connect(lambda text: setattr(self, '_mod_name', text))
        mod_name_layout.addWidget(self.mod_name_edit)
        self.pak_button = QPushButton("Create .pak")
        self.pak_button.clicked.connect(self.create_pak)
        self.pak_button.setEnabled(False)
        mod_name_layout.addWidget(self.pak_button)
        self.show_pak_button = QPushButton("Show Pak Output")
        self.show_pak_button.clicked.connect(self.show_pak_output)
        mod_name_layout.addWidget(self.show_pak_button)
        repack_layout.addLayout(mod_name_layout)

    def _create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def _create_track_selector(self, parent_layout, label_text):
        """Helper to create a file selection and loop point widget group."""
        frame = QWidget()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0,0,0,0)

        browse_layout = QHBoxLayout()
        browse_layout.addWidget(QLabel(label_text))
        path_edit = QLineEdit()
        path_edit.setReadOnly(True)
        browse_layout.addWidget(path_edit)
        browse_button = QPushButton("Browse...")
        browse_layout.addWidget(browse_button)
        layout.addLayout(browse_layout)

        loop_group = QGroupBox("Loop Points (samples)")
        loop_group.setCheckable(True)
        loop_group.setChecked(False)
        loop_layout = QHBoxLayout(loop_group)
        loop_layout.addWidget(QLabel("Start:"))
        loop_start_edit = QLineEdit()
        loop_layout.addWidget(loop_start_edit)
        loop_layout.addWidget(QLabel("End:"))
        loop_end_edit = QLineEdit()
        loop_layout.addWidget(loop_end_edit)
        layout.addWidget(loop_group)

        parent_layout.addWidget(frame)

        var_dict = {
            'path': path_edit,
            'loop': loop_group,
            'start': loop_start_edit,
            'end': loop_end_edit
        }

        browse_button.clicked.connect(lambda: self._select_wav_file(path_edit))
        return var_dict

    def check_tools(self):
        missing_tools = []
        for tool in [ACB_EDITOR, CONVERT_BAT, UNREAL_PAK]:
            if not tool.exists():
                missing_tools.append(str(tool))
        
        if missing_tools:
            QMessageBox.critical(self, "Tools Missing", f"The following tools were not found:\n\n" + "\n".join(missing_tools) + "\n\nPlease ensure the 'tools' folder is correctly set up next to the script.")
            self.close()
        
        # Hide loop widgets on startup
        self.intro_track_vars['loop'].setChecked(False)
        self.lap1_track_vars['loop'].setChecked(False)
        self.final_lap_track_vars['loop'].setChecked(False)

        for hca_name, var_dict in self.menu_track_vars.items():
            var_dict['loop'].setChecked(False)
        for hca_name, var_dict in self.voice_cre_track_vars.items():
            var_dict['loop'].setChecked(False)

    def run_command_threaded(self, target_func, on_complete, on_error, args=(), kwargs=None):
        """Runs a command in a separate thread to avoid freezing the GUI."""
        if kwargs is None:
            kwargs = {}
        self.thread = QThread()
        self.worker = Worker(target_func, *args, **kwargs)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(on_complete)
        self.worker.error.connect(on_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

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

    def on_command_error(self, error):
        self.status_bar.showMessage("Error! Check console for details.")
        QMessageBox.critical(self, "Execution Error", str(error))
        self.reset_ui_state()

    def reset_ui_state(self):
        """Resets buttons to an interactive state after an operation."""
        self.status_bar.showMessage("Ready.")
        self.unpack_button.setEnabled(bool(self._acb_file))
        self.convert_button.setEnabled(bool(self._unpacked_folder))
        self.repack_button.setEnabled(bool(self._unpacked_folder))
        self.pak_button.setEnabled(bool(self._unpacked_folder))

    def _select_wav_file(self, path_edit):
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            caption="Select WAV file",
            filter="WAV files (*.wav);;All files (*.*)",
        )
        if filepath:
            path_edit.setText(filepath)

    def select_common_bgm(self):
        selector = BGMSelectorWindow(self)
        if selector.exec():
            acb_filename = selector.result
            if not acb_filename:
                return

            # Instruct the user to find the file they extracted.
            filepath, _ = QFileDialog.getOpenFileName(
                self,
                caption=f"Locate {acb_filename} (extracted with FModel)",
                filter=f"ACB files (*{acb_filename});;All files (*.*)",
                dir=str(Path.cwd())
            )

            if filepath:
                self.set_acb_file(filepath)

    def set_acb_file(self, filepath):
        """Central function to set the ACB file and reset the UI state."""
        self._acb_file = filepath
        self.acb_file_edit.setText(filepath)
        self.unpack_button.setEnabled(True)
        
        # Reset subsequent steps
        self._unpacked_folder = ""
        self.convert_button.setEnabled(False)

        self.intro_track_vars['path'].setText('')
        self.lap1_track_vars['path'].setText('')
        self.final_lap_track_vars['path'].setText('')
        self.intro_track_vars['loop'].setChecked(False)
        self.lap1_track_vars['loop'].setChecked(False)
        self.final_lap_track_vars['loop'].setChecked(False)

        # Hide conversion options and show the placeholder text
        self.stage_music_frame.setVisible(False)
        self.menu_music_frame.setVisible(False)
        self.voice_cre_frame.setVisible(False)
        self.scroll_area.setVisible(False)
        self.convert_button.setVisible(False)
        self.unpack_first_label.setVisible(True)

        for var_dict in self.menu_track_vars.values():
            var_dict['path'].setText('')
            var_dict['loop'].setChecked(False)
        for var_dict in self.voice_cre_track_vars.values():
            var_dict['path'].setText('')
            var_dict['loop'].setChecked(False)

        self.repack_button.setEnabled(False)
        self.pak_button.setEnabled(False)

        # Show/hide widgets based on filename
        acb_path = Path(filepath)
        if acb_path.stem == "BGM":
            self.menu_music_frame.setVisible(True)
        elif acb_path.stem == "VOICE_CRE":
            self.voice_cre_frame.setVisible(True)
        else:
            self.stage_music_frame.setVisible(True)
            if acb_path.stem.startswith("BGM_STG2"):
                self.intro_track_vars['path'].parent().setVisible(False)
            else:
                self.intro_track_vars['path'].parent().setVisible(True)

    def unpack_acb(self):
        acb_path = Path(self._acb_file)
        unpacked_path = acb_path.parent / acb_path.stem
        self._unpacked_folder = str(unpacked_path)
        print(f"--- Step 1: Unpacking '{acb_path.name}' ---")
        self.status_bar.showMessage(f"Unpacking '{acb_path.name}'...")
        self.unpack_button.setEnabled(False)
        self.run_command_threaded(self._execute_command, self.on_unpack_complete, self.on_command_error, args=([str(ACB_EDITOR), str(acb_path)], False), kwargs={'cwd': None})

    def on_unpack_complete(self, result):
        print("Unpacking complete.")
        self.status_bar.showMessage("Unpacking complete. Ready for audio conversion.")
        unpacked_path = Path(self._unpacked_folder)
        if not unpacked_path.exists():
            QMessageBox.critical(self, "Error", f"Failed to unpack. Folder '{unpacked_path.name}' was not created.")
            self.reset_ui_state()
            return
        
        # Show the conversion options now that unpacking is done
        self.unpack_first_label.setVisible(False)
        self.scroll_area.setVisible(True)
        self.convert_button.setVisible(True)

        QMessageBox.information(self, "Success", f"Unpacked to '{unpacked_path.name}'")
        self.convert_button.setEnabled(True)
        self.repack_button.setEnabled(True)
        self.pak_button.setEnabled(True)
        self.populate_orig_listbox()

    def convert_audio(self):
        """New fully automated conversion process."""
        acb_path = Path(self._acb_file)
        acb_name = acb_path.stem
        print(f"\n--- Step 2: Starting Conversion for '{acb_name}' ---")
        self.status_bar.showMessage(f"Preparing to convert audio for '{acb_name}'...")
        
        if OUTPUT_DIR.exists():
            import shutil
            shutil.rmtree(OUTPUT_DIR)
        os.makedirs(OUTPUT_DIR)
        
        # --- Parse Convert2UNION.bat to find the command ---
        try:
            with open(CONVERT_BAT, 'r') as f:
                lines = f.readlines()
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"Could not find '{CONVERT_BAT}'.")
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
            QMessageBox.critical(self, "Error", f"Could not find a valid VGAudioCli command for '{acb_name}' in '{CONVERT_BAT}'.")
            return

        # --- Prepare list of conversions to run ---
        tasks = []
        is_menu_bgm = acb_path.stem == "BGM"
        is_voice_cre = acb_path.stem == "VOICE_CRE"

        if is_menu_bgm:
            for hca_name, var_dict in self.menu_track_vars.items():
                if var_dict['path'].text():
                    tasks.append((hca_name, var_dict['path'].text(), var_dict['loop'].isChecked(), var_dict['start'].text(), var_dict['end'].text()))
        elif is_voice_cre:
            for hca_name, var_dict in self.voice_cre_track_vars.items():
                if var_dict['path'].text():
                    tasks.append((hca_name, var_dict['path'].text(), var_dict['loop'].isChecked(), var_dict['start'].text(), var_dict['end'].text()))
        else: # Stage music
            if self.intro_track_vars['path'].text():
                tasks.append(("intro", self.intro_track_vars['path'].text(), self.intro_track_vars['loop'].isChecked(), self.intro_track_vars['start'].text(), self.intro_track_vars['end'].text()))
            if self.lap1_track_vars['path'].text():
                tasks.append(("lap1", self.lap1_track_vars['path'].text(), self.lap1_track_vars['loop'].isChecked(), self.lap1_track_vars['start'].text(), self.lap1_track_vars['end'].text()))
            if self.final_lap_track_vars['path'].text():
                tasks.append(("final_lap", self.final_lap_track_vars['path'].text(), self.final_lap_track_vars['loop'].isChecked(), self.final_lap_track_vars['start'].text(), self.final_lap_track_vars['end'].text()))
        
        print("The following files will be converted:")
        for name, wav_path_str, _, _, _ in tasks:
            wav_path = Path(wav_path_str)
            print(f"  - Source: '{wav_path.name}' -> Target: {name}.hca")

        if not tasks:
            QMessageBox.information(self, "Nothing to Convert", "No WAV files were selected for conversion.")
            return

        # --- Run conversions in a thread ---
        self.convert_button.setEnabled(False)
        self.status_bar.showMessage("Converting audio files... this may take a moment.")
        self.run_command_threaded(self._run_conversion_tasks, self.on_convert_complete, self.on_command_error, args=(tasks, command_line, str(TOOLS_DIR)))

    def _run_conversion_tasks(self, tasks, base_command_line, cwd):
        """The actual conversion logic that runs in a thread."""
        import shutil

        # Create temporary input/output dirs inside the tools folder, as the batch script expects
        temp_input_dir = Path(cwd) / "input"
        temp_output_dir = Path(cwd) / "output"

        for name, wav_path_str, has_loop, loop_start, loop_end in tasks:
            wav_path = Path(wav_path_str)
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

            if has_loop:
                start, end = loop_start.strip(), loop_end.strip()
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
        self.status_bar.showMessage("Audio conversion complete. Ready to repack.")
        QMessageBox.information(self, "Success", "Audio conversion complete!")
        self.reset_ui_state()

    def populate_orig_listbox(self):
        """This function now just validates the original file structure."""
        self.original_files = []
        unpacked_path = Path(self._unpacked_folder)
        try:
            self.original_files = sorted([f.name for f in unpacked_path.iterdir() if f.suffix.lower() in ['.hca', '.adx']])
            if Path(self._acb_file).stem != "BGM" and len(self.original_files) < 5:
                QMessageBox.warning(self, "Unexpected File Structure", 
                    f"Warning: Found {len(self.original_files)} audio files, but expected at least 5.\n\n"
                    "The automatic replacement for Intro/Lap1/Final Lap might not work correctly.")
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"Could not find unpacked folder: {unpacked_path}")
            self.original_files = []

    def repack_acb(self):
        print("\n--- Applying Replacements ---")
        self.status_bar.showMessage("Applying replacement audio files...")
        unpacked_path = Path(self._unpacked_folder)
        self.replacement_map = {}

        acb_stem = Path(self._acb_file).stem
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
                QMessageBox.critical(self, "Error", "Cannot apply replacements: Not enough original files found in the unpacked folder.")
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
            QMessageBox.information(self, "No Changes", "No converted tracks found in 'output' folder. Nothing to apply.")
            return

        import shutil
        for original_file, new_file in self.replacement_map.items():
            source_path = OUTPUT_DIR / new_file
            dest_path = unpacked_path / original_file
            print(f"Copying '{source_path}' to '{dest_path}'...")
            shutil.copy2(source_path, dest_path)
        
        print("All replacements applied.")
        QMessageBox.information(self, "Success", f"{len(self.replacement_map)} file(s) replaced successfully in the unpacked folder.")

        print("\n--- Step 3: Repacking ACB ---")
        self.status_bar.showMessage(f"Repacking '{unpacked_path.name}'...")
        self.repack_button.setEnabled(False)
        self.run_command_threaded(self._execute_command, self.on_repack_complete, self.on_command_error, args=([str(ACB_EDITOR), str(unpacked_path)], False), kwargs={'cwd': None})

    def on_repack_complete(self, result):
        print("Repacking complete.")
        self.status_bar.showMessage("ACB repacked successfully. Ready to create .pak file.")
        QMessageBox.information(self, "Success", "ACB folder has been repacked!")
        self.reset_ui_state()

    def create_pak(self):
        mod_name_str = self._mod_name.strip()
        if not mod_name_str:
            QMessageBox.critical(self, "Error", "Mod Name cannot be empty.")
            return

        print(f"\n--- Step 4: Creating Mod Pak '{mod_name_str}.pak' ---")
        self.status_bar.showMessage(f"Creating mod package '{mod_name_str}.pak'...")
        mod_root_folder = Path(mod_name_str)
        criware_folder = mod_root_folder / "UNION" / "Content" / "CriWareData"

        try:
            os.makedirs(criware_folder, exist_ok=True)

            import shutil
            acb_path = Path(self._acb_file)
            print(f"Copying '{acb_path.name}' to mod folder...")
            shutil.copy2(acb_path, criware_folder)

            awb_file = acb_path.with_suffix('.awb')
            if awb_file.exists():
                print(f"Copying '{awb_file.name}' to mod folder...")
                shutil.copy2(awb_file, criware_folder)
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Error preparing files for packing: {e}")
            return

        self.pak_button.setEnabled(False)
        self.run_command_threaded(self._execute_command, self.on_pak_complete, self.on_command_error, args=([str(UNREAL_PAK), str(mod_root_folder.resolve())], True), kwargs={'cwd': None})

    def on_pak_complete(self, result):
        mod_name_str = self._mod_name.strip()
        print(f"Pak file creation complete.")
        self.status_bar.showMessage(f"Mod '{mod_name_str}.pak' created successfully!")
        pak_file = Path(mod_name_str).with_suffix('.pak')
        QMessageBox.information(self, "Mod Creation Complete!", f"Successfully created mod package:\n{pak_file.resolve()}")
        self.reset_ui_state()

    def show_pak_output(self):
        """Opens the script's directory where the .pak file is created."""
        output_dir = Path.cwd()
        try:
            # QDesktopServices.openUrl is more cross-platform
            from PySide6.QtGui import QDesktopServices
            from PySide6.QtCore import QUrl
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_dir)))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open output directory:\n{e}")

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
        QMessageBox.information(self, "Credits", credits_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModBuilderGUI()
    window.show()
    sys.exit(app.exec())
