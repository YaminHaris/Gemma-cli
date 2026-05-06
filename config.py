"""
Configuration management for Gemma CLI.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Set


class Config:
    """Central configuration for Gemma CLI."""

    # Proxy settings
    PROXY_HOST: str = os.getenv("GEMMA_PROXY_HOST", "0.0.0.0")
    PROXY_PORT: int = int(os.getenv("GEMMA_PROXY_PORT", "4000"))

    # Ollama settings
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
    MODEL_NAME: str = os.getenv("GEMMA_MODEL", "gemma4:e4b")

    # Execution settings
    COMMAND_EXECUTION_ENABLED: bool = os.getenv("GEMMA_ENABLE_COMMANDS", "false").lower() == "true"
    COMMAND_TIMEOUT: int = int(os.getenv("GEMMA_COMMAND_TIMEOUT", "30"))
    REQUIRE_USER_CONFIRMATION: bool = os.getenv("GEMMA_REQUIRE_CONFIRMATION", "true").lower() == "true"

    # Logging settings
    LOG_LEVEL: str = os.getenv("GEMMA_LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("GEMMA_LOG_FILE", "gemma-cli.log")

    # Security settings
    DANGEROUS_CHARS: Set[str] = {"|", "&", ";", "`", "$", "(", ")", "<", ">", "\n"}
    MAX_COMMAND_LENGTH: int = int(os.getenv("GEMMA_MAX_COMMAND_LENGTH", "1000"))

    # Whitelisted commands (empty by default - user must enable)
    WHITELISTED_COMMANDS: Set[str] = set(
        os.getenv("GEMMA_WHITELISTED_COMMANDS", "").split(",")
    ) if os.getenv("GEMMA_WHITELISTED_COMMANDS") else set()

    @classmethod
    def validate(cls) -> None:
        """Validate configuration values."""
        if cls.PROXY_PORT < 1 or cls.PROXY_PORT > 65535:
            raise ValueError(f"Invalid port: {cls.PROXY_PORT}")
        
        if cls.COMMAND_TIMEOUT < 1 or cls.COMMAND_TIMEOUT > 3600:
            raise ValueError(f"Invalid timeout: {cls.COMMAND_TIMEOUT}")
        
        if cls.LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError(f"Invalid log level: {cls.LOG_LEVEL}")
        
        if not cls.OLLAMA_URL.startswith("http"):
            raise ValueError(f"Invalid Ollama URL: {cls.OLLAMA_URL}")

    @classmethod
    def to_dict(cls) -> dict:
        """Return configuration as dictionary (without sensitive data)."""
        return {
            "proxy_host": cls.PROXY_HOST,
            "proxy_port": cls.PROXY_PORT,
            "ollama_url": cls.OLLAMA_URL,
            "model_name": cls.MODEL_NAME,
            "command_execution_enabled": cls.COMMAND_EXECUTION_ENABLED,
            "command_timeout": cls.COMMAND_TIMEOUT,
            "require_user_confirmation": cls.REQUIRE_USER_CONFIRMATION,
            "log_level": cls.LOG_LEVEL,
            "log_file": cls.LOG_FILE,
        }


# Validate configuration on import
Config.validate()
