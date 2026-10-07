import pickle
import sys
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).resolve().parent / "data"
SUBSET_PATH = DATA_DIR / "radioml_subset.npz"

MOD_MAPPING = {
    b"BPSK": 0,
    "BPSK": 0,
    b"QPSK": 1,
    "QPSK": 1,
    b"8PSK": 2,
    "8PSK": 2,
    b"CPFSK": 3,
    "CPFSK": 3,
    b"GFSK": 3,
    "GFSK": 3,
    b"QAM16": 4,
    "QAM16": 4,
    b"16QAM": 4,
    "16QAM": 4,
}


def prepare_radioml_subset(pkl_path: Path = None) -> Path:
    """Parses RadioML .pkl dataset and extracts training/testing subset."""
    if pkl_path is None:
        pkl_files = list(DATA_DIR.glob("**/*.pkl"))
        if not pkl_files:
            raise FileNotFoundError(f"No .pkl file found in {DATA_DIR}")
        pkl_path = pkl_files[0]

    print(f"Loading RadioML dataset from {pkl_path}...")
    with open(pkl_path, "rb") as f:
        # Support Python 2 pickle encoding in RadioML
        try:
            raw_data = pickle.load(f, encoding="latin1")
        except TypeError:
            raw_data = pickle.load(f)

    print("Extracting target modulation classes (BPSK, QPSK, 8PSK, FSK, 16QAM)...")
    X_list = []
    y_list = []
    snr_list = []

    for (mod, snr), frames in raw_data.items():
        if mod in MOD_MAPPING:
            target_class = MOD_MAPPING[mod]
            for frame in frames:
                # Frame shape: (2, 128). Tile / interpolate to (2, 1024)
                tile_count = 1024 // frame.shape[1]
                tiled_frame = np.tile(frame, (1, tile_count))

                X_list.append(tiled_frame)
                y_list.append(target_class)
                snr_list.append(snr)

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.int64)
    snrs = np.array(snr_list, dtype=np.int32)

    # Train / Test split (80% train, 20% test)
    np.random.seed(42)
    indices = np.arange(len(y))
    np.random.shuffle(indices)

    split_idx = int(0.8 * len(y))
    train_idx, test_idx = indices[:split_idx], indices[split_idx:]

    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test, snrs_test = X[test_idx], y[test_idx], snrs[test_idx]

    print(f"Dataset subset prepared: {len(X_train)} train, {len(X_test)} test frames.")
    np.savez_compressed(
        SUBSET_PATH,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        snrs_test=snrs_test,
    )
    print(f"Saved prepared subset to {SUBSET_PATH}")
    return SUBSET_PATH


if __name__ == "__main__":
    prepare_radioml_subset()
