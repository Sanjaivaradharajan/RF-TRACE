import numpy as np
from scipy import signal


def remove_dc_offset(iq: np.ndarray) -> np.ndarray:
    """Removes DC bias offset by subtracting the mean of I and Q components."""
    if len(iq) == 0:
        return iq
    dc_i = np.mean(np.real(iq))
    dc_q = np.mean(np.imag(iq))
    return (np.real(iq) - dc_i) + 1j * (np.imag(iq) - dc_q)


def normalize_amplitude(iq: np.ndarray, target_peak: float = 1.0) -> np.ndarray:
    """Normalizes peak amplitude of complex I/Q samples to target_peak."""
    if len(iq) == 0:
        return iq
    max_val = np.max(np.abs(iq))
    if max_val > 1e-12:
        return iq * (target_peak / max_val)
    return iq


def apply_bandpass_filter(
    iq: np.ndarray,
    sample_rate: float,
    low_cutoff_hz: float,
    high_cutoff_hz: float,
    order: int = 4,
) -> np.ndarray:
    """Applies a Butterworth bandpass filter to complex I/Q samples."""
    if len(iq) == 0 or sample_rate <= 0:
        return iq

    nyquist = 0.5 * sample_rate
    low = max(low_cutoff_hz, 1.0) / nyquist
    high = min(high_cutoff_hz, nyquist - 1.0) / nyquist

    if low >= high or low <= 0 or high >= 1.0:
        return iq  # Invalid bounds, return original

    b, a = signal.butter(order, [low, high], btype="bandpass")
    # Filter I and Q independently
    filtered_i = signal.lfilter(b, a, np.real(iq))
    filtered_q = signal.lfilter(b, a, np.imag(iq))
    return filtered_i + 1j * filtered_q


def estimate_noise_floor(iq: np.ndarray) -> float:
    """Estimates the noise floor in dBFS based on the bottom 10th percentile power."""
    if len(iq) == 0:
        return -100.0
    power = np.abs(iq) ** 2
    quiet_samples = np.percentile(power, 10)
    noise_db = 10.0 * np.log10(max(quiet_samples, 1e-12))
    return float(noise_db)


def detect_signal_activity(
    iq: np.ndarray, threshold_db: float = -20.0
) -> np.ndarray:
    """Detects active signal segments exceeding the relative noise threshold.

    Returns boolean array of active sample indices.
    """
    if len(iq) == 0:
        return np.array([], dtype=bool)

    power = np.abs(iq) ** 2
    max_power = np.max(power)
    if max_power < 1e-12:
        return np.zeros(len(iq), dtype=bool)

    power_db = 10.0 * np.log10(power / max_power + 1e-12)
    return power_db > threshold_db


def preprocess_signal(
    iq: np.ndarray, sample_rate: float, apply_filter: bool = False
) -> np.ndarray:
    """Full preprocessing pipeline: DC offset removal -> Normalization -> Filtering."""
    processed = remove_dc_offset(iq)
    processed = normalize_amplitude(processed)
    if apply_filter and sample_rate > 0:
        # Example filter 10% to 90% of bandwidth
        processed = apply_bandpass_filter(
            processed, sample_rate, 0.05 * sample_rate, 0.45 * sample_rate
        )
        processed = normalize_amplitude(processed)
    return processed
