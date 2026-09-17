"""
Centralized app configuration.

All environment variables are loaded here, once, and imported everywhere
else via `from app.config import settings`.

We are NOT connecting to Supabase, Vapi, or an LLM provider yet — that
happens in later phases. Right now this file just proves the env-var
plumbing works.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "FreelancerBot"
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = True

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- Placeholders for future phases (kept here so .env.example stays authoritative) ---
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    # OpenRouter — chat/agent LLM (hosting NVIDIA models)
    # Get a free/low-cost key at https://openrouter.ai/keys
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_CHAT_MODEL: str = "google/gemma-4-26b-a4b-it:free"
    #GROQ_API_KEY: str = "" 
   # GROQ_BASE_URL: str = "https://api.groq.com/openai/v1" 
    #GROQ_CHAT_MODEL: str = "llama-3.3-70b-versatile"

    #GEMINI_CHAT_API_KEY: str = ""
    #GEMINI_CHAT_MODEL: str = "gemini-2.0-flash" 


    #NVIDIA_API_KEY: str = ""
    #NVIDIA_CHAT_MODEL: str = ""

    VAPI_API_KEY: str = ""
    VAPI_WEBHOOK_SECRET: str = ""
    N8N_WEBHOOK_URL: str = ""
    EMAIL_API_KEY: str = ""
    EMAIL_FROM_ADDRESS: str = ""

    GEMINI_API_KEY: str = ""
    GEMINI_EMBED_MODEL: str = "gemini-embedding-001"
    GEMINI_EMBED_DIM: int = 768


    FRONTEND_URL: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_ADDRESS: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )



settings = Settings()
