from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from backend.ai.model import MODULATION_CLASSES, ModulationCNN
from backend.ai.training.generate_dataset import generate_synthetic_dataset
from backend.config import MODELS_DIR, MODULATION_MODEL_PATH

DATA_DIR = Path(__file__).resolve().parent / "data"
SUBSET_PATH = DATA_DIR / "radioml_subset.npz"


def train_and_save_model(
    num_samples_per_class: int = 1000, epochs: int = 20, batch_size: int = 64
) -> float:
    """Trains the PyTorch ResNet CNN on combined RadioML + Oversampled Synthetic datasets."""
    print("Preparing combined training dataset...")
    X_list = []
    y_list = []

    # 1. Load RadioML real dataset if available
    if SUBSET_PATH.exists():
        print(f"Loading RadioML dataset from {SUBSET_PATH}...")
        data = np.load(SUBSET_PATH)
        X_radioml = data["X_train"]
        y_radioml = data["y_train"]

        # Sample up to 20,000 frames for balanced training speed
        if len(X_radioml) > 20000:
            indices = np.random.choice(len(X_radioml), 20000, replace=False)
            X_radioml = X_radioml[indices]
            y_radioml = y_radioml[indices]

        X_list.append(X_radioml)
        y_list.append(y_radioml)

    # 2. Add oversampled RRC pulse-shaped synthetic dataset
    print(
        f"Generating {num_samples_per_class * len(MODULATION_CLASSES)} pulse-shaped synthetic frames..."
    )
    X_syn, y_syn = generate_synthetic_dataset(
        num_samples_per_class=num_samples_per_class
    )
    X_list.append(X_syn)
    y_list.append(y_syn)

    X_data = np.concatenate(X_list, axis=0)
    y_data = np.concatenate(y_list, axis=0)

    # Shuffle combined dataset
    shuffle_indices = np.arange(len(y_data))
    np.random.shuffle(shuffle_indices)
    X_data = X_data[shuffle_indices]
    y_data = y_data[shuffle_indices]

    X_tensor = torch.tensor(X_data)
    y_tensor = torch.tensor(y_data)

    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(
        f"Training PyTorch ResNet CNN model on device: {device} ({len(X_data)} total samples)"
    )

    model = ModulationCNN(num_classes=len(MODULATION_CLASSES)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        correct = 0
        total = 0

        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * batch_x.size(0)
            _, predicted = torch.max(outputs, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()

        scheduler.step()
        accuracy = 100.0 * correct / total
        avg_loss = total_loss / total
        if (epoch + 1) % 5 == 0 or epoch == epochs - 1:
            print(
                f"Epoch [{epoch + 1}/{epochs}] - Loss: {avg_loss:.4f} - Accuracy: {accuracy:.2f}%"
            )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), str(MODULATION_MODEL_PATH))
    print(f"Model successfully saved to {MODULATION_MODEL_PATH}")
    return accuracy


if __name__ == "__main__":
    train_and_save_model()
