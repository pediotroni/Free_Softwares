import os
import sys

def print_tree(path, show_files=True, max_depth=None, current_depth=0, indent_level=0):
    if max_depth is not None and current_depth > max_depth:
        return

    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        print("\t" * indent_level + "[Permission Denied]")
        return

    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            print("\t" * indent_level + f"[{item}]")
            print_tree(full_path, show_files, max_depth, current_depth + 1, indent_level + 1)
        elif show_files:
            print("\t" * indent_level + f"{item}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python tree.py <mode> <max_depth> [path]")
        print("Modes: folder_only | file_and_folder")
        print("Example: python tree.py folder_only 3")
        print("Example: python tree.py file_and_folder 4 /path/to/dir")
        return

    mode = sys.argv[1]
    try:
        max_depth = int(sys.argv[2])
    except ValueError:
        print("Error: max_depth must be an integer!")
        return

    show_files = mode == "file_and_folder"
    start_path = sys.argv[3] if len(sys.argv) > 3 else os.getcwd()

    print(f"[{os.path.basename(start_path) or start_path}]")
    print_tree(start_path, show_files=show_files, max_depth=max_depth, current_depth=0, indent_lev
