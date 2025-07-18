import os
import sys

def print_tree(path, show_files=True, indent_level=0):
    try:
        items = sorted(os.listdir(path))
    except PermissionError:
        print("\t" * indent_level + "[Permission Denied]")
        return

    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            print("\t" * indent_level + f"[{item}]")
            print_tree(full_path, show_files, indent_level + 1)
        elif show_files:
            print("\t" * indent_level + f"{item}")

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("0", "1"):
        print("Usage: python tree_structure.py [0|1]")
        print("1: Include files\n0: Only folders")
        return

    show_files = sys.argv[1] == "1"
    start_path = os.getcwd()  # You can change this to any path

    print(f"[{os.path.basename(start_path) or start_path}]")
    print_tree(start_path, show_files=show_files, indent_level=1)

if __name__ == "__main__":
    main()
