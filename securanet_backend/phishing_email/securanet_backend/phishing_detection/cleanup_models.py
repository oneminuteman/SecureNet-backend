import os
import shutil
import zipfile
from pathlib import Path

# 📌 Paths to your phishing model folders
MODEL_PATHS = [
    Path("securanet_backend/phishing_model"),
    Path("securanet_backend/securanet_backend/phishing_model")
]

def get_size(path: Path) -> float:
    """Calculate folder size in MB."""
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
    return round(total_size / (1024 * 1024), 2)

def delete_checkpoints(model_path: Path):
    """Delete all checkpoint-* folders inside the model folder."""
    for root, dirs, _ in os.walk(model_path):
        for d in dirs:
            if d.startswith("checkpoint-"):
                checkpoint_path = Path(root) / d
                print(f"🗑️  Deleting {checkpoint_path}")
                shutil.rmtree(checkpoint_path, ignore_errors=True)

def compress_model(model_path: Path):
    """Compress model folder into a ZIP file."""
    zip_path = model_path.with_suffix(".zip")
    print(f"📦 Compressing {model_path} → {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(model_path):
            for file in files:
                file_path = Path(root) / file
                zipf.write(file_path, arcname=file_path.relative_to(model_path))
    print(f"✅ Compressed model saved to {zip_path}")

def cleanup_and_compress():
    for model_path in MODEL_PATHS:
        if model_path.exists():
            print(f"\n📍 Checking: {model_path}")
            before_size = get_size(model_path)
            print(f"📏 Size before cleanup: {before_size} MB")

            # Delete only checkpoint-* folders
            delete_checkpoints(model_path)

            after_size = get_size(model_path)
            print(f"📉 Size after cleanup: {after_size} MB")

            # Compress cleaned model folder
            compress_model(model_path)
        else:
            print(f"⚠️ Model folder not found: {model_path}")

if __name__ == "__main__":
    cleanup_and_compress()
