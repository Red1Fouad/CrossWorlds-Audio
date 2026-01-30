import os
import sys
import subprocess
import shlex
import shutil
from pathlib import Path

class ModLogic:
    def __init__(self, tools_dir, output_dir):
        self.TOOLS_DIR = Path(tools_dir)
        self.OUTPUT_DIR = Path(output_dir)
        self.IS_LINUX = sys.platform.startswith("linux")
        
        self.ACB_EDITOR = self.TOOLS_DIR / "AcbEditor.exe"
        self.CONVERT_BAT = self.TOOLS_DIR / "Convert2UNION.bat"
        self.UNREAL_PAK = self.TOOLS_DIR / "UnrealPak.bat"
        
        if self.IS_LINUX:
            # On Linux, check for local ffmpeg binary, otherwise assume system 'ffmpeg'
            if (self.TOOLS_DIR / "ffmpeg").exists():
                self.FFMPEG = self.TOOLS_DIR / "ffmpeg"
            else:
                self.FFMPEG = Path("ffmpeg")
        else:
            self.FFMPEG = self.TOOLS_DIR / "ffmpeg.exe"

    def _to_wine_path(self, path):
        """Converts a Linux path to a Windows path for Wine."""
        if not self.IS_LINUX:
            return str(path)
        try:
            return subprocess.check_output(["winepath", "-w", str(path)]).decode().strip()
        except Exception:
            return str(path)

    def _execute_command(self, command, shell, cwd):
        """The actual command execution logic for the thread."""
        try:
            if self.IS_LINUX:
                cmd_path = Path(command[0])
                # If running a Windows executable or batch file on Linux, use Wine
                if cmd_path.suffix.lower() == ".exe":
                    command = ["wine"] + [str(c) for c in command]
                    shell = False
                elif cmd_path.suffix.lower() == ".bat":
                    # Convert arguments to Wine paths
                    wine_args = [self._to_wine_path(arg) for arg in command[1:]]
                    command = ["wine", "cmd", "/c", str(command[0])] + wine_args
                    shell = False

            if not shell:
                creation_flags = 0x08000000 if sys.platform == "win32" else 0 # CREATE_NO_WINDOW
                subprocess.run(command, check=True, cwd=cwd, creationflags=creation_flags)
                return "Process completed."
            else:
                subprocess.run(command, shell=True, check=True, cwd=cwd)
                return "Process completed."
        except FileNotFoundError:
            raise FileNotFoundError(f"Command not found: {command[0]}")
        except subprocess.CalledProcessError as e:
            error_message = f"An error occurred while running:\n{' '.join(command)}\n\nThe tool may have failed. Exit code: {e.returncode}"
            raise RuntimeError(error_message) from e

    def unpack_acb(self, acb_path):
        unpacked_path = Path(acb_path).parent / Path(acb_path).stem
        self._execute_command([str(self.ACB_EDITOR), str(acb_path)], False, cwd=None)
        return str(unpacked_path)

    def _get_vgaudiocli_command(self, acb_name):
        """Parses Convert2UNION.bat to find the correct VGAudioCli command line."""
        with open(self.CONVERT_BAT, 'r') as f:
            lines = f.readlines()

        command_line = None
        target_label = f":option-{acb_name}"
        for i, line in enumerate(lines):
            if line.strip().lower() == target_label.lower():
                if i + 1 < len(lines):
                    command_line = lines[i+1].strip()
                    break
        
        if not command_line or not command_line.lower().startswith("vgaudiocli.exe"):
            raise ValueError(f"Could not find a valid VGAudioCli command for '{acb_name}' in '{self.CONVERT_BAT}'.")
        
        return command_line

    def _run_conversion_tasks(self, tasks, base_command_line, cwd, progress_callback=None):
        """The actual conversion logic that runs in a thread."""
        temp_input_dir = Path(cwd) / "input"
        temp_output_dir = Path(cwd) / "output"
        total_tasks = len(tasks)

        for i, (name, wav_path_str, has_loop, loop_start, loop_end, gain_db) in enumerate(tasks):
            if progress_callback: progress_callback(i, total_tasks, f"Converting {name}...")
            wav_path = Path(wav_path_str)
            print(f"Converting '{wav_path.name}' for {name}...")

            if temp_input_dir.exists(): shutil.rmtree(temp_input_dir)
            if temp_output_dir.exists(): shutil.rmtree(temp_output_dir)
            os.makedirs(temp_input_dir)
            os.makedirs(temp_output_dir)
            
            temp_wav_path = temp_input_dir / Path(name).with_suffix('.wav').name

            # If the input is not a WAV file OR if we need to apply gain, use ffmpeg.
            needs_ffmpeg = wav_path.suffix.lower() != '.wav' or gain_db != 0.0

            if needs_ffmpeg:
                print(f"  - Processing '{wav_path.name}' with ffmpeg (Gain: {gain_db}dB)...")
                ffmpeg_cmd = [str(self.FFMPEG), '-y', '-i', str(wav_path)]
                if gain_db != 0.0:
                    ffmpeg_cmd.extend(['-filter:a', f'volume={gain_db}dB'])
                ffmpeg_cmd.append(str(temp_wav_path))
                # Use creationflags to hide window
                subprocess.run(ffmpeg_cmd, check=True, capture_output=True, creationflags=0x08000000 if sys.platform == "win32" else 0)
            else:
                shutil.copy2(wav_path, temp_wav_path)

            command_parts = shlex.split(base_command_line)

            if has_loop:
                start, end = loop_start.strip(), loop_end.strip()
                if start and end:
                    command_parts.extend(['-l', f'{start}-{end}'])
                    print(f"  - with loop points: {start}-{end}")
            
            vgaudio_cli_path = Path(cwd) / command_parts[0]
            command_parts[0] = str(vgaudio_cli_path)
            
            if self.IS_LINUX and vgaudio_cli_path.suffix.lower() == ".exe":
                command_parts = ["wine"] + command_parts

            print(f"  - Command: {' '.join(shlex.quote(p) for p in command_parts)}")
            # Use creationflags to hide window
            subprocess.run(command_parts, check=True, cwd=cwd, creationflags=0x08000000 if sys.platform == "win32" else 0)

            converted_files = list(temp_output_dir.glob('*'))
            if converted_files:
                shutil.move(str(converted_files[0]), str(self.OUTPUT_DIR / f"{name}.hca"))

        if temp_input_dir.exists(): shutil.rmtree(temp_input_dir)
        if temp_output_dir.exists(): shutil.rmtree(temp_output_dir)

    def convert_audio(self, acb_path, tasks, progress_callback=None):
        acb_name = Path(acb_path).stem
        
        if self.OUTPUT_DIR.exists():
            shutil.rmtree(self.OUTPUT_DIR)
        os.makedirs(self.OUTPUT_DIR)
        command_line = self._get_vgaudiocli_command(acb_name)
        self._run_conversion_tasks(tasks, command_line, str(self.TOOLS_DIR), progress_callback)

    def repack_acb(self, unpacked_path):
        self._execute_command([str(self.ACB_EDITOR), str(unpacked_path)], False, cwd=None)

    def create_pak(self, mod_name, acb_file_path):
        mod_root_folder = Path(mod_name)
        criware_folder = mod_root_folder / "UNION" / "Content" / "CriWareData"

        os.makedirs(criware_folder, exist_ok=True)

        acb_path = Path(acb_file_path)
        print(f"Copying '{acb_path.name}' to mod folder...")
        shutil.copy2(acb_path, criware_folder)

        awb_file = acb_path.with_suffix('.awb')
        if awb_file.exists():
            print(f"Copying '{awb_file.name}' to mod folder...")
            shutil.copy2(awb_file, criware_folder)

        self._execute_command([str(self.UNREAL_PAK), str(mod_root_folder.resolve())], True, cwd=None)

    def apply_replacements(self, unpacked_path, replacement_map):
        if not replacement_map:
            return 0

        for original_file, new_file in replacement_map.items():
            source_path = self.OUTPUT_DIR / new_file
            dest_path = Path(unpacked_path) / original_file
            if not source_path.exists():
                raise FileNotFoundError(f"Could not find replacement file: {source_path}")
            print(f"Copying '{source_path}' to '{dest_path}'...")
            shutil.copy2(source_path, dest_path)
        
        return len(replacement_map)

    def check_tools(self):
        """Checks if all required tools exist."""
        missing_tools = []
        for tool in [self.ACB_EDITOR, self.CONVERT_BAT, self.UNREAL_PAK, self.FFMPEG]:
            # Skip check for system ffmpeg on Linux
            if self.IS_LINUX and str(tool) == "ffmpeg":
                continue
            if not tool.exists():
                missing_tools.append(str(tool))
        return missing_tools