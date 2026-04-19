# Gemma CLI 🐚🤖

**The professional AI engineer, now 100% local and private.**

Gemma CLI is a high-performance terminal agent built by refactoring the advanced architecture of the Gemini CLI to run exclusively on local **Gemma 4** models via Ollama. 

It provides full terminal control, workspace analysis, and code editing capabilities—all without an internet connection or API fees.

## 🚀 Key Features
- **Local-First Architecture:** Uses a custom FastAPI proxy to bridge professional CLI tools with Ollama.
- **Ubuntu 24.04 Optimized:** Tuned specifically for modern Linux engineering environments.
- **Privacy by Design:** No data ever leaves your machine. No telemetry. No cloud logging.
- **Gemma 4 "Thinking" Support:** Fully supports the new reasoning steps in the latest Gemma models.
- **Low-Latency Streaming:** Expertly tuned SSE streaming compatible with React/Ink terminal UIs.

## 🛠 Prerequisites
- **Linux** (Optimized for Ubuntu 24.04)
- **Ollama** installed and running.
- **NVIDIA GPU** (Optional, but highly recommended for 4B+ models).

## 📥 Installation

```bash
git clone https://github.com/your-username/gemma-cli.git
cd gemma-cli
./install.sh
```

## ⌨️ Usage

Simply type `gemma-cli` from any terminal:
```bash
gemma-cli "Analyze my ROS 2 workspace and fix any build errors."
```

## 🤝 Contributing
This is an open-source project aimed at giving developers professional-grade AI tools that they actually own. We welcome contributions in:
- Model tuning (Repetition penalty/Stop sequences).
- Support for other local backends (LM Studio, vLLM).
- Expanded toolsets for system administration.

---
*Built with ❤️ for the open-source community.*
