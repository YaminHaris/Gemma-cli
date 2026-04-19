#!/bin/bash
set -e

echo "🐚 Gemma CLI: Automated Installer"
echo "---------------------------------"

# 1. Setup Python Environment
echo ">>> Setting up virtual environment..."
python3 -m venv gemma_env
./gemma_env/bin/pip install fastapi uvicorn httpx --quiet

# 2. Check for Ollama
if ! command -v ollama &> /dev/null; then
    echo ">>> Ollama not found. Downloading..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 3. Pull Gemma 4
echo ">>> Pulling Gemma 4 (4B Effective)..."
ollama pull gemma4:e4b

# 4. Create Alias
SHELL_RC="$HOME/.bashrc"
if [[ "$SHELL" == *"zsh"* ]]; then SHELL_RC="$HOME/.zshrc"; fi

if ! grep -q "gemma-cli" "$SHELL_RC"; then
    echo ">>> Adding alias to $SHELL_RC..."
    echo "alias gemma-cli='$(pwd)/gemma-cli.sh'" >> "$SHELL_RC"
    echo "Alias added! Restart your terminal or run 'source $SHELL_RC'."
fi

echo "---------------------------------"
echo "✅ Installation complete! Run 'gemma-cli' to start."
