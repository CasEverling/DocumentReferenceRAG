import os
import json
from typing import Dict, List, Optional, Any, Literal
from abc import ABC, abstractmethod
from openai import OpenAI
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM calls"""
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    response_format: Optional[Dict[str, str]] = None


@dataclass
class LLMResponse:
    """Standardized LLM response"""
    content: str
    model: str
    usage: Dict[str, int]
    raw_response: Any
    finish_reason: str


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], config: LLMConfig) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    @abstractmethod
    def generate_json(self, messages: List[Dict[str, str]], config: LLMConfig) -> Dict[str, Any]:
        """Generate a JSON response from the LLM"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API implementation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
    
    def generate(self, messages: List[Dict[str, str]], config: LLMConfig) -> LLMResponse:
        """Generate a response from OpenAI"""
        try:
            kwargs = {
                "model": config.model,
                "messages": messages,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "top_p": config.top_p,
                "frequency_penalty": config.frequency_penalty,
                "presence_penalty": config.presence_penalty,
            }
            
            if config.response_format:
                kwargs["response_format"] = config.response_format
            
            response = self.client.chat.completions.create(**kwargs)
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                raw_response=response,
                finish_reason=response.choices[0].finish_reason
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def generate_json(self, messages: List[Dict[str, str]], config: LLMConfig) -> Dict[str, Any]:
        """Generate a JSON response from OpenAI"""
        config.response_format = {"type": "json_object"}
        response = self.generate(messages, config)
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {response.content}")
            raise ValueError(f"Invalid JSON response from LLM: {str(e)}")


class LLMClient:
    """Main LLM client interface"""
    
    MODELS = {
        "gpt-4": LLMConfig(model="gpt-4", temperature=0.7, max_tokens=2000),
        "gpt-4-turbo": LLMConfig(model="gpt-4-turbo-preview", temperature=0.7, max_tokens=4000),
        "gpt-4o": LLMConfig(model="gpt-4o", temperature=0.7, max_tokens=4000),
        "gpt-3.5-turbo": LLMConfig(model="gpt-3.5-turbo", temperature=0.7, max_tokens=2000),
    }
    
    def __init__(self, provider: Literal["openai"] = "openai", default_model: str = "gpt-4o", api_key: Optional[str] = None):
        self.default_model = default_model
        if provider == "openai":
            self.provider = OpenAIProvider(api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None,
                 temperature: Optional[float] = None, max_tokens: Optional[int] = None, **kwargs) -> str:
        """Generate a text response"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        config = self._get_config(model, temperature, max_tokens, **kwargs)
        response = self.provider.generate(messages, config)
        return response.content
    
    def generate_with_messages(self, messages: List[Dict[str, str]], model: Optional[str] = None,
                               temperature: Optional[float] = None, max_tokens: Optional[int] = None, **kwargs) -> str:
        """Generate a response with full message history"""
        config = self._get_config(model, temperature, max_tokens, **kwargs)
        response = self.provider.generate(messages, config)
        return response.content
    
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, model: Optional[str] = None,
                     temperature: Optional[float] = None, max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Generate a JSON response"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        config = self._get_config(model, temperature, max_tokens, **kwargs)
        return self.provider.generate_json(messages, config)
    
    def generate_json_with_messages(self, messages: List[Dict[str, str]], model: Optional[str] = None,
                                   temperature: Optional[float] = None, max_tokens: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """Generate a JSON response with full message history"""
        config = self._get_config(model, temperature, max_tokens, **kwargs)
        return self.provider.generate_json(messages, config)
    
    def _get_config(self, model: Optional[str] = None, temperature: Optional[float] = None,
                   max_tokens: Optional[int] = None, **kwargs) -> LLMConfig:
        """Get LLM config with overrides"""
        model_name = model or self.default_model
        
        if model_name in self.MODELS:
            config = self.MODELS[model_name]
        else:
            config = LLMConfig(model=model_name)
        
        if temperature is not None:
            config.temperature = temperature
        if max_tokens is not None:
            config.max_tokens = max_tokens
        
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        return config


# Convenience functions
def generate(prompt: str, **kwargs) -> str:
    """Quick generation function"""
    client = LLMClient()
    return client.generate(prompt, **kwargs)


def generate_json(prompt: str, **kwargs) -> Dict[str, Any]:
    """Quick JSON generation function"""
    client = LLMClient()
    return client.generate_json(prompt, **kwargs)

