# Advanced Web Security Scanner

`vul.py` is a **modular, multithreaded web-security scanner** written in Python 3.  
It helps developers and security engineers perform rapid reconnaissance against a target site, surfacing common mis-configurations and vulnerability indicators.

## Features
- **Security-header audit** – checks for missing CSP, HSTS, X-Frame-Options, etc.  
- **Sensitive-file discovery** – hunts for exposed backups, configs, and `.env` files.  
- **Form analyser** – enumerates HTML forms and their input names.  
- **SSL/TLS check** – validates certificate and negotiates protocol details.  
- **Directory brute-force** – wordlist + extension mangling with thread pooling.  
- **Sub-domain finder** – fast DNS resolution with HTTP probing.  
- **JavaScript endpoint miner** – pulls APIs, URLs, paths, and potential secrets.  
- **Cookie & CORS audit** – flags insecure attributes and overly-permissive ACAO.  
- **CVE look-up** – queries NVD (with a local fallback DB) for matching CVEs.

## Installation
```bash
git clone https://github.com/your-org/advanced-web-security-scanner.git
cd advanced-web-security-scanner
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
## Quick Start
- Full scan of a target :
```python vul.py https://example.com```

- Run selected modules only :
```python vul.py https://example.com --modules headers,dirs,cve```

- Directory brute-force with a custom wordlist & extra extensions :
```
python vul.py https://example.com \
  --wordlist dir.txt --extensions .php,.bak \
  --threads 20
```

Ethical notice
Run the scanner only against systems you own or have explicit permission to test.

## Output
```text id="output"
Two report files are saved under logs/<target-hostname>/ per run:

scan_<timestamp>.txt – human-readable summary
scan_<timestamp>.json – structured results for further parsing
Requirements
```
Create a requirements.txt beside vul.py with the following minimal dependencies:

requests>=2.0
urllib3>=2.0
beautifulsoup4>=4.0

Pin exact versions in production environments to ensure repeatable builds.

## Roadmap
 - Automatic rate-limit adaptation
 - HTML / Markdown report templates
 - Burp Suite plugin export

Contributions are welcome—open an issue or submit a PR!


## License

Released under the MIT License – see LICENSE for details.
```
:contentReference[oaicite:0]{index=0}
```
