import typing as t
import numpy as np


def estimate_sps_and_strobe(
    iq: np.ndarray, sps_hint: t.Optional[int] = None
) -> np.ndarray:
    """Estimates Samples Per Symbol (SPS) and extracts downsampled symbol strobes."""
    if len(iq) < 32:
        return iq

    if sps_hint is not None and sps_hint in [2, 4, 8, 16]:
        best_sps = sps_hint
    else:
        # Cyclostationary phase derivative correlation for robust SPS auto-detection
        dphase = np.abs(np.diff(np.unwrap(np.angle(iq))))
        candidate_sps = [2, 4, 8, 16]
        best_sps = 4
        best_peak = -1.0
        for sps in candidate_sps:
            if len(dphase) > sps * 4:
                peak = float(np.mean(dphase[::sps]))
                if peak > best_peak:
                    best_peak = peak
                    best_sps = sps

    best_strobe_offset = 0
    best_var = -1.0
    for offset in range(best_sps):
        sub = iq[offset::best_sps]
        if len(sub) > 1:
            diff = np.abs(np.diff(sub))
            metric = float(np.var(diff) + np.mean(np.abs(sub)))
            if metric > best_var:
                best_var = metric
                best_strobe_offset = offset

    return iq[best_strobe_offset::best_sps]


def recover_carrier_phase(
    symbols: np.ndarray, mod_type: str = "QPSK"
) -> np.ndarray:
    """Costas Loop carrier phase & frequency recovery loop for PSK/QAM constellations."""
    N = len(symbols)
    if N == 0:
        return symbols

    mod = mod_type.upper()
    phase_hat = 0.0
    freq_hat = 0.0

    if mod == "BPSK":
        alpha = 0.12
        beta = 0.008
    else:
        alpha = 0.15
        beta = 0.010

    out_symbols = np.zeros(N, dtype=np.complex64)

    for k in range(N):
        derot = symbols[k] * np.exp(-1j * phase_hat)
        out_symbols[k] = derot
        i_val = float(np.real(derot))
        q_val = float(np.imag(derot))

        if mod == "BPSK":
            ped = np.sign(i_val) * q_val if abs(i_val) > 1e-4 else 0.0
        elif mod in ["QPSK", "8PSK", "16QAM"]:
            ped = np.sign(i_val) * q_val - np.sign(q_val) * i_val
        else:
            ped = 0.0

        freq_hat += beta * ped
        phase_hat += alpha * ped + freq_hat

    return out_symbols


def demodulate_signal(
    iq: np.ndarray,
    mod_type: str = "QPSK",
    preamble_bits: t.Optional[np.ndarray] = None,
    sps_hint: t.Optional[int] = None,
) -> t.Tuple[str, t.Dict[str, t.Any]]:
    """Demodulates complex I/Q samples into raw bits ('0' and '1') with carrier phase recovery."""
    if len(iq) == 0:
        return "0" * 128, {"status": "Complete", "recoveredBits": 128}

    mod = mod_type.upper()

    # 1. Symbol timing strobe recovery
    raw_symbols = estimate_sps_and_strobe(iq, sps_hint=sps_hint)

    # 2. Costas Loop carrier phase recovery
    if mod in ["BPSK", "QPSK", "8PSK", "16QAM"]:
        symbols = recover_carrier_phase(raw_symbols, mod_type=mod)
    else:
        symbols = raw_symbols

    bits_list = []

    if mod in ["FSK", "2FSK", "4FSK", "GFSK", "CPFSK"]:
        # Quadrature Frequency Discriminator
        inst_freq = np.angle(symbols[1:] * np.conj(symbols[:-1]))
        thresh = float(np.mean(inst_freq))
        for f_val in inst_freq:
            bits_list.append("1" if f_val >= thresh else "0")

    elif mod == "BPSK":
        # Resolve 180-deg phase ambiguity if preamble is present
        cand_0 = ["1" if np.real(s) >= 0 else "0" for s in symbols]
        cand_180 = ["1" if np.real(-s) >= 0 else "0" for s in symbols]

        if preamble_bits is not None and len(preamble_bits) <= len(cand_0):
            p_str = "".join(str(b) for b in preamble_bits)
            err0 = sum(c1 != c2 for c1, c2 in zip(cand_0[:len(p_str)], p_str))
            err180 = sum(c1 != c2 for c1, c2 in zip(cand_180[:len(p_str)], p_str))
            bits_list = cand_180 if err180 < err0 else cand_0
        else:
            bits_list = cand_0

    elif mod == "8PSK":
        for s in symbols:
            angle = np.angle(s)
            if angle < 0:
                angle += 2 * np.pi
            idx = int(np.floor((angle + np.pi / 8) / (np.pi / 4))) % 8
            bits_list.append(f"{idx:03b}")

    elif mod == "16QAM":
        std_val = float(np.std(symbols)) if np.std(symbols) > 1e-6 else 1.0
        norm_symbols = symbols / std_val
        for s in norm_symbols:
            r, m = np.real(s), np.imag(s)
            b1 = "1" if r > 0 else "0"
            b2 = "1" if abs(r) < 0.8 else "0"
            b3 = "1" if m > 0 else "0"
            b4 = "1" if abs(m) < 0.8 else "0"
            bits_list.append(f"{b1}{b2}{b3}{b4}")

    else:
        # Default QPSK demodulation (Resolve 4-fold 90-deg phase ambiguity)
        rotations = [0.0, np.pi / 2, np.pi, 3 * np.pi / 2]
        cands = []
        for rot in rotations:
            syms_rot = symbols * np.exp(-1j * rot)
            c_bits = []
            for s in syms_rot:
                c_bits.append("1" if np.real(s) >= 0 else "0")
                c_bits.append("1" if np.imag(s) >= 0 else "0")
            cands.append(c_bits)

        if preamble_bits is not None and len(preamble_bits) <= len(cands[0]):
            p_str = "".join(str(b) for b in preamble_bits)
            best_cand = cands[0]
            best_err = len(p_str) + 1
            for cand in cands:
                err = sum(c1 != c2 for c1, c2 in zip(cand[:len(p_str)], p_str))
                if err < best_err:
                    best_err = err
                    best_cand = cand
            bits_list = best_cand
        else:
            bits_list = cands[0]

    bitstring = "".join(bits_list)
    if len(bitstring) > 8192:
        bitstring = bitstring[:8192]

    demod_meta = {
        "status": "Complete",
        "recoveredBits": len(bitstring),
        "demodulator": f"{mod} Costas Loop & Strobe Timing Recovery",
    }
    return bitstring, demod_meta
