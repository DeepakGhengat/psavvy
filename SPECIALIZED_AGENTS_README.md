# PSAVVY AI - Specialized Parallel Agents System

## Overview

Advanced autonomous exploitation system with **15 specialized agents** running in **parallel** for maximum efficiency. Each agent is an expert in a specific vulnerability class.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│              PARALLEL ORCHESTRATOR                         │
│  • Coordinates 15 specialized agents                       │
│  • Runs agents in parallel (configurable workers)          │
│  • Aggregates all findings                                 │
│  • AI analysis of combined results                         │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ├─ ThreadPoolExecutor (10 workers)
                     │
         ┌───────────┴────────────────────┐
         │ All agents run simultaneously  │
         └───────────┬────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌─────────┐    ┌──────────┐    ┌──────────┐
│   XSS   │    │   SQLi   │    │   SSRF   │
│  Agent  │    │  Agent   │    │  Agent   │
└─────────┘    └──────────┘    └──────────┘

    ▼                ▼                ▼
┌─────────┐    ┌──────────┐    ┌──────────┐
│  SSTI   │    │  CMDi    │    │   LFI    │
│  Agent  │    │  Agent   │    │  Agent   │
└─────────┘    └──────────┘    └──────────┘

    ▼                ▼                ▼
┌─────────┐    ┌──────────┐    ┌──────────┐
│Subdomain│    │   CSRF   │    │  HTTP    │
│Takeover │    │  Agent   │    │Smuggling │
└─────────┘    └──────────┘    └──────────┘

    ▼                ▼                ▼
┌─────────┐    ┌──────────┐    ┌──────────┐
│  Open   │    │  Nuclei  │    │   CVE    │
│Redirect │    │  Agent   │    │  Seeker  │
└─────────┘    └──────────┘    └──────────┘

    ▼                ▼                ▼
┌─────────┐    ┌──────────┐    ┌──────────┐
│  Nmap   │    │ NoSQLi   │    │   Host   │
│  Vuln   │    │  Agent   │    │  Header  │
└─────────┘    └──────────┘    └──────────┘
```

---

## 15 Specialized Agents

| Agent | Tools Used | Targets | Speed |
|-------|-----------|---------|-------|
| **XSSAgent** | dalfox, XSStrike, Gxss | All URLs | Fast |
| **SQLiAgent** | sqlmap, gf | URLs with params | Medium |
| **SSRFAgent** | ssrfuzz, bssrf, autossrf | All URLs | Fast |
| **SSTIAgent** | SSTImap | All URLs | Medium |
| **CommandInjectionAgent** | commix | Domains | Medium |
| **LFIAgent** | custom payloads, gf | URLs with file params | Fast |
| **SubdomainTakeoverAgent** | subzy, Subhunter | Subdomains | Fast |
| **CSRFAgent** | xsrfprobe | Domains | Slow |
| **HTTPSmugglingAgent** | smuggler | URLs | Fast |
| **OpenRedirectAgent** | Oralyzer | All URLs | Fast |
| **NucleiAgent** | nuclei + templates | Domains & URLs | Medium |
| **CVESeekerAgent** | CVESeeker | Domains | Medium |
| **NmapVulnAgent** | nmap + vuln scripts | Domains | Slow |
| **NoSQLiAgent** | nosqli | URLs | Fast |
| **HostHeaderInjectionAgent** | custom scanner | URLs | Fast |

---

## Usage

### Full Workflow

```bash
# Step 1: Run reconnaissance (creates output/ with targets)
sudo python3 psavvy.py -d target.com

# Step 2: Run parallel autonomous agents
python3 specialized_agents.py target.com

# Step 3: Generate AI report
python3 psavvy_ai.py -d target.com --skip-scan --ai-report
```

### Quick Start

```bash
# Run with default settings (10 parallel workers)
python3 specialized_agents.py target.com

# Run with custom config and more workers
python3 specialized_agents.py target.com config.yaml 15

# Run with fewer workers (lower resource usage)
python3 specialized_agents.py target.com config.yaml 5
```

---

## Key Features

### 1. Parallel Execution
```python
# Run 15 agents simultaneously with ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_agent = {
        executor.submit(agent.scan, targets, parameters): agent
        for agent in self.agents
    }
```

**Benefits:**
- 10-15x faster than sequential
- Utilizes multi-core CPUs
- Completes in minutes instead of hours

### 2. Automatic Output Management
```
output/
├── XSSAgent_findings_*.json
├── SQLiAgent_findings_*.json
├── SSRFAgent_findings_*.json
├── comprehensive_scan_report.json    # All findings
├── filterDNS.txt                     # From recon
├── all_target_urls.txt               # From recon
├── sqli_results.txt                  # SQLi details
├── nuclei_abstract_scan.txt          # Nuclei results
└── ... (all tool outputs)
```

Each agent saves:
- Individual findings as JSON
- Tool output to respective files
- Evidence and PoC for each finding

### 3. Tool Integration

All 30+ tools from PSAVVY install.sh:
```bash
✓ SubEnum          ✓ ParamSpider      ✓ Subhunter
✓ xsrfprobe        ✓ nuclei           ✓ smuggler
✓ commix           ✓ SSTImap          ✓ gitGraber
✓ GitDorker        ✓ Oralyzer         ✓ Host-Header-Scanner
✓ freevulnsearch   ✓ nmap-vulners     ✓ vulscan
✓ sqlmap           ✓ XSStrike         ✓ Nettacker
✓ subzy            ✓ massdns          ✓ gf
✓ Gf-Patterns      ✓ CVESeeker        ✓ autossrf
✓ shuffledns       ✓ anew             ✓ dnsx
✓ httpx            ✓ gau              ✓ ssrfuzz
✓ nosqli           ✓ Gxss             ✓ dalfox
```

### 4. AI-Powered Analysis

After all agents complete:
```python
# AI analyzes combined findings
- Overall security posture
- Critical vulnerabilities
- Possible attack chains
- Remediation priorities
- Business impact assessment
```

### 5. Thread-Safe Operations

```python
# Each agent has thread-safe logging and finding storage
self.lock = threading.Lock()

def save_finding(self, finding):
    with self.lock:
        self.findings.append(finding)
        # Save to file
```

---

## Configuration

### Adjust Parallel Workers

```bash
# Low resource (5 workers)
python3 specialized_agents.py target.com config.yaml 5

# Default (10 workers)
python3 specialized_agents.py target.com

# High performance (15 workers)
python3 specialized_agents.py target.com config.yaml 15

# Maximum (20 workers - requires powerful machine)
python3 specialized_agents.py target.com config.yaml 20
```

**Resource Guidelines:**
- 5 workers: 4GB RAM, 2 CPU cores
- 10 workers: 8GB RAM, 4 CPU cores (recommended)
- 15 workers: 16GB RAM, 8 CPU cores
- 20 workers: 32GB RAM, 16 CPU cores

### config.yaml

```yaml
# AI API Keys (for final analysis)
ANTHROPIC_API_KEY: "your-key"
PERPLEXITY_API_KEY: "your-key"
OPENAI_API_KEY: "your-key"

# Callback URLs
BURP_COLLAB_URL: "https://your-collab.oastify.com"
BLIND_XSS_URL: "https://webhook.site/your-id"
```

---

## Output Format

### Individual Finding JSON
```json
{
  "vuln_type": "SQL Injection",
  "target": "https://example.com/search?q=test",
  "severity": "critical",
  "evidence": "sqlmap identified parameter 'q' as vulnerable...",
  "poc": "python3 Tools/sqlmap/sqlmap.py -u 'https://...' --dbs",
  "validated": false,
  "exploitable": true,
  "impact": "Database access, data theft, authentication bypass",
  "agent": "SQLiAgent",
  "timestamp": "2025-11-24 14:32:15",
  "confidence": 90
}
```

### Comprehensive Report
```json
{
  "target": "example.com",
  "start_time": "2025-11-24 14:30:00",
  "agents_deployed": 15,
  "findings": [...],
  "summary": {
    "total_findings": 47,
    "critical": 5,
    "high": 12,
    "medium": 23,
    "low": 7,
    "by_type": {
      "SQL Injection": 3,
      "XSS": 8,
      "SSRF": 2,
      ...
    }
  },
  "ai_analysis": "...",
  "duration": 342.5
}
```

---

## Performance Comparison

| Method | Agents | Duration | Findings | Speed |
|--------|--------|----------|----------|-------|
| Sequential (old psavvy.py) | N/A | 4-6 hours | ~40 | 1x |
| Autonomous (autonomous_agents.py) | 4 | 2-3 hours | ~35 | 2x |
| **Parallel Specialized** | 15 | 15-30 min | ~50 | **10x** |

---

## Example Output

```
╔══════════════════════════════════════════════════════════════╗
║   PSAVVY AI - PARALLEL AUTONOMOUS EXPLOITATION SYSTEM        ║
║   15 Specialized Agents Running in Parallel                  ║
╚══════════════════════════════════════════════════════════════╝

[14:30:15] [ParallelOrchestrator] Starting parallel autonomous scan
[14:30:15] [ParallelOrchestrator] Deploying 15 specialized agents with 10 workers
[14:30:16] [XSSAgent] Starting XSS scan on 312 targets
[14:30:16] [SQLiAgent] Starting SQL injection scan on 312 targets
[14:30:16] [SSRFAgent] Starting SSRF scan on 312 targets
[14:30:16] [SSTIAgent] Starting SSTI scan on 312 targets
...
[14:32:45] [XSSAgent] Running dalfox scanner...
[14:33:12] [SQLiAgent] Running sqlmap (quick scan)...
[14:34:28] [ParallelOrchestrator] ✓ XSSAgent completed: 8 findings
[14:35:01] [ParallelOrchestrator] ✓ SubdomainTakeoverAgent completed: 2 findings
[14:36:15] [ParallelOrchestrator] ✓ SSRFAgent completed: 3 findings
...
[14:45:22] [ParallelOrchestrator] Generating AI analysis of all findings...
[14:45:50] [ParallelOrchestrator] Comprehensive report saved

╔══════════════════════════════════════════════════════════════╗
║                       SCAN SUMMARY                           ║
╠══════════════════════════════════════════════════════════════╣
║  Agents Deployed:    15                                      ║
║  Total Findings:     47                                      ║
║  Critical:            5                                      ║
║  High:               12                                      ║
║  Medium:             23                                      ║
║  Low:                 7                                      ║
║  Duration:          918.3s                                   ║
╚══════════════════════════════════════════════════════════════╝

Findings by Type:
  • Cross-Site Scripting (XSS): 8
  • SQL Injection: 5
  • SSRF: 3
  • Subdomain Takeover: 2
  • Open Redirect: 4
  • CSRF: 3
  • Host Header Injection: 2
  • LFI: 2
  • Nuclei Detection: 15
  • CVE Detected: 3
```

---

## Advantages Over Previous Systems

| Feature | psavvy.py | autonomous_agents.py | specialized_agents.py |
|---------|-----------|---------------------|---------------------|
| Agents | 0 | 4 | 15 |
| Specialized | No | Partial | Yes |
| Parallel | No | No | Yes |
| Speed | Baseline | 2x | 10x |
| AI Analysis | No | Yes | Yes |
| Tool Coverage | 100% | 30% | 100% |
| Findings Quality | Good | Good | Excellent |

---

## Integration with Other Scripts

### Complete Workflow

```bash
# 1. Initial recon with AI
python3 psavvy_ai.py -d target.com --quick

# 2. Parallel specialized scan
python3 specialized_agents.py target.com

# 3. Generate comprehensive AI report
python3 psavvy_ai.py -d target.com --skip-scan --ai-report

# 4. Interactive analysis
python3 psavvy_ai.py --ai-interactive
```

### Use Cases

**Bug Bounty:**
```bash
# Quick comprehensive scan
python3 psavvy.py -d target.com
python3 specialized_agents.py target.com config.yaml 15
```

**Pentest:**
```bash
# Full scan with validation
python3 autonomous_agents.py target.com
python3 specialized_agents.py target.com
python3 psavvy_ai.py -d target.com --skip-scan --ai-report
```

**Research:**
```bash
# Deep dive with AI assistance
python3 specialized_agents.py target.com
python3 psavvy_ai.py --ai-interactive
# Use "analyze" command in interactive mode
```

---

## Troubleshooting

### "No targets found"
```bash
# Run recon first
python3 psavvy.py -d target.com
# Then run specialized agents
python3 specialized_agents.py target.com
```

### Too Many Workers Error
```bash
# Reduce workers
python3 specialized_agents.py target.com config.yaml 5
```

### Agent Timeout
```bash
# Individual agents have timeouts
# Check output/<agent>_*.txt for partial results
```

### Low Findings
```bash
# Ensure recon created good target list
ls -lh output/*.txt
# Should have filterDNS.txt, all_target_urls.txt, etc.
```

---

## Customization

### Add New Agent

```python
class MyCustomAgent(BaseSpecializedAgent):
    def __init__(self, ai_manager, output_dir):
        super().__init__(ai_manager, "MyCustomAgent", output_dir)

    def scan(self, targets, parameters):
        self.log("Running custom scan...")
        findings = []

        # Your scanning logic
        output, _ = self.execute_tool("my-tool -u target")

        if "vulnerable" in output:
            finding = Finding(
                vuln_type="My Vuln Type",
                target="...",
                severity=VulnSeverity.HIGH,
                evidence=output
            )
            self.save_finding(finding)
            findings.append(finding)

        return findings

# Add to orchestrator
self.agents.append(MyCustomAgent(ai_manager, output_dir))
```

### Modify Existing Agent

Edit the agent's `scan()` method in `specialized_agents.py`.

---

## Best Practices

1. **Always run recon first** - Agents need target lists
2. **Adjust workers to your hardware** - Don't overload
3. **Monitor resource usage** - Use `htop` during scan
4. **Review findings manually** - AI confidence scores help prioritize
5. **Save results** - Keep comprehensive_scan_report.json
6. **Use AI analysis** - Get strategic insights

---

## Credits

- Original PSAVVY: [DeepakGhengat](https://github.com/DeepakGhengat)
- AI Integration: PSAVVY AI Team
- All security tools: Respective authors

---

## License

For authorized security testing only. Follow responsible disclosure.
