import os

def replace_in_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content.replace("Gemini", "Gemma").replace("gemini", "gemma")
        
        if content != new_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
    except:
        pass
    return False

root_dir = "/home/yamin/gemini-cli"
changed_count = 0

for root, dirs, files in os.walk(root_dir):
    if ".git" in root or "node_modules" in root:
        continue
    for file in files:
        if replace_in_file(os.path.join(root, file)):
            changed_count += 1

print(f"Refactored {changed_count} files. The tool is now officially 'Gemma CLI'.")
