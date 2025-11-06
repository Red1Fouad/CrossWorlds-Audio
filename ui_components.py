import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
                                   QLineEdit, QPushButton, QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem,
                                   QScrollArea, QFrame, QMenuBar, QStatusBar, QTabWidget, QGridLayout, QSizePolicy, QDialog, QDialogButtonBox, 
                                   QCheckBox)
    from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QSize
    from PySide6.QtGui import QDesktopServices, QShortcut, QKeySequence, QIcon, QPixmap, QPainter, QColor
    try:
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        MULTIMEDIA_AVAILABLE = True
    except ImportError:
        print("Warning: PySide6.QtMultimedia not found. Audio playback will be disabled. Install with 'pip install PySide6-Addons'")
        MULTIMEDIA_AVAILABLE = False
    from PySide6.QtCore import QUrl
except ImportError:
    print("Error: PySide6 module not found. Please install it using 'pip install PySide6'")
    sys.exit(1)

class BGMSelectorWindow(QFileDialog):
    """A custom file dialog to select from a list of common BGM files."""
    def __init__(self, parent=None):
        super().__init__(parent, "Select Common BGM", "", "ACB Files (*.acb)")
        self.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True) # Use Qt's dialog
        self.result = None

        # Find the QListView and QLineEdit widgets
        self.list_view = self.findChild(QTreeWidget)
        self.line_edit = self.findChild(QLineEdit, "fileNameEdit")

        if self.list_view and self.line_edit:
            self.list_view.setHeaderHidden(True)
            self.list_view.setColumnCount(2)
            self.list_view.itemClicked.connect(self.item_selected)
            self.populate_list()

    def populate_list(self):
        # This is a placeholder. In a real scenario, you'd populate this
        # from your data module.
        from data import FRIENDLY_NAME_MAP
        self.list_view.clear()
        items = []
        for acb_file, friendly_name in FRIENDLY_NAME_MAP.items():
            if acb_file.startswith("BGM_STG"):
                item = QTreeWidgetItem([friendly_name, f"{acb_file}.acb"])
                items.append(item)
        self.list_view.addTopLevelItems(items)
        self.list_view.resizeColumnToContents(0)
        self.list_view.resizeColumnToContents(1)

    def item_selected(self, item, column):
        self.result = item.text(1)
        self.line_edit.setText(f'"{self.result}"') # Set text for visual feedback

    def accept(self):
        # Ensure a result is set if the user clicks "Open"
        # without clicking an item first.
        selected_items = self.list_view.selectedItems()
        if selected_items:
            self.result = selected_items[0].text(1)
        super().accept()

class ImageCard(QFrame):
    """A clickable card widget with an image and a title."""
    clicked = Signal(str, str)  # acb_stem, friendly_name

    def __init__(self, acb_stem, friendly_name, image_path, parent=None):
        super().__init__(parent)
        self.acb_stem = acb_stem
        self.friendly_name = friendly_name

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setLineWidth(1)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(220, 160) # 16:9 image + title

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Image Label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
             # Create a placeholder if image is not found
            pixmap = QPixmap(160*1.77, 160)
            pixmap.fill(QColor('darkgrey'))
            painter = QPainter(pixmap)
            painter.setPen(QColor('white'))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "No Image")
            painter.end()

        self.image_label.setPixmap(pixmap.scaled(
            192, 108, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        layout.addWidget(self.image_label)

        # Title Label
        self.title_label = QLabel(friendly_name)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        layout.addWidget(self.title_label)

        self.setStyleSheet("""
            ImageCard, #ImageCard {
                border: 1px solid palette(mid);
                border-radius: 5px;
            }
            ImageCard:hover, #ImageCard:hover {
                background-color: palette(highlight);
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.acb_stem, self.friendly_name)
        super().mousePressEvent(event)

class TrackEditorWidget(QFrame):
    """A collapsible widget for editing a single track's replacement file and loop points."""
    play_requested = Signal(object)  # Signal that this widget wants to play audio
    normalize_requested = Signal(str) # Signal that this widget wants to normalize audio

    def __init__(self, label_text, show_loop_options=True, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("TrackEditorWidget")

        # --- Data Storage ---
        self.path_edit = None
        self.loop_checkbox = None
        self.loop_start_edit = None
        self.loop_end_edit = None

        # --- Audio Playback ---
        self.player = None
        self.audio_output = None
        if MULTIMEDIA_AVAILABLE:
            self._init_player()

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header (Clickable to collapse) ---
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderFrame")
        self.header_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(8, 5, 8, 5)

        self.toggle_arrow = QLabel("▶")
        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(22, 22)
        self.play_button.setToolTip("Preview Audio")
        self.play_button.setEnabled(False)
        if MULTIMEDIA_AVAILABLE:
            self.play_button.clicked.connect(self.toggle_playback)
        else:
            self.play_button.setVisible(False)
        self.title_label = QLabel(f"<b>{label_text}</b>")
        self.status_label = QLabel("<i>No file selected</i>")
        self.status_label.setObjectName("StatusLabel")

        header_layout.addWidget(self.toggle_arrow)
        header_layout.addWidget(self.play_button)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        main_layout.addWidget(self.header_frame)

        # --- Content (Collapsible) ---
        self.content_frame = QFrame()
        self.content_frame.setObjectName("ContentFrame")
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(8)
        main_layout.addWidget(self.content_frame)

        # File path input
        # A custom QLineEdit that accepts drag-and-drop for file paths.
        class DropLineEdit(QLineEdit):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setAcceptDrops(True)
            def dragEnterEvent(self, event):
                if event.mimeData().hasUrls(): event.acceptProposedAction()
                else: super().dragEnterEvent(event)
            def dropEvent(self, event):
                if event.mimeData().hasUrls():
                    url = event.mimeData().urls()[0]
                    self.setText(url.toLocalFile())
                    event.acceptProposedAction()
                else: super().dropEvent(event)

        browse_layout = QHBoxLayout()
        self.path_edit = DropLineEdit()
        self.path_edit.setPlaceholderText("Drag & drop an audio file here, or use Browse...")
        self.path_edit.textChanged.connect(self._update_status)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.path_edit.clear)
        self.normalize_button = QPushButton("Normalize")
        self.normalize_button.setToolTip("Normalizes this audio file against a reference and saves it as a new WAV file.")
        self.normalize_button.clicked.connect(self.emit_normalize_request)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_for_file)
        browse_layout.addWidget(self.path_edit)
        browse_layout.addWidget(clear_button)
        browse_layout.addWidget(self.normalize_button)
        browse_layout.addWidget(browse_button)
        content_layout.addLayout(browse_layout)

        # Loop options
        if show_loop_options:
            self.loop_widget = QWidget()
            loop_layout = QHBoxLayout(self.loop_widget)
            loop_layout.setContentsMargins(0, 5, 0, 0)

            self.loop_checkbox = QCheckBox("Enable Loop Points (samples)")
            self.loop_checkbox.toggled.connect(self._toggle_loop_edits_enabled)
            loop_layout.addWidget(self.loop_checkbox)

            loop_layout.addStretch()
            loop_layout.addWidget(QLabel("Start:"))
            self.loop_start_edit = QLineEdit()
            self.loop_start_edit.setFixedWidth(80)
            self.loop_start_edit.setEnabled(False) # Start disabled
            loop_layout.addWidget(self.loop_start_edit)
            loop_layout.addWidget(QLabel("End:"))
            self.loop_end_edit = QLineEdit()
            self.loop_end_edit.setFixedWidth(80)
            self.loop_end_edit.setEnabled(False) # Start disabled
            loop_layout.addWidget(self.loop_end_edit)
            content_layout.addWidget(self.loop_widget)

        # --- Styling & Connections ---
        self.header_frame.mousePressEvent = self.toggle_content
        self.content_frame.setVisible(False) # Collapsed by default
        self._update_status()

    def toggle_content(self, event):
        is_visible = not self.content_frame.isVisible()
        self.content_frame.setVisible(is_visible)
        self.toggle_arrow.setText("▼" if is_visible else "▶")

        # Ensure the layout updates correctly after visibility change
        self.content_frame.parentWidget().layout().invalidate()

    def _toggle_loop_edits_enabled(self, checked):
        """Emits the normalize_requested signal with the current file path."""
        self.normalize_requested.emit(self.path_edit.text())

    def _toggle_loop_edits_enabled(self, checked):
        """Enables or disables the loop point input fields based on the checkbox state."""
        if self.loop_start_edit and self.loop_end_edit:
            self.loop_start_edit.setEnabled(checked)
            self.loop_end_edit.setEnabled(checked)

    def _browse_for_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a);;All files (*.*)")
        if filepath:
            self.path_edit.setText(filepath)

    def _update_status(self):
        if self.path_edit.text():
            filename = Path(self.path_edit.text()).name
            self.status_label.setText(f"<b>{filename}</b>")
            self.header_frame.setProperty("hasFile", True)
        else:
            self.status_label.setText("<i>No file selected</i>")
            self.header_frame.setProperty("hasFile", False)

        # Re-polish to apply style changes
        self.header_frame.style().unpolish(self.header_frame)
        self.header_frame.style().polish(self.header_frame)

        # Enable/disable play button
        if MULTIMEDIA_AVAILABLE:
            has_text = bool(self.path_edit.text())
            is_audio = has_text and Path(self.path_edit.text()).suffix.lower() in ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
            self.normalize_button.setEnabled(is_audio)
            self.play_button.setEnabled(is_audio)
            if not has_text:
                self.stop_playback() # Stop playing if text is cleared

    def _init_player(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)

    def toggle_playback(self):
        if not self.player: return

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.stop_playback()
        else:
            self.play_requested.emit(self)
            filepath = self.path_edit.text()
            if filepath and Path(filepath).exists():
                self.player.setSource(QUrl.fromLocalFile(filepath))
                self.player.play()

    def stop_playback(self):
        if self.player and self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self.player.stop()

    def _on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setText("■") # Stop symbol
            self.play_button.setToolTip("Stop Preview")
        else: # Stopped or Paused
            self.play_button.setText("▶") # Play symbol
            self.play_button.setToolTip("Preview Audio")

    def emit_normalize_request(self):
        """Emits the normalize_requested signal with the current file path."""
        self.normalize_requested.emit(self.path_edit.text())

class SettingsDialog(QDialog):
    """A dialog for application settings."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)

        self.main_window = parent
        self._criware_path = self.main_window.criware_folder_path # Store path during dialog session

        layout = QVBoxLayout(self)

        # --- CriWare Folder Selection ---
        criware_group = QGroupBox("Global CriWare Folder")
        group_layout = QVBoxLayout(criware_group)
        layout.addWidget(criware_group)

        self.path_label = QLabel()
        self._update_path_label()
        self.path_label.setWordWrap(True)
        group_layout.addWidget(self.path_label)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        select_button = QPushButton("Select Folder...")
        select_button.clicked.connect(self.select_folder)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.clear_path)
        button_layout.addWidget(select_button)
        button_layout.addWidget(clear_button)
        group_layout.addLayout(button_layout)

        # --- Dialog Buttons (OK/Cancel) ---
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _update_path_label(self):
        if self._criware_path:
            self.path_label.setText(f"<b>Current Path:</b> {self._criware_path}")
        else:
            self.path_label.setText("<i>No folder selected. The app will ask for each .acb file individually.</i>")

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select CriWare Folder")
        if folder_path:
            self._criware_path = Path(folder_path)
            self._update_path_label()

    def clear_path(self):
        self._criware_path = None
        self._update_path_label()