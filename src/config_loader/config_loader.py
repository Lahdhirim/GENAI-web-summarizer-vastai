import json
from pydantic import Field, BaseModel
from typing import Optional
from src.utils.schema import LLMSchema

class WebScraperConfig(BaseModel):
    timeout: Optional[int] = Field(default=10, description="Timeout for HTTP requests in seconds")

class OllamaConfig(BaseModel):
    enable: bool = Field(default=False, description="Enable Ollama LLM")
    model: str = Field(default="mistral", description="Ollama model name")

class HuggingFaceConfig(BaseModel):
    enable: bool = Field(default=False, description="Enable HuggingFace LLM")
    model: str = Field(default="HuggingFaceH4/zephyr-7b-beta", description="HuggingFace model name")
    base_url: Optional[str] = Field(default="https://api-inference.huggingface.co/models", description="HuggingFace API base URL")

class OpenRouterConfig(BaseModel):
    enable: bool = Field(default=False, description="Enable OpenRouter LLM")
    model: str = Field(default="anthropic/claude-3-haiku", description="OpenRouter model name")
    base_url: Optional[str] = Field(default="https://openrouter.ai/api/v1/chat/completions", description="OpenRouter API base URL")

class LLMsConfig(BaseModel):
    ollama: Optional[OllamaConfig] = Field(default=None, description="Ollama configuration")
    huggingface: Optional[HuggingFaceConfig] = Field(default=None, description="HuggingFace configuration")
    openrouter: Optional[OpenRouterConfig] = Field(default=None, description="OpenRouter configuration")

    def get_selected_llm(self) -> Optional[str]:
        """Return the name of the selected LLM provider"""
        if self.ollama and self.ollama.enable:
            return LLMSchema.OLLAMA
        elif self.huggingface and self.huggingface.enable:
            return LLMSchema.HUGGINGFACE
        elif self.openrouter and self.openrouter.enable:
            return LLMSchema.OPENROUTER
        else:
            print("No LLM provider is enabled.")
            return None
    
    def get_selected_llm_config(self):
        """Get configuration for the selected LLM provider"""
        selected_llm = self.get_selected_llm()
        if not selected_llm:
            raise ValueError("No LLM provider is selected")
        
        provider_map = {
            LLMSchema.OLLAMA: self.ollama,
            LLMSchema.HUGGINGFACE: self.huggingface,
            LLMSchema.OPENROUTER: self.openrouter
        }
        
        return provider_map[selected_llm]

class Config(BaseModel):
    web_scraper_config: WebScraperConfig = Field(..., description="Configuration for web scraping")
    llms_config: LLMsConfig = Field(..., description="Configuration for used LLM")
    prompt_files: dict[str, str] = Field(..., description="Dictionary of prompt files")

def config_loader(config_path: str) -> Config:
    try:
        with open(config_path, "r", encoding="utf-8") as file:
            config = json.load(file)
        return Config(**config)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find config file: {config_path}")