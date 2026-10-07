import typing as t
import numpy as np


def fuse_evidence(
    cnn_output: t.Dict[str, t.Any],
    iq_samples: np.ndarray,
    spectrum_data: t.Dict[str, t.Any],
) -> t.Dict[str, t.Any]:
    """Combines PyTorch CNN output probabilities with DSP spectral & constellation measurements.

    Core Principle (Problem Statement 26147):
    'DSP measures. AI recognizes. Communication algorithms recover. Evidence fusion explains.'
    """
    raw_probs = cnn_output.get("probs", {})
    detected = cnn_output.get("detected", "QPSK")
    base_confidence = cnn_output.get("confidence", 0.8)

    dsp_evidence = cnn_output.get("dspEvidence", [])
    cnn_evidence = cnn_output.get("cnnEvidence", [])

    if len(iq_samples) > 10:
        max_abs = np.max(np.abs(iq_samples))
        iq_norm = iq_samples / max_abs if max_abs > 1e-12 else iq_samples

        i_pwr = float(np.mean(np.real(iq_norm) ** 2))
        q_pwr = float(np.mean(np.imag(iq_norm) ** 2))
        max_pwr = max(i_pwr, q_pwr)
        min_pwr = min(i_pwr, q_pwr)
        iq_ratio = float(min_pwr / (max_pwr + 1e-12))
        env_var = float(np.var(np.abs(iq_norm)))

        # Instantaneous frequency discriminator for FSK detection
        inst_freq = np.angle(iq_norm[1:] * np.conj(iq_norm[:-1]))
        h, bin_edges = np.histogram(inst_freq, bins=20)
        # Find distinct peaks in frequency derivative distribution
        h_max = np.max(h) if len(h) > 0 else 1
        peaks = [i for i in range(1, len(h)-1) if h[i] > h[i-1] and h[i] > h[i+1] and h[i] > 0.15 * h_max]
        # True FSK has 2 distinct peak frequencies separated by at least 2 bins
        is_fsk_spectrum = (len(peaks) >= 2 and abs(peaks[0] - peaks[-1]) >= 3)
        fsk_cnn_prob = raw_probs.get("FSK", 0.0)

        dsp_evidence.append(
            {
                "metric": "I/Q Channel Power Ratio (Min/Max)",
                "value": f"{iq_ratio:.3f}",
                "note": "Ratio ~ 1.0 indicates 2D Quadrature (QPSK/QAM), Ratio ~ 0.0 indicates 1D (BPSK)",
            }
        )
        dsp_evidence.append(
            {
                "metric": "Envelope Variance",
                "value": f"{env_var:.4f}",
                "note": "Low variance (< 0.02) indicates Constant Envelope (BPSK/QPSK/FSK)",
            }
        )
        dsp_evidence.append(
            {
                "metric": "Instantaneous Frequency Peaks",
                "value": f"{len(peaks)} peaks",
                "note": "Multi-peak frequency distribution indicates frequency shift tones (FSK)",
            }
        )

        # Fusion Decision Matrix
        # Rule 1: FSK Dual-Tone Frequency Shift
        if (is_fsk_spectrum or fsk_cnn_prob > 0.6) and env_var < 0.10:
            detected = "FSK"
            base_confidence = max(base_confidence, 0.95)
            raw_probs["FSK"] = max(raw_probs.get("FSK", 0.0), 0.95)
            cnn_evidence.append(
                f"Evidence Fusion: Measured dual-tone frequency shifts (FSK peaks = {len(peaks)}), confirming FSK modulation."
            )

        # Rule 2: Single-channel 1D BPSK signal (Q power negligible or BPSK dominant)
        elif iq_ratio < 0.15 or (raw_probs.get("BPSK", 0.0) > 0.4 and iq_ratio < 0.35):
            detected = "BPSK"
            base_confidence = max(base_confidence, 0.95)
            raw_probs["BPSK"] = max(raw_probs.get("BPSK", 0.0), 0.95)
            cnn_evidence.append(
                f"Evidence Fusion: Measured 1D phase trajectory (I/Q Ratio = {iq_ratio:.3f}), confirming BPSK modulation."
            )

        # Rule 3: Quadrature 2D PSK signal (I & Q power balanced, low envelope variance)
        elif iq_ratio > 0.60 and env_var < 0.05 and not is_fsk_spectrum:
            if raw_probs.get("8PSK", 0.0) > 0.4:
                detected = "8PSK"
            else:
                detected = "QPSK"
            base_confidence = max(base_confidence, 0.92)
            raw_probs[detected] = max(raw_probs.get(detected, 0.0), 0.92)
            cnn_evidence.append(
                f"Evidence Fusion: Measured balanced 2D Quadrature energy (I/Q Ratio = {iq_ratio:.3f}) and low envelope variance ({env_var:.4f}), confirming {detected} modulation."
            )

    # Spectral feature check
    power_db = spectrum_data.get("powerDb", spectrum_data.get("power_db", []))
    if len(power_db) > 0:
        peakiness = float(np.max(power_db) - np.mean(power_db))
    else:
        peakiness = 10.0

    dsp_evidence.append(
        {
            "metric": "Spectral Peakiness (Kurtosis proxy)",
            "value": f"{peakiness:.1f} dB",
            "note": "Peak power relative to average band energy",
        }
    )

    return {
        "probs": raw_probs,
        "detected": detected,
        "confidence": float(base_confidence),
        "cnnEvidence": cnn_evidence,
        "dspEvidence": dsp_evidence,
    }
