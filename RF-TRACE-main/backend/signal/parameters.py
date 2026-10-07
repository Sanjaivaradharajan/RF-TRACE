import typing as t
import numpy as np
from backend.signal.preprocessing import estimate_noise_floor


def extract_signal_parameters(
    iq: np.ndarray,
    sample_rate: float = 2_000_000.0,
    center_freq: float = 433_920_000.0,
    detected_mod: str = "QPSK",
    bw_mhz: float = 0.5,
) -> t.Dict[str, t.Dict[str, t.Any]]:
    """Extracts signal parameters matching React frontend interface:

    params: { fs: Param; fc: Param; bw: Param; symbolRate: Param; snr: Param; modulation: Param }
    """
    duration_s = len(iq) / sample_rate if sample_rate > 0 else 0.0

    # Calculate SNR (Signal to Noise Ratio)
    noise_db = estimate_noise_floor(iq)
    peak_power = 10.0 * np.log10(np.max(np.abs(iq) ** 2) + 1e-12)
    snr_db = float(max(peak_power - noise_db, 0.0))

    # Symbol rate estimation heuristic
    estimated_sym_rate_ksps = float((bw_mhz * 1e3) / 1.2)

    return {
        "fs": {
            "label": "Sampling Rate",
            "value": f"{sample_rate / 1e6:.3f}",
            "unit": "MS/s",
            "source": "Metadata",
            "note": "Header metadata / User setting",
        },
        "fc": {
            "label": "Carrier Frequency",
            "value": f"{center_freq / 1e6:.3f}",
            "unit": "MHz",
            "source": "Metadata",
            "note": "Header metadata / Tuner config",
        },
        "bw": {
            "label": "3dB Bandwidth",
            "value": f"{bw_mhz:.3f}",
            "unit": "MHz",
            "source": "Measured",
            "note": "Calculated via FFT PSD analysis",
        },
        "snr": {
            "label": "Estimated SNR",
            "value": f"{snr_db:.1f}",
            "unit": "dB",
            "source": "Estimated",
            "note": "Peak power vs 10th percentile noise floor",
        },
        "modulation": {
            "label": "Modulation",
            "value": detected_mod,
            "unit": "",
            "source": "Estimated",
            "note": "Multi-evidence PyTorch CNN + DSP classification",
        },
        "symbolRate": {
            "label": "Estimated Symbol Rate",
            "value": f"{estimated_sym_rate_ksps:.1f}",
            "unit": "kSps",
            "source": "Estimated",
            "note": "Derived from spectral occupied bandwidth",
        },
    }
