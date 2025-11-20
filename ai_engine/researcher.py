"""
AI-Powered Vulnerability Researcher
Uses Perplexity for real-time CVE and exploit research
"""

from typing import Dict, List, Any, Optional
from .providers import AIProviderManager


class VulnerabilityResearcher:
    """
    Conducts real-time vulnerability research using Perplexity AI.
    Searches for CVEs, exploits, PoCs, and latest security information.
    """

    def __init__(self, ai_manager: AIProviderManager):
        self.ai_manager = ai_manager
        self.system_prompt = """You are a cybersecurity researcher with access to real-time information.
Your role is to research vulnerabilities, CVEs, exploits, and security advisories.

When researching, provide:
1. Accurate CVE identifiers and details
2. Exploit availability and public PoCs
3. Affected versions and products
4. Patch status and mitigation
5. Real-world exploitation evidence
6. Latest security advisories

Always cite sources and provide links when available.
Focus on actionable intelligence for security testing."""

    def research_cve(self, cve_id: str) -> str:
        """
        Research a specific CVE for detailed information
        """
        prompt = f"""Research CVE {cve_id} and provide comprehensive details:

## CVE DETAILS

### Basic Information
- CVE ID: {cve_id}
- CVSS Score & Vector
- CWE Classification
- Affected Products/Versions
- Vendor/Advisory Links

### Technical Analysis
- Vulnerability type and root cause
- Attack prerequisites
- Exploitation complexity
- Authentication requirements

### Exploit Intelligence
- Public exploits available? (ExploitDB, GitHub, etc.)
- Metasploit/nuclei modules?
- PoC code links
- In-the-wild exploitation reported?

### Remediation
- Patch availability and version
- Workarounds if no patch
- Detection methods

### References
- NVD link
- Vendor advisory
- Security researcher writeups
- PoC/Exploit links

Provide the most up-to-date information available."""

        return self.ai_manager.query_for_research(prompt, self.system_prompt)

    def find_exploits(self, product: str, version: str = None) -> str:
        """
        Search for known exploits for a product/version
        """
        version_str = f"version {version}" if version else "all versions"

        prompt = f"""Find known exploits and vulnerabilities for {product} ({version_str}):

## EXPLOIT RESEARCH: {product}

### Known CVEs
List all relevant CVEs with:
- CVE ID
- Severity (Critical/High/Medium/Low)
- Brief description
- Exploit available?

### Public Exploits
Search ExploitDB, GitHub, PacketStorm for:
- Exploit title
- Type (RCE, SQLi, XSS, etc.)
- Link/Reference
- Reliability rating

### Metasploit Modules
- Module path
- Description
- Requirements

### Nuclei Templates
- Template ID
- Detection/Exploitation
- Link

### Recent Security Advisories
- Date
- Advisory ID
- Summary
- Patch status

### Attack Surface
- Default ports/services
- Common misconfigurations
- Known weak points

Prioritize by exploitability and impact."""

        return self.ai_manager.query_for_research(prompt, self.system_prompt)

    def research_vulnerability_class(self, vuln_class: str) -> str:
        """
        Research a class of vulnerabilities for testing techniques
        """
        prompt = f"""Research {vuln_class} vulnerabilities comprehensively:

## VULNERABILITY CLASS: {vuln_class}

### Overview
- Technical explanation
- Common causes
- Impact categories

### Detection Methods
- Automated scanning tools
- Manual testing techniques
- Specific payloads/patterns

### Exploitation Techniques
Current methods with examples:
1. Technique name
   - How it works
   - Example payload
   - Success indicators

### Recent Notable Instances
- Recent CVEs of this type
- High-profile breaches
- Bug bounty examples

### WAF/Defense Bypass
- Common protections
- Known bypass techniques
- Evasion payloads

### Prevention & Mitigation
- Secure coding practices
- Configuration hardening
- Detection/monitoring

### Testing Methodology
Step-by-step testing approach:
1. [Step]
2. [Step]
...

### Tools & Resources
- Specialized scanners
- Payload repositories
- Learning resources

Provide actionable testing intelligence."""

        return self.ai_manager.query_for_research(prompt, self.system_prompt)

    def get_latest_vulns(self, technology: str, days: int = 30) -> str:
        """
        Get latest vulnerabilities for a technology
        """
        prompt = f"""Find the latest vulnerabilities disclosed for {technology} in the past {days} days:

## LATEST VULNERABILITIES: {technology}

### Critical/High Severity (Last {days} days)

| CVE ID | Severity | Description | Exploit? | Patch? |
|--------|----------|-------------|----------|--------|

### Details for Most Critical

For each critical/high CVE:
- **CVE-XXXX-XXXXX**
  - CVSS: X.X
  - Description
  - Affected versions
  - Exploit status
  - Remediation

### Emerging Threats
- Actively exploited vulnerabilities
- Zero-days
- Trending in security community

### Patch Tuesday / Updates
Recent security updates from vendor

### Security Advisories
- Vendor advisories
- CERT alerts
- Security researcher disclosures

Focus on actionable items for security testing."""

        return self.ai_manager.query_for_research(prompt, self.system_prompt)

    def research_target_technology(self, target: str) -> str:
        """
        Research security information for a target domain/technology
        """
        prompt = f"""Research security-relevant information for: {target}

## TARGET INTELLIGENCE: {target}

### Technology Fingerprint
Based on public information:
- Web technologies likely used
- Infrastructure hints
- Known software versions

### Historical Vulnerabilities
- Past CVEs affecting similar technology
- Previous security incidents (if public)
- Bug bounty findings (public)

### Attack Surface Analysis
- Common entry points
- Likely vulnerability types
- Testing priorities

### Relevant Exploits
- Exploits for detected technologies
- Default credential lists
- Known misconfigurations

### Security Posture Indicators
- Security headers typically seen
- WAF/CDN indications
- Security.txt, bug bounty program

### Recommended Testing Focus
Based on technology stack:
1. [Vulnerability type] - Why
2. [Vulnerability type] - Why
...

### OSINT Resources
- Shodan/Censys queries
- GitHub dorks
- Google dorks

Provide actionable reconnaissance intelligence."""

        return self.ai_manager.query_for_research(prompt, self.system_prompt)

    def find_poc_code(self, cve_or_vuln: str) -> str:
        """
        Search for proof-of-concept code
        """
        prompt = f"""Find proof-of-concept code and exploit resources for: {cve_or_vuln}

## POC/EXPLOIT SEARCH

### GitHub Repositories
- Repository URL
- Description
- Language
- Last updated
- Stars/reliability indicator

### ExploitDB Entries
- EDB-ID
- Title
- Type
- Platform
- Link

### Other Sources
- PacketStorm
- VulDB
- 0day.today
- Security blogs

### Code Snippets
If available, provide:
```
[Relevant PoC code snippet]
```

### Usage Instructions
How to use the PoC:
1. Prerequisites
2. Configuration
3. Execution
4. Expected output

### Modifications Needed
- Customization required
- Target-specific changes
- Payload modifications

### Quality Assessment
- Code maturity
- Reliability
- Safety for testing

Prioritize reliable, well-documented PoCs."""

        return self.ai_manager.query_for_research(prompt, self.system_prompt)

    def get_waf_bypass_research(self, waf_name: str) -> str:
        """
        Research WAF bypass techniques
        """
        prompt = f"""Research bypass techniques for {waf_name}:

## WAF BYPASS RESEARCH: {waf_name}

### WAF Characteristics
- Vendor/version info
- Detection methods
- Known signatures

### Documented Bypasses
From security research:
1. **Bypass Name**
   - Technique
   - Payload example
   - Source/reference

### Payload Transformations
Effective encodings and mutations:
- URL encoding variations
- Unicode tricks
- Comment insertion
- Case manipulation

### Recent Research
- Conference talks
- Blog posts
- Security papers

### Testing Methodology
How to test for bypasses:
1. [Step]
2. [Step]

### Working Payloads
For common vulnerability types:
- XSS: [bypass payloads]
- SQLi: [bypass payloads]
- Command injection: [bypass payloads]

### Tools
- Automated bypass tools
- Fuzzing approaches

Provide tested, reliable bypass techniques."""

        return self.ai_manager.query_for_research(prompt, self.system_prompt)

    def research_exploitation_chain(self, findings: List[str]) -> str:
        """
        Research how to chain multiple findings
        """
        findings_str = "\n".join([f"- {f}" for f in findings])

        prompt = f"""Research exploitation chains for these findings:

{findings_str}

## EXPLOITATION CHAIN RESEARCH

### Chain Possibilities
Based on public research and known techniques:

1. **Chain: [Name]**
   - Step 1: [Finding] -> [Action]
   - Step 2: [Finding] -> [Action]
   - Final impact: [What's achieved]
   - Public examples: [Similar chains in wild]

### Required Conditions
For each chain:
- Prerequisites
- Success likelihood
- Complexity

### Similar Real-World Attacks
- Case studies
- CTF writeups
- Bug bounty reports

### Recommended Chain
Most likely to succeed based on research:
- Detailed steps
- Tools needed
- Expected outcome

### Alternative Approaches
If primary chain fails

Research similar attack patterns and provide evidence-based recommendations."""

        return self.ai_manager.query_for_research(prompt, self.system_prompt)
