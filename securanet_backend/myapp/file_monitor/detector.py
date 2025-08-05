import os

def is_suspicious_change(file_path, change_type):
    # Suspicious if file renamed to one of these extensions
    suspicious_exts = ['.locked', '.enc', '.crypt', '.r5a', '.encrypted']
    ext = os.path.splitext(file_path)[1].lower()

    if change_type == 'renamed' and ext in suspicious_exts:
        return True
    return False

