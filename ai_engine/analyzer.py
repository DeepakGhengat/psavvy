"""
AI-Powered Vulnerability Analyzer
Uses Claude for deep analysis and false positive detection
"""

import os
import json
import glob
from typing import Dict, List, Any, Optional
from .providers import AIProviderManager


class VulnerabilityAnalyzer:
    """
    Analyzes scan results using AI to identify, prioritize, and validate vulnerabilities.
    Uses Claude for deep reasoning and analysis capabilities.
    """

    def __init__(self, ai_manager: AIProviderManager):
        self.ai_manager = ai_manager
        self.system_prompt = """You are an expert security researcher and penetration tester with deep knowledge of:
- OWASP Top 10 vulnerabilities
- CVE analysis and exploitation
- Web application security testing
- Network security assessment
- False positive identification

Analyze security scan results with precision. Provide actionable insights, severity ratings (Critical/High/Medium/Low/Info),
confidence scores (0-100%), and clear remediation steps. Be thorough but concise."""

    def analyze_scan_results(self, output_dir: str) -> Dict[str, Any]:
        """
        Analyze all scan results from output directory
        Returns comprehensive analysis with prioritized findings
        """
        findings = self._collect_findings(output_dir)

        if not findings:
            return {"error": "No scan results found in output directory"}

        # Prepare analysis prompt
        prompt = f"""Analyze these security scan results and provide:

1. **CRITICAL FINDINGS** (immediate action required)
2. **HIGH SEVERITY** (exploit within 24-48 hours)
3. **MEDIUM SEVERITY** (should be addressed soon)
4. **LOW SEVERITY** (minor issues)
5. **FALSE POSITIVE CANDIDATES** (likely not real vulnerabilities)

For each finding, provide:
- Vulnerability type
- Affected asset/URL
- Confidence score (0-100%)
- CVSS score estimate
- Brief exploitation scenario
- Remediation steps

SCAN RESULTS:
{self._format_findings(findings)}

Respond in structured markdown format."""

        analysis = self.ai_manager.query_for_analysis(prompt, self.system_prompt)

        return {
            "raw_findings": findings,
            "ai_analysis": analysis,
            "files_analyzed": list(findings.keys())
        }

    def verify_vulnerability(self, vuln_type: str, raw_result: str, target: str) -> Dict[str, Any]:
        """
        Verify if a specific finding is a true positive or false positive
        """
        prompt = f"""Analyze this potential vulnerability and determine if it's a true positive:

**Vulnerability Type:** {vuln_type}
**Target:** {target}
**Scanner Output:**
```
{raw_result[:3000]}  # Truncate to avoid token limits
```

Provide:
1. **Verdict:** TRUE_POSITIVE / FALSE_POSITIVE / NEEDS_VERIFICATION
2. **Confidence:** 0-100%
3. **Reasoning:** Why you believe this assessment
4. **Verification Steps:** Manual steps to confirm
5. **Evidence Indicators:** What in the output supports your verdict"""

        result = self.ai_manager.query_for_analysis(prompt, self.system_prompt)

        return {
            "vulnerability_type": vuln_type,
            "target": target,
            "ai_verdict": result
        }

    def correlate_findings(self, output_dir: str) -> str:
        """
        Find attack chains and correlations between different vulnerabilities
        """
        findings = self._collect_findings(output_dir)

        prompt = f"""Analyze these security findings and identify:

1. **ATTACK CHAINS**: Multi-step attack paths (e.g., XSS -> Session Hijacking -> Account Takeover)
2. **CORRELATED VULNERABILITIES**: Findings that amplify each other's impact
3. **PIVOT OPPORTUNITIES**: How one compromised asset leads to others
4. **EXPLOITATION SEQUENCE**: Recommended order to exploit vulnerabilities
5. **COMBINED IMPACT**: Overall risk when vulnerabilities are chained

Think like an attacker - how would you combine these findings for maximum impact?

FINDINGS:
{self._format_findings(findings)}

Provide detailed attack scenarios with step-by-step exploitation paths."""

        return self.ai_manager.query_for_analysis(prompt, self.system_prompt)

    def assess_severity(self, vulnerability: str, context: str) -> Dict[str, Any]:
        """
        Provide detailed severity assessment with CVSS-like scoring
        """
        prompt = f"""Calculate security severity for this vulnerability:

**Vulnerability:** {vulnerability}
**Context:** {context}

Provide CVSS v3.1 style assessment:

1. **Attack Vector:** Network/Adjacent/Local/Physical
2. **Attack Complexity:** Low/High
3. **Privileges Required:** None/Low/High
4. **User Interaction:** None/Required
5. **Scope:** Changed/Unchanged
6. **Confidentiality Impact:** None/Low/High
7. **Integrity Impact:** None/Low/High
8. **Availability Impact:** None/Low/High

Calculate:
- Base Score (0.0-10.0)
- Severity Rating (Critical/High/Medium/Low/None)
- Attack difficulty assessment
- Potential business impact"""

        return {
            "vulnerability": vulnerability,
            "severity_assessment": self.ai_manager.query_for_analysis(prompt, self.system_prompt)
        }

    def triage_all_findings(self, output_dir: str) -> str:
        """
        Perform comprehensive triage of all scan results
        Returns prioritized action list
        """
        findings = self._collect_findings(output_dir)

        prompt = f"""Perform security triage on these scan results. Act as a security operations analyst.

Create a prioritized action list:

## IMMEDIATE ACTIONS (Next 1-4 hours)
- Critical vulnerabilities requiring instant attention
- Active exploitation indicators

## SHORT-TERM ACTIONS (Next 24-48 hours)
- High severity issues
- Easily exploitable vulnerabilities

## MEDIUM-TERM ACTIONS (Next week)
- Medium severity findings
- Requires more complex exploitation

## LONG-TERM IMPROVEMENTS (Next month)
- Low severity issues
- Best practice recommendations

For each action item provide:
- [ ] Task description
- Affected asset
- Estimated effort
- Required skills/tools

SCAN RESULTS:
{self._format_findings(findings)}"""

        return self.ai_manager.query_for_analysis(prompt, self.system_prompt)

    def _collect_findings(self, output_dir: str) -> Dict[str, str]:
        """Collect all findings from output directory"""
        findings = {}

        if not os.path.exists(output_dir):
            return findings

        for filepath in glob.glob(os.path.join(output_dir, "*.txt")):
            try:
                with open(filepath, 'r', errors='ignore') as f:
                    content = f.read()
                    if content.strip():  # Only include non-empty files
                        findings[os.path.basename(filepath)] = content
            except Exception as e:
                findings[os.path.basename(filepath)] = f"Error reading file: {str(e)}"

        return findings

    def _format_findings(self, findings: Dict[str, str]) -> str:
        """Format findings for AI prompt"""
        formatted = []
        for filename, content in findings.items():
            # Truncate very large files
            truncated = content[:5000] if len(content) > 5000 else content
            formatted.append(f"=== {filename} ===\n{truncated}\n")

        return "\n".join(formatted)
