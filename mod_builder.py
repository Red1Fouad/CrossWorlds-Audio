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
