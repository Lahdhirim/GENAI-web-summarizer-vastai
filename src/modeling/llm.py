import os
from abc import ABC, abstractmethod
from typing import Union
import subprocess
import requests
from src.config_loader.config_loader import OllamaConfig, OpenRouterConfig, HuggingFaceConfig, LLMsConfig
from src.utils.schema import LLMSchema

class BaseLLM(ABC):
    """Abstract base class for LLM implementations"""
    
    def __init__(self, config: Union[OllamaConfig, OpenRouterConfig, HuggingFaceConfig]):
        self.config = config
    
    @abstractmethod
    def call(self, content: str, prompt: str) -> str:
        """Call the LLM with a prompt and return the response"""
        pass

class OllamaLLM(BaseLLM):
    """Ollama LLM implementation"""
    
    def __init__(self, config: OllamaConfig):
        super().__init__(config)
    
    def call(self, content: str, prompt: str) -> str:

        full_prompt = f"{prompt}\nThe contents of this website is as follows:\n{content}"

        try:
            result = subprocess.run(
                ["ollama", "run", self.config.model],
                input=full_prompt.encode(),
                capture_output=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Ollama error: {result.stderr.decode()}")
            
            output = result.stdout.decode()
            return output.strip()
        
        except FileNotFoundError:
            raise Exception("Ollama not found. Make sure Ollama is installed")

class HuggingFaceLLM(BaseLLM):
    """HuggingFace LLM implementation"""
    
    def __init__(self, config: HuggingFaceConfig):
        super().__init__(config)
        self.api_url = f"{self.config.base_url}/{self.config.model}"
    
    def call(self, content: str, prompt: str) -> str:

        headers = {
            "Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"
        }
        
        payload = {
            "inputs": content
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                return result[0].get("summary_text", "").strip()
            else:
                raise Exception(f"HuggingFace error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"HuggingFace request failed: {str(e)}")

class OpenRouterLLM(BaseLLM):
    """OpenRouter LLM implementation"""
    
    def __init__(self, config: OpenRouterConfig):
        super().__init__(config)
    
    def call(self, content: str, prompt: str) -> str:

        full_prompt = f"{prompt}\nThe contents of this website is as follows:\n{content}"

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": full_prompt}]
        }
        
        try:
            response = requests.post(
                self.config.base_url, 
                headers=headers, 
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            
            elif response.status_code == 429:
            # Handle rate limiting
                raise Exception(
                    "🚧 Oops! The daily request limit for OpenRouter has been reached.\n\n"
                    "Don't worry, it just means *a lot of people* used the service today.\n\n"
                    "Please try again tomorrow.\n\n"
                    "Even AI needs a nap sometimes... 💤"
                )
            
            else:
                raise Exception(f"OpenRouter error: {response.status_code} - {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter request failed: {str(e)}")

class LLMSelector:
    """Class to create LLM instances based on configuration"""

    def __init__(self, config: LLMsConfig):
        self.config = config
    
    def create_llm_from_config(self) -> BaseLLM:
        """Create LLM instance from AnonymisationConfig"""
        provider = self.config.get_selected_llm()
        llm_config = self.config.get_selected_llm_config()
        
        if provider == LLMSchema.OLLAMA:
            return OllamaLLM(llm_config)
        elif provider == LLMSchema.HUGGINGFACE:
            return HuggingFaceLLM(llm_config)
        elif provider == LLMSchema.OPENROUTER:
            return OpenRouterLLM(llm_config)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")