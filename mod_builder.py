import os
import sys
import json, configparser
import time
from pathlib import Path
import shutil
import subprocess
import wave

try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit,
                                   QPushButton, QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem, QTabWidget, QGridLayout, QSplashScreen,
                                   QScrollArea, QFrame, QMenuBar, QStatusBar, QProgressBar)
    from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
    from PySide6.QtGui import QDesktopServices, QShortcut, QKeySequence, QIcon, QPixmap
    from PySide6.QtCore import QUrl
except ImportError:
    print("Error: PySide6 module not found. Please install it using 'pip install PySide6'")
    sys.exit(1)

import data
from ui_components import BGMSelectorWindow, ImageCard, TrackEditorWidget, SettingsDialog, LogWindow
from volume_logic import normalize_audio_file
from mod_logic import ModLogic

# --- Configuration ---
# Set the paths to your tools relative to this script.
TOOLS_DIR = Path("tools")
OUTPUT_DIR = Path("output")
SAMPLES_DIR = TOOLS_DIR / "samples"
MUSIC_REF_PATH = SAMPLES_DIR / "music.wav"
VOICE_SFX_REF_PATH = SAMPLES_DIR / "voice.wav"
APP_VERSION = "1.5"
SESSION_FILE = Path("session.json")
GITHUB_REPO = "Red1Fouad/CrossWorlds-Audio"

# --- Track Indices Mapping ---
# Format: "BGM_STGxxxx": (announce_idx, trans_idx, trans_short_idx)
# Indices are 0-based (User Input - 1). None means the track does not exist.
ADDITIONAL_TRACK_INDICES = {
    "BGM_STG1001": (5, 6, 7), "BGM_STG1003": (5, 6, 7), "BGM_STG1005": (5, 6, None),
    "BGM_STG1016": (5, 7, 6), "BGM_STG1017": (5, 7, 6), "BGM_STG1018": (5, 7, 6),
    "BGM_STG1020": (5, 6, None), "BGM_STG1021": (5, 6, 7), "BGM_STG1022": (5, 7, 6),
    "BGM_STG1023": (5, 7, 6), "BGM_STG1024": (5, 6, 7), "BGM_STG1025": (5, 6, None),
    "BGM_STG1026": (6, 7, 8), "BGM_STG1027": (5, 6, None), "BGM_STG1028": (5, 6, 7),
    "BGM_STG1029": (5, 6, None), "BGM_STG1030": (4, 5, 6), "BGM_STG1031": (5, 7, 6),
    "BGM_STG1032": (5, 7, 6), "BGM_STG1033": (5, 6, None), "BGM_STG1034": (6, 7, None),
    "BGM_STG1035": (5, 6, 7), "BGM_STG1036": (5, 6, None), "BGM_STG1037": (5, 6, 7),
    "BGM_STG2001": (4, 14, 5), "BGM_STG2002": (4, 5, 6), "BGM_STG2003": (4, 6, 5),
    "BGM_STG2004": (3, 5, 4), "BGM_STG2005": (4, 5, 6), "BGM_STG2007": (4, 5, 6),
    "BGM_STG2009": (4, 5, 6), "BGM_STG2010": (4, 6, 5), "BGM_STG2011": (4, 5, 6),
    "BGM_STG2012": (4, 5, None), "BGM_STG2014": (4, 5, 6), "BGM_STG2015": (4, 5, None),
    "BGM_STG2016": (4, 5, 6), "BGM_STG2017": (4, 5, 6), "BGM_STG2019": (4, 5, None),
}

# --- New BGM Tracks ---
BGM_TRACKS = {
    "Ceremony Jingle": "00000_streaming",
    # Team Sonic
    "Sonic Victory": "00017_streaming", "Tails Victory": "00019_streaming", "Knuckles Victory": "00010_streaming",
    # Team Rose
    "Amy Victory": "00001_streaming", "Cream Victory": "00005_streaming", "Big Victory": "00002_streaming",
    # Team Dark
    "Shadow Victory": "00015_streaming", "Rouge Victory": "00013_streaming", "E-123 Omega Victory": "00012_streaming",
    # Team Silver
    "Silver Victory": "00016_streaming", "Blaze Victory": "00003_streaming",
    # Team Eggman
    "Eggman Victory": "00006_streaming", "Metal Sonic Victory": "00011_streaming", "Sage Victory": "00014_streaming", "Eggpawn Victory": "00007_streaming",
    # Team Chaotix
    "Vector Victory": "00020_streaming", "Charmy Victory": "00004_streaming", "Espio Victory": "00008_streaming",
    # Team Babylon
    "Jet Victory": "00009_streaming", "Wave Victory": "00021_streaming", "Storm Victory": "00018_streaming",
    # Team Zeti
    "Zavok Victory": "00022_streaming", "Zazz Victory": "00023_streaming",
    # Results & Ceremony
    "Post Ceremony Music": "00024_streaming",
    "Grand Prix Final Race Results": "00030_streaming",
    "Race Results 1": "00042_streaming", "Race Results 2": "00043_streaming", "Race Results 3": "00044_streaming", "Race Results 4": "00045_streaming",
    # Race Finish Jingles
    "Forces Race Finish": "00060_streaming", "Sonic Adventure Race Finish": "00061_streaming", "Race Finish": "00062_streaming",
    "Forces Race Finish 2": "00063_streaming", "Sonic Adventure Race Finish 2": "00064_streaming", "Race Finish 2": "00065_streaming",
    "Forces Race Finish 3": "00066_streaming", "Sonic Adventure Race Finish 3": "00067_streaming", "Race Finish 3": "00068_streaming",
    "Forces Race Finish 4": "00069_streaming", "Sonic Adventure Race Finish 4": "00070_streaming", "Race Finish 4": "00071_streaming",
    "White Space Race Finish": "00072_streaming", "White Space Race Finish 2": "00074_streaming", "White Space Race Finish 3": "00075_streaming",
    "Kronos Island Race Finish": "00076_streaming", "Unleashed Race Finish": "00077_streaming",
}

BGM_LOOPABLE_TRACKS = [
    "00024_streaming", "00030_streaming", "00042_streaming", "00043_streaming",
    "00044_streaming", "00045_streaming",
]

def find_loop_points_task(file_path_str):
    """
    Task to run in a background thread for finding loop points using the pymusiclooper CLI.
    This is done via CLI to avoid Qt threading conflicts, as pymusiclooper uses PyQt.
    """
    import subprocess
    import re

    # Determine command based on environment (Frozen/Packaged vs Source)
    if getattr(sys, 'frozen', False):
        # If running as a packaged exe, assume pymusiclooper is in the system PATH
        command = ["pymusiclooper", "export-points", "--path", file_path_str]
    else:
        # If running from source, use the current python interpreter
        command = [
            sys.executable,
            "-m",
            "pymusiclooper",
            "export-points",
            "--path",
            file_path_str
        ]

    try:
        # Prevent console window popup on Windows
        cflags = 0x08000000 if sys.platform == "win32" else 0
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', creationflags=cflags)
        output = result.stdout
        start_match = re.search(r"LOOP_START: (\d+)", output)
        end_match = re.search(r"LOOP_END: (\d+)", output)
        if start_match and end_match:
            return [(int(start_match.group(1)), int(end_match.group(1)))]
        return [] # No loop points found in output
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        stderr = e.stderr if hasattr(e, 'stderr') else "N/A"
        raise RuntimeError(f"pymusiclooper CLI failed.\nCommand: {' '.join(command)}\nError: {e}\nDetails: {stderr}") from e

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

class StreamRedirector(QObject):
    """Redirects stream output to a signal."""
    text_written = Signal(str)
    def __init__(self, stream=None):
        super().__init__()
        self._stream = stream
    
    def write(self, text):
        if self._stream:
            try:
                self._stream.write(text)
                self._stream.flush()
            except Exception: pass
        self.text_written.emit(str(text))
        
    def flush(self):
        if self._stream:
            try:
                self._stream.flush()
            except Exception: pass

class ModBuilderGUI(QMainWindow):
    # A dedicated, thread-safe signal for updating the status bar
    update_status_bar = Signal(str, int)

    def __init__(self, splash=None):
        super().__init__()
        self.base_title = f"CrossWorlds Music Mod Builder v{APP_VERSION}"
        self.setWindowTitle("CrossWorlds Music Mod Builder - Select a Category")
        self.resize(1280, 720)

        # Set application icon
        self.setWindowIcon(QIcon("tools/ico.ico"))

        self.active_threads = [] # Keep references to active threads
        self.autoloop_threads = {} # Map widgets to their specific threads for cancellation

        self.config = configparser.ConfigParser()
        self.settings_file = Path("settings.ini")
        self._track_file_cache = {}
        self._current_acb_stem = None

        self.logic = ModLogic(TOOLS_DIR, OUTPUT_DIR)

        # --- Menu Bar ---
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # Add Recent Files submenu
        self.recent_files_menu = file_menu.addMenu("Recent Files")
        self.recent_files = [] # Will be populated by load_settings
        self.MAX_RECENT_FILES = 10

        file_menu.addSeparator()
        settings_action = file_menu.addAction("Settings...")
        settings_action.triggered.connect(self.show_settings_dialog)


        help_menu = menu_bar.addMenu("Help")
        credits_action = help_menu.addAction("Credits")
        credits_action.triggered.connect(self.show_credits)

        # --- State Variables ---
        self._acb_file = ""
        self._unpacked_folder = ""
        self._mod_name = "MyAwesomeMusicMod"
        self.original_files = []
        self._acb_path_cache = {} # Cache for selected ACB paths per session
        self.criware_folder_path = None
        self.debug_logging_enabled = False

        # --- New state vars for direct file selection ---
        self.intro_track_vars = {}
        self.lap1_track_vars = {}
        self.final_lap_track_vars = {}

        self.all_track_editors = [] # To manage audio playback
        # --- New state vars for menu music ---
        self.special_track_vars = {}
        self.voice_search_bar = None
        self._image_file_cache = None # Cache for smart image search

        central_widget = QWidget() 
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # --- Create Main UI Structure ---
        # 1. Selection Screen (Tabs with Cards)
        self.selection_screen = QWidget()
        self.main_layout.addWidget(self.selection_screen)
        self._create_selection_screen(QVBoxLayout(self.selection_screen))

        # 2. Editor Screen (Steps 1-3) - Initially hidden
        self.editor_screen = QWidget()
        self.main_layout.addWidget(self.editor_screen)
        self._create_editor_screen(QVBoxLayout(self.editor_screen))

        # --- Load settings after UI is created ---
        app = QApplication.instance()
        if splash:
            splash.showMessage("Loading settings...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, Qt.white)
            if app: app.processEvents()
        self.load_settings()

        if splash:
            splash.showMessage("Loading session data...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, Qt.white)
            if app: app.processEvents()
        self.load_session_data()

        if splash:
            splash.showMessage("Initializing UI...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, Qt.white)
            if app: app.processEvents()
        self.update_recent_files_menu()
        self.editor_screen.setVisible(False)


        # --- Check for tools on startup ---
        self.check_tools()

        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # Connect our new signal to the status bar's slot
        self.update_status_bar.connect(self.status_bar.showMessage)

        # Add version label to the status bar
        version_label = QLabel(f"v{APP_VERSION}")
        self.status_bar.addPermanentWidget(version_label)

        # Check for updates on startup
        if splash:
            splash.showMessage("Checking for updates...", Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignHCenter, Qt.white)
            if app: app.processEvents()
        QTimer.singleShot(1000, self.check_for_updates) # Delay slightly to not block startup

        self.update_status_bar.emit("Ready.", 0)

        # --- Shortcuts ---
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self.focus_search_bar)
        
        # --- Global Stylesheet ---
        self.setStyleSheet("""
            #TrackEditorWidget {
                border: 1px solid palette(mid);
                border-radius: 5px;
                margin-bottom: 5px;
            }
            #HeaderFrame {
                background-color: palette(button);
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            #HeaderFrame[hasFile="true"] {
                background-color: palette(highlight);
            }
            #ContentFrame {
                background-color: palette(base);
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;
                border-top: 1px solid palette(mid);
            }
        """)

    def closeEvent(self, event):
        """Clean up temporary folders on application close."""
        # Save settings before closing
        self._capture_current_track_state()
        self.save_session_data()
        self.save_settings()

        print("Cleaning up temporary folders...")
        
        # Clean up the main output directory that holds converted .hca files
        if OUTPUT_DIR.exists():
            try:
                shutil.rmtree(OUTPUT_DIR)
                print(f"Removed temporary directory: {OUTPUT_DIR}")
            except Exception as e:
                print(f"Error removing {OUTPUT_DIR}: {e}")

        # Clean up temporary conversion folders that might be left inside tools
        tools_input = TOOLS_DIR / "input"
        tools_output = TOOLS_DIR / "output"
        
        if tools_input.exists():
            try:
                shutil.rmtree(tools_input)
                print(f"Removed temporary directory: {tools_input}")
            except Exception as e:
                print(f"Error removing {tools_input}: {e}")

        # Stop any lingering audio players
        self.stop_all_audio()

        event.accept()

    def _find_image_path(self, acb_stem, friendly_name, image_folder):
        """
        Finds the path for a card's image.
        1. Tries the direct path: tools/images/<category>/<acb_stem>.png
        2. If not found, performs a keyword search within all image subdirectories.
        """
        # --- 1. Try the direct, fast path first ---
        direct_path = TOOLS_DIR / "images" / image_folder / f"{acb_stem}.png"
        if direct_path.exists():
            return direct_path

        # --- 2. If not found, perform a smarter keyword search ---
        # Build a cache of all image files on the first run
        if self._image_file_cache is None:
            self._image_file_cache = list((TOOLS_DIR / "images").rglob("*.png"))

        # Prepare keywords from the friendly name (e.g., "Ocean View" -> ["ocean", "view"])
        # Also remove characters that might be in filenames but not titles
        keywords = friendly_name.lower().replace(":", "").replace("-", "").replace("&", "").split()
        if not keywords:
            return "" # No keywords to search for

        possible_matches = []
        # Search the cached file list
        for image_path in self._image_file_cache:
            filename_lower = image_path.name.lower()
            # Check if all keywords are present in the filename
            if all(keyword in filename_lower for keyword in keywords):
                possible_matches.append(image_path)

        # --- 3. If we have matches, find the best one ---
        if possible_matches:
            # The best match is likely the one with the shortest filename.
            # e.g., for "Sonic", "sonic.png" is a better match than "metalsonic.png".
            best_match = min(possible_matches, key=lambda p: len(p.name))
            return best_match
            
        # --- 3. If still not found, return an empty path ---
        return ""

    def _create_selection_screen(self, layout):
        """Creates the initial screen with tabs for selecting a music pack."""
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Define categories and their image subfolders
        categories = {
            "Stages": ("BGM_STG1", "stages"),
            "CrossWorlds": ("BGM_STG2", "crossworlds"),
            "DLC Stages": ("BGM_EXTND", "dlc"),
            "Menus": ("BGM", "menus"),
            "Voices": ("VOICE_", "voices"),
            "Misc": ("SE_", "misc"),
        }

        # Create a tab for each category
        for tab_name, (prefix, image_folder) in categories.items():
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            tab_content = QWidget()
            grid_layout = QGridLayout(tab_content)
            grid_layout.setSpacing(15)
            scroll_area.setWidget(tab_content)
            tab_widget.addTab(scroll_area, tab_name)

            # Populate the tab with cards
            col, row = 0, 0
            for acb_stem, friendly_name in data.FRIENDLY_NAME_MAP.items():
                # Special handling for menus to avoid including stages
                if prefix == "BGM" and (acb_stem.startswith("BGM_STG") or acb_stem.startswith("BGM_EXTND")):
                    continue
                
                # Special handling for guest characters to ensure they only appear in the Misc tab.
                is_guest_char = acb_stem in ["SE_EXTND10_CHARA", "SE_EXTND11_CHARA", "SE_EXTND12_CHARA", "SE_EXTND15_CHARA"]
                if (tab_name == "Voices" and is_guest_char):
                    continue

                # Exclude character music packs from DLC Stages tab (they are accessed via Misc -> Character)
                if prefix == "BGM_EXTND" and acb_stem in ["BGM_EXTND10", "BGM_EXTND11", "BGM_EXTND12", "BGM_EXTND15"]:
                    continue

                if acb_stem.startswith(prefix):
                    image_path = self._find_image_path(acb_stem, friendly_name, image_folder)
                    card = ImageCard(acb_stem, friendly_name, image_path)
                    card.clicked.connect(self.on_card_selected)
                    grid_layout.addWidget(card, row, col)
                    col += 1
                    if col >= 5: # 5 cards per row for 16:9
                        col = 0
                        row += 1

    def _create_editor_screen(self, main_layout):
        """Creates the main editor widgets (Steps 1-3), initially hidden."""
        # Top Navigation Bar
        nav_layout = QHBoxLayout()
        back_button = QPushButton("⬅ Back to Selection")
        back_button.clicked.connect(self.show_selection_screen)
        nav_layout.addWidget(back_button, 0, Qt.AlignmentFlag.AlignLeft)
        nav_layout.addStretch()
        main_layout.addLayout(nav_layout)

        # Main Content Layout (Split Left/Right)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # --- Left Column (Steps 1 & 3) ---
        left_column = QVBoxLayout()
        content_layout.addLayout(left_column, 1) # Stretch 1

        # --- Step 1: Unpack ---
        unpack_group = QGroupBox("Step 1: Select & Unpack ACB")
        left_column.addWidget(unpack_group)
        unpack_layout = QVBoxLayout(unpack_group)
        
        acb_layout = QHBoxLayout()
        acb_layout.addWidget(QLabel("Selected ACB File:"))
        self.acb_file_edit = QLineEdit()
        self.acb_file_edit.setReadOnly(True)
        acb_layout.addWidget(self.acb_file_edit)
        unpack_layout.addLayout(acb_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        locate_file_button = QPushButton("Locate File...")
        locate_file_button.clicked.connect(self.locate_acb_file)
        btn_layout.addWidget(locate_file_button)
        self.unpack_button = QPushButton("Unpack")
        self.unpack_button.clicked.connect(self.unpack_acb)
        self.unpack_button.setEnabled(False)
        btn_layout.addWidget(self.unpack_button)
        unpack_layout.addLayout(btn_layout)

        self.unpack_progress = QProgressBar()
        self.unpack_progress.setVisible(False)
        unpack_layout.addWidget(self.unpack_progress)

        # --- Step 3: Repack (formerly Step 4) ---
        left_column.addSpacing(20)
        repack_group = QGroupBox("Step 3: Repack & Create Mod")
        left_column.addWidget(repack_group)
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
        repack_layout.addLayout(mod_name_layout)

        pak_layout = QHBoxLayout()
        self.pak_button = QPushButton("Create .pak")
        self.pak_button.clicked.connect(self.create_pak)
        self.pak_button.setEnabled(False)
        pak_layout.addWidget(self.pak_button)
        self.show_pak_button = QPushButton("Show Pak Output")
        self.show_pak_button.clicked.connect(self.show_pak_output)
        pak_layout.addWidget(self.show_pak_button)
        repack_layout.addLayout(pak_layout)

        left_column.addStretch() # Push items to top

        # --- Right Column (Step 2) ---
        right_column = QVBoxLayout()
        content_layout.addLayout(right_column, 2) # Stretch 2 (Wider)

        convert_group = QGroupBox("Step 2: Convert Audio")
        right_column.addWidget(convert_group)
        convert_outer_layout = QVBoxLayout(convert_group)

        # Add a placeholder label
        self.unpack_first_label = QLabel("Please select and unpack an ACB file in Step 1 to see conversion options.")
        self.unpack_first_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.unpack_first_label.setWordWrap(True)
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

        # Initialize Stage Track Editors
        self.intro_track_vars = TrackEditorWidget("Intro Music")
        self.intro_track_vars.play_requested.connect(self.on_play_requested)
        self.intro_track_vars.autoloop_requested.connect(self.on_autoloop_requested)
        self.intro_track_vars.cancel_autoloop_requested.connect(self.on_cancel_autoloop)
        self.intro_track_vars.normalize_requested.connect(lambda path: self._update_path_after_normalize(self.intro_track_vars, path, 'music'))
        stage_layout.addWidget(self.intro_track_vars)

        self.lap1_track_vars = TrackEditorWidget("Lap 1 Music")
        self.lap1_track_vars.play_requested.connect(self.on_play_requested)
        self.lap1_track_vars.autoloop_requested.connect(self.on_autoloop_requested)
        self.lap1_track_vars.cancel_autoloop_requested.connect(self.on_cancel_autoloop)
        self.lap1_track_vars.normalize_requested.connect(lambda path: self._update_path_after_normalize(self.lap1_track_vars, path, 'music'))
        stage_layout.addWidget(self.lap1_track_vars)

        self.final_lap_track_vars = TrackEditorWidget("Final Lap Music")
        self.final_lap_track_vars.play_requested.connect(self.on_play_requested)
        self.final_lap_track_vars.autoloop_requested.connect(self.on_autoloop_requested)
        self.final_lap_track_vars.cancel_autoloop_requested.connect(self.on_cancel_autoloop)
        self.final_lap_track_vars.normalize_requested.connect(lambda path: self._update_path_after_normalize(self.final_lap_track_vars, path, 'music'))
        stage_layout.addWidget(self.final_lap_track_vars)

        self.transition_track_vars = TrackEditorWidget("Transition Music (Normal)")
        self.transition_track_vars.play_requested.connect(self.on_play_requested)
        self.transition_track_vars.autoloop_requested.connect(self.on_autoloop_requested)
        self.transition_track_vars.cancel_autoloop_requested.connect(self.on_cancel_autoloop)
        self.transition_track_vars.normalize_requested.connect(lambda path: self._update_path_after_normalize(self.transition_track_vars, path, 'music'))
        stage_layout.addWidget(self.transition_track_vars)

        # Add Copy Button
        copy_btn_layout = QHBoxLayout()
        copy_btn_layout.addStretch()
        self.copy_trans_btn = QPushButton("↓ Copy Normal Transition settings to Short Transition ↓")
        self.copy_trans_btn.clicked.connect(self.copy_transition_settings)
        copy_btn_layout.addWidget(self.copy_trans_btn)
        copy_btn_layout.addStretch()
        stage_layout.addLayout(copy_btn_layout)

        self.transition_short_track_vars = TrackEditorWidget("Transition Music (Short)")
        self.transition_short_track_vars.play_requested.connect(self.on_play_requested)
        self.transition_short_track_vars.autoloop_requested.connect(self.on_autoloop_requested)
        self.transition_short_track_vars.cancel_autoloop_requested.connect(self.on_cancel_autoloop)
        self.transition_short_track_vars.normalize_requested.connect(lambda path: self._update_path_after_normalize(self.transition_short_track_vars, path, 'music'))
        stage_layout.addWidget(self.transition_short_track_vars)

        self.announce_track_vars = TrackEditorWidget("Final Lap Announcement")
        self.announce_track_vars.play_requested.connect(self.on_play_requested)
        self.announce_track_vars.autoloop_requested.connect(self.on_autoloop_requested)
        self.announce_track_vars.cancel_autoloop_requested.connect(self.on_cancel_autoloop)
        self.announce_track_vars.normalize_requested.connect(lambda path: self._update_path_after_normalize(self.announce_track_vars, path, 'music'))
        stage_layout.addWidget(self.announce_track_vars)

        self.all_track_editors.extend([self.intro_track_vars, self.lap1_track_vars, self.final_lap_track_vars, self.transition_track_vars, self.transition_short_track_vars, self.announce_track_vars])
        # --- New Menu Music Frame ---
        # This single frame will be used for Menu, Voice, and DLC tracks
        self.special_track_frame = QWidget()
        special_track_layout = QVBoxLayout(self.special_track_frame)
        special_track_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.addWidget(self.special_track_frame)

        # This frame will be populated dynamically in set_acb_file

        self.scroll_layout.addStretch()

        # Buttons outside the scrollable area
        convert_btn_layout = QHBoxLayout()
        
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.clicked.connect(self.clear_all_tracks)
        self.clear_all_button.setVisible(False)
        convert_btn_layout.addWidget(self.clear_all_button)

        self.convert_button = QPushButton("Convert Selected Audio")
        self.convert_button.clicked.connect(self.convert_audio)
        self.convert_button.setEnabled(False)
        self.convert_button.setVisible(False)
        convert_btn_layout.addWidget(self.convert_button)
        
        convert_outer_layout.addLayout(convert_btn_layout)

    def copy_transition_settings(self):
        self.transition_short_track_vars.path_edit.setText(self.transition_track_vars.path_edit.text())
        self.transition_short_track_vars.loop_checkbox.setChecked(self.transition_track_vars.loop_checkbox.isChecked())
        self.transition_short_track_vars.loop_start_edit.setText(self.transition_track_vars.loop_start_edit.text())
        self.transition_short_track_vars.loop_end_edit.setText(self.transition_track_vars.loop_end_edit.text())

    def on_card_selected(self, acb_stem, friendly_name):
        """Handles the click event from an ImageCard."""
        # New logic for misc characters
        if acb_stem in ["SE_EXTND10_CHARA", "SE_EXTND11_CHARA", "SE_EXTND12_CHARA", "SE_EXTND15_CHARA"]:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(f"Select Mod Type for {friendly_name}")
            msg_box.setText(f"Which audio type do you want to modify for {friendly_name}?")
            music_button = msg_box.addButton("Music", QMessageBox.ButtonRole.ActionRole)
            sfx_button = msg_box.addButton("SFX", QMessageBox.ButtonRole.ActionRole)
            cancel_button = msg_box.addButton(QMessageBox.StandardButton.Cancel)
            
            msg_box.exec()
            
            clicked_button = msg_box.clickedButton()
            if clicked_button == music_button:
                # Change the stem from SE_... to BGM_...
                acb_stem = acb_stem.replace("SE_", "BGM_").replace("_CHARA", "")
            elif clicked_button == sfx_button:
                # Keep the original acb_stem
                pass
            else: # Cancel was clicked
                return

        filepath = None

        # 1. Try to find the file in the selected CriWare folder first.
        if self.criware_folder_path:
            potential_path = self.criware_folder_path / f"{acb_stem}.acb"
            if potential_path.exists():
                filepath = str(potential_path)
                print(f"Found '{acb_stem}.acb' in CriWare folder.")
            else:
                print(f"Could not find '{acb_stem}.acb' in CriWare folder. Falling back to manual selection.")

        # 2. If not found in CriWare folder, fall back to existing logic (cache or prompt).
        if not filepath:
            filepath = self._acb_path_cache.get(acb_stem)

            # If the cached path is invalid or doesn't exist, clear it and prompt again.
            if filepath and not Path(filepath).exists():
                print(f"Cached path for {acb_stem} is invalid. Prompting for new file.")
                filepath = None
                del self._acb_path_cache[acb_stem]

            # If no valid cached path, prompt the user.
            if not filepath:
                filepath = self._prompt_for_acb_file(acb_stem)
                if filepath:
                    # Store the newly selected path in the cache for this session.
                    self._acb_path_cache[acb_stem] = filepath
                else:
                    # User cancelled the file dialog, so we do nothing.
                    print("File selection cancelled.")
                    return

        # If we have a valid filepath (either from cache or prompt), proceed.
        if filepath:
            self.add_to_recent_files(filepath)
            self.editor_screen.setVisible(True)
            self.selection_screen.setVisible(False)

            # Set the file and trigger auto-unpack
            self.set_acb_file(filepath, auto_unpack=True)

    def _create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def load_settings(self):
        """Loads settings from settings.ini."""
        if not self.settings_file.exists():
            print("settings.ini not found. Using default settings.")
            return

        self.config.read(self.settings_file)
        if 'Settings' in self.config:
            path_str = self.config['Settings'].get('criware_folder', '')
            if path_str:
                self.criware_folder_path = Path(path_str)
                print(f"Loaded CriWare folder path: {self.criware_folder_path}")
            
            self.debug_logging_enabled = self.config['Settings'].getboolean('debug_logging', False)
            if self.debug_logging_enabled:
                self._show_log_window()
            
            recent_files_str = self.config['Settings'].get('recent_files', '')
            if recent_files_str:
                # Filter out any empty strings that might result from splitting
                self.recent_files = [p for p in recent_files_str.split(',') if p]
                print(f"Loaded {len(self.recent_files)} recent files.")

    def save_settings(self):
        """Saves current settings to settings.ini."""
        if 'Settings' not in self.config:
            self.config.add_section('Settings')
        path_str = str(self.criware_folder_path) if self.criware_folder_path else ""
        self.config['Settings']['criware_folder'] = path_str
        self.config['Settings']['debug_logging'] = str(self.debug_logging_enabled)

        # Limit to max and save
        self.config['Settings']['recent_files'] = ",".join(self.recent_files[:self.MAX_RECENT_FILES])
        with open(self.settings_file, 'w') as configfile:
            self.config.write(configfile)
        print(f"Saved settings to {self.settings_file}.")

    def load_session_data(self):
        """Loads the session data (track paths) from JSON."""
        if SESSION_FILE.exists():
            try:
                with open(SESSION_FILE, 'r') as f:
                    self._track_file_cache = json.load(f)
                print(f"Loaded session data from {SESSION_FILE}")
            except Exception as e:
                print(f"Failed to load session data: {e}")

    def save_session_data(self):
        """Saves the session data to JSON."""
        with open(SESSION_FILE, 'w') as f:
            json.dump(self._track_file_cache, f, indent=2)
        print(f"Saved session data to {SESSION_FILE}")

    def check_tools(self):
        missing_tools = self.logic.check_tools()

    def show_selection_screen(self):
        self.selection_screen.setVisible(True)
        self.editor_screen.setVisible(False)
        self.setWindowTitle("CrossWorlds Music Mod Builder - Select a Category")

    def check_tools(self):
        missing_tools = self.logic.check_tools()
        if missing_tools is None:
            missing_tools = []

        # Check for ffmpeg (Required for the new sanitization fix)
        if not (TOOLS_DIR / "ffmpeg.exe").exists() and not shutil.which("ffmpeg"):
            missing_tools.append("ffmpeg.exe")

        if missing_tools:
            QMessageBox.critical(self, "Tools Missing", f"The following tools were not found:\n\n" + "\n".join(missing_tools) + "\n\nPlease ensure the 'tools' folder is correctly set up next to the script.")
            self.close()
        
        # Hide loop widgets on startup
        self.intro_track_vars.loop_checkbox.setChecked(False)
        self.lap1_track_vars.loop_checkbox.setChecked(False)
        self.final_lap_track_vars.loop_checkbox.setChecked(False)
        self.transition_track_vars.loop_checkbox.setChecked(False)
        self.transition_short_track_vars.loop_checkbox.setChecked(False)
        self.announce_track_vars.loop_checkbox.setChecked(False)

    def check_for_updates(self):
        """Initiates a background check for a new version on GitHub."""
        self.update_status_bar.emit("Checking for updates...", 0)
        self.run_command_threaded(
            self._perform_update_check,
            on_complete=self.on_update_check_complete,
            on_error=self.on_update_check_error
        )

    def _perform_update_check(self):
        """The actual update check logic that runs in a thread."""
        from urllib import request
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        try:
            with request.urlopen(api_url, timeout=10) as response: # 10-second timeout
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    latest_version_tag = data.get("tag_name", "").lstrip('v')
                    
                    # Simple version comparison
                    if latest_version_tag and latest_version_tag > APP_VERSION:
                        assets = data.get("assets", [])
                        download_url = None
                        # Find the correct .7z file
                        for asset in assets:
                            if asset.get("name") == f"CrossWorlds-Music-Editor{latest_version_tag}.7z":
                                download_url = asset.get("browser_download_url")
                                break
                        if download_url:
                            return {"new_version": latest_version_tag, "url": download_url}
        except Exception as e:
            print(f"Update check failed: {e}")
        return None # No update or an error occurred

    def on_update_check_complete(self, result):
        self.update_status_bar.emit("Ready.", 2000) # Show "Ready" for 2 seconds
        if result:
            reply = QMessageBox.information(self, "Update Available",
                                          f"A new version ({result['new_version']}) is available!\n\nWould you like to open the download page?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                QDesktopServices.openUrl(QUrl(result['url']))

    def on_update_check_error(self, error):
        self.update_status_bar.emit("Update check failed.", 3000)

    def focus_search_bar(self):
        if self.voice_search_bar and self.voice_search_bar.isVisible():
            self.voice_search_bar.setFocus()

    def _clear_layout(self, layout):
        """Removes all widgets from a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self._clear_layout(item.layout())

    def _populate_special_track_frame(self, acb_stem):
        """Dynamically populates the special tracks frame with the correct selectors."""
        self._clear_layout(self.special_track_frame.layout())
        self.special_track_vars.clear()
        self.all_track_editors = [self.intro_track_vars, self.lap1_track_vars, self.final_lap_track_vars, self.transition_track_vars, self.transition_short_track_vars, self.announce_track_vars] # Reset
        self.voice_search_bar = None
        track_dict = {}
        is_voice_acb = acb_stem.startswith("VOICE_")
        
        if is_voice_acb:
            track_dict_name = f"VOICE_{acb_stem.split('_')[1]}_TRACKS"
            track_dict = getattr(data, track_dict_name, {})
        elif acb_stem == "SE_EXTND10_CHARA": # Miku - check this before SPECIAL_TRACK_MAP
            track_dict = data.VOICE_EXTND10_CHARA_TRACKS
            is_voice_acb = True # Treat her like a voice ACB for UI purposes
        elif acb_stem == "SE_EXTND11_CHARA": # Joker
            track_dict = data.VOICE_EXTND11_CHARA_TRACKS
            is_voice_acb = True
        elif acb_stem == "SE_EXTND12_CHARA": # Ichiban
            track_dict = data.VOICE_EXTND12_CHARA_TRACKS
            is_voice_acb = True # Treat her like a voice ACB for UI purposes
        elif acb_stem == "SE_EXTND15_CHARA": # NiGHTS
            track_dict = data.VOICE_EXTND15_CHARA_TRACKS
            is_voice_acb = True
        elif acb_stem == "BGM_EXTND04": # Minecraft uses its own full dictionary
            track_dict = data.DLC_MINECRAFT_TRACKS
        elif acb_stem == "BGM":
            track_dict = data.SPECIAL_TRACK_MAP.get("BGM", {}).copy()
            track_dict.update(BGM_TRACKS)
        elif acb_stem == "SE_COURSE":
            track_dict = data.SE_COURSE_TRACKS
        elif acb_stem in data.SPECIAL_TRACK_MAP:
            track_dict = data.SPECIAL_TRACK_MAP[acb_stem]


        # Add search bar
        if is_voice_acb or acb_stem == "BGM": # This now includes Miku and BGM
            self.voice_search_bar = QLineEdit()
            placeholder = "Search Voice Lines... (Ctrl+F)" if is_voice_acb else "Search Tracks... (Ctrl+F)"
            self.voice_search_bar.setPlaceholderText(placeholder)
            self.voice_search_bar.textChanged.connect(self._filter_special_lines)
            self.special_track_frame.layout().addWidget(self.voice_search_bar)

        if not track_dict:
            label = QLabel(f"No track structure defined for {acb_stem} in data.py yet.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.special_track_frame.layout().addWidget(label)
            return

        show_loops = not is_voice_acb # No loops for voice lines
        for label, hca_name in track_dict.items():
            can_loop = show_loops
            if acb_stem == "BGM":
                # Check if the track is one of the newly added ones
                if hca_name in BGM_TRACKS.values():
                    can_loop = hca_name in BGM_LOOPABLE_TRACKS
                else: # Otherwise, it's an original menu track, which should be loopable
                    can_loop = True
            elif acb_stem in data.NON_LOOPABLE_SPECIAL_TRACKS:
                if hca_name in data.NON_LOOPABLE_SPECIAL_TRACKS.get(acb_stem, []):
                    can_loop = False
            editor_widget = TrackEditorWidget(label, show_loop_options=can_loop)
            editor_widget.play_requested.connect(self.on_play_requested)
            editor_widget.autoloop_requested.connect(self.on_autoloop_requested)
            editor_widget.cancel_autoloop_requested.connect(self.on_cancel_autoloop)
            editor_widget.normalize_requested.connect(lambda path, track_type='sfx' if acb_stem.startswith("SE_") else 'voice': self.on_normalize_requested(path, track_type))
            self.special_track_vars[hca_name] = editor_widget
            self.all_track_editors.append(editor_widget)
            self.special_track_frame.layout().addWidget(editor_widget)

    def _filter_special_lines(self, text):
        """Hides/shows voice line widgets based on the search text."""
        search_text = text.lower()
        layout = self.special_track_frame.layout()

        # Iterate through all widgets in the layout
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget is None or widget == self.voice_search_bar:
                continue
            
            # Check the title label of our custom widget
            if isinstance(widget, TrackEditorWidget):
                is_match = search_text in widget.title_label.text().lower()
                widget.setVisible(is_match)

    def run_command_threaded(self, target_func, on_complete, on_error, args=(), kwargs=None):
        """Runs a command in a separate thread to avoid freezing the GUI."""
        if kwargs is None:
            kwargs = {}
        thread = QThread()
        worker = Worker(target_func, *args, **kwargs)
        worker.moveToThread(thread)

        # Store references
        self.active_threads.append((thread, worker))

        thread.started.connect(worker.run)
        worker.finished.connect(on_complete, Qt.QueuedConnection)
        worker.error.connect(on_error, Qt.QueuedConnection)

        # Clean up when finished
        worker.finished.connect(thread.quit) # On success, tell the thread to quit
        worker.error.connect(thread.quit)    # Also tell the thread to quit on error

        # Once the thread has finished its event loop, we can safely delete the objects
        thread.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda: self.active_threads.remove((thread, worker)))

        thread.start()
        return thread, worker

    def on_command_error(self, error):
        self.update_status_bar.emit("Error! Check console for details.", 0)
        QMessageBox.critical(self, "Execution Error", str(error))
        self.reset_ui_state()

    def reset_ui_state(self):
        """Resets buttons to an interactive state after an operation."""
        self.update_status_bar.emit("Ready.", 0)
        self.unpack_button.setEnabled(bool(self._acb_file))
        self.convert_button.setEnabled(bool(self._unpacked_folder))
        self.repack_button.setEnabled(bool(self._unpacked_folder))
        self.pak_button.setEnabled(bool(self._unpacked_folder))
        self.unpack_progress.setVisible(False)

    def stop_all_audio(self):
        """Stops playback on all track editor widgets."""
        for editor in self.all_track_editors:
            editor.stop_playback()

    def on_play_requested(self, requesting_widget):
        """When one widget wants to play, stop all others first."""
        for editor in self.all_track_editors:
            if editor is not requesting_widget:
                editor.stop_playback()

    def on_normalize_requested(self, source_path_str, track_type):
        """Handles the normalization request from a TrackEditorWidget."""
        if not source_path_str:
            QMessageBox.warning(self, "No File", "Please select an audio file first.")
            return

        source_path = Path(source_path_str)
        if not source_path.exists():
            QMessageBox.critical(self, "File Not Found", f"The file '{source_path.name}' could not be found.")
            return

        if track_type == 'music':
            ref_path = MUSIC_REF_PATH
        elif track_type in ['voice', 'sfx']:
            ref_path = VOICE_SFX_REF_PATH
        else:
            QMessageBox.critical(self, "Error", f"Unknown track type '{track_type}' for normalization.")
            return

        if not ref_path.exists():
            QMessageBox.critical(self, "Reference File Missing", f"The reference audio file is missing:\n{ref_path}")
            return

        # The output will be a WAV file with a '_norm' suffix in the same directory.
        output_path = source_path.with_name(f"{source_path.stem}_norm.wav")

        self.update_status_bar.emit(f"Normalizing '{source_path.name}'...", 0)
        try:
            normalize_audio_file(str(source_path), str(ref_path), str(output_path))
            self.update_status_bar.emit(f"Normalization complete. Saved as '{output_path.name}'.", 5000)
            QMessageBox.information(self, "Normalization Complete", f"Normalized audio saved as:\n{output_path.name}\n\nThe file path in the editor has been updated for you.")
            return str(output_path) # Return the new path
        except Exception as e:
            self.on_command_error(e)

    def _update_path_after_normalize(self, editor, path, track_type):
        """Helper to update the text field after normalization."""
        new_path = self.on_normalize_requested(path, track_type)
        if new_path:
            editor.path_edit.setText(new_path)

    def install_package(self, package_name, editor_widget):
        self.update_status_bar.emit(f"Installing {package_name}...", 0)
        editor_widget.on_autoloop_started() # Show the progress bar on the widget

        self.run_command_threaded(
            self._pip_install,
            on_complete=lambda result: self.on_install_complete(result, package_name, editor_widget),
            on_error=lambda error: self.on_install_error(error, package_name, editor_widget),
            args=(package_name,)
        )

    def _pip_install(self, package_name):
        import subprocess
        command = [sys.executable, "-m", "pip", "install", package_name]
        try:
            # For Windows, to prevent a console window from popping up
            cflags = 0x08000000 if sys.platform == "win32" else 0
            # Using capture_output to hide the pip install text from the console unless there's an error
            result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8', creationflags=cflags)
            return result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            stderr = e.stderr if hasattr(e, 'stderr') else "N/A"
            raise RuntimeError(f"Failed to install '{package_name}'.\n"
                               f"Command: {' '.join(command)}\n"
                               f"Error: {e}\nDetails: {stderr}") from e

    def on_install_complete(self, result, package_name, editor_widget):
        self.update_status_bar.emit(f"Successfully installed {package_name}.", 5000)
        editor_widget.on_autoloop_finished(None) # Reset UI
        QMessageBox.information(self, "Installation Successful",
                                f"'{package_name}' has been installed successfully.\n\n"
                                "Please restart the application to use this feature.")

    def on_install_error(self, error, package_name, editor_widget):
        editor_widget.on_autoloop_finished(None) # Reset the specific widget's UI
        self.update_status_bar.emit(f"Failed to install {package_name}.", 0)
        error_message = (f"Failed to install '{package_name}'.\n\nPlease ensure you have Python and pip installed and accessible from your system's PATH.\nYou can also try installing it manually by opening a command prompt and running:\n\npip install {package_name}\n\nDetails:\n{error}")
        QMessageBox.critical(self, "Installation Failed", error_message)
        self.reset_ui_state() # Reset global buttons

    def on_autoloop_requested(self, editor_widget, file_path_str):
        """Handles the auto-loop request from a TrackEditorWidget."""
        if not file_path_str or not Path(file_path_str).exists():
            QMessageBox.warning(self, "File Not Found", "Please select a valid audio file first.")
            return

        if not editor_widget.loop_checkbox:
            QMessageBox.information(self, "Not Applicable", "Auto-loop is not available for this type of track.")
            return

        reply = QMessageBox.information(self, "Auto-Loop Analysis",
                                      "This will analyze the audio file to find the best loop points. "
                                      "This process can take a while, especially for long files.\n\n"
                                      "Please note: The results are not always perfect and may require manual adjustment.\n\n"
                                      "The application may appear to freeze, but it is working in the background. "
                                      "Continue?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return

        editor_widget.on_autoloop_started()
        self.update_status_bar.emit(f"Finding loop points for '{Path(file_path_str).name}'...", 0)

        # Check if pymusiclooper is available (either bundled or in system PATH)
        has_pymusiclooper = False
        try:
            import pymusiclooper
            has_pymusiclooper = True
        except ImportError:
            # If import fails, check if it's in the system PATH (e.g. installed globally)
            if shutil.which("pymusiclooper"):
                has_pymusiclooper = True

        if not has_pymusiclooper:
            # If frozen (packaged), we can't auto-install easily. Tell user to install globally.
            if getattr(sys, 'frozen', False):
                QMessageBox.warning(self, "Dependency Missing",
                                      "The 'Auto-Loop' feature requires 'pymusiclooper'.\n\n"
                                      "Since you are using the packaged version, please install it manually by opening a command prompt and running:\n\n"
                                      "pip install pymusiclooper")
                editor_widget.on_autoloop_finished(None)
                return

            # If running from source, offer auto-install
            reply = QMessageBox.warning(self, "Dependency Missing",
                                          "The 'Auto-Loop' feature requires the 'pymusiclooper' package, which is not installed.\n\n"
                                          "Would you like to attempt to install it now? (Requires an internet connection)",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.install_package('pymusiclooper', editor_widget)
            else:
                editor_widget.on_autoloop_finished(None) # Reset the UI
            return

        thread, worker = self.run_command_threaded(
            find_loop_points_task,
            on_complete=lambda result: self.on_autoloop_complete(editor_widget, result),
            on_error=lambda error: self.on_autoloop_error(editor_widget, error),
            args=(file_path_str,)
        )
        self.autoloop_threads[editor_widget] = (thread, worker)

    def on_autoloop_complete(self, editor_widget, loop_points):
        if editor_widget in self.autoloop_threads: del self.autoloop_threads[editor_widget]
        editor_widget.on_autoloop_finished(loop_points)
        self.update_status_bar.emit("Loop point analysis complete.", 5000)

        if loop_points:
            best_loop = loop_points[0]
            QMessageBox.information(self, "Loop Points Found", f"Successfully found loop points!\n\nStart: {best_loop[0]} samples\nEnd:   {best_loop[1]} samples\n\nThe fields have been updated for you.")
        else:
            QMessageBox.warning(self, "No Loop Points Found", "Could not find any suitable loop points for this audio file.")

    def on_autoloop_error(self, editor_widget, error):
        if editor_widget in self.autoloop_threads: del self.autoloop_threads[editor_widget]
        editor_widget.on_autoloop_finished(None) # Reset the specific widget's UI
        self.on_command_error(error)

    def on_cancel_autoloop(self, editor_widget):
        """Cancels the running auto-loop task for the specific widget."""
        if editor_widget in self.autoloop_threads:
            thread, worker = self.autoloop_threads[editor_widget]
            if thread.isRunning():
                thread.terminate()
                thread.wait()
            del self.autoloop_threads[editor_widget]
            editor_widget.on_autoloop_finished(None)
            self.update_status_bar.emit("Auto-loop cancelled.", 2000)

    def _prompt_for_acb_file(self, acb_filename_stem):
        """Opens a file dialog to locate an ACB file and returns the selected path or None."""
        filter_str = f"Specific ACB ({acb_filename_stem}.acb);;All ACB files (*.acb);;All files (*.*)"

        filepath, _ = QFileDialog.getOpenFileName(
            self,
            caption=f"Locate {acb_filename_stem}.acb (extracted with FModel)",
            filter=filter_str,
            dir=str(Path.cwd())
        )
        return filepath if filepath else None

    def set_acb_file(self, filepath, auto_unpack=False):
        """Central function to set the ACB file and reset the UI state."""
        # Capture state of the PREVIOUS ACB before switching
        self._capture_current_track_state()

        self._acb_file = filepath
        if filepath:
            self._current_acb_stem = Path(filepath).stem
        else:
            self._current_acb_stem = None

        self.acb_file_edit.setText(filepath)
        self.unpack_button.setEnabled(True)
        
        # Update window title with friendly name
        acb_stem = Path(filepath).stem
        if filepath: # Only update title if a file is actually set
            friendly_name = data.FRIENDLY_NAME_MAP.get(acb_stem)
            if friendly_name:
                self.setWindowTitle(f"{self.base_title} - [{friendly_name}]")
            else:
                self.setWindowTitle(f"{self.base_title} - [{acb_stem}]")

        # Reset subsequent steps
        self._unpacked_folder = ""
        self.convert_button.setEnabled(False)

        for track in [self.intro_track_vars, self.lap1_track_vars, self.final_lap_track_vars, self.transition_track_vars, self.transition_short_track_vars, self.announce_track_vars]:
            track.path_edit.clear()
            if track.loop_checkbox:
                track.loop_checkbox.setChecked(False)
            if track.loop_start_edit:
                track.loop_start_edit.clear()
            if track.loop_end_edit:
                track.loop_end_edit.clear()

        # Hide conversion options and show the placeholder text
        self.stage_music_frame.setVisible(False)
        self.special_track_frame.setVisible(False)
        self.scroll_area.setVisible(False)
        self.convert_button.setVisible(False)
        self.clear_all_button.setVisible(False)
        self.unpack_first_label.setVisible(True)

        # Clear special track vars, they will be repopulated
        for var_dict in list(self.special_track_vars.values()):
            var_dict.path_edit.setText('')
            if var_dict.loop_checkbox:
                var_dict.loop_checkbox.setChecked(False)

        self.repack_button.setEnabled(False)
        self.pak_button.setEnabled(False)

        # Show/hide widgets based on filename
        acb_path = Path(filepath)
        acb_stem = acb_path.stem

        if acb_stem.startswith("VOICE_") or acb_stem in ["SE_EXTND10_CHARA", "SE_EXTND11_CHARA", "SE_EXTND12_CHARA", "SE_EXTND15_CHARA"] or acb_stem == "BGM" or acb_stem in data.SPECIAL_TRACK_MAP or acb_stem == "BGM_EXTND04" or acb_stem == "SE_COURSE":
            self.special_track_frame.setVisible(True)
            self._populate_special_track_frame(acb_stem)
        else:
            self.stage_music_frame.setVisible(True)
            if acb_path.stem.startswith("BGM_STG2"):
                self.intro_track_vars.setVisible(False)
            else:
                self.intro_track_vars.setVisible(True)
            
            # Hide/Show Short Transition based on availability
            if acb_stem in ADDITIONAL_TRACK_INDICES:
                _, _, trans_short_idx = ADDITIONAL_TRACK_INDICES[acb_stem]
                self.transition_short_track_vars.setVisible(trans_short_idx is not None)
                self.copy_trans_btn.setVisible(trans_short_idx is not None)
            else:
                self.transition_short_track_vars.setVisible(True)
                self.copy_trans_btn.setVisible(True)

        # Restore state for the NEW ACB
        self._restore_track_state()

        if auto_unpack and self._acb_file:
            QTimer.singleShot(100, self.unpack_acb)

    def locate_acb_file(self):
        """Handles the 'Locate File...' button click in the editor screen."""
        acb_filename_stem = Path(self._acb_file).stem if self._acb_file else "game"

        filepath = self._prompt_for_acb_file(acb_filename_stem)
        if filepath:
            self.add_to_recent_files(filepath)
            self.set_acb_file(filepath, auto_unpack=False) # Don't auto-unpack when using the button

    def _get_original_file_index(self, hca_filename):
        """Helper to find the 0-based index of a specific HCA filename in the sorted original_files list."""
        try:
            return self.original_files.index(hca_filename)
        except ValueError:
            return None # File not found in unpacked folder

    def unpack_acb(self):
        acb_path = Path(self._acb_file)
        print(f"--- Step 1: Unpacking '{acb_path.name}' ---")
        self.update_status_bar.emit(f"Unpacking '{acb_path.name}'...", 0)
        self.unpack_button.setEnabled(False)
        
        self.unpack_progress.setRange(0, 0) # Indeterminate mode
        self.unpack_progress.setVisible(True)
        
        self.run_command_threaded(self.logic.unpack_acb, self.on_unpack_complete, self.on_command_error, args=(acb_path,))

    def on_unpack_complete(self, result):
        self.unpack_progress.setVisible(False)
        print("Unpacking complete.")
        self.update_status_bar.emit("Unpacking complete. Ready for audio conversion.", 0)
        self._unpacked_folder = result
        unpacked_path = Path(result)
        if not unpacked_path.exists():
            QMessageBox.critical(self, "Error", f"Failed to unpack. Folder '{unpacked_path.name}' was not created.")
            self.reset_ui_state()
            return
        
        # Show the conversion options now that unpacking is done
        self.unpack_first_label.setVisible(False)
        self.scroll_area.setVisible(True)
        self.convert_button.setVisible(True)
        self.clear_all_button.setVisible(True)

        QMessageBox.information(self, "Success", f"Unpacked to '{unpacked_path.name}'")
        self.convert_button.setEnabled(True)
        self.repack_button.setEnabled(True)
        self.pak_button.setEnabled(True)
        self.populate_orig_listbox()

    def sanitize_wav(self, input_path_str):
        """
        Ensures all audio files are a standard 16-bit PCM WAV by running them through ffmpeg.
        This fixes issues with files from external tools (like amplifier scripts)
        that output 32-bit Float WAVs, and guarantees compatibility with the modding tools.
        """
        input_path = Path(input_path_str)

        # Always run files through ffmpeg to guarantee a standard 16-bit PCM WAV format.
        self.update_status_bar.emit(f"Sanitizing '{input_path.name}' to 16-bit PCM...", 0)
        if QApplication.instance():
            QApplication.instance().processEvents()
        
        output_path = input_path.with_name(f"{input_path.stem}_16bit.wav")
        
        ffmpeg_cmd = "ffmpeg"
        tools_ffmpeg = TOOLS_DIR / "ffmpeg.exe"
        if tools_ffmpeg.exists():
            ffmpeg_cmd = str(tools_ffmpeg)
        
        cmd = [ffmpeg_cmd, "-y", "-i", str(input_path), "-c:a", "pcm_s16le", str(output_path)]
        
        try:
            cflags = 0x08000000 if sys.platform == "win32" else 0
            subprocess.run(cmd, check=True, capture_output=True, creationflags=cflags)
            print(f"Sanitized: {input_path.name} -> {output_path.name}")
            return str(output_path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"Failed to sanitize '{input_path.name}'. Ensure ffmpeg is installed.")
            return input_path_str

    def convert_audio(self):
        """New fully automated conversion process."""
        acb_path = Path(self._acb_file)
        print(f"\n--- Step 2: Starting Conversion for '{acb_path.stem}' ---")
        self.update_status_bar.emit(f"Preparing to convert audio for '{acb_path.stem}'...", 0)

        # --- Prepare list of conversions to run ---
        acb_stem = acb_path.stem
        tasks = [] # hca_name, path, is_looping, start, end
        if acb_stem.startswith("VOICE_") or acb_stem in ["SE_EXTND10_CHARA", "SE_EXTND11_CHARA", "SE_EXTND12_CHARA", "SE_EXTND15_CHARA"] or acb_stem == "BGM" or acb_stem in data.SPECIAL_TRACK_MAP or acb_stem == "BGM_EXTND04" or acb_stem == "SE_COURSE":
            for hca_name, var_dict in self.special_track_vars.items():
                if var_dict.path_edit.text():
                    is_looping = var_dict.loop_checkbox and var_dict.loop_checkbox.isChecked()
                    start_widget = var_dict.loop_start_edit
                    end_widget = var_dict.loop_end_edit
                    start_text = start_widget.text() if start_widget else ""
                    end_text = end_widget.text() if end_widget else ""

                    tasks.append((hca_name, var_dict.path_edit.text(), is_looping, start_text, end_text))
        else: # Stage music
            if self.intro_track_vars.path_edit.text():
                tasks.append(("intro", self.intro_track_vars.path_edit.text(), self.intro_track_vars.loop_checkbox.isChecked(), self.intro_track_vars.loop_start_edit.text(), self.intro_track_vars.loop_end_edit.text()))
            if self.lap1_track_vars.path_edit.text():
                tasks.append(("lap1", self.lap1_track_vars.path_edit.text(), self.lap1_track_vars.loop_checkbox.isChecked(), self.lap1_track_vars.loop_start_edit.text(), self.lap1_track_vars.loop_end_edit.text()))
            if self.final_lap_track_vars.path_edit.text():
                tasks.append(("final_lap", self.final_lap_track_vars.path_edit.text(), self.final_lap_track_vars.loop_checkbox.isChecked(), self.final_lap_track_vars.loop_start_edit.text(), self.final_lap_track_vars.loop_end_edit.text()))
            if self.transition_track_vars.path_edit.text():
                tasks.append(("transition", self.transition_track_vars.path_edit.text(), self.transition_track_vars.loop_checkbox.isChecked(), self.transition_track_vars.loop_start_edit.text(), self.transition_track_vars.loop_end_edit.text()))
            if self.transition_short_track_vars.path_edit.text():
                tasks.append(("transition_short", self.transition_short_track_vars.path_edit.text(), self.transition_short_track_vars.loop_checkbox.isChecked(), self.transition_short_track_vars.loop_start_edit.text(), self.transition_short_track_vars.loop_end_edit.text()))
            if self.announce_track_vars.path_edit.text():
                tasks.append(("announce", self.announce_track_vars.path_edit.text(), self.announce_track_vars.loop_checkbox.isChecked(), self.announce_track_vars.loop_start_edit.text(), self.announce_track_vars.loop_end_edit.text()))
        
        # Validate loop points for commas
        for name, _, is_looping, start, end in tasks:
            if is_looping:
                if ',' in start or ',' in end:
                    QMessageBox.warning(self, "Invalid Loop Points", 
                                        f"Error in track '{name}': Loop points cannot contain commas.\n\n"
                                        f"Start: {start}\nEnd: {end}\n\n"
                                        "Please remove the commas (e.g., change '1,234' to '1234') and try again.")
                    return
                try:
                    if int(start) >= int(end):
                        QMessageBox.warning(self, "Invalid Loop Points",
                                            f"Error in track '{name}': Loop End must be greater than Loop Start.\n\n"
                                            f"Start: {start}\nEnd: {end}")
                        return
                except ValueError:
                    pass # Commas are already handled, this will catch other non-integer values

        # Sanitize WAV files (fix for 32-bit float / incompatible WAVs)
        sanitized_tasks = []
        for name, wav_path_str, is_looping, start, end in tasks:
            safe_path = self.sanitize_wav(wav_path_str)
            sanitized_tasks.append((name, safe_path, is_looping, start, end))
        tasks = sanitized_tasks

        print("The following files will be converted:")
        for name, wav_path_str, _, _, _ in tasks:
            wav_path = Path(wav_path_str)
            print(f"  - Source: '{wav_path.name}' -> Target: {name}.hca")

        if not tasks:
            QMessageBox.information(self, "Nothing to Convert", "No WAV files were selected for conversion.")
            return

        # --- Run conversions in a thread ---
        self.convert_button.setEnabled(False)
        self.update_status_bar.emit("Converting audio files... this may take a moment.", 0)
        try:
            self.run_command_threaded(self.logic.convert_audio, self.on_convert_complete, self.on_command_error, args=(acb_path, tasks))
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
            self.reset_ui_state()

    def on_convert_complete(self, result):
        print("All conversions complete.")
        self.update_status_bar.emit("Audio conversion complete. Ready to repack.", 0)
        QMessageBox.information(self, "Success", "Audio conversion complete!")
        self.reset_ui_state()

    def clear_all_tracks(self):
        """Clears all input fields in the currently active track editors."""
        reply = QMessageBox.question(self, "Clear All", "Are you sure you want to clear all selected files?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for editor in self.all_track_editors:
                editor.path_edit.clear()
                if editor.loop_checkbox:
                    editor.loop_checkbox.setChecked(False)
            self.update_status_bar.emit("All tracks cleared.", 0)

    def _capture_current_track_state(self):
        """Saves the current UI state to the cache for the current ACB."""
        if not self._current_acb_stem:
            return

        state = {}
        for editor in self.all_track_editors:
            path = editor.path_edit.text()
            # Save state even if empty, to remember that it was cleared
            track_data = {
                "path": path,
                "loop_enabled": editor.loop_checkbox.isChecked() if editor.loop_checkbox else False,
                "loop_start": editor.loop_start_edit.text() if editor.loop_start_edit else "",
                "loop_end": editor.loop_end_edit.text() if editor.loop_end_edit else ""
            }
            state[editor.original_label_text] = track_data
        
        self._track_file_cache[self._current_acb_stem] = state

    def _restore_track_state(self):
        """Restores UI state from cache for the current ACB."""
        if not self._current_acb_stem or self._current_acb_stem not in self._track_file_cache:
            return
        
        state = self._track_file_cache[self._current_acb_stem]
        for editor in self.all_track_editors:
            if editor.original_label_text in state:
                data = state[editor.original_label_text]
                editor.path_edit.setText(data.get("path", ""))
                if editor.loop_checkbox:
                    editor.loop_checkbox.setChecked(data.get("loop_enabled", False))
                if editor.loop_start_edit:
                    editor.loop_start_edit.setText(data.get("loop_start", ""))
                if editor.loop_end_edit:
                    editor.loop_end_edit.setText(data.get("loop_end", ""))

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
        self.update_status_bar.emit("Applying replacement audio files...", 0)
        replacement_map = {}

        acb_stem = Path(self._acb_file).stem
        is_special_acb_for_onetoone = acb_stem.startswith("VOICE_") or acb_stem in ["SE_EXTND10_CHARA", "SE_EXTND11_CHARA", "SE_EXTND12_CHARA", "SE_EXTND15_CHARA"] or acb_stem == "BGM" or acb_stem in data.SPECIAL_TRACK_MAP or acb_stem == "BGM_EXTND04" or acb_stem == "SE_COURSE"
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
        if is_special_acb_for_onetoone: # For Menu, Voice, and Spongebob (one-to-one mapping)
            for hca_name, var_dict in self.special_track_vars.items():
                # SE_COURSE uses .adx, others use .hca
                file_ext = "adx" if acb_stem == "SE_COURSE" else "hca"
                converted_file = OUTPUT_DIR / f"{hca_name}.{file_ext}"
                if converted_file.exists():
                    replacement_map[f"{hca_name}.{file_ext}"] = f"{hca_name}.{file_ext}"
            
            # Handle implicit intros for SpongeBob
            if acb_stem == "BGM_EXTND05":
                final_lap_hca_name = "00024_streaming"
                final_lap_intro_hca_name = "00025_streaming"
                if (OUTPUT_DIR / f"{final_lap_hca_name}.hca").exists():
                    replacement_map[f"{final_lap_intro_hca_name}.hca"] = f"{final_lap_hca_name}.hca"
            
            # Handle implicit shorts for Miku (BGM_EXTND10)
            if acb_stem == "BGM_EXTND10":
                # Map Main -> Short
                miku_shorts = {
                    "00084_streaming": "00085_streaming", # Denkoh Sekka
                    "00086_streaming": "00087_streaming", # Denkoh Sekka FL
                    "00088_streaming": "00089_streaming", # Piko Piko
                    "00090_streaming": "00091_streaming", # Piko Piko FL
                    "00092_streaming": "00093_streaming", # Jet Black
                    "00094_streaming": "00095_streaming", # Jet Black FL
                    "00097_streaming": "00098_streaming", # SAI LOVE FL
                    "00099_streaming": "00100_streaming", # TREASURE GARDEN
                    "00101_streaming": "00102_streaming", # TREASURE GARDEN FL
                }
                for main, short in miku_shorts.items():
                    if (OUTPUT_DIR / f"{main}.hca").exists():
                        replacement_map[f"{short}.hca"] = f"{main}.hca"
            
            # Handle implicit shorts for PAC-MAN (BGM_EXTND06)
            if acb_stem == "BGM_EXTND06":
                pacman_shorts = {
                    "00043_streaming": ["00044_streaming", "00045_streaming"], # PAC-Village -> shorts
                    "00046_streaming": ["00047_streaming"], # Maze -> short
                    "00048_streaming": ["00049_streaming"], # PAC-Village FL -> short
                    "00050_streaming": ["00051_streaming"], # Maze FL -> short
                }
                for main, shorts in pacman_shorts.items():
                    if (OUTPUT_DIR / f"{main}.hca").exists():
                        for short in shorts:
                            replacement_map[f"{short}.hca"] = f"{main}.hca"

        elif acb_stem in special_structures:
            print(f"Applying special structure for {acb_stem}...")
            structure = special_structures[acb_stem] # This structure contains either indices or hca_filenames
            
            if (OUTPUT_DIR / "lap1.hca").exists():
                if structure["lap1"] is not None: replacement_map[self.original_files[structure["lap1"]]] = "lap1.hca"
                if structure["lap1_intro"] is not None: replacement_map[self.original_files[structure["lap1_intro"]]] = "lap1.hca"
            
            if (OUTPUT_DIR / "final_lap.hca").exists():
                if structure["final_lap"] is not None: replacement_map[self.original_files[structure["final_lap"]]] = "final_lap.hca"
                if structure["final_lap_intro"] is not None: replacement_map[self.original_files[structure["final_lap_intro"]]] = "final_lap.hca"
            
            if not is_crossworlds and (OUTPUT_DIR / "intro.hca").exists():
                if structure["intro"] is not None: replacement_map[self.original_files[structure["intro"]]] = "intro.hca"

        else: # Default logic for other stage tracks
            if len(self.original_files) < 5:
                QMessageBox.critical(self, "Error", "Cannot apply replacements: Not enough original files found in the unpacked folder.")
                return

            if (OUTPUT_DIR / "lap1.hca").exists():
                replacement_map[self.original_files[0]] = "lap1.hca" # Lap 1
                # Check to avoid index out of bounds if there's only 1 file
                if len(self.original_files) > 1:
                    replacement_map[self.original_files[1]] = "lap1.hca" # Lap 1 intro
            if (OUTPUT_DIR / "final_lap.hca").exists():
                if len(self.original_files) > 2:
                    replacement_map[self.original_files[2]] = "final_lap.hca" # Final Lap
                if len(self.original_files) > 3:
                    replacement_map[self.original_files[3]] = "final_lap.hca" # Final Lap intro
            if not is_crossworlds and (OUTPUT_DIR / "intro.hca").exists():
                if len(self.original_files) > 4:
                    replacement_map[self.original_files[4]] = "intro.hca" # Intro

        # Apply additional tracks (Announce, Transition, Transition Short)
        if acb_stem in ADDITIONAL_TRACK_INDICES:
            ann_idx, trans_idx, trans_short_idx = ADDITIONAL_TRACK_INDICES[acb_stem]
            
            if ann_idx is not None and (OUTPUT_DIR / "announce.hca").exists():
                if ann_idx < len(self.original_files):
                    replacement_map[self.original_files[ann_idx]] = "announce.hca"
            
            if trans_idx is not None and (OUTPUT_DIR / "transition.hca").exists():
                if trans_idx < len(self.original_files):
                    replacement_map[self.original_files[trans_idx]] = "transition.hca"

            if trans_short_idx is not None and (OUTPUT_DIR / "transition_short.hca").exists():
                if trans_short_idx < len(self.original_files):
                    replacement_map[self.original_files[trans_short_idx]] = "transition_short.hca"

        try:
            files_replaced = self.logic.apply_replacements(self._unpacked_folder, replacement_map)
            if files_replaced > 0:
                QMessageBox.information(self, "Success", f"{files_replaced} file(s) replaced successfully in the unpacked folder.")
            else:
                QMessageBox.information(self, "No Changes", "No converted tracks found in 'output' folder. Nothing to apply.")
                return
        except FileNotFoundError as e:
            QMessageBox.critical(self, "File Not Found", str(e))
            return

        print("\n--- Step 3: Repacking ACB ---")
        unpacked_path = Path(self._unpacked_folder)
        self.update_status_bar.emit(f"Repacking '{unpacked_path.name}'...", 0)
        self.repack_button.setEnabled(False) # Disable button during operation
        self.run_command_threaded(self.logic.repack_acb, self.on_repack_complete, self.on_command_error, args=(unpacked_path,))

    def on_repack_complete(self, result):
        print("Repacking complete.")
        self.update_status_bar.emit("ACB repacked successfully. Ready to create .pak file.", 0)
        QMessageBox.information(self, "Success", "ACB folder has been repacked!")
        self.reset_ui_state()

    def create_pak(self):
        mod_name_str = self._mod_name.strip()
        if not mod_name_str:
            QMessageBox.critical(self, "Error", "Mod Name cannot be empty.")
            return

        print(f"\n--- Step 4: Creating Mod Pak '{mod_name_str}.pak' ---")
        self.update_status_bar.emit(f"Creating mod package '{mod_name_str}.pak'...", 0)
        try:
            self.pak_button.setEnabled(False)
            self.run_command_threaded(self.logic.create_pak, self.on_pak_complete, self.on_command_error, args=(mod_name_str, self._acb_file))
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Error preparing files for packing: {e}")
            self.reset_ui_state()

    def on_pak_complete(self, result):
        mod_name_str = self._mod_name.strip()
        print(f"Pak file creation complete.")
        self.update_status_bar.emit(f"Mod '{mod_name_str}.pak' created successfully!", 0)
        pak_file = Path(mod_name_str).with_suffix('.pak')
        QMessageBox.information(self, "Mod Creation Complete!", f"Successfully created mod package:\n{pak_file.resolve()}")
        self.reset_ui_state()

    def show_pak_output(self):
        """Opens the script's directory where the .pak file is created."""
        output_dir = Path.cwd()
        try:
            # QDesktopServices.openUrl is more cross-platform
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

    def add_to_recent_files(self, filepath):
        """Adds a file to the top of the recent files list."""
        if not filepath:
            return
        
        # Remove if it already exists to avoid duplicates and move to top
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        
        # Add to the top of the list
        self.recent_files.insert(0, filepath)
        
        # Limit the list size
        self.recent_files = self.recent_files[:self.MAX_RECENT_FILES]
        
        # Update the menu
        self.update_recent_files_menu()

    def update_recent_files_menu(self):
        """Clears and repopulates the 'Recent Files' menu."""
        self.recent_files_menu.clear()
        
        if not self.recent_files:
            empty_action = self.recent_files_menu.addAction("No Recent Files")
            empty_action.setEnabled(False)
        else:
            for filepath in self.recent_files:
                # Use a lambda to capture the filepath for the slot
                action = self.recent_files_menu.addAction(filepath)
                action.triggered.connect(lambda checked=False, fp=filepath: self.open_recent_file(fp))

        self.recent_files_menu.addSeparator()
        clear_action = self.recent_files_menu.addAction("Clear Recent Files")
        clear_action.triggered.connect(self.clear_recent_files)

    def open_recent_file(self, filepath):
        """Opens a file from the recent files menu."""
        path = Path(filepath)
        if not path.exists():
            QMessageBox.warning(self, "File Not Found", f"The file '{filepath}' could not be found. It will be removed from the recent files list.")
            self.recent_files.remove(filepath)
            self.update_recent_files_menu()
            return
            
        # This logic is similar to on_card_selected
        self.add_to_recent_files(filepath) # Also add it here to move it to the top
        self.editor_screen.setVisible(True)
        self.selection_screen.setVisible(False)
        self.set_acb_file(filepath, auto_unpack=True)

    def clear_recent_files(self):
        """Clears the recent files list and menu."""
        self.recent_files.clear()
        self.update_recent_files_menu()

    def show_settings_dialog(self):
        """Opens the settings dialog."""
        dialog = SettingsDialog(self)
        if dialog.exec(): # This is a blocking call
            # OK was clicked, update the path in the main window
            self.criware_folder_path = dialog._criware_path
            
            old_debug = self.debug_logging_enabled
            self.debug_logging_enabled = dialog._debug_enabled
            
            if self.debug_logging_enabled and not old_debug:
                self._show_log_window()
            elif not self.debug_logging_enabled and old_debug:
                self._hide_log_window()
            
            self.save_settings() # Save immediately on change
            print(f"CriWare folder path updated to: {self.criware_folder_path}")

    def _setup_log_redirection(self):
        if hasattr(self, '_redirectors_setup') and self._redirectors_setup:
            return

        self.log_window = LogWindow()
        
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        
        self.stdout_redirector = StreamRedirector(self._original_stdout)
        self.stderr_redirector = StreamRedirector(self._original_stderr)
        
        self.stdout_redirector.text_written.connect(self.log_window.append_text)
        self.stderr_redirector.text_written.connect(self.log_window.append_text)
        
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector
        
        self._redirectors_setup = True

    def _show_log_window(self):
        self._setup_log_redirection()
        self.log_window.show()
        self.debug_logging_enabled = True

    def _hide_log_window(self):
        if hasattr(self, 'log_window') and self.log_window:
            self.log_window.hide()
        self.debug_logging_enabled = False

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show splash screen
    splash_pix = QPixmap("tools/splash.png")
    if splash_pix.isNull():
        # If splash.png is not found, use the app icon as a fallback
        splash_pix = QPixmap("tools/ico.ico")
    
    splash = QSplashScreen(splash_pix, Qt.WindowType.WindowStaysOnTopHint)
    splash.show()
    app.processEvents() # Ensure splash screen is displayed

    window = ModBuilderGUI(splash)
    window.show()
    splash.finish(window)
    sys.exit(app.exec())
