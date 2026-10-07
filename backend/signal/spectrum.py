import typing as t
import numpy as np
from scipy import signal


def compute_spectrum(
    iq: np.ndarray,
    sample_rate: float = 2_000_000.0,
    center_freq_hz: float = 433_920_000.0,
    nfft: int = 1024,
) -> t.Dict[str, t.Any]:
    """Computes FFT Power Spectral Density (PSD) matching React frontend interface:

    spectrum: { freqMHz: number[]; powerDb: number[]; fcMHz: number; bwMHz: number }
    """
    if len(iq) == 0:
        fc = float(center_freq_hz / 1e6)
        return {
            "freqMHz": [fc - 1.0, fc, fc + 1.0],
            "powerDb": [-100.0, -100.0, -100.0],
            "fcMHz": fc,
            "bwMHz": 0.0,
        }

    # Welch PSD for complex signals
    nperseg = min(nfft, len(iq))
    freqs_rel, psd = signal.welch(
        iq, fs=sample_rate, nperseg=nperseg, return_onesided=False
    )

    # Shift frequencies so 0 Hz is in the middle
    freqs_shifted = np.fft.fftshift(freqs_rel)
    psd_shifted = np.fft.fftshift(psd)

    # Absolute frequencies in MHz
    freqs_mhz = (freqs_shifted + center_freq_hz) / 1e6

    # Convert to dB power scale
    power_db = 10.0 * np.log10(psd_shifted + 1e-12)
    max_pwr = np.max(power_db)
    power_db_norm = power_db - max_pwr  # Peak normalized to 0 dB

    # 3dB Bandwidth estimation
    above_3db = power_db_norm > -3.0
    if np.any(above_3db):
        bw_hz = np.max(freqs_shifted[above_3db]) - np.min(freqs_shifted[above_3db])
        bw_mhz = float(max(bw_hz / 1e6, 0.01))
    else:
        bw_mhz = sample_rate / 2e6

    # Subsample to ~256 points for smooth SVG chart rendering
    stride = max(1, len(freqs_mhz) // 256)
    sub_freqs = [float(val) for val in freqs_mhz[::stride]]
    sub_powers = [float(val) for val in power_db_norm[::stride]]

    return {
        "freqMHz": sub_freqs,
        "powerDb": sub_powers,
        "fcMHz": float(center_freq_hz / 1e6),
        "bwMHz": float(bw_mhz),
    }
