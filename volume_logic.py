import os
import wave
import numpy as np
import struct
from pathlib import Path
import math

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True

    # Explicitly set the path to ffmpeg.exe from the tools directory.
    # This makes the app more portable and less reliant on system PATH.
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
    Normalizes the source audio file to match the RMS volume of the reference file.
    The output is always a WAV file.
    """
    source_path = Path(source_path_str)
    output_path = Path(output_path_str)

    # 1. Calculate target RMS from reference file
    reference_pcm = get_audio_pcm(reference_path_str)
    target_rms = calculate_rms(reference_pcm)
    if target_rms == 0:
        print(f"Warning: Reference file '{Path(reference_path_str).name}' is silent. Cannot normalize.")
        return

    # 2. Load source audio
    source_audio = AudioSegment.from_file(source_path)

    # 3. Get source PCM data for calculation
    # We can reuse the loaded source_audio to get samples, but get_audio_pcm is fine
    source_pcm_for_calc = np.array(source_audio.get_array_of_samples()).astype(np.float32)

    # 4. Calculate scaling factor
    source_rms = calculate_rms(source_pcm_for_calc)
    if source_rms == 0: # Avoid division by zero for silent files
        print(f"Skipping normalization for silent file: {source_path.name}")
        source_audio.export(output_path, format="wav")
        return

    ratio = target_rms / source_rms
    
    # pydub uses dB for volume changes
    db_change = 20 * math.log10(ratio)

    # 5. Apply gain and export
    normalized_audio = source_audio.apply_gain(db_change)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    normalized_audio.export(output_path, format="wav")
    print(f"Normalized '{source_path.name}' against '{Path(reference_path_str).name}'. Saved to '{output_path}'")