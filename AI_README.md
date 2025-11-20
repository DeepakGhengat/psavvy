# PSAVVY AI - AI-Powered Security Assessment Framework

## Overview

PSAVVY AI transforms the original PSAVVY framework into an intelligent, AI-powered vulnerability scanner and exploitation assistant. It integrates three major AI providers to deliver comprehensive security analysis, intelligent payload generation, and automated report creation.

## AI Providers

| Provider | Best For | Features |
|----------|----------|----------|
| **Claude (Anthropic)** | Deep Analysis & Reasoning | Vulnerability analysis, exploitation guidance, attack chain identification |
| **Perplexity** | Real-time Research | CVE lookups, exploit searches, latest vulnerability info |
| **ChatGPT (OpenAI)** | Content Generation | Payload creation, report writing, WAF bypass techniques |

## Installation

### 1. Install Base PSAVVY
```bash
git clone https://github.com/DeepakGhengat/psavvy.git
cd psavvy
sudo bash install.sh
```

### 2. Install AI Dependencies
```bash
sudo bash install_ai.sh
```

### 3. Configure API Keys
```bash
# Copy the config template
cp config.yaml config.yaml.backup

# Edit and add your API keys
nano config.yaml
```

Required API keys:
- `ANTHROPIC_API_KEY` - Get from [Anthropic Console](https://console.anthropic.com/)
- `PERPLEXITY_API_KEY` - Get from [Perplexity Settings](https://www.perplexity.ai/settings/api)
- `OPENAI_API_KEY` - Get from [OpenAI Platform](https://platform.openai.com/api-keys)

## Usage

### Full Scan with AI Analysis
```bash
# Scan target and analyze results with AI
sudo python3 psavvy_ai.py -d target.com --ai-analyze

# Scan and generate comprehensive AI report
sudo python3 psavvy_ai.py -d target.com --ai-report

# Full scan with both analysis and report
sudo python3 psavvy_ai.py -d target.com --ai-analyze --ai-report
```

### AI-Only Operations (No Scanning)

#### Generate Payloads
```bash
# XSS payloads
python3 psavvy_ai.py --ai-payloads xss

# XSS with WAF bypass context
python3 psavvy_ai.py --ai-payloads xss --context '{"waf": "cloudflare", "technology": "PHP"}'

# SQL injection payloads
python3 psavvy_ai.py --ai-payloads sqli --context '{"dbms": "mysql"}'

# SSTI payloads
python3 psavvy_ai.py --ai-payloads ssti --context '{"engine": "jinja2"}'

# SSRF payloads
python3 psavvy_ai.py --ai-payloads ssrf --context '{"cloud": "aws"}'

# Command injection
python3 psavvy_ai.py --ai-payloads cmdi --context '{"os": "linux"}'

# LFI payloads
python3 psavvy_ai.py --ai-payloads lfi --context '{"os": "linux", "technology": "php"}'
```

#### Research Vulnerabilities
```bash
# Research specific CVE
python3 psavvy_ai.py --ai-research CVE-2024-1234

# Research vulnerability class
python3 psavvy_ai.py --ai-research "SQL Injection"

# Research product vulnerabilities
python3 psavvy_ai.py --ai-research "Apache Struts"
```

#### Get Exploitation Guidance
```bash
# Get exploitation plan
python3 psavvy_ai.py --ai-exploit "SQL Injection" --context '{"target": "example.com/login", "technology": "PHP/MySQL"}'
```

### Interactive AI Mode
```bash
python3 psavvy_ai.py --ai-interactive
```

Commands in interactive mode:
- `analyze` - Analyze scan results
- `research` - Research CVE/vulnerability
- `payloads` - Generate payloads
- `exploit` - Get exploitation guidance
- `report` - Generate report
- `quit` - Exit

### Skip Scanning (Analysis Only)
```bash
# Analyze existing results without scanning
python3 psavvy_ai.py -d target.com --skip-scan --ai-analyze
```

### Quick Scan Mode
```bash
# Faster scan with reduced tools
sudo python3 psavvy_ai.py -d target.com --quick --ai-analyze
```

## AI Features

### 1. Vulnerability Analysis
- **Result Triage**: Prioritizes findings by severity and exploitability
- **False Positive Detection**: Identifies likely false positives
- **Attack Chain Analysis**: Correlates findings for multi-step attacks
- **Severity Scoring**: CVSS-style scoring for each finding

### 2. Intelligent Payload Generation
- **Context-Aware**: Generates payloads based on target technology
- **WAF Bypass**: Creates evasion payloads for specific WAFs
- **Multiple Formats**: Encoded, obfuscated, and raw variants
- **Effectiveness Ratings**: Ranks payloads by success probability

### 3. Real-Time Research
- **CVE Lookup**: Detailed CVE information with exploits
- **Exploit Search**: Finds PoCs from GitHub, ExploitDB, etc.
- **Latest Vulnerabilities**: Recent disclosures for technologies
- **WAF Bypass Research**: Documented bypass techniques

### 4. Exploitation Assistance
- **Step-by-Step Plans**: Detailed exploitation procedures
- **Code Generation**: PoC exploit code generation
- **Failure Analysis**: Debugging failed exploitation attempts
- **Privilege Escalation**: Post-exploitation guidance

### 5. Automated Reporting
- **Executive Summary**: Non-technical overview for leadership
- **Technical Report**: Detailed findings for security teams
- **Remediation Guide**: Prioritized fix recommendations
- **Compliance Mapping**: Map to frameworks (PCI-DSS, HIPAA, etc.)

## Output Files

AI-generated outputs are saved to `output/`:

```
output/
├── AI_Analysis.md           # Comprehensive vulnerability analysis
├── AI_Triage.md              # Prioritized action items
├── AI_Attack_Chains.md       # Multi-step attack paths
└── reports/
    ├── executive_summary.md  # Executive summary
    ├── technical_report.md   # Technical details
    ├── remediation_guide.md  # Fix recommendations
    └── full_report.md        # Complete report
```

## Configuration

### config.yaml Structure

```yaml
# AI API Keys
ANTHROPIC_API_KEY: "your-claude-api-key"
PERPLEXITY_API_KEY: "your-perplexity-api-key"
OPENAI_API_KEY: "your-openai-api-key"

# Testing Callbacks
BURP_COLLAB_URL: "https://your-collaborator.oastify.com"
BLIND_XSS_URL: "https://webhook.site/your-id"

# AI Settings
ai_settings:
  claude_model: "claude-sonnet-4-20250514"
  perplexity_model: "llama-3.1-sonar-large-128k-online"
  openai_model: "gpt-4-turbo-preview"
  max_tokens: 4096
```

## Architecture

```
psavvy/
├── psavvy_ai.py              # Main AI-enhanced script
├── psavvy.py                 # Original script (still works)
├── config.yaml               # AI configuration
├── ai_engine/                # AI modules
│   ├── __init__.py
│   ├── providers.py          # Claude, Perplexity, ChatGPT clients
│   ├── analyzer.py           # Vulnerability analysis
│   ├── payload_generator.py  # Payload generation
│   ├── exploiter.py          # Exploitation assistance
│   ├── reporter.py           # Report generation
│   └── researcher.py         # CVE/exploit research
├── Tools/                    # Security tools
├── output/                   # Scan results & AI reports
└── install_ai.sh             # AI dependency installer
```

## API Usage & Costs

### Estimated API Costs (per assessment)

| Operation | Claude | Perplexity | ChatGPT | Estimated Cost |
|-----------|--------|------------|---------|----------------|
| Full Analysis | ~10K tokens | - | - | ~$0.15 |
| Triage | ~5K tokens | - | - | ~$0.08 |
| Attack Chains | ~5K tokens | - | - | ~$0.08 |
| Report Gen | - | - | ~20K tokens | ~$0.60 |
| CVE Research | - | ~5K tokens | - | ~$0.05 |
| Payload Gen | - | - | ~5K tokens | ~$0.15 |

**Total per assessment: ~$1-2**

### Rate Limits
- Claude: 40 requests/minute (default tier)
- Perplexity: 20 requests/minute
- OpenAI: 60 requests/minute (default tier)

## Examples

### Example 1: Complete Security Assessment
```bash
# Full scan with AI analysis and report
sudo python3 psavvy_ai.py -d example.com --ai-analyze --ai-report
```

### Example 2: Research Before Testing
```bash
# Research target technology first
python3 psavvy_ai.py --ai-research "WordPress"

# Generate appropriate payloads
python3 psavvy_ai.py --ai-payloads sqli --context '{"dbms": "mysql", "technology": "WordPress"}'

# Then run targeted scan
sudo python3 psavvy_ai.py -d example.com --ai-analyze
```

### Example 3: Analyze Existing Results
```bash
# If you already have scan results
python3 psavvy_ai.py -d example.com --skip-scan --ai-analyze --ai-report
```

### Example 4: Interactive Investigation
```bash
python3 psavvy_ai.py --ai-interactive

PSAVVY-AI> research CVE-2023-44487
PSAVVY-AI> payloads ssrf
PSAVVY-AI> analyze
PSAVVY-AI> report example.com
```

## Troubleshooting

### "No AI providers available"
- Verify API keys in config.yaml
- Check API key validity and billing status
- Ensure internet connectivity

### "AI modules not loaded"
- Run `sudo bash install_ai.sh`
- Check Python version (3.8+ required)
- Verify imports: `python3 -c "from ai_engine import *"`

### Slow AI Responses
- Reduce `max_tokens` in config
- Use smaller context windows
- Check API rate limits

### Empty Analysis Results
- Ensure scan completed and output files exist
- Check output directory has .txt files
- Verify file permissions

## Legal Notice

**IMPORTANT**: PSAVVY AI is designed for authorized security testing only.

- Always obtain written permission before testing
- Follow responsible disclosure practices
- Comply with all applicable laws and regulations
- AI-generated exploits are for educational/testing purposes only

## Credits

- Original PSAVVY: [DeepakGhengat](https://github.com/DeepakGhengat)
- AI Integration: PSAVVY AI Team
- Security Tools: Various open-source projects (see install.sh)

## License

This project is for educational and authorized security testing purposes only.
