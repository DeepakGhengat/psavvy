"""
AI Provider Clients for Claude, Perplexity, and ChatGPT
"""

import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    def query(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass


class ClaudeProvider(AIProvider):
    """Anthropic Claude API Provider - Best for deep analysis and reasoning"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"

    def query(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }

        messages = [{"role": "user", "content": prompt}]

        data = {
            "model": kwargs.get("model", self.model),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": messages
        }

        if system_prompt:
            data["system"] = system_prompt

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]
        except Exception as e:
            return f"Claude API Error: {str(e)}"

    def is_available(self) -> bool:
        return bool(self.api_key)


class PerplexityProvider(AIProvider):
    """Perplexity API Provider - Best for real-time research and CVE lookups"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "llama-3.1-sonar-large-128k-online"

    def query(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.2),
            "return_citations": True,
            "search_recency_filter": kwargs.get("recency", "month")
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Perplexity API Error: {str(e)}"

    def is_available(self) -> bool:
        return bool(self.api_key)


class ChatGPTProvider(AIProvider):
    """OpenAI ChatGPT API Provider - Best for payload generation and reports"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4-turbo-preview"

    def query(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "temperature": kwargs.get("temperature", 0.7)
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"ChatGPT API Error: {str(e)}"

    def is_available(self) -> bool:
        return bool(self.api_key)


class AIProviderManager:
    """
    Manages multiple AI providers and routes queries to appropriate providers
    based on task type for optimal results.
    """

    def __init__(self, config: Dict[str, str]):
        self.providers = {}

        # Initialize providers based on available API keys
        if config.get("ANTHROPIC_API_KEY"):
            self.providers["claude"] = ClaudeProvider(config["ANTHROPIC_API_KEY"])

        if config.get("PERPLEXITY_API_KEY"):
            self.providers["perplexity"] = PerplexityProvider(config["PERPLEXITY_API_KEY"])

        if config.get("OPENAI_API_KEY"):
            self.providers["chatgpt"] = ChatGPTProvider(config["OPENAI_API_KEY"])

    def get_provider(self, name: str) -> Optional[AIProvider]:
        """Get a specific provider by name"""
        return self.providers.get(name)

    def available_providers(self) -> List[str]:
        """List all available providers"""
        return [name for name, provider in self.providers.items() if provider.is_available()]

    def query_for_analysis(self, prompt: str, system_prompt: str = None) -> str:
        """Route analysis queries to Claude (best for reasoning)"""
        if "claude" in self.providers:
            return self.providers["claude"].query(prompt, system_prompt)
        return self._fallback_query(prompt, system_prompt)

    def query_for_research(self, prompt: str, system_prompt: str = None) -> str:
        """Route research queries to Perplexity (best for real-time info)"""
        if "perplexity" in self.providers:
            return self.providers["perplexity"].query(prompt, system_prompt)
        return self._fallback_query(prompt, system_prompt)

    def query_for_generation(self, prompt: str, system_prompt: str = None) -> str:
        """Route generation queries to ChatGPT (best for creative tasks)"""
        if "chatgpt" in self.providers:
            return self.providers["chatgpt"].query(prompt, system_prompt)
        return self._fallback_query(prompt, system_prompt)

    def query_all(self, prompt: str, system_prompt: str = None) -> Dict[str, str]:
        """Query all available providers and return combined results"""
        results = {}
        for name, provider in self.providers.items():
            if provider.is_available():
                results[name] = provider.query(prompt, system_prompt)
        return results

    def _fallback_query(self, prompt: str, system_prompt: str = None) -> str:
        """Fallback to any available provider"""
        for provider in self.providers.values():
            if provider.is_available():
                return provider.query(prompt, system_prompt)
        return "Error: No AI providers available. Please configure API keys."
