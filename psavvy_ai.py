#!/usr/bin/env python3
"""
PSAVVY AI - AI-Powered Security Assessment & Vulnerability Verification System
Integrates Claude (Anthropic), Perplexity, and ChatGPT (OpenAI) for intelligent
vulnerability scanning, analysis, and exploitation assistance.

Author: DeepakGhengat (Original PSAVVY)
AI Enhancement: PSAVVY AI Team
Version: 2.0.0

Usage:
    # Full scan with AI analysis
    python3 psavvy_ai.py -d target.com --ai-analyze

    # Generate AI report
    python3 psavvy_ai.py -d target.com --ai-report

    # AI payload generation
    python3 psavvy_ai.py --ai-payloads xss --context '{"waf": "cloudflare"}'

    # Research CVE
    python3 psavvy_ai.py --ai-research CVE-2024-1234

    # Interactive AI mode
    python3 psavvy_ai.py --ai-interactive
"""

import subprocess
import os
import sys
import argparse
import json
import yaml
from datetime import datetime
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import AI modules
try:
    from ai_engine import (
        AIProviderManager,
        VulnerabilityAnalyzer,
        PayloadGenerator,
        ExploitationAssistant,
        ReportGenerator,
        VulnerabilityResearcher
    )
    AI_AVAILABLE = True
except ImportError as e:
    print(f"\033[93m[!] AI modules not fully loaded: {e}\033[0m")
    AI_AVAILABLE = False


def execute_command(command):
    """Execute shell command and handle errors"""
    try:
        subprocess.run(command, shell=True)
    except Exception as e:
        print(f"\033[91m[ERROR] Command failed: {e}\033[0m")


def print_header(header_text, color="red"):
    """Print colored section header"""
    colors = {
        "red": "\033[1;31;40m",
        "green": "\033[1;32;40m",
        "yellow": "\033[1;33;40m",
        "blue": "\033[1;34;40m",
        "cyan": "\033[1;36;40m"
    }
    reset = "\033[0m"
    print(f"{colors.get(color, colors['red'])}{header_text}{reset}")


def print_ai_banner():
    """Print AI-enhanced banner"""
    banner = """
\033[1;36m
    ____  _____  ___ _    ___    ___ ___
   / __ \\/ ___/ / | | |  / / |  / / / | |
  / /_/ /\\__ \\ / /| | | / /| | / / / /| |
 / ____/___/ // ___ | |/ / | |/ / / ___ |
/_/    /____//_/  |_|___/  |___/ /_/  |_|

    \033[1;33mAI-Powered Security Framework v2.0\033[0m
    \033[1;32mClaude + Perplexity + ChatGPT Integration\033[0m
"""
    print(banner)


def load_config(config_path: str) -> Dict[str, str]:
    """Load configuration from file (supports txt and yaml)"""
    config = {}

    if not os.path.exists(config_path):
        return config

    # Try YAML first
    if config_path.endswith(('.yaml', '.yml')):
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
            if yaml_config:
                # Flatten nested config
                for key, value in yaml_config.items():
                    if isinstance(value, dict):
                        for k, v in value.items():
                            config[k] = v
                    else:
                        config[key] = value
    else:
        # Original txt format
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

    return config


def get_url_from_config(config_file, option):
    """Get URL from config file (legacy support)"""
    config = load_config(config_file)
    return config.get(option, '')


def initialize_ai(config: Dict[str, str]) -> Optional[AIProviderManager]:
    """Initialize AI provider manager"""
    if not AI_AVAILABLE:
        print("\033[91m[!] AI modules not available\033[0m")
        return None

    ai_manager = AIProviderManager(config)
    available = ai_manager.available_providers()

    if not available:
        print("\033[91m[!] No AI providers configured. Add API keys to config.\033[0m")
        return None

    print(f"\033[92m[+] AI Providers available: {', '.join(available)}\033[0m")
    return ai_manager


def domains_search(domain, commands, output_dir):
    """Execute scanning commands for domain enumeration"""
    total = len(commands)
    for i, (header_text, cmd) in enumerate(commands, 1):
        if header_text:
            print_header(f"[{i}/{total}] {header_text}")
        cmd(domain, output_dir)


def ai_analyze_results(ai_manager: AIProviderManager, output_dir: str, target: str):
    """Run AI analysis on scan results"""
    print_header("AI Vulnerability Analysis", "cyan")

    analyzer = VulnerabilityAnalyzer(ai_manager)

    # Comprehensive analysis
    print("\n[*] Analyzing scan results...")
    analysis = analyzer.analyze_scan_results(output_dir)

    # Save analysis
    analysis_path = os.path.join(output_dir, "AI_Analysis.md")
    with open(analysis_path, 'w') as f:
        f.write(f"# AI Vulnerability Analysis\n")
        f.write(f"## Target: {target}\n")
        f.write(f"## Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
        f.write(analysis.get('ai_analysis', 'No analysis available'))

    print(f"\033[92m[+] Analysis saved to: {analysis_path}\033[0m")

    # Triage
    print("\n[*] Performing vulnerability triage...")
    triage = analyzer.triage_all_findings(output_dir)
    triage_path = os.path.join(output_dir, "AI_Triage.md")
    with open(triage_path, 'w') as f:
        f.write(f"# Vulnerability Triage\n\n{triage}")

    print(f"\033[92m[+] Triage saved to: {triage_path}\033[0m")

    # Attack chain analysis
    print("\n[*] Finding attack chains...")
    chains = analyzer.correlate_findings(output_dir)
    chains_path = os.path.join(output_dir, "AI_Attack_Chains.md")
    with open(chains_path, 'w') as f:
        f.write(f"# Attack Chain Analysis\n\n{chains}")

    print(f"\033[92m[+] Attack chains saved to: {chains_path}\033[0m")

    return analysis


def ai_generate_report(ai_manager: AIProviderManager, output_dir: str, target: str):
    """Generate AI-powered security report"""
    print_header("AI Report Generation", "cyan")

    reporter = ReportGenerator(ai_manager)

    print("\n[*] Generating comprehensive report...")
    reports = reporter.generate_full_report(output_dir, target)

    # Save reports
    report_dir = os.path.join(output_dir, "reports")
    os.makedirs(report_dir, exist_ok=True)

    for report_name, content in reports.items():
        report_path = os.path.join(report_dir, f"{report_name}.md")
        with open(report_path, 'w') as f:
            f.write(content)
        print(f"\033[92m[+] {report_name} saved to: {report_path}\033[0m")

    return reports


def ai_generate_payloads(ai_manager: AIProviderManager, vuln_type: str, context: Dict[str, Any]):
    """Generate AI-powered payloads"""
    print_header(f"AI Payload Generation: {vuln_type}", "cyan")

    generator = PayloadGenerator(ai_manager)

    payload_methods = {
        'xss': generator.generate_xss_payloads,
        'sqli': generator.generate_sqli_payloads,
        'ssti': generator.generate_ssti_payloads,
        'ssrf': generator.generate_ssrf_payloads,
        'cmdi': generator.generate_command_injection,
        'lfi': generator.generate_lfi_payloads
    }

    if vuln_type.lower() in payload_methods:
        payloads = payload_methods[vuln_type.lower()](context)
    else:
        payloads = generator.generate_custom_payloads(vuln_type, context)

    print(f"\n{payloads}")
    return payloads


def ai_research(ai_manager: AIProviderManager, query: str, research_type: str = "cve"):
    """Conduct AI-powered security research"""
    print_header(f"AI Security Research: {query}", "cyan")

    researcher = VulnerabilityResearcher(ai_manager)

    if research_type == "cve" or query.upper().startswith("CVE-"):
        result = researcher.research_cve(query)
    elif research_type == "exploits":
        result = researcher.find_exploits(query)
    elif research_type == "vuln_class":
        result = researcher.research_vulnerability_class(query)
    elif research_type == "target":
        result = researcher.research_target_technology(query)
    elif research_type == "waf":
        result = researcher.get_waf_bypass_research(query)
    else:
        result = researcher.find_poc_code(query)

    print(f"\n{result}")
    return result


def ai_exploitation_guidance(ai_manager: AIProviderManager, vuln_type: str, context: Dict[str, Any]):
    """Get AI-powered exploitation guidance"""
    print_header(f"AI Exploitation Guidance: {vuln_type}", "cyan")

    assistant = ExploitationAssistant(ai_manager)

    plan = assistant.create_exploitation_plan(vuln_type, context)
    print(f"\n{plan}")
    return plan


def ai_interactive_mode(ai_manager: AIProviderManager, output_dir: str):
    """Interactive AI assistant mode"""
    print_header("AI Interactive Mode", "cyan")
    print("\nCommands:")
    print("  analyze    - Analyze scan results")
    print("  research   - Research CVE/vulnerability")
    print("  payloads   - Generate payloads")
    print("  exploit    - Get exploitation guidance")
    print("  report     - Generate report")
    print("  quit       - Exit interactive mode")
    print()

    analyzer = VulnerabilityAnalyzer(ai_manager)
    generator = PayloadGenerator(ai_manager)
    researcher = VulnerabilityResearcher(ai_manager)
    assistant = ExploitationAssistant(ai_manager)
    reporter = ReportGenerator(ai_manager)

    while True:
        try:
            user_input = input("\033[1;36mPSAVVY-AI> \033[0m").strip()

            if not user_input:
                continue

            parts = user_input.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "quit" or command == "exit":
                print("Exiting AI mode.")
                break

            elif command == "analyze":
                print("\n[*] Running analysis...")
                result = analyzer.analyze_scan_results(output_dir)
                print(result.get('ai_analysis', 'No results'))

            elif command == "research":
                if not args:
                    args = input("Enter CVE/vulnerability to research: ")
                result = researcher.research_cve(args)
                print(f"\n{result}")

            elif command == "payloads":
                vuln_type = args or input("Payload type (xss/sqli/ssti/ssrf/cmdi/lfi): ")
                context_str = input("Context JSON (or press Enter for default): ")
                context = json.loads(context_str) if context_str else {}
                result = generator.generate_custom_payloads(vuln_type, context)
                print(f"\n{result}")

            elif command == "exploit":
                vuln = args or input("Vulnerability type: ")
                target = input("Target: ")
                result = assistant.create_exploitation_plan(vuln, {"target": target})
                print(f"\n{result}")

            elif command == "report":
                target = args or input("Target name for report: ")
                reports = reporter.generate_full_report(output_dir, target)
                print("\nReport generated successfully!")

            elif command == "help":
                print("\nAvailable commands: analyze, research, payloads, exploit, report, quit")

            else:
                # Treat as general query to Claude
                print("\n[*] Processing query...")
                result = ai_manager.query_for_analysis(user_input)
                print(f"\n{result}")

        except KeyboardInterrupt:
            print("\n")
            continue
        except Exception as e:
            print(f"\033[91m[!] Error: {e}\033[0m")


def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="PSAVVY AI - AI-Powered Security Assessment Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full scan with AI analysis
  python3 psavvy_ai.py -d example.com --ai-analyze

  # Scan and generate AI report
  python3 psavvy_ai.py -d example.com --ai-report

  # Generate XSS payloads with WAF bypass
  python3 psavvy_ai.py --ai-payloads xss --context '{"waf": "cloudflare"}'

  # Research a CVE
  python3 psavvy_ai.py --ai-research CVE-2024-1234

  # Interactive AI mode
  python3 psavvy_ai.py --ai-interactive

  # Traditional scan (no AI)
  python3 psavvy_ai.py -d example.com
        """
    )

    # Target options
    parser.add_argument("-d", "--domain", type=str, help="Target domain")
    parser.add_argument("-c", "--config", type=str, default="config.yaml",
                        help="Config file path (default: config.yaml)")

    # AI options
    parser.add_argument("--ai-analyze", action="store_true",
                        help="Run AI analysis on scan results")
    parser.add_argument("--ai-report", action="store_true",
                        help="Generate AI-powered report")
    parser.add_argument("--ai-payloads", type=str,
                        help="Generate AI payloads (xss/sqli/ssti/ssrf/cmdi/lfi)")
    parser.add_argument("--ai-research", type=str,
                        help="Research CVE/vulnerability")
    parser.add_argument("--ai-exploit", type=str,
                        help="Get exploitation guidance for vulnerability")
    parser.add_argument("--ai-interactive", action="store_true",
                        help="Start interactive AI mode")
    parser.add_argument("--context", type=str, default="{}",
                        help="JSON context for AI operations")

    # Scan options
    parser.add_argument("--skip-scan", action="store_true",
                        help="Skip scanning, only run AI analysis")
    parser.add_argument("--quick", action="store_true",
                        help="Quick scan (reduced tools)")

    args = parser.parse_args()

    # Print banner
    print_ai_banner()

    # Load configuration
    config = load_config(args.config)
    if not config:
        # Try legacy config
        config = load_config("config.txt")

    # Setup output directory
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize AI if needed
    ai_manager = None
    if any([args.ai_analyze, args.ai_report, args.ai_payloads,
            args.ai_research, args.ai_exploit, args.ai_interactive]):
        ai_manager = initialize_ai(config)
        if not ai_manager:
            print("\033[91m[!] AI features require API keys in config\033[0m")
            if not args.domain:
                sys.exit(1)

    # Handle AI-only operations
    if args.ai_payloads:
        context = json.loads(args.context)
        ai_generate_payloads(ai_manager, args.ai_payloads, context)
        return

    if args.ai_research:
        ai_research(ai_manager, args.ai_research)
        return

    if args.ai_exploit:
        context = json.loads(args.context)
        ai_exploitation_guidance(ai_manager, args.ai_exploit, context)
        return

    if args.ai_interactive:
        ai_interactive_mode(ai_manager, output_dir)
        return

    # Domain scanning
    if args.domain:
        domain = args.domain
        print(f"\033[92m[+] Target: {domain}\033[0m")

        if not args.skip_scan:
            # Define scanning commands (same as original psavvy.py)
            commands = [
                ("SubDomain Enumeration", lambda domain, output_dir: execute_command(f"bash Tools/SubEnum/subenum.sh -d {domain} -r -p")),
                ("", lambda domain, output_dir: execute_command(f"shuffledns -d {domain} -r dns-resolvers.txt -w subdomains-top1million-110000.txt -mode bruteforce | anew subs.txt")),
                ("", lambda domain, output_dir: subprocess.run(["cat", "subs.txt"] + [file for file in os.listdir() if file.startswith("resolved")], stdout=open("finalsubs.txt", "w"))),
                ("", lambda domain, output_dir: execute_command("cat finalsubs.txt | dnsx -silent | httpx -silent | anew filterDNS.txt")),
                ("", lambda domain, output_dir: os.rename("filterDNS.txt", os.path.join(output_dir, "filterDNS.txt")) if os.path.exists("filterDNS.txt") else None),
                ("", lambda domain, output_dir: execute_command(f"sed 's/https:\\/\\///' output/filterDNS.txt | anew > output/nonhttpsfilterDNS.txt")),
                ("Collecting URLs and Hidden Params", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | httpx -silent | tee -a output/all_target_urls.txt")),
                ("", lambda domain, output_dir: execute_command(f"sudo paramspider -l output/filterDNS.txt | tee -a output/Params_list.txt && mkdir -p output/Paramspider_Result && mv results output/Paramspider_Result 2>/dev/null || true")),
                ("SubDomain TakeOver", lambda domain, output_dir: execute_command(f"./Tools/Subhunter/subhunter -l output/nonhttpsfilterDNS.txt | tee -a output/Subdomaintakeover1.txt")),
                ("", lambda domain, output_dir: execute_command(f"./Tools/subzy/subzy run --targets output/nonhttpsfilterDNS.txt --hide_fails | tee -a output/Subdomaintakeover.txt")),
                ("CSRF Checks", lambda domain, output_dir: execute_command(f"mkdir -p output/csrf && xargs -a output/nonhttpsfilterDNS.txt -I{{}} sh -c 'xsrfprobe -u {{}} -d 5 -v --crawl --malicious -o output/csrf/ --no-verify --random-agent'")),
                ("HTTP Req Smuggling", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | python3 Tools/smuggler/smuggler.py -m GET,POST | tee -a output/smuggler_results.txt")),
                ("Nuclei Scanning", lambda domain, output_dir: execute_command(f"nuclei -l output/filterDNS.txt -t Tools/nuclei-templates/ -o output/nuclei_abstract_scan.txt")),
                ("", lambda domain, output_dir: execute_command(f"nuclei -l output/all_target_urls.txt -t Tools/nuclei-templates/ -o output/nuclei_fullurls_scan.txt")),
                ("Command Injection", lambda domain, output_dir: execute_command(f"python3 Tools/commix/commix.py -m output/filterDNS.txt --batch --crawl=5 --all --smart | tee -a output/commixlogs.txt")),
                ("SSTI Scanning", lambda domain, output_dir: execute_command(f"python3 Tools/SSTImap/sstimap.py --load-urls output/all_target_urls.txt -A --delay 3 -l 5 --os-shell | tee -a output/SSTI_Allurls_Scans.txt")),
                ("", lambda domain, output_dir: execute_command(f"python3 Tools/SSTImap/sstimap.py --load-urls output/filterDNS.txt -A -c 5 --delay 3 -l 5 --os-shell | tee -a output/SSTI_scans.txt")),
                ("LFI Parameter Findings", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | sudo gf lfi | tee -a output/lfi_params.txt")),
                ("Github Recon", lambda domain, output_dir: execute_command(f"python3 Tools/gitGraber/gitGraber.py -k Tools/gitGraber/keywordsfile.txt -q \"{domain}\" | tee -a output/gitrecon.txt")),
                ("Github Dorking", lambda domain, output_dir: execute_command(f"python3 Tools/GitDorker/GitDorker.py -tf Tools/GitDorker/tf/TOKENSFILE -q {domain} -d Tools/GitDorker/Dorks/alldorksv3 | tee -a output/github_dorking.txt")),
                ("Host Header Injection", lambda domain, output_dir: execute_command(f"bash Tools/Host-Header-Injection-Vulnerability-Scanner/script.sh -l output/all_target_urls.txt | tee -a output/host_header_injection_results.txt")),
                ("Open Redirect Testing", lambda domain, output_dir: execute_command(f"python3 Tools/Oralyzer/oralyzer.py -l output/all_target_urls.txt -crlf | tee -a output/OpenRedirect.txt")),
                ("IDOR URLs Collection", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | grep -E '\\.json$|\\.yaml$|\\.xml$|\\.php$|\\.aspx$|\\.jsp$' | tee -a output/IDOR.txt")),
                ("Nmap Vulnerability Scan", lambda domain, output_dir: execute_command(f"sudo nmap -sV -sC -A -Pn -v -p- --script='Tools/freevulnsearch/freevulnsearch.nse','Tools/nmap-vulners/vulners.nse','Tools/vulscan/vulscan.nse' -oN output/nmapScan.txt -iL output/nonhttpsfilterDNS.txt")),
                ("SSRF Detection", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | bssrf -v -t 10 -l {get_url_from_config(args.config, 'BURP_COLLAB_URL')} | tee -a output/bulkssrf_result.txt")),
                ("", lambda domain, output_dir: execute_command(f"python3 Tools/autossrf/autossrf.py -f output/all_target_urls.txt -v | tee -a output/SSRFAUTO_result.txt")),
                ("", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | ssrfuzz scan -x 'GET','POST' | tee -a output/ssrfuzz_results.txt")),
                ("", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | sudo gf ssrf | tee -a output/ssrf_urls.txt")),
                ("SQL Injection", lambda domain, output_dir: execute_command(f"cat output/nonhttpsfilterDNS.txt | gau | sudo gf sqli | tee -a output/sqli_urls.txt")),
                ("", lambda domain, output_dir: execute_command(f"python3 Tools/sqlmap/sqlmap.py -m 'output/sqli_urls.txt' --tamper=between,randomcase,space2comment --level=5 --risk=3 --time-sec=20 --random-agent -v 3 -b --batch -f -a | tee -a output/sqli_results_1.txt")),
                ("NoSQL Injection", lambda domain, output_dir: execute_command(f"xargs -a output/all_target_urls.txt -I{{}} sh -c 'nosqli scan --insecure -t {{}}' | tee -a output/Nosqli_Scan_results.txt")),
                ("XSS Scanning", lambda domain, output_dir: execute_command(f"cat output/filterDNS.txt | gau | Gxss -p XSS | tee -a output/Reflect_XSS_urls.txt")),
                ("", lambda domain, output_dir: execute_command(f"xargs -a output/filterDNS.txt -I{{}} sh -c 'python3 Tools/XSStrike/xsstrike.py -u {{}} --crawl --blind' | tee -a output/XSS_Results_1.txt")),
                ("", lambda domain, output_dir: execute_command(f"xargs -a output/Reflect_XSS_urls.txt -I{{}} sh -c 'python3 Tools/XSStrike/xsstrike.py -u {{}} -f XSSPayloads.txt' | tee -a output/XSS_Results_2.txt")),
                ("", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | dalfox pipe | tee -a output/XSS_Results_3.txt")),
                ("", lambda domain, output_dir: execute_command(f"cat output/all_target_urls.txt | dalfox pipe -b {get_url_from_config(args.config, 'BLIND_XSS_URL')} | tee -a output/Blind_XSS_Results.txt")),
                ("OWASP Nettacker", lambda domain, output_dir: execute_command(f"python3 Tools/Nettacker/nettacker.py -l output/nonhttpsfilterDNS.txt --profile all -t 500 | tee -a output/nettackerresults.txt")),
                ("CVE Detection", lambda domain, output_dir: execute_command(f"python3 Tools/CVESeeker/cveSeeker.py --file output/nonhttpsfilterDNS.txt --project CVESProject | tee -a output/CVEScanResult.txt && [ -d 'CVESProject' ] && mv CVESProject output/")),
                ("Cleanup", lambda domain, output_dir: execute_command(f"find . -maxdepth 1 -name '*.txt' ! -name 'dns-resolvers.txt' ! -name 'config.txt' ! -name 'XSSPayloads.txt' ! -name 'subdomains-top1million-110000.txt' -delete")),
            ]

            # Quick scan uses fewer tools
            if args.quick:
                commands = commands[:15]  # Only first 15 commands

            # Run scanning
            print_header("Starting Security Scan", "green")
            domains_search(domain, commands, output_dir)

        # Run AI analysis if requested
        if args.ai_analyze and ai_manager:
            ai_analyze_results(ai_manager, output_dir, domain)

        # Generate AI report if requested
        if args.ai_report and ai_manager:
            ai_generate_report(ai_manager, output_dir, domain)

        print_header("Scan Complete!", "green")
        print(f"\033[92m[+] Results saved to: {output_dir}\033[0m")

    else:
        if not any([args.ai_payloads, args.ai_research, args.ai_exploit, args.ai_interactive]):
            print("Please provide a domain using -d option or use AI-only features.")
            print("Use --help for usage information.")


if __name__ == "__main__":
    main()
