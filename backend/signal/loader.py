from dataclasses import dataclass
from pathlib import Path
import struct
import typing as t
import wave
import numpy as np


@dataclass
class SignalBuffer:
    iq_samples: np.ndarray  # Complex array [I + j*Q]
    sample_rate: float  # Sampling rate in Hz
    center_freq: float  # Center frequency in Hz
    duration_s: float  # Duration in seconds
    file_format: str  # 'IQ' or 'WAV'
    sample_format: str  # 'int8', 'int16', 'float32', etc.
    filename: str
    num_samples: int


def load_wav_file(
    file_path: Path, center_freq: float = 433_920_000.0
) -> SignalBuffer:
    """Loads a .wav file and converts audio channels into complex I/Q samples."""
    with wave.open(str(file_path), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        sample_rate = float(wf.getframerate())
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    # Determine sample format
    if sampwidth == 1:
        dtype = np.uint8
        data = np.frombuffer(raw_bytes, dtype=dtype).astype(np.float32) - 128.0
        data /= 128.0
        sample_fmt = "int8"
    elif sampwidth == 2:
        dtype = np.int16
        data = np.frombuffer(raw_bytes, dtype=dtype).astype(np.float32) / 32768.0
        sample_fmt = "int16"
    elif sampwidth == 4:
        dtype = np.float32
        data = np.frombuffer(raw_bytes, dtype=dtype)
        sample_fmt = "float32"
    else:
        # Default fallback to 16-bit
        data = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        sample_fmt = "int16"

    # Convert to complex I/Q
    if n_channels >= 2:
        # Channel 0 = I (In-Phase), Channel 1 = Q (Quadrature)
        i_samples = data[0::n_channels]
        q_samples = data[1::n_channels]
        min_len = min(len(i_samples), len(q_samples))
        iq_samples = i_samples[:min_len] + 1j * q_samples[:min_len]
    else:
        # Mono channel: Real signal -> Analytic signal
        i_samples = data
        iq_samples = i_samples + 1j * np.zeros_like(i_samples)

    num_samples = len(iq_samples)
    duration_s = num_samples / sample_rate if sample_rate > 0 else 0.0

    return SignalBuffer(
        iq_samples=iq_samples,
        sample_rate=sample_rate,
        center_freq=center_freq,
        duration_s=duration_s,
        file_format="WAV",
        sample_format=sample_fmt,
        filename=file_path.name,
        num_samples=num_samples,
    )


def load_raw_iq_file(
    file_path: Path,
    sample_rate: float = 2_000_000.0,
    center_freq: float = 433_920_000.0,
    sample_format: str = "auto",
) -> SignalBuffer:
    """Loads a raw .iq / .cfile containing interleaved I/Q samples."""
    with open(file_path, "rb") as f:
        raw_bytes = f.read()

    sample_format_lower = str(sample_format).lower()

    if sample_format_lower in ["auto", "default", "none", ""]:
        # Auto-detect float32 vs int16 vs uint8
        if len(raw_bytes) >= 1000:
            test_f32 = np.frombuffer(raw_bytes[:4000], dtype=np.float32)
            max_f32 = np.max(np.abs(test_f32))
            if (
                0.001 <= max_f32 <= 50.0
                and not np.isnan(max_f32)
                and not np.isinf(max_f32)
            ):
                sample_format_lower = "float32"
            else:
                sample_format_lower = "int16"
        else:
            sample_format_lower = "float32"

    if "8" in sample_format_lower or "cu8" in sample_format_lower:
        raw_data = (
            np.frombuffer(raw_bytes, dtype=np.uint8).astype(np.float32) - 128.0
        ) / 128.0
        fmt_str = "int8"
    elif (
        "32" in sample_format_lower
        or "float" in sample_format_lower
        or "cf32" in sample_format_lower
    ):
        raw_data = np.frombuffer(raw_bytes, dtype=np.float32)
        fmt_str = "float32"
    else:
        # Default int16 (cs16)
        raw_data = (
            np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        )
        fmt_str = "int16"

    # Interleaved I, Q, I, Q...
    i_samples = raw_data[0::2]
    q_samples = raw_data[1::2]
    min_len = min(len(i_samples), len(q_samples))
    iq_samples = i_samples[:min_len] + 1j * q_samples[:min_len]

    num_samples = len(iq_samples)
    duration_s = num_samples / sample_rate if sample_rate > 0 else 0.0

    return SignalBuffer(
        iq_samples=iq_samples,
        sample_rate=sample_rate,
        center_freq=center_freq,
        duration_s=duration_s,
        file_format="IQ",
        sample_format=fmt_str,
        filename=file_path.name,
        num_samples=num_samples,
    )


def load_signal(
    file_path: Path,
    sample_rate: float = 2_000_000.0,
    center_freq: float = 433_920_000.0,
    sample_format: str = "auto",
) -> SignalBuffer:
    """Unified signal loader detecting file extension."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Signal file not found: {file_path}")

    ext = path.suffix.lower()
    if ext == ".wav":
        return load_wav_file(path, center_freq=center_freq)
    else:
        return load_raw_iq_file(
            path,
            sample_rate=sample_rate,
            center_freq=center_freq,
            sample_format=sample_format,
        )
