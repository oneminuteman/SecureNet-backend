#!/usr/bin/env python
import os
import re

def fix_imports():
    """Recursively search for ourapp references and replace them"""
    root_dir = "."
    old_module = "ourapp"
    new_module = "ourapp"
    
    # Track files changed
    files_changed = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip virtual environment directories
        if '.venv' in dirpath or 'env' in dirpath or 'venv' in dirpath:
            continue
            
        # Skip directories that shouldn't be modified
        if '__pycache__' in dirpath or '.git' in dirpath:
            continue
        
        for filename in filenames:
            # Only process Python files
            if not filename.endswith('.py'):
                continue
                
            filepath = os.path.join(dirpath, filename)
            
            # Read file content
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check if the file contains the old module name
            if old_module in content:
                # Replace all occurrences
                new_content = content.replace(old_module, new_module)
                
                # Write back the updated content
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"Updated references in: {filepath}")
                files_changed += 1
    
    print(f"\nTotal files updated: {files_changed}")

if __name__ == "__main__":
    fix_imports()