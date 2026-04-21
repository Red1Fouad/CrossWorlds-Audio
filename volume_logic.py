import os
import sys
import wave
import numpy as np
import struct
from pathlib import Path
import math
import subprocess
import json

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True

    # Explicitly set the path to ffmpeg.exe from the tools directory.
    # This makes the app more portable and less reliant on system PATH.
    if sys.platform.startswith("linux"):
        # On Linux, try local binary first, otherwise assume system ffmpeg (pydub default)
        ffmpeg_path = Path("tools/ffmpeg").resolve()
        if ffmpeg_path.exists():
            AudioSegment.converter = str(ffmpeg_path)
            print(f"pydub: Successfully set ffmpeg path to {ffmpeg_path}")
    else:
        ffmpeg_path = Path("tools/ffmpeg.exe").resolve()
        if ffmpeg_path.exists():
            AudioSegment.converter = str(ffmpeg_path)
            print(f"pydub: Successfully set ffmpeg path to {ffmpeg_path}")
        else:
            print(f"pydub Warning: ffmpeg.exe not found at '{ffmpeg_path}'. Conversion of non-WAV files may fail.")

except ImportError:
    PYDUB_AVAILABLE = False
    print("Warning: pydub is not installed. Volume normalization will be limited to WAV files. Install with 'pip install pydub'")

def read_wav_chunks(file):
    with open(file, 'rb') as f:
        data = f.read()
    riff = data[:4].decode('ascii')
    if riff != 'RIFF':
        raise ValueError("Not a valid RIFF file")
    file_size = struct.unpack('<I', data[4:8])[0]
    wave_header = data[8:12].decode('ascii')
    if wave_header != 'WAVE':
        raise ValueError("Not a valid WAV file")

    pos = 12
    chunks = {}

    while pos + 8 <= len(data):
        chunk_id = data[pos:pos+4].decode('ascii', errors="replace")
        chunk_size = struct.unpack('<I', data[pos+4:pos+8])[0]
        start = pos + 8
        end = start + chunk_size
        if end > len(data):
            break
        chunk_data = data[start:end]
        chunks[chunk_id] = chunk_data
        pos = end
        if chunk_size % 2 == 1:
            pos += 1
    return chunks, file_size

def write_wav_chunks(chunks, output_file, original_size):
    with open(output_file, 'wb') as f:
        f.write(b'RIFF')
        f.write(struct.pack('<I', original_size))
        f.write(b'WAVE')
        for chunk_id, chunk_data in chunks.items():
            f.write(chunk_id.encode('ascii'))
            f.write(struct.pack('<I', len(chunk_data)))
            f.write(chunk_data)

def calculate_rms(audio_data):
    """Calculates the Root Mean Square of the audio data."""
    return np.sqrt(np.mean(np.square(audio_data), dtype=np.float64))

def get_audio_pcm(file_path):
    """Load any audio file using pydub and return raw PCM int16 numpy array."""
    if not PYDUB_AVAILABLE:
        raise ImportError("pydub is required for normalizing non-WAV files.")
    
    audio = AudioSegment.from_file(file_path)
    # Convert to mono for consistent RMS measurement
    audio = audio.set_channels(1)
    # Resample to a common rate if needed, though RMS is less sensitive to this
    audio = audio.set_frame_rate(44100)

    raw = np.array(audio.get_array_of_samples()).astype(np.int16)
    return raw.astype(np.float32)

def normalize_audio_file(source_path_str, reference_path_str, output_path_str):
    """
    Normalizes the source audio file to EBU R128 standards (-10.4 LUFS) using FFmpeg.
    The reference_path_str argument is kept for compatibility but is no longer used.
    """
    source_path = Path(source_path_str)
    output_path = Path(output_path_str)

    # 1. Resolve FFmpeg path
    ffmpeg_path = "ffmpeg"
    if sys.platform.startswith("linux"):
        local_ffmpeg = Path("tools/ffmpeg").resolve()
    else:
        local_ffmpeg = Path("tools/ffmpeg.exe").resolve()
    
    if local_ffmpeg.exists():
        ffmpeg_path = str(local_ffmpeg)

    # Normalization Targets
    TARGET_LUFS = -10.4
    TARGET_TP = -0.3
    TARGET_LRA = 11

    creation_flags = 0x08000000 if sys.platform == "win32" else 0

    try:
        # Pass 1: Analysis
        # We use resolve() to ensure paths are absolute and properly handled by the OS/Subprocess
        analyze_cmd = [
            ffmpeg_path, "-y", "-i", str(source_path.resolve()),
            "-af", f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}:print_format=json",
            "-f", "null", "-"
        ]
        
        result = subprocess.run(analyze_cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', creationflags=creation_flags)
        
        # Extract JSON from ffmpeg output (contained in stderr)
        output = result.stderr
        start = output.find("{")
        end = output.rfind("}") + 1
        if start == -1 or end == 0:
            raise ValueError("FFmpeg could not analyze the audio file. It might be corrupted or in an unsupported format.")
            
        json_str = output[start:end]
        stats = json.loads(json_str)
        
        # Pass 2: Normalization
        normalize_cmd = [
            ffmpeg_path, "-y", "-i", str(source_path.resolve()),
            "-af", (
                f"loudnorm=I={TARGET_LUFS}:TP={TARGET_TP}:LRA={TARGET_LRA}:"
                f"measured_I={stats['input_i']}:"
                f"measured_LRA={stats['input_lra']}:"
                f"measured_TP={stats['input_tp']}:"
                f"measured_thresh={stats['input_thresh']}:"
                f"offset={stats['target_offset']}:"
                f"linear=true"
            ),
            "-ar", "44100",
            str(output_path.resolve())
        ]
        
        subprocess.run(normalize_cmd, check=True, capture_output=True, creationflags=creation_flags)
        print(f"Normalized '{source_path.name}' using EBU R128 two-pass (-10.4 LUFS).")

    except (ValueError, json.JSONDecodeError, KeyError, subprocess.CalledProcessError) as e:
        print(f"Normalization failed for {source_path.name}: {e}")
        # Propagate error so the UI can notify the user
        raise RuntimeError(f"FFmpeg normalization failed: {e}") from e