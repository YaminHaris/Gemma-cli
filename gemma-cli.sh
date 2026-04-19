#!/bin/bash

# Configuration
GEMMA_CLI_DIR="/home/yamin/gemma-cli"
OLLAMA_BIN="$GEMMA_CLI_DIR/ollama_v20/bin/ollama"
PYTHON_BIN="$GEMMA_CLI_DIR/gemma_env/bin/python3"
PROXY_SCRIPT="$GEMMA_CLI_DIR/gemma_proxy_v2.py"

# 1. Start Ollama Server if not running
if ! pgrep -f "ollama serve" > /dev/null; then
    echo ">>> Starting Ollama server..."
    nohup "$OLLAMA_BIN" serve > "$GEMMA_CLI_DIR/ollama.log" 2>&1 &
    sleep 5
fi

# 2. Start Gemma Proxy
pkill -f "python3 $PROXY_SCRIPT" 2>/dev/null
echo ">>> Starting Gemma proxy v2..."
nohup "$PYTHON_BIN" "$PROXY_SCRIPT" > "$GEMMA_CLI_DIR/proxy.log" 2>&1 &

# Wait for proxy
echo ">>> Waiting for proxy to initialize..."
for i in {1..20}; do
    if curl -s http://localhost:4000/v1/models > /dev/null; then
        echo ">>> Proxy is ready."
        break
    fi
    sleep 1
done

# 3. Export Environment Variables
export GOOGLE_CLOUD_PROJECT="local-gemma-project"
export CODE_ASSIST_ENDPOINT="http://localhost:4000"
export GOOGLE_GEMINI_BASE_URL="http://localhost:4000"
export GEMINI_API_KEY="local-gemma-key"
export GOOGLE_API_KEY="local-gemma-key"
export GEMINI_CLI_AUTH_METHOD="gemini-api-key" # Force auth method

# Ensure interactive mode doesn't trigger onboarding again
export NO_ONBOARDING="true"

echo ">>> Redirected gemini-cli to local Gemma 4."
echo ">>> Launching Gemini CLI..."

# 4. Run Gemini CLI
gemini "$@"
