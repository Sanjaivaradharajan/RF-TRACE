import sys
from pathlib import Path
import wave
import numpy as np
import pytest

# Add project root to python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.signal.loader import load_signal, SignalBuffer
from backend.signal.preprocessing import (
    remove_dc_offset,
    normalize_amplitude,
    estimate_noise_floor,
    preprocess_signal,
)


def test_preprocessing_dc_and_norm():
    # Synthetic IQ signal with DC bias
    t = np.linspace(0, 1, 1000)
    raw_iq = (np.cos(2 * np.pi * 10 * t) + 2.0) + 1j * (
        np.sin(2 * np.pi * 10 * t) - 1.5
    )

    clean_iq = remove_dc_offset(raw_iq)
    assert abs(np.mean(np.real(clean_iq))) < 1e-5
    assert abs(np.mean(np.imag(clean_iq))) < 1e-5

    norm_iq = normalize_amplitude(clean_iq)
    assert abs(np.max(np.abs(norm_iq)) - 1.0) < 1e-5


def test_wav_loader(tmp_path):
    wav_file = tmp_path / "test_signal.wav"
    sample_rate = 44100
    n_samples = 4410

    # Write 16-bit stereo WAV
    t = np.linspace(0, 0.1, n_samples)
    left = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    right = (np.cos(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    interleaved = np.empty((n_samples * 2,), dtype=np.int16)
    interleaved[0::2] = left
    interleaved[1::2] = right

    with wave.open(str(wav_file), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(interleaved.tobytes())

    sig_buf = load_signal(wav_file)
    assert isinstance(sig_buf, SignalBuffer)
    assert sig_buf.file_format == "WAV"
    assert sig_buf.sample_rate == 44100
    assert sig_buf.num_samples == n_samples
    assert len(sig_buf.iq_samples) == n_samples
