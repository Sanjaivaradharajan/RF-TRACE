import typing as t
import numpy as np


def get_ideal_constellation_points(mod_type: str = "QPSK") -> t.List[t.Dict[str, float]]:
    """Returns ideal constellation reference points (i, q) for a given modulation."""
    mod = mod_type.upper()
    points = []

    if mod == "BPSK":
        ref = [complex(-1, 0), complex(1, 0)]
    elif mod == "8PSK":
        ref = [np.exp(1j * 2 * np.pi * k / 8) for k in range(8)]
    elif mod == "16QAM":
        vals = [-3, -1, 1, 3]
        scale = 1.0 / np.sqrt(10.0)
        ref = [complex(i * scale, q * scale) for i in vals for q in vals]
    elif mod in ["FSK", "2FSK", "4FSK"]:
        ref = [complex(-0.7, 0), complex(0.7, 0)]
    else:
        # Default QPSK
        scale = 1.0 / np.sqrt(2.0)
        ref = [
            complex(scale, scale),
            complex(-scale, scale),
            complex(-scale, -scale),
            complex(scale, -scale),
        ]

    for pt in ref:
        points.append({"i": float(np.real(pt)), "q": float(np.imag(pt))})
    return points


def extract_constellation(
    iq: np.ndarray, max_points: int = 2000, mod_type: str = "QPSK"
) -> t.Dict[str, t.Any]:
    """Extracts complex I/Q samples matching React frontend interface:

    constellation: { rx: { i: number; q: number }[]; ideal: { i: number; q: number }[] }
    """
    if len(iq) == 0:
        return {"rx": [], "ideal": get_ideal_constellation_points(mod_type)}

    # Subsample or clip to max_points
    if len(iq) > max_points:
        indices = np.linspace(0, len(iq) - 1, max_points, dtype=int)
        samples = iq[indices]
    else:
        samples = iq

    # Scale so standard deviation fits comfortably inside plot bounds [-1.5, +1.5]
    std_val = np.std(samples)
    scale = 0.7 / std_val if std_val > 1e-6 else 1.0
    scaled_samples = samples * scale

    rx_points = []
    for s in scaled_samples:
        rx_points.append({"i": float(np.real(s)), "q": float(np.imag(s))})

    ideal_points = get_ideal_constellation_points(mod_type)

    return {
        "rx": rx_points,
        "ideal": ideal_points,
    }
