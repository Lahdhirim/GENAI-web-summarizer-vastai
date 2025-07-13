class LLMSchema:
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    OPENROUTER = "openrouter"

class EmailSchema:
    SUBJECT = "Subject"
    FROM = "From"
    TO = "To"

class SessionStateSchema:
    LOGGING_STARTED = "logging_started_logged"
    CONFIG_LOADED = "config_loaded_logged"
    SCRAPER_INITIALIZED = "web_scraper_initialized_logged"
    LLM_INITIALIZED = "llm_initialized_logged"
    SUMMARY = "summary"
    SEND_EMAIL_CLICKED = "send_email_clicked"
