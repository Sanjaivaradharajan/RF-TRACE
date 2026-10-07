from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import torch
from backend.ai.model import MODULATION_CLASSES, ModulationCNN
from backend.config import MODULATION_MODEL_PATH

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
SUBSET_PATH = Path(__file__).resolve().parent / "data" / "radioml_subset.npz"


def evaluate_model_performance(subset_path: Path = SUBSET_PATH) -> dict:
    """Evaluates PyTorch CNN model across SNR levels and exports performance plots."""
    if not subset_path.exists():
        print(f"Subset file {subset_path} not found. Running synthetic evaluation...")
        from backend.ai.training.generate_dataset import generate_synthetic_dataset

        X_test, y_test = generate_synthetic_dataset(num_samples_per_class=100)
        snrs_test = np.random.choice(
            [-10, -5, 0, 5, 10, 15, 20], size=len(y_test)
        )
    else:
        print(f"Loading prepared RadioML test dataset from {subset_path}...")
        data = np.load(subset_path)
        X_test = data["X_test"]
        y_test = data["y_test"]
        snrs_test = data["snrs_test"]

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = ModulationCNN(num_classes=len(MODULATION_CLASSES)).to(device)

    if MODULATION_MODEL_PATH.exists():
        model.load_state_dict(torch.load(MODULATION_MODEL_PATH, map_location=device))
        print(f"Loaded model weights from {MODULATION_MODEL_PATH}")

    model.eval()

    unique_snrs = sorted(list(set(snrs_test)))
    snr_acc_dict = {}

    y_pred_all = []
    y_true_all = []

    print("\n--- Model Accuracy by Signal-to-Noise Ratio (SNR) ---")
    for snr in unique_snrs:
        indices = np.where(snrs_test == snr)[0]
        if len(indices) == 0:
            continue

        X_snr = torch.tensor(X_test[indices]).to(device)
        y_snr = y_test[indices]

        with torch.no_grad():
            outputs = model(X_snr)
            _, preds = torch.max(outputs, 1)
            preds_np = preds.cpu().numpy()

        acc = 100.0 * np.sum(preds_np == y_snr) / len(y_snr)
        snr_acc_dict[snr] = acc
        print(f"SNR {snr:3d} dB: Accuracy = {acc:6.2f}% ({len(y_snr)} samples)")

        y_pred_all.extend(preds_np)
        y_true_all.extend(y_snr)

    # Plot SNR vs Accuracy Curve
    plt.figure(figsize=(8, 5))
    plt.plot(
        list(snr_acc_dict.keys()),
        list(snr_acc_dict.values()),
        "o-",
        color="#3ddbc0",
        linewidth=2.5,
    )
    plt.title("RF-TRACE PyTorch CNN: Classification Accuracy vs SNR", fontsize=12)
    plt.xlabel("Signal-to-Noise Ratio (dB)", fontsize=11)
    plt.ylabel("Classification Accuracy (%)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.ylim(0, 105)

    snr_plot_path = RESULTS_DIR / "snr_accuracy_curve.png"
    plt.savefig(snr_plot_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved SNR Accuracy Curve plot to: {snr_plot_path}")

    # Plot Confusion Matrix
    num_classes = len(MODULATION_CLASSES)
    cm = np.zeros((num_classes, num_classes), dtype=int)
    for t_val, p_val in zip(y_true_all, y_pred_all):
        cm[t_val, p_val] += 1

    plt.figure(figsize=(7, 6))
    plt.imshow(cm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.title("RF-TRACE Modulation Classification Confusion Matrix", fontsize=12)
    plt.colorbar()

    tick_marks = np.arange(num_classes)
    plt.xticks(tick_marks, MODULATION_CLASSES, rotation=45)
    plt.yticks(tick_marks, MODULATION_CLASSES)

    thresh = cm.max() / 2.0
    for i in range(num_classes):
        for j in range(num_classes):
            plt.text(
                j,
                i,
                format(cm[i, j], "d"),
                horizontalalignment="center",
                color="white" if cm[i, j] > thresh else "black",
            )

    plt.ylabel("True Label", fontsize=11)
    plt.xlabel("Predicted Label", fontsize=11)
    plt.tight_layout()

    cm_plot_path = RESULTS_DIR / "confusion_matrix.png"
    plt.savefig(cm_plot_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Saved Confusion Matrix plot to: {cm_plot_path}")

    return snr_acc_dict


if __name__ == "__main__":
    evaluate_model_performance()
