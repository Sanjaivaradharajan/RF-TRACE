import typing as t
import numpy as np
from scipy import signal


def compute_waterfall(
    iq: np.ndarray,
    sample_rate: float = 2_000_000.0,
    center_freq_hz: float = 433_920_000.0,
    time_bins: int = 64,
    freq_bins: int = 64,
) -> t.Dict[str, t.Any]:
    """Computes STFT Spectrogram heatmap matrix matching React frontend interface:

    waterfall: { data: number[][]; fMinMHz: number; fMaxMHz: number; durationS: number }
    """
    duration_s = len(iq) / sample_rate if sample_rate > 0 else 1.0
    f_min_mhz = float((center_freq_hz - sample_rate / 2.0) / 1e6)
    f_max_mhz = float((center_freq_hz + sample_rate / 2.0) / 1e6)

    if len(iq) < 128:
        empty_grid = [[0.0] * freq_bins for _ in range(time_bins)]
        return {
            "data": empty_grid,
            "fMinMHz": f_min_mhz,
            "fMaxMHz": f_max_mhz,
            "durationS": float(duration_s),
        }

    nperseg = min(256, len(iq) // 10 if len(iq) > 2560 else 128)
    nperseg = max(nperseg, 32)

    freqs, times, stft_matrix = signal.spectrogram(
        iq, fs=sample_rate, nperseg=nperseg, return_onesided=False
    )

    # Shift frequencies so 0 Hz is centered
    stft_matrix = np.fft.fftshift(stft_matrix, axes=0)
    power_db = 10.0 * np.log10(np.abs(stft_matrix) ** 2 + 1e-12)

    # Normalize matrix values from 0.0 (quiet) to 1.0 (peak intensity) using percentile dynamic range
    vmin = float(np.percentile(power_db, 5))
    vmax = float(np.percentile(power_db, 99.5))
    if vmax > vmin + 1e-6:
        norm_matrix = np.clip((power_db - vmin) / (vmax - vmin), 0.0, 1.0)
    else:
        norm_matrix = np.zeros_like(power_db)

    # Resample 2D matrix to exact (time_bins, freq_bins) grid size
    t_indices = np.linspace(0, norm_matrix.shape[1] - 1, time_bins, dtype=int)
    f_indices = np.linspace(0, norm_matrix.shape[0] - 1, freq_bins, dtype=int)

    grid = []
    for ti in t_indices:
        row = [float(norm_matrix[fi, ti]) for fi in f_indices]
        grid.append(row)

    return {
        "data": grid,
        "fMinMHz": f_min_mhz,
        "fMaxMHz": f_max_mhz,
        "durationS": float(duration_s),
    }
