import typing as t
import numpy as np

from backend.ai.classifier import ModulationClassifier
from backend.fec.viterbi import analyze_fec_candidates
from backend.fusion.evidence_fusion import fuse_evidence
from backend.signal.constellation import extract_constellation
from backend.signal.loader import SignalBuffer
from backend.signal.parameters import extract_signal_parameters
from backend.signal.preprocessing import preprocess_signal
from backend.signal.spectrum import compute_spectrum
from backend.signal.waterfall import compute_waterfall
from backend.demodulation.demodulator import demodulate_signal

# Global classifier instance
classifier_instance = ModulationClassifier()


def generate_full_analysis_report(
    buffer: SignalBuffer,
    sample_rate_override: t.Optional[float] = None,
    center_freq_override: t.Optional[float] = None,
) -> t.Dict[str, t.Any]:
    """Runs all 12 pipeline stages on the signal buffer and produces JSON report."""
    sample_rate = sample_rate_override or buffer.sample_rate or 2_000_000.0
    center_freq = center_freq_override or buffer.center_freq or 433_920_000.0

    # 1 & 2. Preprocessing (DC offset removal & peak normalization without destroying FSK phase derivatives)
    iq_clean = preprocess_signal(buffer.iq_samples, sample_rate, apply_filter=False)

    # 3. DSP Visualizations (Spectrum, Waterfall, Constellation)
    spectrum_res = compute_spectrum(iq_clean, sample_rate, center_freq)
    waterfall_res = compute_waterfall(iq_clean, sample_rate, center_freq)

    # 4 & 5. AI CNN Recognition + Evidence Fusion
    cnn_raw = classifier_instance.classify_iq(iq_clean)
    fusion_res = fuse_evidence(cnn_raw, iq_clean, spectrum_res)

    detected_mod = fusion_res["detected"]

    # 3b. Constellation with ideal reference for detected modulation
    constellation_res = extract_constellation(iq_clean, mod_type=detected_mod)

    # 6. Parameter Extraction
    params = extract_signal_parameters(
        iq_clean,
        sample_rate=sample_rate,
        center_freq=center_freq,
        detected_mod=detected_mod,
        bw_mhz=spectrum_res["bwMHz"],
    )

    # 7 & 8. Demodulation & Bit Recovery
    bits, demod_meta = demodulate_signal(iq_clean, mod_type=detected_mod)

    # 9 & 10. FEC & Interleaving candidate analysis
    fec_candidates = analyze_fec_candidates(bits)

    # 12. Final Consolidated Signal Profile JSON output
    file_info = {
        "name": buffer.filename,
        "sizeBytes": int(buffer.num_samples * 4),
        "format": buffer.file_format,
        "sampleFormat": buffer.sample_format,
        "durationS": float(buffer.duration_s),
    }

    return {
        "file": file_info,
        "params": params,
        "spectrum": spectrum_res,
        "waterfall": waterfall_res,
        "constellation": constellation_res,
        "modulation": fusion_res,
        "bits": bits,
        "demod": demod_meta,
        "fec": fec_candidates,
    }
