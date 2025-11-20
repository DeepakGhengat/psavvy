"""
AI-Powered Payload Generator
Uses ChatGPT for creative payload generation with context awareness
"""

from typing import Dict, List, Any, Optional
from .providers import AIProviderManager


class PayloadGenerator:
    """
    Generates context-aware security testing payloads using AI.
    Uses ChatGPT for creative generation with WAF bypass capabilities.
    """

    def __init__(self, ai_manager: AIProviderManager):
        self.ai_manager = ai_manager
        self.system_prompt = """You are an expert security researcher specializing in payload crafting for:
- XSS (Cross-Site Scripting) with WAF bypass
- SQL Injection with various DBMS
- Command Injection with shell escape
- SSTI (Server-Side Template Injection)
- SSRF (Server-Side Request Forgery)
- Path Traversal / LFI

Generate payloads that are:
1. Context-aware (considering filters, WAF, technology stack)
2. Evasive (bypass common security measures)
3. Effective (achieve the intended security test goal)
4. Safe for authorized testing (use harmless indicators like alert, id, whoami)

IMPORTANT: These payloads are for authorized security testing only."""

    def generate_xss_payloads(self, context: Dict[str, Any]) -> str:
        """
        Generate XSS payloads optimized for specific context
        """
        prompt = f"""Generate 15 advanced XSS payloads for this context:

**Target Context:**
- Input location: {context.get('input_location', 'unknown')}
- Technology: {context.get('technology', 'unknown')}
- WAF detected: {context.get('waf', 'unknown')}
- Encoding needed: {context.get('encoding', 'none')}
- Character restrictions: {context.get('restrictions', 'none')}
- Browser target: {context.get('browser', 'all')}

Generate payloads in these categories:
1. **Polyglot payloads** (work in multiple contexts)
2. **WAF bypass variants** (encode/obfuscate)
3. **Event handler based** (onerror, onload, etc.)
4. **DOM-based XSS** (client-side manipulation)
5. **Blind XSS** (callback payloads)

For each payload provide:
- The payload
- Execution context (HTML/JS/attribute)
- Bypass technique used
- Expected behavior

Format as a ready-to-use payload list."""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_sqli_payloads(self, context: Dict[str, Any]) -> str:
        """
        Generate SQL injection payloads for specific DBMS and context
        """
        prompt = f"""Generate 15 advanced SQL injection payloads for:

**Target Context:**
- DBMS: {context.get('dbms', 'unknown')}
- Injection point: {context.get('injection_point', 'parameter')}
- Quote type: {context.get('quote_type', 'unknown')}
- WAF/Filter: {context.get('waf', 'none')}
- Blind/Error-based: {context.get('technique', 'both')}

Generate payloads for:
1. **Authentication bypass**
2. **Union-based extraction**
3. **Error-based extraction**
4. **Blind boolean-based**
5. **Time-based blind**
6. **Stacked queries**

Include:
- Raw payload
- URL-encoded version
- Tamper script compatible format
- Expected response indicator

Target databases: MySQL, PostgreSQL, MSSQL, Oracle, SQLite"""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_ssti_payloads(self, context: Dict[str, Any]) -> str:
        """
        Generate SSTI payloads for various template engines
        """
        prompt = f"""Generate SSTI (Server-Side Template Injection) payloads for:

**Target Context:**
- Template engine: {context.get('engine', 'unknown')}
- Technology: {context.get('technology', 'Python/Jinja2')}
- Goal: {context.get('goal', 'RCE')}
- Restrictions: {context.get('restrictions', 'none')}

Generate payloads for these engines:
1. **Jinja2** (Python)
2. **Twig** (PHP)
3. **Freemarker** (Java)
4. **Velocity** (Java)
5. **Smarty** (PHP)
6. **ERB** (Ruby)

Include:
- Detection payloads ({{{{7*7}}}})
- Information disclosure
- File read payloads
- RCE payloads
- Bypass techniques for common filters

Provide 3 payloads per engine with explanations."""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_ssrf_payloads(self, context: Dict[str, Any]) -> str:
        """
        Generate SSRF payloads with bypass techniques
        """
        prompt = f"""Generate SSRF payloads for:

**Target Context:**
- Callback server: {context.get('callback', 'BURP_COLLAB')}
- Protocol: {context.get('protocol', 'HTTP')}
- Bypass needed: {context.get('bypass', 'IP filtering')}
- Cloud provider: {context.get('cloud', 'unknown')}

Generate payloads for:
1. **Basic SSRF** (localhost, 127.0.0.1)
2. **IP bypass** (decimal, octal, hex encoding)
3. **DNS rebinding** techniques
4. **Protocol smuggling** (gopher, file, dict)
5. **Cloud metadata** (AWS, GCP, Azure)
6. **URL parser differentials**

Include:
- Raw payload
- Encoded variants
- Expected response/indicator
- What sensitive data it accesses

Provide 20 ready-to-use payloads."""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_command_injection(self, context: Dict[str, Any]) -> str:
        """
        Generate command injection payloads
        """
        prompt = f"""Generate OS command injection payloads for:

**Target Context:**
- OS: {context.get('os', 'Linux')}
- Shell: {context.get('shell', 'bash')}
- Injection point: {context.get('point', 'parameter')}
- Filters: {context.get('filters', 'none')}

Generate payloads using:
1. **Command separators** (; | || && \\n)
2. **Command substitution** ($() ``)
3. **Encoding bypass** (hex, base64)
4. **Wildcard abuse** (/???/???)
5. **Environment variables**
6. **Time-based blind** (sleep, ping)

Include:
- Detection payloads
- Data exfiltration payloads
- Reverse shell payloads
- Blind command execution

Provide both Linux and Windows variants."""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_lfi_payloads(self, context: Dict[str, Any]) -> str:
        """
        Generate LFI/Path Traversal payloads
        """
        prompt = f"""Generate LFI/Path Traversal payloads for:

**Target Context:**
- OS: {context.get('os', 'Linux')}
- Technology: {context.get('technology', 'PHP')}
- Filter bypass: {context.get('filters', 'basic')}
- Goal: {context.get('goal', 'file read')}

Generate payloads for:
1. **Basic traversal** (../)
2. **Encoding bypass** (double URL, unicode)
3. **Null byte injection** (%00)
4. **Wrapper abuse** (php://filter, zip://)
5. **Log poisoning** for RCE
6. **Interesting files** to target

Target files:
- Linux: /etc/passwd, /etc/shadow, SSH keys, configs
- Windows: boot.ini, win.ini, SAM, web.config
- Application: config files, logs, source code

Provide 25 payloads with expected outputs."""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def generate_custom_payloads(self, vuln_type: str, context: Dict[str, Any]) -> str:
        """
        Generate custom payloads for any vulnerability type
        """
        prompt = f"""Generate advanced security testing payloads for:

**Vulnerability Type:** {vuln_type}
**Context:** {json.dumps(context, indent=2) if isinstance(context, dict) else context}

Requirements:
1. Generate 10-15 unique payloads
2. Include bypass techniques
3. Provide encoded variants
4. Explain expected behavior
5. Rate effectiveness (1-10)

Format each payload as:
```
Payload: [actual payload]
Encoded: [URL/HTML encoded]
Bypass: [technique used]
Expected: [what happens on success]
Rating: [1-10]
```"""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)

    def optimize_payload(self, payload: str, target_waf: str) -> str:
        """
        Optimize an existing payload for WAF bypass
        """
        prompt = f"""Optimize this security testing payload to bypass {target_waf}:

**Original Payload:**
```
{payload}
```

Provide:
1. **5 optimized variants** with different bypass techniques
2. **Encoding transformations** (URL, HTML, Unicode, Base64)
3. **Obfuscation methods** (case variation, comments, whitespace)
4. **Alternative syntax** (different functions, operators)
5. **Chunked/split versions**

For each variant explain:
- What bypass technique is used
- Why it might evade the WAF
- How to test if it works"""

        return self.ai_manager.query_for_generation(prompt, self.system_prompt)


# Import json for custom_payloads
import json
