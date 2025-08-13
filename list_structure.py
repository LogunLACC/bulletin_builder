import os

# Change this to the root of your project if needed
project_root = os.path.dirname(os.path.abspath(__file__))

output_file = os.path.join(project_root, "project_structure.txt")

with open(output_file, "w", encoding="utf-8") as f:
    for root, dirs, files in os.walk(project_root):
        # Ignore hidden dirs like .git, __pycache__, build, dist
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("__pycache__", "build", "dist")]
        level = root.replace(project_root, "").count(os.sep)
        indent = "    " * level
        f.write(f"{indent}{os.path.basename(root)}/\n")
        subindent = "    " * (level + 1)
        for filename in files:
            f.write(f"{subindent}{filename}\n")

print(f"✅ Project structure saved to {output_file}")
