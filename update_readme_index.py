import subprocess
import re
import os

# Step 1: Run the shell script to generate index.md
try:
    subprocess.run(["bash", "generate_index.sh"], check=True)
    print("✅ Shell script 'generate_index' executed successfully.")
except subprocess.CalledProcessError as e:
    print("❌ Error running 'generate_index':", e)
    exit(1)
    
# File paths
index_path = "index.md"
readme_path = "README.md"

# Read index.md content
with open(index_path, "r", encoding="utf-8") as f:
    index_content = f.read()

# Read README.md content
with open(readme_path, "r", encoding="utf-8") as f:
    readme_content = f.read()

# Regex to find the Project Index section
pattern = r"(# Project Index \(Sorted by LAB Number\)\n)(.*?)(\n#|\Z)"  # Match until next header or end of file

# Replace the old index with the new one
new_readme_content = re.sub(pattern, r"\1" + index_content + r"\3", readme_content, flags=re.DOTALL)

# Write back to README.md
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(new_readme_content)

print("✅ README.md updated with new index from index.md.")

# Step 6: Delete index.md
try:
    os.remove("index.md")
    print("🗑️ index.md removed successfully.")
except FileNotFoundError:
    print("⚠️ index.md not found for deletion.")
except Exception as e:
    print("❌ Error deleting index.md:", e)
