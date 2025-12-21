import sys
import struct
from pathlib import Path

try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit,
                                   QPushButton, QFileDialog, QMessageBox, QTreeWidget, QTreeWidgetItem, QScrollArea,
                                   QFrame, QMenuBar, QStatusBar, QTabWidget, QGridLayout, QSizePolicy, QDialog,
                                   QDialogButtonBox, QCheckBox, QSlider, QStyleOptionSlider, QStyle, QProgressBar)
    from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer, QSize, QRect
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

class LoopSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.loop_start = 0
        self.loop_end = 0
        self.looping_enabled = False

    def set_loop_points(self, start, end):
        self.loop_start = start
        self.loop_end = end
        self.update()

    def set_looping_enabled(self, enabled):
        self.looping_enabled = enabled
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.looping_enabled or self.maximum() <= 0:
            return

        painter = QPainter(self)
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        
        style = self.style()
        groove_rect = style.subControlRect(QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderGroove, self)
        
        if self.orientation() == Qt.Orientation.Horizontal:
            span = self.maximum() - self.minimum()
            if span > 0:
                w = groove_rect.width()
                x_start = groove_rect.left() + int((self.loop_start - self.minimum()) / span * w)
                x_end = groove_rect.left() + int((self.loop_end - self.minimum()) / span * w)
                
                x_start = max(groove_rect.left(), min(x_start, groove_rect.right()))
                x_end = max(groove_rect.left(), min(x_end, groove_rect.right()))
                
                if x_end > x_start:
                    highlight_rect = QRect(x_start, groove_rect.top(), x_end - x_start, groove_rect.height())
                    painter.fillRect(highlight_rect, QColor(0, 255, 0, 100))
        
        painter.end()

class TrackEditorWidget(QFrame):
    """A collapsible widget for editing a single track's replacement file and loop points."""
    play_requested = Signal(object)  # Signal that this widget wants to play audio
    normalize_requested = Signal(str) # Signal that this widget wants to normalize audio
    autoloop_requested = Signal(object, str) # Signal with self and path

    def __init__(self, label_text, show_loop_options=True, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("TrackEditorWidget")
        self.original_label_text = label_text

        # --- Data Storage ---
        self.path_edit = None
        self.loop_checkbox = None
        self.loop_start_edit = None
        self.loop_end_edit = None
        self._last_filepath = None # To prevent re-scanning the same file
        self._sample_rate = 0 # For loop point conversion
        self.playback_mode = None # 'normal' or 'loop'
        self._manual_stop = False
        self.loop_timer = None

        # --- Audio Playback ---
        self.player = None
        self.audio_output = None

        # --- Main Layout ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header (Clickable to collapse) ---
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderFrame")
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(8, 5, 8, 5)

        self.play_button = QPushButton("▶")
        self.play_button.setFixedSize(22, 22)
        self.play_button.setToolTip("Preview Audio")
        self.play_button.setEnabled(False)
        
        # New Loop Preview Button
        self.loop_preview_button = QPushButton("Loop")
        self.loop_preview_button.setFixedSize(40, 22)
        self.loop_preview_button.setToolTip("Preview Loop Points")
        self.loop_preview_button.setEnabled(False)
        self.loop_preview_button.setVisible(show_loop_options)

        if MULTIMEDIA_AVAILABLE:
            self.play_button.clicked.connect(self.toggle_playback)
            self.loop_preview_button.clicked.connect(self.toggle_loop_preview)
        else:
            self.play_button.setVisible(False)
            self.loop_preview_button.setVisible(False)
        self.title_label = QLabel(f"<b>{label_text}</b>")
        self.status_label = QLabel("<i>No file selected</i>")
        self.status_label.setObjectName("StatusLabel")

        header_layout.addWidget(self.play_button)
        header_layout.addWidget(self.loop_preview_button)
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

        # Playback Slider and Time Label
        playback_layout = QHBoxLayout()
        playback_layout.setSpacing(10)

        self.playback_slider = LoopSlider(Qt.Orientation.Horizontal)
        self.playback_slider.setEnabled(False)

        self.time_label = QLabel("--:-- / --:--")
        self.time_label.setFixedWidth(90)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.setToolTip("Volume")

        if MULTIMEDIA_AVAILABLE:
            self.playback_slider.valueChanged.connect(self.set_position)
            self.volume_slider.valueChanged.connect(self.set_volume)
            playback_layout.addWidget(self.playback_slider)
            playback_layout.addWidget(self.time_label)
            playback_layout.addWidget(self.volume_slider)
        else:
            self.playback_slider.setVisible(False)
            self.time_label.setVisible(False)
            self.volume_slider.setVisible(False)
        content_layout.addLayout(playback_layout)

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

        self.autoloop_button = QPushButton("Auto-Loop")
        self.autoloop_button.setToolTip("Automatically finds the best loop points for this audio file.\nRequires 'pymusiclooper' to be installed.")
        self.autoloop_button.clicked.connect(self.emit_autoloop_request)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self._browse_for_file)
        browse_layout.addWidget(self.path_edit)
        browse_layout.addWidget(clear_button)
        browse_layout.addWidget(self.normalize_button)
        browse_layout.addWidget(self.autoloop_button)
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
        else:
            self.autoloop_button.setVisible(False)

        self.autoloop_progress = QProgressBar()
        self.autoloop_progress.setVisible(False)
        self.autoloop_progress.setTextVisible(False)
        content_layout.addWidget(self.autoloop_progress)

        # --- Styling & Connections ---
        self.content_frame.setVisible(True) # Always visible

        if MULTIMEDIA_AVAILABLE:
            self._init_player()

        self._update_status()

    def _format_time(self, ms):
        """Formats milliseconds into MM:SS."""
        if ms <= 0:
            return "00:00"
        
        seconds = int((ms / 1000) % 60)
        minutes = int((ms / (1000 * 60)) % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _toggle_loop_edits_enabled(self, checked):
        """Enables or disables the loop point input fields based on the checkbox state."""
        if self.loop_start_edit and self.loop_end_edit:
            self.loop_start_edit.setEnabled(checked)
            self.loop_end_edit.setEnabled(checked)

    def _browse_for_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.wav *.mp3 *.flac *.ogg *.m4a);;All files (*.*)")
        if filepath:
            self.path_edit.setText(filepath)

    def _try_load_loop_points(self, filepath):
        """Attempts to read loop points from the WAV 'smpl' chunk."""
        try:
            with open(filepath, 'rb') as f:
                header = f.read(12)
                if header[:4] != b'RIFF' or header[8:] != b'WAVE':
                    return

                while True:
                    chunk_header = f.read(8)
                    if len(chunk_header) < 8: break
                    
                    chunk_id = chunk_header[:4]
                    chunk_size = struct.unpack('<I', chunk_header[4:])[0]
                    
                    if chunk_id == b'smpl':
                        # Read smpl chunk body
                        smpl_data = f.read(chunk_size)
                        # We need at least 36 bytes to reach the loop list
                        # Offset 28 (4 bytes): Num Sample Loops
                        # Offset 36 (start of loops): Cue Point ID (4), Type (4), Start (4), End (4)...
                        if len(smpl_data) >= 48: # 36 header + 12 bytes into first loop to get start/end
                            num_loops = struct.unpack('<I', smpl_data[28:32])[0]
                            if num_loops > 0:
                                # Read first loop (offsets are relative to the start of smpl_data)
                                # Loop struct starts at 36. 
                                # Start is at 36+8=44, End is at 36+12=48
                                loop_start = struct.unpack('<I', smpl_data[44:48])[0]
                                loop_end = struct.unpack('<I', smpl_data[48:52])[0]
                                
                                self.loop_checkbox.setChecked(True)
                                self.loop_start_edit.setText(str(loop_start))
                                self.loop_end_edit.setText(str(loop_end))
                                print(f"Auto-detected loop points for {Path(filepath).name}: {loop_start}-{loop_end}")
                        return # Found smpl, stop scanning
                    else:
                        f.seek(chunk_size, 1) # Skip chunk
                        if chunk_size % 2 == 1: f.seek(1, 1) # Handle padding
        except Exception as e:
            print(f"Could not read loop points: {e}")

    def _update_status(self):
        filepath = self.path_edit.text()
        if filepath:
            filename = Path(filepath).name
            self.status_label.setText(f"<b>{filename}</b>")
            self.header_frame.setProperty("hasFile", True)
        else:
            self.status_label.setText("<i>No file selected</i>")
            self.header_frame.setProperty("hasFile", False)
            self._sample_rate = 0
            if MULTIMEDIA_AVAILABLE:
                self.playback_slider.setEnabled(False)
                self.playback_slider.setValue(0)
                self.time_label.setText("--:-- / --:--")

        # Re-polish to apply style changes
        self.header_frame.style().unpolish(self.header_frame)
        self.header_frame.style().polish(self.header_frame)

        # Enable/disable play button
        if MULTIMEDIA_AVAILABLE:
            has_text = bool(filepath)
            is_audio = False
            if has_text:
                try:
                    is_audio = Path(filepath).exists() and Path(filepath).suffix.lower() in ['.wav', '.mp3', '.flac', '.ogg', '.m4a', '.brstm']
                except Exception:
                    is_audio = False # Handle invalid path characters during typing

            self.normalize_button.setEnabled(is_audio)
            self.autoloop_button.setEnabled(is_audio)
            self.play_button.setEnabled(is_audio)
            self.playback_slider.setEnabled(is_audio)
            if self.loop_checkbox:
                self.loop_preview_button.setEnabled(is_audio)

            if not has_text:
                self.stop_playback() # Stop playing if text is cleared

        # Auto-detect loop points and get sample rate if it's a new valid file
        if filepath and Path(filepath).exists() and filepath != self._last_filepath:
            self._last_filepath = filepath
            
            # Get sample rate for loop conversion
            if MULTIMEDIA_AVAILABLE:
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(filepath)
                    self._sample_rate = audio.frame_rate
                except Exception as e:
                    print(f"Could not get sample rate for {filepath}: {e}")
                    self._sample_rate = 0

            if self.loop_checkbox and Path(filepath).suffix.lower() == '.wav':
                self._try_load_loop_points(filepath)
        elif not filepath:
            self._last_filepath = None

    def emit_autoloop_request(self):
        """Emits the autoloop_requested signal with self and the current file path."""
        self.autoloop_requested.emit(self, self.path_edit.text())

    def on_autoloop_started(self):
        """Called when the auto-loop process begins."""
        self.autoloop_progress.setRange(0, 0)
        self.autoloop_progress.setVisible(True)
        self.play_button.setEnabled(False)
        self.loop_preview_button.setEnabled(False)
        self.normalize_button.setEnabled(False)
        self.autoloop_button.setEnabled(False)

    def on_autoloop_finished(self, loop_points):
        """Called when the auto-loop process finishes."""
        self.autoloop_progress.setVisible(False)
        self._update_status() # This will re-evaluate and set button states

        if loop_points and self.loop_checkbox:
            best_loop = loop_points[0]
            loop_start, loop_end = best_loop[0], best_loop[1]
            self.loop_checkbox.setChecked(True)
            self.loop_start_edit.setText(str(loop_start))
            self.loop_end_edit.setText(str(loop_end))

    def _init_player(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.player.playbackStateChanged.connect(self._on_playback_state_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)

        # Set initial volume
        self.audio_output.setVolume(self.volume_slider.value() / 100.0)
        
        self.loop_timer = QTimer(self)
        self.loop_timer.setInterval(10) # High frequency check for smoother looping
        self.loop_timer.timeout.connect(self._check_loop)

    def toggle_playback(self):
        if not self.player: return

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.stop_playback()
        else:
            self.play_requested.emit(self)
            filepath = self.path_edit.text()
            if filepath and Path(filepath).exists():
                self.playback_mode = 'normal'
                self.player.setSource(QUrl.fromLocalFile(filepath))
                self.player.play()

    def toggle_loop_preview(self):
        if not self.player: return

        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.stop_playback()
        else:
            # Validate loop points before starting
            try:
                start_sample = int(self.loop_start_edit.text())
                end_sample = int(self.loop_end_edit.text())
                if start_sample < 0 or end_sample <= start_sample:
                    if end_sample <= start_sample:
                        QMessageBox.warning(self, "Invalid Loop Points", "Loop End must be greater than Loop Start.")
                        return
                    raise ValueError("Loop points are invalid.")
            except ValueError:
                QMessageBox.warning(self, "Invalid Loop Points", "Please enter valid, positive integer values for loop start and end points.")
                return

            self.play_requested.emit(self)
            filepath = self.path_edit.text()
            if filepath and Path(filepath).exists():
                self.playback_mode = 'loop'
                self._manual_stop = False
                
                # Update slider visualization
                try:
                    start_samples = int(self.loop_start_edit.text())
                    end_samples = int(self.loop_end_edit.text())
                    start_ms = int((start_samples / self._sample_rate) * 1000)
                    end_ms = int((end_samples / self._sample_rate) * 1000)
                    self.playback_slider.set_loop_points(start_ms, end_ms)
                    self.playback_slider.set_looping_enabled(True)
                except (ValueError, ZeroDivisionError):
                    pass

                self.player.setSource(QUrl.fromLocalFile(filepath))
                self.player.play()
                self.loop_timer.start()

    def stop_playback(self):
        self._manual_stop = True
        if self.loop_timer:
            self.loop_timer.stop()
        if self.player and self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self.player.stop()
        self.playback_mode = None
        if self.playback_slider:
            self.playback_slider.set_looping_enabled(False)

    def _on_playback_state_changed(self, state):
        is_playing = state == QMediaPlayer.PlaybackState.PlayingState
        
        if is_playing:
            if self.playback_mode == 'loop':
                self.loop_preview_button.setText("■")
                self.loop_preview_button.setToolTip("Stop Preview")
                self.play_button.setEnabled(False)
            else: # normal playback
                self.play_button.setText("■")
                self.play_button.setToolTip("Stop Preview")
                if self.loop_preview_button:
                    self.loop_preview_button.setEnabled(False)
        else: # Stopped or Paused
            # Check if we hit the end of the file while in loop mode
            if self.playback_mode == 'loop' and not self._manual_stop:
                try:
                    start_samples = int(self.loop_start_edit.text())
                    if self._sample_rate > 0:
                        start_ms = int((start_samples / self._sample_rate) * 1000)
                        self.player.setPosition(start_ms)
                        self.player.play()
                        return
                except Exception:
                    pass

            self.play_button.setText("▶") # Play symbol
            self.play_button.setToolTip("Preview Audio")
            self.play_button.setEnabled(True)
            if self.loop_preview_button:
                self.loop_preview_button.setText("Loop")
                self.loop_preview_button.setToolTip("Preview Loop Points")
                self.loop_preview_button.setEnabled(True)
            self.playback_mode = None # Reset mode on stop

    def _check_loop(self):
        """Called by timer to check loop condition with higher frequency."""
        if self.playback_mode == 'loop' and self._sample_rate > 0 and self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            try:
                position = self.player.position()
                start_samples = int(self.loop_start_edit.text())
                end_samples = int(self.loop_end_edit.text())
                
                start_ms = int((start_samples / self._sample_rate) * 1000)
                end_ms = int((end_samples / self._sample_rate) * 1000)

                if position >= end_ms:
                    seek_pos = start_ms
                    # Compensate for timer granularity to keep rhythm smooth
                    overshoot = position - end_ms
                    if 0 < overshoot < 200: 
                        seek_pos += overshoot
                    if seek_pos >= end_ms: seek_pos = start_ms 
                    self.player.setPosition(seek_pos)
            except (ValueError, ZeroDivisionError) as e:
                print(f"Error during loop check: {e}")
                self.stop_playback()

    def position_changed(self, position):
        # Update slider
        self.playback_slider.blockSignals(True)
        self.playback_slider.setValue(position)
        self.playback_slider.blockSignals(False)

        # Update time label
        duration = self.player.duration()
        self.time_label.setText(f"{self._format_time(position)} / {self._format_time(duration)}")

    def duration_changed(self, duration):
        self.playback_slider.setRange(0, duration)
        position = self.player.position()
        self.time_label.setText(f"{self._format_time(position)} / {self._format_time(duration)}")

    def set_position(self, position):
        # This check is important to prevent seeking when the player itself updates the slider's position
        if self.player and self.player.position() != position:
            self.player.setPosition(position)

    def set_volume(self, volume):
        """Sets the player volume."""
        if self.audio_output:
            self.audio_output.setVolume(volume / 100.0)

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