"""
PSAVVY AI Engine - Multi-Provider AI Integration
Integrates Claude (Anthropic), Perplexity, and ChatGPT (OpenAI)
for intelligent vulnerability scanning and exploitation assistance.
"""

from .providers import AIProviderManager, ClaudeProvider, PerplexityProvider, ChatGPTProvider
from .analyzer import VulnerabilityAnalyzer
from .payload_generator import PayloadGenerator
from .exploiter import ExploitationAssistant
from .reporter import ReportGenerator
from .researcher import VulnerabilityResearcher

__version__ = "1.0.0"
__all__ = [
    'AIProviderManager',
    'ClaudeProvider',
    'PerplexityProvider',
    'ChatGPTProvider',
    'VulnerabilityAnalyzer',
    'PayloadGenerator',
    'ExploitationAssistant',
    'ReportGenerator',
    'VulnerabilityResearcher'
]
