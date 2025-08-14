import os

def get_folder_size(folder):
    total = 0
    for dirpath, _, filenames in os.walk(folder):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total += os.path.getsize(fp)
    return total

model_dirs = [
    r"C:\Users\USER\SecuraNet_project\SecureNet-backend\securanet_backend\phishing_model",  # Your first model path
    r"C:\Users\USER\SecuraNet_project\SecureNet-backend\securanet_backend\securanet_backend\phishing_model"          # Your second model path
]

for model_dir in model_dirs:
    size_mb = get_folder_size(model_dir) / (1024 * 1024)
    print(f"{model_dir}: {size_mb:.2f} MB")