import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
import numpy as np
from backend.demodulation.demodulator import demodulate_signal, recover_carrier_phase

# Fix random seed for 100% deterministic ground-truth testing
np.random.seed(42)

PREAMBLE_BPSK = np.array([1, 1, 0, 0, 1, 1, 0, 1], dtype=int)
PREAMBLE_QPSK = np.array([1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1], dtype=int)


def generate_bpsk_signal(bits: np.ndarray, sps: int = 4, phase_deg: float = 0.0, snr_db=None, freq_offset: float = 0.0):
    """Generates complex BPSK baseband samples with controlled phase rotation, SNR, and frequency offset."""
    full_bits = np.concatenate([PREAMBLE_BPSK, bits])
    symbols = np.where(full_bits == 1, 1.0, -1.0)
    samples = np.repeat(symbols, sps).astype(np.complex64)

    t = np.arange(len(samples))
    phase_rad = np.radians(phase_deg) + 2 * np.pi * freq_offset * t
    rot_samples = samples * np.exp(1j * phase_rad)

    if snr_db is not None:
        noise_pwr = 10**(-snr_db / 10.0)
        noise = (np.random.normal(0, np.sqrt(noise_pwr / 2.0), len(samples)) +
                 1j * np.random.normal(0, np.sqrt(noise_pwr / 2.0), len(samples)))
        rot_samples += noise

    return rot_samples, full_bits


def generate_qpsk_signal(bits: np.ndarray, sps: int = 4, phase_deg: float = 0.0, snr_db=None, freq_offset: float = 0.0):
    """Generates complex QPSK baseband samples with controlled phase rotation, SNR, and frequency offset."""
    full_bits = np.concatenate([PREAMBLE_QPSK, bits])
    if len(full_bits) % 2 != 0:
        full_bits = full_bits[:-1]

    i_b = full_bits[0::2]
    q_b = full_bits[1::2]

    i_s = np.where(i_b == 1, 1.0, -1.0)
    q_s = np.where(q_b == 1, 1.0, -1.0)

    symbols = (i_s + 1j * q_s) / np.sqrt(2.0)
    samples = np.repeat(symbols, sps).astype(np.complex64)

    t = np.arange(len(samples))
    phase_rad = np.radians(phase_deg) + 2 * np.pi * freq_offset * t
    rot_samples = samples * np.exp(1j * phase_rad)

    if snr_db is not None:
        noise_pwr = 10**(-snr_db / 10.0)
        noise = (np.random.normal(0, np.sqrt(noise_pwr / 2.0), len(samples)) +
                 1j * np.random.normal(0, np.sqrt(noise_pwr / 2.0), len(samples)))
        rot_samples += noise

    return rot_samples, full_bits


def test_demodulation_ber_tables():
    """Runs complete Phase 3, 4, 8, 9 BER test suite and prints exact formatted markdown tables."""
    np.random.seed(42)
    test_bits = np.random.randint(0, 2, 1024)

    phases = [0, 15, 30, 45, 60, 90, 135, 180, 225, 270, 315]

    print("\n============================================================")
    print("RF-TRACE STAGE 1 — DEMODULATION BER TEST")
    print("============================================================")

    print("\nBPSK Clean Phase Test")
    print("------------------------------------------------------------")
    print(f"{'Phase':<10} {'SNR':<10} {'Bits':<10} {'Errors':<10} {'BER':<10}")

    for ph in phases:
        iq, full_b = generate_bpsk_signal(test_bits, sps=4, phase_deg=ph)
        bit_str, _ = demodulate_signal(iq, mod_type="BPSK", preamble_bits=PREAMBLE_BPSK, sps_hint=4)
        rec_bits = np.array([int(b) for b in bit_str[len(PREAMBLE_BPSK):len(PREAMBLE_BPSK)+len(test_bits)]])
        errs = int(np.sum(test_bits != rec_bits))
        ber = errs / len(test_bits)
        print(f"{ph:3d}°       clean      {len(test_bits):<10} {errs:<10} {ber:.4f}")
        assert ber == 0.0, f"BPSK phase {ph} deg failed with BER {ber}"

    print("\nQPSK Clean Phase Test")
    print("------------------------------------------------------------")
    print(f"{'Phase':<10} {'SNR':<10} {'Bits':<10} {'Errors':<10} {'BER':<10}")

    for ph in phases:
        iq, full_b = generate_qpsk_signal(test_bits, sps=4, phase_deg=ph)
        bit_str, _ = demodulate_signal(iq, mod_type="QPSK", preamble_bits=PREAMBLE_QPSK, sps_hint=4)
        rec_bits = np.array([int(b) for b in bit_str[len(PREAMBLE_QPSK):len(PREAMBLE_QPSK)+len(test_bits)]])
        errs = int(np.sum(test_bits != rec_bits))
        ber = errs / len(test_bits)
        print(f"{ph:3d}°       clean      {len(test_bits):<10} {errs:<10} {ber:.4f}")
        assert ber == 0.0, f"QPSK phase {ph} deg failed with BER {ber}"

    print("\nNOISE TEST")
    print("------------------------------------------------------------")
    print(f"{'Modulation':<12} {'SNR':<10} {'Bits':<10} {'Errors':<10} {'BER':<10}")

    snrs = [30, 20, 10, 5]
    for snr in snrs:
        iq, full_b = generate_bpsk_signal(test_bits, sps=4, phase_deg=45.0, snr_db=snr)
        bit_str, _ = demodulate_signal(iq, mod_type="BPSK", preamble_bits=PREAMBLE_BPSK, sps_hint=4)
        rec_bits = np.array([int(b) for b in bit_str[len(PREAMBLE_BPSK):len(PREAMBLE_BPSK)+len(test_bits)]])
        errs = int(np.sum(test_bits != rec_bits))
        ber = errs / len(test_bits)
        print(f"{'BPSK':<12} {snr:2d} dB      {len(test_bits):<10} {errs:<10} {ber:.4f}")

    for snr in snrs:
        iq, full_b = generate_qpsk_signal(test_bits, sps=4, phase_deg=45.0, snr_db=snr)
        bit_str, _ = demodulate_signal(iq, mod_type="QPSK", preamble_bits=PREAMBLE_QPSK, sps_hint=4)
        rec_bits = np.array([int(b) for b in bit_str[len(PREAMBLE_QPSK):len(PREAMBLE_QPSK)+len(test_bits)]])
        errs = int(np.sum(test_bits != rec_bits))
        ber = errs / len(test_bits)
        print(f"{'QPSK':<12} {snr:2d} dB      {len(test_bits):<10} {errs:<10} {ber:.4f}")

    print("\nFREQUENCY OFFSET TEST")
    print("------------------------------------------------------------")
    for f_off, name in [(0.001, "+0.001 Fs"), (-0.001, "-0.001 Fs")]:
        iq, _ = generate_bpsk_signal(test_bits, sps=4, phase_deg=30.0, freq_offset=f_off)
        bit_str, _ = demodulate_signal(iq, mod_type="BPSK", preamble_bits=PREAMBLE_BPSK, sps_hint=4)
        rec_bits = np.array([int(b) for b in bit_str[len(PREAMBLE_BPSK):len(PREAMBLE_BPSK)+len(test_bits)]])
        errs = int(np.sum(test_bits != rec_bits))
        ber = errs / len(test_bits)
        print(f"BPSK Freq Offset ({name}): Errors = {errs} / {len(test_bits)} | BER = {ber:.4f}")


if __name__ == "__main__":
    test_demodulation_ber_tables()
