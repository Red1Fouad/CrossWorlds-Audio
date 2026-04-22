import os
import sys
import subprocess
import shlex
import shutil
from pathlib import Path
import xml.etree.ElementTree as ET
import re

class ModLogic:
    def __init__(self, tools_dir, output_dir):
        self.TOOLS_DIR = Path(tools_dir)
        self.OUTPUT_DIR = Path(output_dir)
        self.IS_LINUX = sys.platform.startswith("linux")
        
        self.ACB_EDITOR = self.TOOLS_DIR / "AcbEditor.exe"
        self.CONVERT_BAT = self.TOOLS_DIR / "Convert2UNION.bat"
        self.UNREAL_PAK = self.TOOLS_DIR / "UnrealPak.bat"
        self.CRI_UTF_TOOL = self.TOOLS_DIR / "KwasTools" / "cri_utf_tool.exe"
        
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
            stripped = line.strip().lower()
            if stripped == target_label.lower():
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

    def repack_acb_kwastools(self, original_acb_path, replacement_map, unpacked_folder_str):
        """
        Repacks the ACB using the KwasTools XML injection method.
        """
        original_acb = Path(original_acb_path)
        unpacked_folder = Path(unpacked_folder_str)
        
        # The output ACB should replace the one that AcbEditor would have created/modified.
        target_acb = unpacked_folder.parent / (unpacked_folder.name + ".acb")
        
        # Create a temp directory for work
        temp_dir = unpacked_folder.parent / "temp_kwastools"
        if temp_dir.exists(): shutil.rmtree(temp_dir)
        temp_dir.mkdir()
        
        try:
            # Copy original ACB to temp
            temp_acb = temp_dir / original_acb.name
            shutil.copy2(original_acb, temp_acb)
            
            # Copy original AWB to temp if it exists (Required for valid XML generation of existing tracks)
            original_awb = original_acb.with_suffix('.awb')
            if original_awb.exists():
                print(f"Copying original AWB for reference: {original_awb.name}")
                shutil.copy2(original_awb, temp_dir / original_awb.name)
            
            # Extract XML
            self._execute_command([str(self.CRI_UTF_TOOL), temp_acb.name], False, cwd=str(temp_dir))
            
            xml_file = temp_acb.with_suffix('.acb.xml')
            if not xml_file.exists():
                raise FileNotFoundError("Failed to extract XML from ACB.")
                
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Find StreamAwbTocWorkOld -> AWB
            awb_node = None
            for record in root.iter('record'):
                if record.get('name') == 'StreamAwbTocWorkOld':
                    awb_node = record.find('AWB')
                    break
            
            if awb_node is None:
                # Fallback: search for AWB anywhere
                awb_node = root.find('.//AWB')
            
            if awb_node is None:
                raise ValueError("Could not find <AWB> tag in ACB XML.")
                
            # --- MEMORIZE & PRUNE LOGIC ---
            entries = awb_node.findall('entry')
            count_file = original_acb.with_suffix('.kwas_orig_count')
            
            original_count = 0
            if not count_file.exists():
                original_count = len(entries)
                try:
                    with open(count_file, 'w') as f:
                        f.write(str(original_count))
                    print(f"Memorized original entry count: {original_count}")
                except Exception as e:
                    print(f"Warning: Could not save original count: {e}")
            else:
                try:
                    with open(count_file, 'r') as f:
                        original_count = int(f.read().strip())
                    print(f"Loaded original entry count: {original_count}")
                except Exception as e:
                    print(f"Warning: Could not read original count: {e}")
                    original_count = len(entries)

            # Prune entries beyond original_count
            if len(entries) > original_count:
                entries_to_remove = entries[original_count:]
                print(f"Pruning {len(entries_to_remove)} entries beyond original count...")
                for e in entries_to_remove:
                    awb_node.remove(e)
                
                # Note: We don't strictly need to revert rows here because any row pointing 
                # to a removed entry will either be updated by the new replacements below, 
                # or is effectively broken/reset (which is expected if we removed the track).

            # Determine new ID start
            existing_ids = [int(e.get('id')) for e in awb_node.findall('entry')]
            next_id = max(existing_ids) + 1 if existing_ids else 1000
            
            # Process replacements
            for orig_filename, new_filename in replacement_map.items():
                stem = Path(orig_filename).stem
                # Remove _streaming suffix if present
                if "_streaming" in stem:
                    stem = stem.replace("_streaming", "")
                
                # Try to extract number
                match = re.search(r'^(\d+)', stem)
                if not match:
                    print(f"Skipping {orig_filename}: filename does not start with an ID.")
                    continue
                
                track_id = int(match.group(1))
                new_file_abs_path = (self.OUTPUT_DIR / new_filename).resolve()
                
                # Add entry to AWB
                new_entry = ET.SubElement(awb_node, 'entry')
                new_entry.set('id', str(next_id))
                new_entry.set('path', str(new_file_abs_path).replace('\\', '/'))
                
                # Update row for this track_id
                for row in root.findall('.//row'):
                    recs = {r.get('name'): r for r in row.findall('record')}
                    if 'StreamAwbId' in recs and recs['StreamAwbId'].get('value') == str(track_id):
                        if 'MemoryAwbId' in recs:
                            recs['MemoryAwbId'].set('value', str(next_id))
                        if 'Streaming' in recs:
                            recs['Streaming'].set('value', '0')
                
                next_id += 1
                
            # Save XML and Repack
            tree.write(xml_file, encoding='utf-8', xml_declaration=False)
            self._execute_command([str(self.CRI_UTF_TOOL), xml_file.name], False, cwd=str(temp_dir))
            
            if target_acb.exists(): target_acb.unlink()
            shutil.copy2(temp_acb, target_acb)
            
        finally:
            if temp_dir.exists():
                try: shutil.rmtree(temp_dir)
                except: pass

    def create_pak(self, mod_name, acb_file_path, include_awb=True):
        mod_root_folder = Path(mod_name)
        criware_folder = mod_root_folder / "UNION" / "Content" / "CriWareData"

        os.makedirs(criware_folder, exist_ok=True)

        acb_path = Path(acb_file_path)
        print(f"Copying '{acb_path.name}' to mod folder...")
        shutil.copy2(acb_path, criware_folder)

        if include_awb:
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

    def create_ai_voice(self, original_acb_path, ai_voice_dir):
        """Creates an AI version of the voice ACB."""
        original_acb = Path(original_acb_path)
        stem = original_acb.stem # e.g. VOICE_EGP
        
        # Ensure output dir exists
        ai_dir = Path(ai_voice_dir)
        ai_dir.mkdir(parents=True, exist_ok=True)
        
        # Target paths
        target_acb = ai_dir / original_acb.name
        target_awb = ai_dir / original_acb.with_suffix('.awb').name
        
        # Copy files
        print(f"Copying {original_acb.name} to {ai_dir}...")
        shutil.copy2(original_acb, target_acb)
        os.chmod(target_acb, 0o777) # Ensure writable
        
        if original_acb.with_suffix('.awb').exists():
            shutil.copy2(original_acb.with_suffix('.awb'), target_awb)
            os.chmod(target_awb, 0o777)
            
        # Extract XML
        print(f"Extracting XML from {target_acb.name}...")
        self._execute_command([str(self.CRI_UTF_TOOL.resolve()), target_acb.name], False, cwd=str(ai_dir))
        
        xml_file = target_acb.with_suffix('.acb.xml')
        if not xml_file.exists():
            raise FileNotFoundError(f"Failed to extract XML: {xml_file}")
            
        # Edit XML
        parts = stem.split('_')
        if len(parts) >= 2:
            char_code = parts[1].lower()
            search_str = f"voice_{char_code}"
            replace_str = f"voice_{char_code}AI"
            
            print(f"Editing XML: Replacing '{search_str}' with '{replace_str}'...")
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content.replace(search_str, replace_str)
            
            with open(xml_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

        # Repack ACB from XML
        print(f"Repacking ACB from XML...")
        self._execute_command([str(self.CRI_UTF_TOOL.resolve()), xml_file.name], False, cwd=str(ai_dir))
        
        # Rename to *AI.acb/awb
        final_acb_path = ai_dir / f"{stem}AI.acb"
        final_awb_path = ai_dir / f"{stem}AI.awb"
        
        if target_acb.exists():
            if final_acb_path.exists(): final_acb_path.unlink()
            target_acb.rename(final_acb_path)
            
        if target_awb.exists():
            if final_awb_path.exists(): final_awb_path.unlink()
            target_awb.rename(final_awb_path)

        return str(final_acb_path)

    def check_tools(self):
        """Checks if all required tools exist."""
        missing_tools = []
        for tool in [self.ACB_EDITOR, self.CONVERT_BAT, self.UNREAL_PAK, self.FFMPEG, self.CRI_UTF_TOOL]:
            # Skip check for system ffmpeg on Linux
            if self.IS_LINUX and str(tool) == "ffmpeg":
                continue
            if not tool.exists():
                missing_tools.append(str(tool))
        return missing_tools