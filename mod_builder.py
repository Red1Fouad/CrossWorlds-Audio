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
        "2016": "White Cave", "2017": "Cyber Space", "2019": "Digital Circuit"
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
                filename = f"BGM_STG{id_num}.acb" if category != "Menu & System" else "BGM.acb"
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
        ttk.Entry(unpack_frame, textvariable=self.acb_file, state='readonly').grid(row=0, column=1, columnspan=3, sticky=tk.EW, padx=5)
        
        ttk.Button(unpack_frame, text="Select Common BGM...", command=self.select_common_bgm).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Button(unpack_frame, text="Browse Manually...", command=self.select_acb_manual).grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        self.unpack_button = ttk.Button(unpack_frame, text="Unpack", command=self.unpack_acb, state=tk.DISABLED)
        self.unpack_button.grid(row=1, column=3, sticky=tk.E, padx=5, pady=5)
        unpack_frame.columnconfigure(1, weight=1)

        # --- Step 2: Convert ---
        convert_outer_frame = ttk.LabelFrame(parent, text="Step 2: Convert Audio", padding="10")
        convert_outer_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create a canvas and a scrollbar for the scrollable area
        canvas = tk.Canvas(convert_outer_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(convert_outer_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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
            canvas.yview_scroll(delta, "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel) # Windows/macOS
        canvas.bind_all("<Button-4>", _on_mousewheel)   # Linux scroll up
        canvas.bind_all("<Button-5>", _on_mousewheel)   # Linux scroll down

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

        # Convert button is outside the scrollable area
        self.convert_button = ttk.Button(convert_outer_frame, text="Convert Selected Audio", command=self.convert_audio, state=tk.DISABLED)
        self.convert_button.pack(pady=10)

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
        self._toggle_loop_widgets(self.intro_widgets, self.intro_loops_var)
        self._toggle_loop_widgets(self.lap1_widgets, self.lap1_loops_var)
        self._toggle_loop_widgets(self.final_lap_widgets, self.final_lap_loops_var)
        for var_dict in self.menu_track_vars.values():
            var_dict['path'].set('')
            var_dict['loop'].set(False)
            # Loop widgets are toggled off during check_tools init

        self.repack_button.config(state=tk.DISABLED)
        self.pak_button.config(state=tk.DISABLED)

        # Show/hide widgets based on filename
        acb_path = Path(filepath)
        if acb_path.stem == "BGM":
            self.stage_music_frame.pack_forget()
            self.menu_music_frame.pack(fill=tk.X)
        else:
            self.menu_music_frame.pack_forget()
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

        if is_menu_bgm:
            for hca_name, var_dict in self.menu_track_vars.items():
                if var_dict['path'].get():
                    tasks.append((hca_name, var_dict['path'], var_dict['loop'], var_dict['start'], var_dict['end']))
        else:
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
        is_crossworlds = acb_stem.startswith("BGM_STG2")

        # Build the replacement map based on converted files
        if is_menu_bgm:
            for hca_name, var_dict in self.menu_track_vars.items():
                converted_file = OUTPUT_DIR / f"{hca_name}.hca"
                if converted_file.exists():
                    self.replacement_map[f"{hca_name}.hca"] = f"{hca_name}.hca"
        else:
            if len(self.original_files) < 5:
                messagebox.showerror("Error", "Cannot apply replacements: Not enough original files found in the unpacked folder.")
                return

            if (OUTPUT_DIR / "lap1.hca").exists():
                self.replacement_map[self.original_files[0]] = "lap1.hca" # Lap 1
                self.replacement_map[self.original_files[1]] = "lap1.hca" # Lap 1 intro
            if (OUTPUT_DIR / "final_lap.hca").exists():
                self.replacement_map[self.original_files[2]] = "final_lap.hca" # Final Lap
                self.replacement_map[self.original_files[3]] = "final_lap.hca" # Final Lap intro
            if not is_crossworlds and (OUTPUT_DIR / "intro.hca").exists():
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
if __name__ == "__main__":
    app = ModBuilderGUI()
    app.mainloop()
