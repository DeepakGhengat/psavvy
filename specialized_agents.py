"""
PSAVVY AI - Advanced Autonomous Agent System v2.0
Specialized agents for each vulnerability type with parallel execution

Features:
- 15+ specialized vulnerability agents
- Parallel multi-agent execution
- Integrates all 30+ tools from PSAVVY
- Results saved to output/ folder
"""

import subprocess
import os
import json
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import threading
import queue

# Import AI providers
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ai_engine import AIProviderManager
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


class VulnSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Finding:
    """Represents a discovered vulnerability"""
    vuln_type: str
    target: str
    severity: VulnSeverity
    evidence: str
    poc: str = ""
    validated: bool = False
    exploitable: bool = False
    impact: str = ""
    agent_name: str = ""
    timestamp: str = ""
    confidence: int = 0  # 0-100%


@dataclass
class AgentTask:
    """Task for an agent to execute"""
    task_id: str
    task_type: str
    target: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    depends_on: List[str] = field(default_factory=list)
    status: AgentStatus = AgentStatus.IDLE
    result: Any = None


class BaseSpecializedAgent(ABC):
    """Base class for specialized vulnerability agents"""

    def __init__(self, ai_manager: AIProviderManager, name: str, output_dir: str = "output"):
        self.ai_manager = ai_manager
        self.name = name
        self.status = AgentStatus.IDLE
        self.findings: List[Finding] = []
        self.logs: List[str] = []
        self.output_dir = output_dir
        self.lock = threading.Lock()

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{self.name}] {message}"
        with self.lock:
            self.logs.append(log_entry)
            print(log_entry)

    def execute_tool(self, command: str, timeout: int = 300) -> Tuple[str, int]:
        """Execute a security tool and return output"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.path.dirname(os.path.abspath(__file__))
            )
            return result.stdout + result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "Command timed out", -1
        except Exception as e:
            return f"Error: {str(e)}", -1

    def save_finding(self, finding: Finding):
        """Save finding to output directory"""
        finding.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        finding.agent_name = self.name

        with self.lock:
            self.findings.append(finding)

            # Save to individual file
            filename = f"{self.name}_{finding.vuln_type.replace(' ', '_')}_{int(time.time())}.json"
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w') as f:
                json.dump({
                    "vuln_type": finding.vuln_type,
                    "target": finding.target,
                    "severity": finding.severity.value,
                    "evidence": finding.evidence,
                    "poc": finding.poc,
                    "validated": finding.validated,
                    "exploitable": finding.exploitable,
                    "impact": finding.impact,
                    "agent": finding.agent_name,
                    "timestamp": finding.timestamp,
                    "confidence": finding.confidence
                }, f, indent=2)

    @abstractmethod
    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        """Main scanning method - must be implemented by each agent"""
        pass


# ============================================================================
# SPECIALIZED AGENTS - One for each vulnerability type
# ============================================================================

class XSSAgent(BaseSpecializedAgent):
    """Specialized agent for Cross-Site Scripting"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "XSSAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting XSS scan on {len(targets)} targets")
        findings = []

        # Tool 1: Dalfox
        self.log("Running dalfox scanner...")
        for target in targets[:100]:  # Limit for performance
            output, _ = self.execute_tool(f"echo '{target}' | dalfox pipe --silence --format json 2>/dev/null", timeout=60)
            if "POC" in output or "Vulnerable" in output.lower():
                finding = Finding(
                    vuln_type="Cross-Site Scripting (XSS)",
                    target=target,
                    severity=VulnSeverity.HIGH,
                    evidence=output[:1000],
                    confidence=85
                )
                self.save_finding(finding)
                findings.append(finding)

        # Tool 2: XSStrike
        self.log("Running XSStrike...")
        urls_file = os.path.join(self.output_dir, "filterDNS.txt")
        if os.path.exists(urls_file):
            output, _ = self.execute_tool(
                f"xargs -a {urls_file} -I{{}} -P 3 sh -c 'python3 Tools/XSStrike/xsstrike.py -u {{}} --crawl' 2>/dev/null | head -200",
                timeout=300
            )
            if "vulnerable" in output.lower():
                # Parse XSStrike output
                for line in output.split('\n'):
                    if 'vulnerable' in line.lower() or 'xss' in line.lower():
                        finding = Finding(
                            vuln_type="XSS",
                            target=line[:200],
                            severity=VulnSeverity.HIGH,
                            evidence=line,
                            confidence=75
                        )
                        self.save_finding(finding)
                        findings.append(finding)

        # Tool 3: Gxss for reflected XSS
        self.log("Scanning for reflected XSS...")
        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")
        if os.path.exists(all_urls):
            output, _ = self.execute_tool(f"cat {all_urls} | Gxss -p XSS 2>/dev/null | head -50")
            if output:
                for url in output.strip().split('\n'):
                    if url.startswith('http'):
                        finding = Finding(
                            vuln_type="Reflected XSS",
                            target=url,
                            severity=VulnSeverity.MEDIUM,
                            evidence=f"Reflection detected: {url}",
                            confidence=60
                        )
                        self.save_finding(finding)
                        findings.append(finding)

        self.log(f"XSS scan complete: {len(findings)} findings")
        return findings


class SQLiAgent(BaseSpecializedAgent):
    """Specialized agent for SQL Injection"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "SQLiAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting SQL injection scan on {len(targets)} targets")
        findings = []

        # Extract potential SQLi URLs
        self.log("Identifying SQL injection candidates...")
        sqli_urls_file = os.path.join(self.output_dir, "sqli_urls.txt")

        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")
        if os.path.exists(all_urls):
            self.execute_tool(f"cat {all_urls} | gf sqli > {sqli_urls_file} 2>/dev/null")

        if not os.path.exists(sqli_urls_file):
            self.log("No SQL injection candidates found")
            return findings

        # Tool 1: SQLMap with basic scan
        self.log("Running sqlmap (quick scan)...")
        output, _ = self.execute_tool(
            f"python3 Tools/sqlmap/sqlmap.py -m '{sqli_urls_file}' --batch --level=2 --risk=2 --threads=5 --smart 2>/dev/null | head -300",
            timeout=600
        )

        # Parse sqlmap output
        if "is vulnerable" in output.lower() or "injectable" in output.lower():
            for line in output.split('\n'):
                if 'Parameter:' in line or 'vulnerable' in line.lower():
                    finding = Finding(
                        vuln_type="SQL Injection",
                        target=line[:200],
                        severity=VulnSeverity.CRITICAL,
                        evidence=output[:2000],
                        confidence=90
                    )
                    self.save_finding(finding)
                    findings.append(finding)

        # Save detailed results
        result_file = os.path.join(self.output_dir, "sqli_results.txt")
        with open(result_file, 'w') as f:
            f.write(output)

        self.log(f"SQL injection scan complete: {len(findings)} findings")
        return findings


class SSRFAgent(BaseSpecializedAgent):
    """Specialized agent for Server-Side Request Forgery"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "SSRFAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting SSRF scan on {len(targets)} targets")
        findings = []

        callback_url = parameters.get('BURP_COLLAB_URL', 'http://interact.sh')

        # Tool 1: Extract SSRF candidates
        self.log("Identifying SSRF candidates...")
        ssrf_urls_file = os.path.join(self.output_dir, "ssrf_urls.txt")
        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")

        if os.path.exists(all_urls):
            self.execute_tool(f"cat {all_urls} | gf ssrf > {ssrf_urls_file} 2>/dev/null")

        # Tool 2: ssrfuzz
        if os.path.exists(ssrf_urls_file):
            self.log("Running ssrfuzz...")
            output, _ = self.execute_tool(
                f"cat {ssrf_urls_file} | ssrfuzz scan -x GET,POST 2>/dev/null | head -100",
                timeout=300
            )

            if output:
                result_file = os.path.join(self.output_dir, "ssrfuzz_results.txt")
                with open(result_file, 'w') as f:
                    f.write(output)

                for line in output.split('\n'):
                    if 'vulnerable' in line.lower() or 'ssrf' in line.lower():
                        finding = Finding(
                            vuln_type="SSRF",
                            target=line[:200],
                            severity=VulnSeverity.HIGH,
                            evidence=line,
                            confidence=70
                        )
                        self.save_finding(finding)
                        findings.append(finding)

        # Tool 3: bssrf (bulk SSRF)
        self.log("Running bulk SSRF check...")
        domains_file = os.path.join(self.output_dir, "nonhttpsfilterDNS.txt")
        if os.path.exists(domains_file):
            output, _ = self.execute_tool(
                f"cat {domains_file} | gau | bssrf -v -t 10 -l {callback_url} 2>/dev/null | head -100",
                timeout=300
            )

            if output:
                result_file = os.path.join(self.output_dir, "bulkssrf_result.txt")
                with open(result_file, 'w') as f:
                    f.write(output)

        # Tool 4: autossrf
        self.log("Running autossrf...")
        if os.path.exists(all_urls):
            output, _ = self.execute_tool(
                f"python3 Tools/autossrf/autossrf.py -f {all_urls} -v 2>/dev/null | head -100",
                timeout=300
            )

            if "vulnerable" in output.lower():
                finding = Finding(
                    vuln_type="SSRF",
                    target="Multiple endpoints",
                    severity=VulnSeverity.HIGH,
                    evidence=output[:1000],
                    confidence=75
                )
                self.save_finding(finding)
                findings.append(finding)

        self.log(f"SSRF scan complete: {len(findings)} findings")
        return findings


class SSTIAgent(BaseSpecializedAgent):
    """Specialized agent for Server-Side Template Injection"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "SSTIAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting SSTI scan on {len(targets)} targets")
        findings = []

        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")

        if os.path.exists(all_urls):
            self.log("Running SSTImap...")
            output, _ = self.execute_tool(
                f"python3 Tools/SSTImap/sstimap.py --load-urls {all_urls} -A --delay 2 -l 3 2>/dev/null | head -200",
                timeout=600
            )

            result_file = os.path.join(self.output_dir, "SSTI_scans.txt")
            with open(result_file, 'w') as f:
                f.write(output)

            if "confirmed" in output.lower() or "injectable" in output.lower():
                for line in output.split('\n'):
                    if 'injectable' in line.lower() or 'vulnerable' in line.lower():
                        finding = Finding(
                            vuln_type="Server-Side Template Injection",
                            target=line[:200],
                            severity=VulnSeverity.CRITICAL,
                            evidence=output[:2000],
                            confidence=85
                        )
                        self.save_finding(finding)
                        findings.append(finding)

        self.log(f"SSTI scan complete: {len(findings)} findings")
        return findings


class CommandInjectionAgent(BaseSpecializedAgent):
    """Specialized agent for Command Injection"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "CommandInjectionAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting command injection scan on {len(targets)} targets")
        findings = []

        domains_file = os.path.join(self.output_dir, "filterDNS.txt")

        if os.path.exists(domains_file):
            self.log("Running commix...")
            output, _ = self.execute_tool(
                f"python3 Tools/commix/commix.py -m {domains_file} --batch --crawl=3 --smart 2>/dev/null | head -200",
                timeout=600
            )

            result_file = os.path.join(self.output_dir, "commixlogs.txt")
            with open(result_file, 'w') as f:
                f.write(output)

            if "is vulnerable" in output.lower() or "injectable" in output.lower():
                for line in output.split('\n'):
                    if 'vulnerable' in line.lower():
                        finding = Finding(
                            vuln_type="Command Injection",
                            target=line[:200],
                            severity=VulnSeverity.CRITICAL,
                            evidence=output[:2000],
                            confidence=90
                        )
                        self.save_finding(finding)
                        findings.append(finding)

        self.log(f"Command injection scan complete: {len(findings)} findings")
        return findings


class LFIAgent(BaseSpecializedAgent):
    """Specialized agent for Local File Inclusion"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "LFIAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting LFI scan on {len(targets)} targets")
        findings = []

        # Extract LFI candidates
        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")
        lfi_params_file = os.path.join(self.output_dir, "lfi_params.txt")

        if os.path.exists(all_urls):
            self.log("Extracting LFI parameters...")
            self.execute_tool(f"cat {all_urls} | gf lfi > {lfi_params_file} 2>/dev/null")

            if os.path.exists(lfi_params_file):
                with open(lfi_params_file, 'r') as f:
                    lfi_urls = [line.strip() for line in f if line.strip()][:50]

                # Test LFI payloads
                lfi_payloads = [
                    "....//....//....//etc/passwd",
                    "../../../etc/passwd%00",
                    "..%2f..%2f..%2fetc/passwd"
                ]

                for url in lfi_urls:
                    for payload in lfi_payloads:
                        test_url = url.replace("FUZZ", payload) if "FUZZ" in url else f"{url}{payload}"
                        output, _ = self.execute_tool(f"curl -s '{test_url}' 2>/dev/null | head -20", timeout=30)

                        if "root:" in output or "bin/bash" in output:
                            finding = Finding(
                                vuln_type="Local File Inclusion",
                                target=url,
                                severity=VulnSeverity.HIGH,
                                evidence=output[:500],
                                poc=f"curl '{test_url}'",
                                confidence=85
                            )
                            self.save_finding(finding)
                            findings.append(finding)
                            break  # Found LFI, move to next URL

        self.log(f"LFI scan complete: {len(findings)} findings")
        return findings


class SubdomainTakeoverAgent(BaseSpecializedAgent):
    """Specialized agent for Subdomain Takeover"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "SubdomainTakeoverAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting subdomain takeover scan")
        findings = []

        subdomains_file = os.path.join(self.output_dir, "nonhttpsfilterDNS.txt")

        if os.path.exists(subdomains_file):
            # Tool 1: subzy
            self.log("Running subzy...")
            output, _ = self.execute_tool(
                f"./Tools/subzy/subzy run --targets {subdomains_file} --hide_fails 2>/dev/null",
                timeout=300
            )

            result_file = os.path.join(self.output_dir, "Subdomaintakeover.txt")
            with open(result_file, 'w') as f:
                f.write(output)

            if "vulnerable" in output.lower() or "takeover" in output.lower():
                for line in output.split('\n'):
                    if 'vulnerable' in line.lower():
                        finding = Finding(
                            vuln_type="Subdomain Takeover",
                            target=line[:200],
                            severity=VulnSeverity.HIGH,
                            evidence=line,
                            confidence=80
                        )
                        self.save_finding(finding)
                        findings.append(finding)

            # Tool 2: Subhunter
            self.log("Running Subhunter...")
            output2, _ = self.execute_tool(
                f"./Tools/Subhunter/subhunter -l {subdomains_file} 2>/dev/null",
                timeout=300
            )

            result_file2 = os.path.join(self.output_dir, "Subdomaintakeover1.txt")
            with open(result_file2, 'w') as f:
                f.write(output2)

        self.log(f"Subdomain takeover scan complete: {len(findings)} findings")
        return findings


class CSRFAgent(BaseSpecializedAgent):
    """Specialized agent for CSRF"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "CSRFAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting CSRF scan on {len(targets)} targets")
        findings = []

        csrf_dir = os.path.join(self.output_dir, "csrf")
        os.makedirs(csrf_dir, exist_ok=True)

        domains_file = os.path.join(self.output_dir, "nonhttpsfilterDNS.txt")

        if os.path.exists(domains_file):
            self.log("Running xsrfprobe...")
            # Run on subset to avoid timeout
            output, _ = self.execute_tool(
                f"head -20 {domains_file} | xargs -I{{}} sh -c 'xsrfprobe -u {{}} -d 3 --crawl -o {csrf_dir}/ --no-verify' 2>/dev/null",
                timeout=600
            )

            # Check results
            for csrf_file in os.listdir(csrf_dir):
                filepath = os.path.join(csrf_dir, csrf_file)
                if os.path.isfile(filepath):
                    with open(filepath, 'r') as f:
                        content = f.read()
                        if "vulnerable" in content.lower() or "csrf" in content.lower():
                            finding = Finding(
                                vuln_type="CSRF",
                                target=csrf_file,
                                severity=VulnSeverity.MEDIUM,
                                evidence=content[:500],
                                confidence=70
                            )
                            self.save_finding(finding)
                            findings.append(finding)

        self.log(f"CSRF scan complete: {len(findings)} findings")
        return findings


class HTTPSmugglingAgent(BaseSpecializedAgent):
    """Specialized agent for HTTP Request Smuggling"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "HTTPSmugglingAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting HTTP smuggling scan")
        findings = []

        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")

        if os.path.exists(all_urls):
            self.log("Running smuggler...")
            output, _ = self.execute_tool(
                f"cat {all_urls} | head -50 | python3 Tools/smuggler/smuggler.py -m GET,POST 2>/dev/null",
                timeout=300
            )

            result_file = os.path.join(self.output_dir, "smuggler_results.txt")
            with open(result_file, 'w') as f:
                f.write(output)

            if "vulnerable" in output.lower() or "smuggling" in output.lower():
                finding = Finding(
                    vuln_type="HTTP Request Smuggling",
                    target="Multiple endpoints",
                    severity=VulnSeverity.CRITICAL,
                    evidence=output[:1000],
                    confidence=75
                )
                self.save_finding(finding)
                findings.append(finding)

        self.log(f"HTTP smuggling scan complete: {len(findings)} findings")
        return findings


class OpenRedirectAgent(BaseSpecializedAgent):
    """Specialized agent for Open Redirect"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "OpenRedirectAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting open redirect scan")
        findings = []

        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")

        if os.path.exists(all_urls):
            self.log("Running Oralyzer...")
            output, _ = self.execute_tool(
                f"python3 Tools/Oralyzer/oralyzer.py -l {all_urls} -crlf 2>/dev/null | head -100",
                timeout=300
            )

            result_file = os.path.join(self.output_dir, "OpenRedirect.txt")
            with open(result_file, 'w') as f:
                f.write(output)

            if "vulnerable" in output.lower() or "redirect" in output.lower():
                for line in output.split('\n'):
                    if 'vulnerable' in line.lower() or 'redirect' in line.lower():
                        finding = Finding(
                            vuln_type="Open Redirect",
                            target=line[:200],
                            severity=VulnSeverity.MEDIUM,
                            evidence=line,
                            confidence=70
                        )
                        self.save_finding(finding)
                        findings.append(finding)

        self.log(f"Open redirect scan complete: {len(findings)} findings")
        return findings


class NucleiAgent(BaseSpecializedAgent):
    """Specialized agent for Nuclei template-based scanning"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "NucleiAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting Nuclei scan")
        findings = []

        domains_file = os.path.join(self.output_dir, "filterDNS.txt")
        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")

        # Scan domains
        if os.path.exists(domains_file):
            self.log("Running Nuclei on domains...")
            output, _ = self.execute_tool(
                f"nuclei -l {domains_file} -t Tools/nuclei-templates/ -severity critical,high -o {self.output_dir}/nuclei_abstract_scan.txt 2>/dev/null",
                timeout=600
            )

        # Scan URLs
        if os.path.exists(all_urls):
            self.log("Running Nuclei on URLs...")
            output2, _ = self.execute_tool(
                f"nuclei -l {all_urls} -t Tools/nuclei-templates/ -severity critical,high -o {self.output_dir}/nuclei_fullurls_scan.txt 2>/dev/null",
                timeout=600
            )

        # Parse results
        for result_file in ["nuclei_abstract_scan.txt", "nuclei_fullurls_scan.txt"]:
            filepath = os.path.join(self.output_dir, result_file)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    for line in f:
                        if line.strip():
                            # Parse nuclei output format
                            finding = Finding(
                                vuln_type="Nuclei Detection",
                                target=line[:200],
                                severity=VulnSeverity.HIGH,
                                evidence=line,
                                confidence=80
                            )
                            self.save_finding(finding)
                            findings.append(finding)

        self.log(f"Nuclei scan complete: {len(findings)} findings")
        return findings


class CVESeekerAgent(BaseSpecializedAgent):
    """Specialized agent for CVE detection"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "CVESeekerAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting CVE detection scan")
        findings = []

        domains_file = os.path.join(self.output_dir, "nonhttpsfilterDNS.txt")

        if os.path.exists(domains_file):
            self.log("Running CVESeeker...")
            output, _ = self.execute_tool(
                f"python3 Tools/CVESeeker/cveSeeker.py --file {domains_file} --project CVESProject 2>/dev/null",
                timeout=600
            )

            result_file = os.path.join(self.output_dir, "CVEScanResult.txt")
            with open(result_file, 'w') as f:
                f.write(output)

            # Move project folder
            if os.path.exists("CVESProject"):
                import shutil
                shutil.move("CVESProject", self.output_dir)

            if "CVE-" in output:
                for line in output.split('\n'):
                    if 'CVE-' in line:
                        finding = Finding(
                            vuln_type="CVE Detected",
                            target=line[:200],
                            severity=VulnSeverity.HIGH,
                            evidence=line,
                            confidence=85
                        )
                        self.save_finding(finding)
                        findings.append(finding)

        self.log(f"CVE detection complete: {len(findings)} findings")
        return findings


class NmapVulnAgent(BaseSpecializedAgent):
    """Specialized agent for Nmap vulnerability scanning"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "NmapVulnAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting Nmap vulnerability scan")
        findings = []

        domains_file = os.path.join(self.output_dir, "nonhttpsfilterDNS.txt")

        if os.path.exists(domains_file):
            self.log("Running Nmap with vulnerability scripts...")
            output, _ = self.execute_tool(
                f"sudo nmap -sV -sC -Pn --script='Tools/freevulnsearch/freevulnsearch.nse','Tools/nmap-vulners/vulners.nse','Tools/vulscan/vulscan.nse' -oN {self.output_dir}/nmapScan.txt -iL {domains_file} --top-ports 100 2>/dev/null",
                timeout=1800  # 30 min for nmap
            )

            result_file = os.path.join(self.output_dir, "nmapScan.txt")
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    content = f.read()
                    if "CVE-" in content or "vulnerable" in content.lower():
                        for line in content.split('\n'):
                            if 'CVE-' in line or 'vulnerable' in line.lower():
                                finding = Finding(
                                    vuln_type="Nmap Vulnerability Detection",
                                    target=line[:200],
                                    severity=VulnSeverity.MEDIUM,
                                    evidence=line,
                                    confidence=75
                                )
                                self.save_finding(finding)
                                findings.append(finding)

        self.log(f"Nmap scan complete: {len(findings)} findings")
        return findings


class NoSQLiAgent(BaseSpecializedAgent):
    """Specialized agent for NoSQL Injection"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "NoSQLiAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting NoSQL injection scan")
        findings = []

        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")

        if os.path.exists(all_urls):
            self.log("Running nosqli scanner...")
            output, _ = self.execute_tool(
                f"head -50 {all_urls} | xargs -I{{}} sh -c 'nosqli scan --insecure -t {{}}' 2>/dev/null | head -100",
                timeout=300
            )

            result_file = os.path.join(self.output_dir, "Nosqli_Scan_results.txt")
            with open(result_file, 'w') as f:
                f.write(output)

            if "vulnerable" in output.lower() or "injection" in output.lower():
                for line in output.split('\n'):
                    if 'vulnerable' in line.lower():
                        finding = Finding(
                            vuln_type="NoSQL Injection",
                            target=line[:200],
                            severity=VulnSeverity.HIGH,
                            evidence=line,
                            confidence=80
                        )
                        self.save_finding(finding)
                        findings.append(finding)

        self.log(f"NoSQL injection scan complete: {len(findings)} findings")
        return findings


class HostHeaderInjectionAgent(BaseSpecializedAgent):
    """Specialized agent for Host Header Injection"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "HostHeaderInjectionAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting host header injection scan")
        findings = []

        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")

        if os.path.exists(all_urls):
            self.log("Running Host Header Injection scanner...")
            output, _ = self.execute_tool(
                f"bash Tools/Host-Header-Injection-Vulnerability-Scanner/script.sh -l {all_urls} 2>/dev/null",
                timeout=300
            )

            result_file = os.path.join(self.output_dir, "host_header_injection_results.txt")
            with open(result_file, 'w') as f:
                f.write(output)

            if "vulnerable" in output.lower():
                for line in output.split('\n'):
                    if 'vulnerable' in line.lower():
                        finding = Finding(
                            vuln_type="Host Header Injection",
                            target=line[:200],
                            severity=VulnSeverity.MEDIUM,
                            evidence=line,
                            confidence=70
                        )
                        self.save_finding(finding)
                        findings.append(finding)

        self.log(f"Host header injection scan complete: {len(findings)} findings")
        return findings


# ============================================================================
# PARALLEL ORCHESTRATOR
# ============================================================================

class ParallelOrchestrator:
    """
    Orchestrator that runs multiple specialized agents in parallel
    """

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        self.ai_manager = ai_manager
        self.output_dir = output_dir
        self.all_findings: List[Finding] = []
        self.logs: List[str] = []

        # Initialize all specialized agents
        self.agents = [
            XSSAgent(ai_manager, output_dir),
            SQLiAgent(ai_manager, output_dir),
            SSRFAgent(ai_manager, output_dir),
            SSTIAgent(ai_manager, output_dir),
            CommandInjectionAgent(ai_manager, output_dir),
            LFIAgent(ai_manager, output_dir),
            SubdomainTakeoverAgent(ai_manager, output_dir),
            CSRFAgent(ai_manager, output_dir),
            HTTPSmugglingAgent(ai_manager, output_dir),
            OpenRedirectAgent(ai_manager, output_dir),
            NucleiAgent(ai_manager, output_dir),
            CVESeekerAgent(ai_manager, output_dir),
            NmapVulnAgent(ai_manager, output_dir),
            NoSQLiAgent(ai_manager, output_dir),
            HostHeaderInjectionAgent(ai_manager, output_dir),
        ]

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [ParallelOrchestrator] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def run_parallel_scan(self, target: str, config: Dict = None, max_workers: int = 10) -> Dict[str, Any]:
        """
        Run all specialized agents in parallel
        """
        config = config or {}
        start_time = time.time()

        self.log(f"Starting parallel autonomous scan on {target}")
        self.log(f"Deploying {len(self.agents)} specialized agents with {max_workers} workers")
        self.log("=" * 80)

        results = {
            "target": target,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "agents_deployed": len(self.agents),
            "findings": [],
            "summary": {},
            "logs": []
        }

        # Collect targets from recon results
        targets = self._collect_targets_from_output()
        parameters = config.copy()

        # Run agents in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_agent = {
                executor.submit(agent.scan, targets, parameters): agent
                for agent in self.agents
            }

            for future in as_completed(future_to_agent):
                agent = future_to_agent[future]
                try:
                    findings = future.result()
                    self.all_findings.extend(findings)
                    self.log(f"✓ {agent.name} completed: {len(findings)} findings")
                except Exception as e:
                    self.log(f"✗ {agent.name} failed: {str(e)}")

        # Generate AI analysis of all findings
        self.log("=" * 80)
        self.log("Generating AI analysis of all findings...")

        if self.all_findings:
            analysis = self._generate_ai_analysis()
            results["ai_analysis"] = analysis

        # Generate summary
        results["findings"] = [self._finding_to_dict(f) for f in self.all_findings]
        results["summary"] = self._generate_summary()
        results["duration"] = time.time() - start_time

        # Save comprehensive report
        self._save_comprehensive_report(results)

        self.log("=" * 80)
        self.log(f"Parallel scan complete!")
        self.log(f"Total findings: {len(self.all_findings)}")
        self.log(f"Duration: {results['duration']:.2f} seconds")
        self.log(f"Speed: {len(self.agents) / (results['duration'] / 60):.2f} agents/minute")

        return results

    def _collect_targets_from_output(self) -> List[str]:
        """Collect targets from output directory files"""
        targets = []

        # Read from various output files
        files_to_check = [
            "filterDNS.txt",
            "nonhttpsfilterDNS.txt",
            "all_target_urls.txt"
        ]

        for filename in files_to_check:
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    targets.extend([line.strip() for line in f if line.strip()])

        return list(set(targets))  # Remove duplicates

    def _generate_ai_analysis(self) -> str:
        """Use AI to analyze all findings"""
        findings_summary = "\n".join([
            f"- {f.vuln_type} ({f.severity.value}) on {f.target[:100]}"
            for f in self.all_findings[:50]  # Limit for token size
        ])

        prompt = f"""Analyze these security findings from autonomous scan:

Total findings: {len(self.all_findings)}

Findings:
{findings_summary}

Provide:
1. Overall security posture assessment
2. Most critical vulnerabilities requiring immediate attention
3. Attack chains possible by combining findings
4. Recommended remediation priorities
5. Estimated business impact"""

        return self.ai_manager.query_for_analysis(prompt)

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate scan summary"""
        summary = {
            "total_findings": len(self.all_findings),
            "critical": len([f for f in self.all_findings if f.severity == VulnSeverity.CRITICAL]),
            "high": len([f for f in self.all_findings if f.severity == VulnSeverity.HIGH]),
            "medium": len([f for f in self.all_findings if f.severity == VulnSeverity.MEDIUM]),
            "low": len([f for f in self.all_findings if f.severity == VulnSeverity.LOW]),
            "by_type": {}
        }

        # Count by vulnerability type
        for finding in self.all_findings:
            vuln_type = finding.vuln_type
            if vuln_type not in summary["by_type"]:
                summary["by_type"][vuln_type] = 0
            summary["by_type"][vuln_type] += 1

        return summary

    def _save_comprehensive_report(self, results: Dict):
        """Save comprehensive JSON report"""
        report_file = os.path.join(self.output_dir, "comprehensive_scan_report.json")
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        self.log(f"Comprehensive report saved: {report_file}")

    def _finding_to_dict(self, finding: Finding) -> Dict:
        """Convert Finding to dictionary"""
        return {
            "vuln_type": finding.vuln_type,
            "target": finding.target,
            "severity": finding.severity.value,
            "evidence": finding.evidence[:500],  # Truncate for JSON size
            "poc": finding.poc,
            "validated": finding.validated,
            "exploitable": finding.exploitable,
            "impact": finding.impact,
            "agent": finding.agent_name,
            "timestamp": finding.timestamp,
            "confidence": finding.confidence
        }


def run_parallel_autonomous_scan(target: str, config_path: str = "config.yaml", max_workers: int = 10):
    """
    Main function to run parallel autonomous security scan

    Usage:
        python3 specialized_agents.py target.com
        python3 specialized_agents.py target.com config.yaml 15
    """
    # Load config
    config = {}
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
        except:
            # Fallback to simple key=value format
            with open(config_path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value

    # Initialize AI
    ai_manager = AIProviderManager(config)

    if not ai_manager.available_providers():
        print("WARNING: No AI providers configured. AI analysis will be limited.")
        print("Add API keys to config.yaml for full functionality.")

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║   PSAVVY AI - PARALLEL AUTONOMOUS EXPLOITATION SYSTEM        ║
    ║   15 Specialized Agents Running in Parallel                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Create orchestrator and run
    orchestrator = ParallelOrchestrator(ai_manager, output_dir)
    results = orchestrator.run_parallel_scan(target, config, max_workers)

    # Print summary
    summary = results.get("summary", {})
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                       SCAN SUMMARY                           ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  Agents Deployed:    {results.get('agents_deployed', 0):2d}                                  ║
    ║  Total Findings:     {summary.get('total_findings', 0):3d}                                 ║
    ║  Critical:           {summary.get('critical', 0):3d}                                 ║
    ║  High:               {summary.get('high', 0):3d}                                 ║
    ║  Medium:             {summary.get('medium', 0):3d}                                 ║
    ║  Low:                {summary.get('low', 0):3d}                                 ║
    ║  Duration:           {results.get('duration', 0):6.1f}s                             ║
    ╚══════════════════════════════════════════════════════════════╝

    Detailed results saved to: output/comprehensive_scan_report.json
    """)

    # Print findings by type
    if summary.get("by_type"):
        print("\n    Findings by Type:")
        for vuln_type, count in sorted(summary["by_type"].items(), key=lambda x: x[1], reverse=True):
            print(f"      • {vuln_type}: {count}")

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 specialized_agents.py <target> [config_path] [max_workers]")
        print("\nExample:")
        print("  python3 specialized_agents.py example.com")
        print("  python3 specialized_agents.py example.com config.yaml 15")
        print("\nNote: Run reconnaissance first with psavvy.py or psavvy_ai.py")
        sys.exit(1)

    target = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else "config.yaml"
    max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    run_parallel_autonomous_scan(target, config_path, max_workers)
