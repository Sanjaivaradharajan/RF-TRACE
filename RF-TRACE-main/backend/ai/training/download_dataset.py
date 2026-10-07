import os
import shutil
import sys
import zipfile
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

KAGGLE_DATASET_REFS = [
    "nolasthitnotomorrow/radioml2016-deepsigcom",
    "hridayeshrana/radioml2016a",
    "pinxau1000/radioml2018",
]


def download_radioml_dataset() -> Path:
    """Downloads RadioML dataset from Kaggle using local credentials."""
    import kaggle

    print(f"Authenticating Kaggle API...")
    kaggle.api.authenticate()

    downloaded = False
    for dataset_ref in KAGGLE_DATASET_REFS:
        try:
            print(
                f"Attempting download of dataset '{dataset_ref}' to {DATA_DIR}..."
            )
            kaggle.api.dataset_download_files(
                dataset_ref, path=str(DATA_DIR), unzip=True
            )
            downloaded = True
            print(f"Successfully downloaded '{dataset_ref}'!")
            break
        except Exception as e:
            print(f"Failed download for '{dataset_ref}': {e}")
            continue

    if not downloaded:
        raise RuntimeError("Failed to download RadioML dataset from Kaggle refs.")

    print("Searching for dataset files...")
    # Find .pkl or .h5 file inside DATA_DIR
    data_files = (
        list(DATA_DIR.glob("**/*.pkl"))
        + list(DATA_DIR.glob("**/*.h5"))
        + list(DATA_DIR.glob("**/*.dat"))
    )

    if not data_files:
        # Check zip or tar.gz files
        archives = list(DATA_DIR.glob("**/*.zip")) + list(
            DATA_DIR.glob("**/*.tar.gz")
        )
        for zf in archives:
            if zf.suffix == ".zip":
                print(f"Extracting zip archive: {zf.name}")
                with zipfile.ZipFile(zf, "r") as z:
                    z.extractall(DATA_DIR)

        data_files = (
            list(DATA_DIR.glob("**/*.pkl"))
            + list(DATA_DIR.glob("**/*.h5"))
            + list(DATA_DIR.glob("**/*.dat"))
        )

    if not data_files:
        raise FileNotFoundError(
            f"Could not locate RadioML dataset file (.pkl/.h5) in {DATA_DIR}"
        )

    target_file = data_files[0]
    print(f"Successfully located RadioML dataset file: {target_file}")
    return target_file


if __name__ == "__main__":
    download_radioml_dataset()
