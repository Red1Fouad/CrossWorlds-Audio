import os
import subprocess
import shlex
import shutil
from pathlib import Path

class ModLogic:
    def __init__(self, tools_dir, output_dir):
        self.TOOLS_DIR = Path(tools_dir)
        self.OUTPUT_DIR = Path(output_dir)
        self.ACB_EDITOR = self.TOOLS_DIR / "AcbEditor.exe"
        self.CONVERT_BAT = self.TOOLS_DIR / "Convert2UNION.bat"
        self.FFMPEG = self.TOOLS_DIR / "ffmpeg.exe"
        self.UNREAL_PAK = self.TOOLS_DIR / "UnrealPak.bat"

    def _execute_command(self, command, shell, cwd):
        """The actual command execution logic for the thread."""
        try:
            if not shell:
                creation_flags = 0
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

    def _run_conversion_tasks(self, tasks, base_command_line, cwd):
        """The actual conversion logic that runs in a thread."""
        temp_input_dir = Path(cwd) / "input"
        temp_output_dir = Path(cwd) / "output"

        for name, wav_path_str, has_loop, loop_start, loop_end in tasks:
            wav_path = Path(wav_path_str)
            print(f"Converting '{wav_path.name}' for {name}...")

            if temp_input_dir.exists(): shutil.rmtree(temp_input_dir)
            if temp_output_dir.exists(): shutil.rmtree(temp_output_dir)
            os.makedirs(temp_input_dir)
            os.makedirs(temp_output_dir)

            # If the input is not a WAV file, convert it to a temporary WAV using ffmpeg.
            # Otherwise, just copy it.
            if wav_path.suffix.lower() != '.wav':
                print(f"  - '{wav_path.name}' is not a WAV file. Converting with ffmpeg...")
                temp_wav_path = temp_input_dir / wav_path.with_suffix('.wav').name
                ffmpeg_cmd = [str(self.FFMPEG), '-i', str(wav_path), str(temp_wav_path)]
                subprocess.run(ffmpeg_cmd, check=True, capture_output=True) # Capture output to hide ffmpeg info
            else:
                temp_wav_path = temp_input_dir / Path(name).with_suffix('.wav').name
                shutil.copy2(wav_path, temp_wav_path)

            command_parts = shlex.split(base_command_line)

            if has_loop:
                start, end = loop_start.strip(), loop_end.strip()
                if start and end:
                    command_parts.extend(['-l', f'{start}-{end}'])
                    print(f"  - with loop points: {start}-{end}")
            
            vgaudio_cli_path = Path(cwd) / command_parts[0]
            command_parts[0] = str(vgaudio_cli_path)
            
            print(f"  - Command: {' '.join(shlex.quote(p) for p in command_parts)}")
            subprocess.run(command_parts, check=True, cwd=cwd)

            converted_files = list(temp_output_dir.glob('*'))
            if converted_files:
                shutil.move(str(converted_files[0]), str(self.OUTPUT_DIR / f"{name}.hca"))

        if temp_input_dir.exists(): shutil.rmtree(temp_input_dir)
        if temp_output_dir.exists(): shutil.rmtree(temp_output_dir)

    def convert_audio(self, acb_path, tasks):
        acb_name = Path(acb_path).stem
        
        if self.OUTPUT_DIR.exists():
            shutil.rmtree(self.OUTPUT_DIR)
        os.makedirs(self.OUTPUT_DIR)
        command_line = self._get_vgaudiocli_command(acb_name)
        self._run_conversion_tasks(tasks, command_line, str(self.TOOLS_DIR))

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
            if not tool.exists():
                missing_tools.append(str(tool))
        return missing_tools