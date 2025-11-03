import os
import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
                                   QLineEdit, QPushButton, QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem,
                                   QScrollArea, QFrame, QMenuBar, QStatusBar)
    from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
    from PySide6.QtGui import QDesktopServices, QShortcut, QKeySequence
    from PySide6.QtCore import QUrl
except ImportError:
    print("Error: PySide6 module not found. Please install it using 'pip install PySide6'")
    sys.exit(1)

import data
from ui_components import BGMSelectorWindow
from mod_logic import ModLogic

# --- Configuration ---
# Set the paths to your tools relative to this script.
TOOLS_DIR = Path("tools")
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

        self.logic = ModLogic(TOOLS_DIR, OUTPUT_DIR)

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

        # --- New state vars for direct file selection ---
        self.intro_track_vars = {}
        self.lap1_track_vars = {}
        self.final_lap_track_vars = {}

        # --- New state vars for menu music ---
        self.menu_track_vars = {}
        self.voice_cre_track_vars = {}
        self.voice_search_bar = None

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

        # --- Shortcuts ---
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self.focus_search_bar)

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

        for label, hca_name in data.MENU_BGM_TRACKS.items():
            self.menu_track_vars[hca_name] = self._create_track_selector(menu_layout, label)
            if hca_name != list(data.MENU_BGM_TRACKS.values())[-1]:
                menu_layout.addWidget(self._create_separator())

        # --- Dynamic Voice Line Frame ---
        self.voice_cre_frame = QWidget()
        voice_layout = QVBoxLayout(self.voice_cre_frame)
        voice_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.addWidget(self.voice_cre_frame)

        # This frame will be populated dynamically in set_acb_file

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

    def _create_track_selector(self, parent_layout, label_text, show_loop_options=True):
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

        parent_layout.addWidget(frame)

        var_dict = {
            'path': path_edit,
            'loop': None,
            'start': None,
            'end': None
        }

        if show_loop_options:
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

            var_dict['loop'] = loop_group
            var_dict['start'] = loop_start_edit
            var_dict['end'] = loop_end_edit

        browse_button.clicked.connect(lambda: self._select_wav_file(path_edit))
        return var_dict

    def check_tools(self):
        missing_tools = self.logic.check_tools()
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

    def _populate_voice_frame(self, character_code):
        """Dynamically populates the voice frame with selectors for the given character."""
        self._clear_layout(self.voice_cre_frame.layout())
        self.voice_cre_track_vars.clear()
        self.voice_search_bar = None

        # Add search bar
        search_layout = QHBoxLayout()
        self.voice_search_bar = QLineEdit()
        self.voice_search_bar.setPlaceholderText("Search Voice Lines... (Ctrl+F)")
        self.voice_search_bar.textChanged.connect(self._filter_voice_lines)
        self.voice_cre_frame.layout().addWidget(self.voice_search_bar)

        # Get the correct track dictionary from the data module
        track_dict_name = f"VOICE_{character_code}_TRACKS"
        track_dict = getattr(data, track_dict_name, {})

        if not track_dict:
            label = QLabel(f"No voice lines defined for {character_code} in data.py yet.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.voice_cre_frame.layout().addWidget(label)
            return

        for label, hca_name in track_dict.items():
            self.voice_cre_track_vars[hca_name] = self._create_track_selector(self.voice_cre_frame.layout(), label, show_loop_options=False)
            if hca_name != list(track_dict.values())[-1]:
                self.voice_cre_frame.layout().addWidget(self._create_separator())

        # Reset loop checks for the newly created widgets
        for var_dict in self.voice_cre_track_vars.values():
            if var_dict.get('loop'):
                var_dict['loop'].setChecked(False)

    def _filter_voice_lines(self, text):
        """Hides/shows voice line widgets based on the search text."""
        search_text = text.lower()
        layout = self.voice_cre_frame.layout()

        # Iterate through all widgets in the layout
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget is None or widget == self.voice_search_bar:
                continue

            # Find the label within the widget
            label = widget.findChild(QLabel)
            if label:
                is_match = search_text in label.text().lower()
                widget.setVisible(is_match)
                
                # Also hide/show the separator that might be after it
                next_item = layout.itemAt(i + 1)
                if next_item and isinstance(next_item.widget(), QFrame):
                    next_item.widget().setVisible(is_match)

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
            caption="Select Audio File",
            filter="Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a);;All files (*.*)",
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
        # Clear voice vars, they will be repopulated
        for var_dict in list(self.voice_cre_track_vars.values()):
            var_dict['path'].setText('')

        self.repack_button.setEnabled(False)
        self.pak_button.setEnabled(False)

        # Show/hide widgets based on filename
        acb_path = Path(filepath)
        if acb_path.stem == "BGM":
            self.menu_music_frame.setVisible(True)
        elif acb_path.stem.startswith("VOICE_"):
            character_code = acb_path.stem.split('_')[1]
            self.voice_cre_frame.setVisible(True)
            self._populate_voice_frame(character_code)
        else:
            self.stage_music_frame.setVisible(True)
            if acb_path.stem.startswith("BGM_STG2"):
                self.intro_track_vars['path'].parent().setVisible(False)
            else:
                self.intro_track_vars['path'].parent().setVisible(True)

    def unpack_acb(self):
        acb_path = Path(self._acb_file)
        print(f"--- Step 1: Unpacking '{acb_path.name}' ---")
        self.status_bar.showMessage(f"Unpacking '{acb_path.name}'...")
        self.unpack_button.setEnabled(False)
        self.run_command_threaded(self.logic.unpack_acb, self.on_unpack_complete, self.on_command_error, args=(acb_path,))

    def on_unpack_complete(self, result):
        print("Unpacking complete.")
        self.status_bar.showMessage("Unpacking complete. Ready for audio conversion.")
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

        QMessageBox.information(self, "Success", f"Unpacked to '{unpacked_path.name}'")
        self.convert_button.setEnabled(True)
        self.repack_button.setEnabled(True)
        self.pak_button.setEnabled(True)
        self.populate_orig_listbox()

    def convert_audio(self):
        """New fully automated conversion process."""
        acb_path = Path(self._acb_file)
        print(f"\n--- Step 2: Starting Conversion for '{acb_path.stem}' ---")
        self.status_bar.showMessage(f"Preparing to convert audio for '{acb_path.stem}'...")

        # --- Prepare list of conversions to run ---
        tasks = []
        is_menu_bgm = acb_path.stem == "BGM"
        is_voice_acb = acb_path.stem.startswith("VOICE_")

        if is_menu_bgm:
            for hca_name, var_dict in self.menu_track_vars.items():
                if var_dict['path'].text():
                    tasks.append((hca_name, var_dict['path'].text(), var_dict['loop'].isChecked(), var_dict['start'].text(), var_dict['end'].text()))
        elif is_voice_acb:
            for hca_name, var_dict in self.voice_cre_track_vars.items():
                if var_dict['path'].text():
                    tasks.append((hca_name, var_dict['path'].text(), False, "", "")) # Always False for loops
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
        try:
            self.run_command_threaded(self.logic.convert_audio, self.on_convert_complete, self.on_command_error, args=(acb_path, tasks))
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))
            self.reset_ui_state()

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
        replacement_map = {}

        acb_stem = Path(self._acb_file).stem
        is_menu_bgm = acb_stem == "BGM"
        is_voice_acb = acb_stem.startswith("VOICE_")
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
                    replacement_map[hca_name + ".hca"] = hca_name + ".hca"
        elif is_voice_acb:
            for hca_name, var_dict in self.voice_cre_track_vars.items():
                converted_file = OUTPUT_DIR / f"{hca_name}.hca"
                if converted_file.exists():
                    replacement_map[hca_name + ".hca"] = hca_name + ".hca"
        elif acb_stem in special_structures:
            print(f"Applying special structure for {acb_stem}...")
            structure = special_structures[acb_stem]
            
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
        self.status_bar.showMessage(f"Repacking '{unpacked_path.name}'...")
        self.repack_button.setEnabled(False)
        self.run_command_threaded(self.logic.repack_acb, self.on_repack_complete, self.on_command_error, args=(unpacked_path,))

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
        try:
            self.pak_button.setEnabled(False)
            self.run_command_threaded(self.logic.create_pak, self.on_pak_complete, self.on_command_error, args=(mod_name_str, self._acb_file))
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Error preparing files for packing: {e}")
            self.reset_ui_state()

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
