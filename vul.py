import requests
import argparse
import logging
import socket
import ssl
import re
import json
import os
import sys
import urllib3
import concurrent.futures
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Set, Tuple

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_DIR_WORDLIST = [
    'admin', 'administrator', 'login', 'dashboard', 'panel',
    'wp-admin', 'wp-login.php', 'wp-content', 'wp-includes',
    'api', 'api/v1', 'api/v2', 'api/v3', 'graphql',
    'swagger', 'swagger-ui', 'api-docs', 'docs', 'redoc',
    'phpmyadmin', 'phpinfo.php', 'info.php', 'test.php',
    'console', 'shell', 'terminal', 'cmd',
    'backup', 'backups', 'bak', 'old', 'temp', 'tmp',
    'uploads', 'upload', 'files', 'media', 'images', 'assets',
    'static', 'public', 'private', 'internal',
    'config', 'configuration', 'settings', 'setup', 'install',
    '.env', '.git', '.git/config', '.git/HEAD', '.svn', '.svn/entries',
    '.htaccess', '.htpasswd', 'web.config', 'crossdomain.xml',
    'robots.txt', 'sitemap.xml', 'security.txt', '.well-known/security.txt',
    'server-status', 'server-info', 'status', 'health', 'healthcheck',
    'debug', 'trace', 'test', 'testing', 'dev', 'development', 'staging',
    'database', 'db', 'sql', 'mysql', 'postgres', 'mongodb',
    'log', 'logs', 'error_log', 'access_log', 'debug.log',
    'cgi-bin', 'cgi', 'bin', 'scripts',
    'user', 'users', 'account', 'accounts', 'profile', 'register', 'signup',
    'auth', 'authenticate', 'authorization', 'oauth', 'token', 'jwt',
    'search', 'query', 'find',
    'download', 'downloads', 'export', 'import',
    'admin/login', 'admin/dashboard', 'admin/config',
    'wp-json', 'wp-json/wp/v2/users', 'xmlrpc.php',
    'vendor', 'node_modules', 'composer.json', 'package.json',
    'Dockerfile', 'docker-compose.yml', '.dockerenv',
    '.DS_Store', 'Thumbs.db', 'desktop.ini',
    'README.md', 'README.txt', 'CHANGELOG.md', 'LICENSE',
    'ckeditor', 'tinymce', 'elfinder', 'filemanager',
    'cpanel', 'webmail', 'mail', 'email',
    'jenkins', 'gitlab', 'jira', 'confluence', 'grafana', 'kibana',
    'prometheus', 'metrics', 'monitoring',
    'actuator', 'actuator/env', 'actuator/health', 'actuator/info',
    'elmah.axd', 'trace.axd', 'web.config.bak',
    'solr', 'elasticsearch', 'redis', 'memcached',
    'socket.io', 'sockjs', 'websocket',
    'sitemap', 'feed', 'rss', 'atom',
    'proxy', 'gateway', 'loadbalancer',
    'api/swagger.json', 'api/openapi.json', 'openapi.yaml',
    'adminer.php', 'adminer', 'pma',
    'wp-cron.php', 'cron', 'crontab',
    '.bash_history', '.ssh', 'id_rsa', '.npmrc', '.env.local', '.env.production',
    'debug/vars', 'debug/pprof',
    'manager/html', 'manager/status',
    'invoker/JMXInvokerServlet',
    'jmx-console', 'web-console',
    'axis2-admin', 'axis2',
    'wp-config.php', 'wp-config.php.bak', 'wp-config.php.old',
    'config.php', 'config.php.bak', 'config.inc.php',
    'database.yml', 'database.sql', 'dump.sql', 'data.sql',
    'error', 'errors', '404', '500',
    'secret', 'secrets', 'credentials',
    'api/admin', 'api/debug', 'api/test', 'api/config',
    'graphiql', 'playground',
    '__debug__', '_debug_toolbar',
]

DEFAULT_SUBDOMAIN_WORDLIST = [
    'www', 'mail', 'ftp', 'smtp', 'pop', 'imap', 'webmail',
    'admin', 'administrator', 'panel', 'cpanel', 'whm',
    'dev', 'development', 'staging', 'stage', 'test', 'testing', 'qa',
    'beta', 'alpha', 'demo', 'sandbox', 'preview',
    'api', 'api2', 'api3', 'rest', 'graphql',
    'app', 'application', 'apps', 'mobile', 'm',
    'cdn', 'static', 'assets', 'media', 'images', 'img', 'files',
    'ns1', 'ns2', 'ns3', 'ns4', 'dns', 'dns1', 'dns2',
    'vpn', 'remote', 'gateway', 'proxy', 'edge',
    'db', 'database', 'mysql', 'postgres', 'mongo', 'redis', 'sql',
    'git', 'gitlab', 'github', 'svn', 'repo', 'repository',
    'ci', 'cd', 'jenkins', 'build', 'deploy',
    'monitor', 'monitoring', 'grafana', 'kibana', 'prometheus', 'nagios', 'zabbix',
    'log', 'logs', 'syslog', 'elk', 'elastic', 'elasticsearch',
    'jira', 'confluence', 'wiki', 'docs', 'documentation',
    'blog', 'cms', 'wp', 'wordpress', 'drupal', 'joomla',
    'shop', 'store', 'ecommerce', 'cart', 'pay', 'payment', 'billing',
    'auth', 'sso', 'login', 'id', 'identity', 'oauth', 'accounts',
    'chat', 'support', 'help', 'helpdesk', 'ticket', 'tickets',
    'crm', 'erp', 'hr', 'intranet', 'internal', 'portal',
    'backup', 'backups', 'bak', 'old', 'archive',
    'search', 'solr',
    'web', 'www2', 'www3', 'web1', 'web2',
    'mx', 'mx1', 'mx2', 'exchange',
    'cloud', 'aws', 'azure', 's3',
    'status', 'health', 'uptime',
    'news', 'newsletter', 'events', 'calendar',
    'video', 'stream', 'streaming', 'live',
    'secure', 'ssl', 'https',
    'data', 'analytics', 'stats', 'statistics', 'tracking',
]

KNOWN_CVES = {
    'apache': [
        {'id': 'CVE-2021-41773', 'severity': 9.8, 'desc': 'Apache 2.4.49 - Path Traversal & RCE'},
        {'id': 'CVE-2021-42013', 'severity': 9.8, 'desc': 'Apache 2.4.49-2.4.50 - Path Traversal & RCE (bypass of CVE-2021-41773)'},
        {'id': 'CVE-2023-25690', 'severity': 9.8, 'desc': 'Apache 2.4.0-2.4.55 - HTTP Request Smuggling'},
        {'id': 'CVE-2023-43622', 'severity': 7.5, 'desc': 'Apache 2.4.55-2.4.57 - HTTP/2 DoS'},
        {'id': 'CVE-2024-27316', 'severity': 7.5, 'desc': 'Apache 2.4.17-2.4.58 - HTTP/2 CONTINUATION DoS'},
    ],
    'nginx': [
        {'id': 'CVE-2021-23017', 'severity': 7.7, 'desc': 'nginx 0.6.18-1.20.0 - DNS Resolver Off-by-One Heap Write'},
        {'id': 'CVE-2022-41741', 'severity': 7.8, 'desc': 'nginx 1.1.3-1.23.2 - mp4 module memory corruption'},
        {'id': 'CVE-2024-7347',  'severity': 4.7, 'desc': 'nginx 1.5.13+ - mp4 module buffer over-read'},
    ],
    'php': [
        {'id': 'CVE-2024-4577',  'severity': 9.8, 'desc': 'PHP CGI Argument Injection RCE (Windows)'},
        {'id': 'CVE-2024-2961',  'severity': 8.8, 'desc': 'PHP iconv() buffer overflow'},
        {'id': 'CVE-2023-3824',  'severity': 9.8, 'desc': 'PHP phar buffer overflow'},
    ],
    'iis': [
        {'id': 'CVE-2023-36899', 'severity': 7.5, 'desc': 'IIS - ASP.NET Elevation of Privilege'},
        {'id': 'CVE-2022-30209', 'severity': 7.4, 'desc': 'IIS - Security Feature Bypass'},
    ],
    'openssl': [
        {'id': 'CVE-2024-5535',  'severity': 9.1, 'desc': 'OpenSSL - SSL_select_next_proto buffer overread'},
        {'id': 'CVE-2024-0727',  'severity': 5.5, 'desc': 'OpenSSL - PKCS12 NULL pointer dereference'},
        {'id': 'CVE-2023-5678',  'severity': 5.3, 'desc': 'OpenSSL - DH key generation excessive time'},
    ],
    'express': [
        {'id': 'CVE-2024-29041', 'severity': 6.1, 'desc': 'Express.js - Open Redirect via malformed URLs'},
    ],
    'tomcat': [
        {'id': 'CVE-2024-50379', 'severity': 9.8, 'desc': 'Tomcat - RCE via TOCTOU race condition on case-insensitive FS'},
        {'id': 'CVE-2024-23672', 'severity': 7.5, 'desc': 'Tomcat - WebSocket DoS'},
        {'id': 'CVE-2023-46589', 'severity': 7.5, 'desc': 'Tomcat - HTTP Request Smuggling'},
    ],
}

JS_PATTERNS = {
    'api_endpoints': re.compile(
        r'''(?:["'`])(/(?:api|v[0-9]+|graphql|rest|ajax|ws)[/][^\s"'`<>{}|\\^]{2,80})(?:["'`])''',
        re.IGNORECASE
    ),
    'full_urls': re.compile(
        r'''(?:["'`])(https?://[^\s"'`<>{}|\\^]{5,200})(?:["'`])''',
        re.IGNORECASE
    ),
    'relative_paths': re.compile(
        r'''(?:["'`])(/[a-zA-Z0-9_\-./]{2,80}(?:\.[a-zA-Z]{2,6})?)(?:["'`])''',
    ),
    'potential_secrets': re.compile(
        r'''(?:api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token|secret[_-]?key|'''
        r'''private[_-]?key|password|passwd|credentials|bearer|authorization)'''
        r'''\s*[:=]\s*["'`]([^"'`\s]{8,200})["'`]''',
        re.IGNORECASE
    ),
}


class SecurityScanner:
    def __init__(self, target_url: str, timeout: int = 5,
                 wordlist: Optional[str] = None,
                 extensions: Optional[str] = None,
                 sub_wordlist: Optional[str] = None,
                 threads: int = 10):
        self.target_url = target_url if target_url.startswith('http') else f"https://{target_url}"
        self.target_url = self.target_url.rstrip('/')
        self.timeout = timeout
        self.threads = threads
        self.wordlist = wordlist
        self.extensions = [e.strip() for e in extensions.split(',')] if extensions else []
        self.sub_wordlist = sub_wordlist
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.results = {}
        self.parsed_url = urlparse(self.target_url)
        self.hostname = self.parsed_url.netloc
        self.base_domain = self._extract_base_domain()

    def _extract_base_domain(self) -> str:
        parts = self.hostname.split('.')
        if len(parts) >= 2:
            return '.'.join(parts[-2:])
        return self.hostname

    def check_security_headers(self):
        logger.info(f"Checking security headers for {self.target_url}")
        try:
            response = self.session.get(self.target_url, timeout=self.timeout, verify=False)
            headers = response.headers

            required_headers = [
                'Content-Security-Policy',
                'Strict-Transport-Security',
                'X-Content-Type-Options',
                'X-Frame-Options',
                'Referrer-Policy'
            ]

            missing = [h for h in required_headers if h not in headers]
            self.results['missing_headers'] = missing

        except requests.RequestException as e:
            logger.error(f"Failed to connect for headers: {e}")

    def check_common_files(self):
        common_paths = [
            '/.env',
            '/.git/config',
            '/config.php',
            '/backup.sql',
            '/wp-config.php.bak'
        ]
        found_files = []

        logger.info("Scanning for common sensitive files...")
        for path in common_paths:
            url = urljoin(self.target_url, path)
            try:
                response = self.session.get(url, timeout=self.timeout, verify=False)
                if response.status_code == 200:
                    found_files.append(url)
            except requests.RequestException:
                continue

        self.results['exposed_files'] = found_files

    def check_forms(self):
        logger.info("Scanning forms for potential injection points...")
        try:
            response = self.session.get(self.target_url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            forms = soup.find_all('form')

            form_details = []
            for form in forms:
                action = form.get('action')
                method = form.get('method', 'get').lower()
                inputs = [i.get('name') for i in form.find_all('input') if i.get('name')]
                form_details.append({'action': action, 'method': method, 'inputs': inputs})

            self.results['forms'] = form_details
        except Exception as e:
            logger.error(f"Error parsing forms: {e}")

    def check_ssl_certificate(self):
        logger.info("Checking SSL/TLS Configuration...")
        hostname = self.hostname
        if ':' in hostname:
            hostname = hostname.split(':')[0]
        port = 443

        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    logger.info(f"SSL Certificate is valid for {hostname}")
                    self.results['ssl_info'] = "Valid"
        except Exception as e:
            logger.warning(f"SSL/TLS Error or Insecure: {e}")
            self.results['ssl_info'] = f"Insecure/Error: {e}"

    def _load_wordlist(self, path: Optional[str], default: list) -> list:
        if path:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    words = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                logger.info(f"Loaded {len(words)} entries from {path}")
                return words
            except FileNotFoundError:
                logger.error(f"Wordlist file not found: {path}. Using built-in wordlist.")
        return default

    def _bruteforce_single(self, path: str) -> Optional[Dict]:
        url = f"{self.target_url}/{path.lstrip('/')}"
        try:
            resp = self.session.get(url, timeout=self.timeout, verify=False, allow_redirects=False)
            if resp.status_code in (200, 201, 204, 301, 302, 307, 308, 403):
                return {
                    'url': url,
                    'status': resp.status_code,
                    'size': len(resp.content),
                    'redirect': resp.headers.get('Location', '') if resp.status_code in (301, 302, 307, 308) else ''
                }
        except requests.RequestException:
            pass
        return None

    def dir_bruteforce(self):
        logger.info(f"Starting Directory Bruteforce on {self.target_url}")
        words = self._load_wordlist(self.wordlist, DEFAULT_DIR_WORDLIST)

        paths = list(words)
        for word in words:
            for ext in self.extensions:
                ext = ext if ext.startswith('.') else f'.{ext}'
                paths.append(f"{word}{ext}")

        logger.info(f"Bruteforcing {len(paths)} paths with {self.threads} threads...")

        found = {'200': [], '301_302': [], '403': []}
        completed = 0
        total = len(paths)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_path = {executor.submit(self._bruteforce_single, p): p for p in paths}
            for future in concurrent.futures.as_completed(future_to_path):
                completed += 1
                if completed % 50 == 0 or completed == total:
                    logger.info(f"  Progress: {completed}/{total} ({completed*100//total}%)")

                result = future.result()
                if result:
                    status = result['status']
                    if status in (200, 201, 204):
                        found['200'].append(result)
                        logger.info(f"  [200] {result['url']} ({result['size']} bytes)")
                    elif status in (301, 302, 307, 308):
                        found['301_302'].append(result)
                        logger.info(f"  [{status}] {result['url']} -> {result['redirect']}")
                    elif status == 403:
                        found['403'].append(result)
                        logger.info(f"  [403] {result['url']} (Forbidden)")

        self.results['dir_bruteforce'] = found
        total_found = sum(len(v) for v in found.values())
        logger.info(f"Directory bruteforce complete. {total_found} interesting paths found.")

    def _resolve_subdomain(self, subdomain: str) -> Optional[Dict]:
        fqdn = f"{subdomain}.{self.base_domain}"
        try:
            addrs = socket.getaddrinfo(fqdn, None)
            ips = list(set(addr[4][0] for addr in addrs))

            http_status = None
            for scheme in ['https', 'http']:
                try:
                    resp = self.session.get(f"{scheme}://{fqdn}", timeout=self.timeout,
                                            verify=False, allow_redirects=False)
                    http_status = resp.status_code
                    break
                except requests.RequestException:
                    continue

            return {
                'subdomain': fqdn,
                'ips': ips,
                'http_status': http_status
            }
        except (socket.gaierror, socket.herror, OSError):
            return None

    def discover_subdomains(self):
        logger.info(f"Starting Subdomain Discovery for {self.base_domain}")
        words = self._load_wordlist(self.sub_wordlist, DEFAULT_SUBDOMAIN_WORDLIST)
        logger.info(f"Testing {len(words)} subdomains with {self.threads} threads...")

        found_subs = []
        completed = 0
        total = len(words)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_sub = {executor.submit(self._resolve_subdomain, w): w for w in words}
            for future in concurrent.futures.as_completed(future_to_sub):
                completed += 1
                if completed % 25 == 0 or completed == total:
                    logger.info(f"  Progress: {completed}/{total} ({completed*100//total}%)")

                result = future.result()
                if result:
                    found_subs.append(result)
                    status_str = f"HTTP {result['http_status']}" if result['http_status'] else "No HTTP"
                    logger.info(f"  FOUND: {result['subdomain']} -> {', '.join(result['ips'])} ({status_str})")

        self.results['subdomains'] = found_subs
        logger.info(f"Subdomain discovery complete. {len(found_subs)} subdomains found.")

    def discover_js_endpoints(self):
        logger.info(f"Starting JS Endpoint Discovery for {self.target_url}")

        try:
            response = self.session.get(self.target_url, timeout=self.timeout, verify=False)
            soup = BeautifulSoup(response.text, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Failed to fetch target page: {e}")
            return

        js_urls: Set[str] = set()
        for script in soup.find_all('script', src=True):
            src = script['src']
            if src.startswith('//'):
                src = f"https:{src}"
            elif src.startswith('/'):
                src = f"{self.parsed_url.scheme}://{self.hostname}{src}"
            elif not src.startswith('http'):
                src = f"{self.target_url}/{src}"
            js_urls.add(src)

        inline_scripts = []
        for script in soup.find_all('script', src=False):
            if script.string:
                inline_scripts.append(script.string)

        logger.info(f"Found {len(js_urls)} external JS files and {len(inline_scripts)} inline scripts")

        all_endpoints: Set[str] = set()
        all_urls: Set[str] = set()
        all_secrets: List[Dict] = []
        all_paths: Set[str] = set()

        def analyze_js_content(content: str, source: str):
            for match in JS_PATTERNS['api_endpoints'].finditer(content):
                all_endpoints.add(match.group(1))

            skip_domains = {'googleapis.com', 'gstatic.com', 'cloudflare.com',
                            'jquery.com', 'bootstrapcdn.com', 'fontawesome.com',
                            'google-analytics.com', 'googletagmanager.com',
                            'facebook.com', 'twitter.com', 'w3.org'}
            for match in JS_PATTERNS['full_urls'].finditer(content):
                url = match.group(1)
                parsed = urlparse(url)
                if not any(skip in parsed.netloc for skip in skip_domains):
                    all_urls.add(url)

            skip_extensions = {'.css', '.png', '.jpg', '.jpeg', '.gif', '.svg',
                               '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map'}
            for match in JS_PATTERNS['relative_paths'].finditer(content):
                path = match.group(1)
                if not any(path.endswith(ext) for ext in skip_extensions):
                    all_paths.add(path)

            for match in JS_PATTERNS['potential_secrets'].finditer(content):
                secret_value = match.group(1)
                if not all(c == '*' or c == 'x' for c in secret_value):
                    all_secrets.append({
                        'source': source,
                        'value': f"{secret_value[:12]}{'*' * max(0, len(secret_value) - 12)}",
                        'context': match.group(0)[:80]
                    })

        for js_url in js_urls:
            try:
                resp = self.session.get(js_url, timeout=self.timeout, verify=False)
                if resp.status_code == 200:
                    analyze_js_content(resp.text, js_url)
            except requests.RequestException:
                logger.warning(f"  Failed to fetch: {js_url}")

        for i, script_content in enumerate(inline_scripts):
            analyze_js_content(script_content, f"inline_script_{i}")

        self.results['js_endpoints'] = {
            'api_endpoints': sorted(all_endpoints),
            'urls': sorted(all_urls),
            'paths': sorted(all_paths),
            'potential_secrets': all_secrets,
            'js_files_analyzed': len(js_urls) + len(inline_scripts)
        }

        total = len(all_endpoints) + len(all_urls) + len(all_paths) + len(all_secrets)
        logger.info(f"JS analysis complete. {total} items discovered.")

    def audit_cookies_cors(self):
        logger.info(f"Starting Cookie & CORS Audit for {self.target_url}")

        cookie_issues = []
        try:
            resp = self.session.get(self.target_url, timeout=self.timeout, verify=False)
            raw_cookies = resp.headers.get('Set-Cookie', '')

            for cookie in self.session.cookies:
                issues = []
                if not cookie.secure:
                    issues.append('Missing Secure flag')
                if not cookie.has_nonstandard_attr('HttpOnly') and 'httponly' not in str(cookie).lower():
                    issues.append('Missing HttpOnly flag')
                if 'samesite' not in str(cookie).lower():
                    issues.append('Missing SameSite attribute')

                if issues:
                    cookie_issues.append({
                        'name': cookie.name,
                        'domain': cookie.domain,
                        'issues': issues
                    })

            if 'Set-Cookie' in resp.headers:
                for key, value in resp.raw.headers.items():
                    if key.lower() == 'set-cookie':
                        cookie_name = value.split('=')[0].strip()
                        issues = []
                        val_lower = value.lower()
                        if 'secure' not in val_lower:
                            issues.append('Missing Secure flag')
                        if 'httponly' not in val_lower:
                            issues.append('Missing HttpOnly flag')
                        if 'samesite' not in val_lower:
                            issues.append('Missing SameSite attribute')

                        if issues:
                            existing_names = [c['name'] for c in cookie_issues]
                            if cookie_name not in existing_names:
                                cookie_issues.append({
                                    'name': cookie_name,
                                    'domain': self.hostname,
                                    'issues': issues
                                })

        except requests.RequestException as e:
            logger.error(f"Failed to check cookies: {e}")

        cors_issues = []
        test_origins = [
            'https://evil.com',
            'https://attacker.example.com',
            'null',
            f'https://sub.{self.base_domain}',
            f'https://{self.base_domain}.evil.com',
        ]

        for origin in test_origins:
            try:
                headers = {'Origin': origin}
                resp = self.session.get(self.target_url, headers=headers,
                                        timeout=self.timeout, verify=False)

                acao = resp.headers.get('Access-Control-Allow-Origin', '')
                acac = resp.headers.get('Access-Control-Allow-Credentials', '').lower()

                if acao:
                    issue = {
                        'test_origin': origin,
                        'acao': acao,
                        'credentials': acac == 'true',
                        'severity': 'LOW'
                    }

                    if acao == '*':
                        issue['finding'] = 'Wildcard origin allowed'
                        issue['severity'] = 'MEDIUM'
                        if acac == 'true':
                            issue['finding'] = 'Wildcard origin with credentials — CRITICAL misconfiguration!'
                            issue['severity'] = 'CRITICAL'
                    elif acao == origin and origin not in (f'https://{self.base_domain}',
                                                          f'https://sub.{self.base_domain}'):
                        issue['finding'] = f'Arbitrary origin reflected: {origin}'
                        issue['severity'] = 'HIGH'
                        if acac == 'true':
                            issue['finding'] += ' WITH credentials — CRITICAL!'
                            issue['severity'] = 'CRITICAL'
                    elif acao == 'null':
                        issue['finding'] = 'null origin allowed'
                        issue['severity'] = 'MEDIUM'
                    else:
                        continue

                    cors_issues.append(issue)

            except requests.RequestException:
                continue

        self.results['cookie_audit'] = cookie_issues
        self.results['cors_audit'] = cors_issues
        logger.info(f"Cookie audit: {len(cookie_issues)} cookies with issues")
        logger.info(f"CORS audit: {len(cors_issues)} potential misconfigurations")

    def _parse_server_tech(self, headers: dict) -> List[Dict]:
        technologies = []
        patterns = [
            (r'(Apache)[/ ]+(\d+\.\d+\.\d+)', 'apache'),
            (r'(nginx)[/ ]+(\d+\.\d+\.\d+)', 'nginx'),
            (r'(PHP)[/ ]+(\d+\.\d+\.\d+)', 'php'),
            (r'(Microsoft-IIS)[/ ]+(\d+\.\d+)', 'iis'),
            (r'(OpenSSL)[/ ]+(\d+\.\d+\.\d+\w*)', 'openssl'),
            (r'(Express)', 'express'),
            (r'(Tomcat)[/ ]+(\d+\.\d+\.\d+)', 'tomcat'),
            (r'(Kestrel)', 'kestrel'),
            (r'(Werkzeug)[/ ]+(\d+\.\d+\.\d+)', 'werkzeug'),
            (r'(gunicorn)[/ ]+(\d+\.\d+\.\d+)', 'gunicorn'),
        ]

        header_values = []
        for key in ('Server', 'X-Powered-By', 'X-AspNet-Version', 'X-Generator'):
            val = headers.get(key, '')
            if val:
                header_values.append(val)

        for header_val in header_values:
            for pattern, tech_key in patterns:
                match = re.search(pattern, header_val, re.IGNORECASE)
                if match:
                    name = match.group(1)
                    version = match.group(2) if match.lastindex >= 2 else 'unknown'
                    technologies.append({
                        'name': name,
                        'version': version,
                        'key': tech_key,
                        'raw_header': header_val
                    })

        return technologies

    def _query_nvd_api(self, keyword: str) -> List[Dict]:
        cves = []
        try:
            api_url = 'https://services.nvd.nist.gov/rest/json/cves/2.0'
            params = {
                'keywordSearch': keyword,
                'resultsPerPage': 10,
            }
            resp = requests.get(api_url, params=params, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                for vuln in data.get('vulnerabilities', []):
                    cve_data = vuln.get('cve', {})
                    cve_id = cve_data.get('id', 'N/A')

                    descriptions = cve_data.get('descriptions', [])
                    desc = 'No description'
                    for d in descriptions:
                        if d.get('lang') == 'en':
                            desc = d.get('value', desc)[:150]
                            break

                    metrics = cve_data.get('metrics', {})
                    score = None
                    for metric_key in ('cvssMetricV31', 'cvssMetricV30', 'cvssMetricV2'):
                        metric_list = metrics.get(metric_key, [])
                        if metric_list:
                            score = metric_list[0].get('cvssData', {}).get('baseScore')
                            break

                    cves.append({
                        'id': cve_id,
                        'severity': score or 0.0,
                        'desc': desc
                    })

            elif resp.status_code == 403:
                logger.warning("NVD API rate limit hit. Using fallback database.")
                return []
        except Exception as e:
            logger.warning(f"NVD API request failed: {e}. Using fallback database.")
        return cves

    def lookup_cves(self):
        logger.info(f"Starting CVE Lookup for {self.target_url}")

        try:
            resp = self.session.get(self.target_url, timeout=self.timeout, verify=False)
        except requests.RequestException as e:
            logger.error(f"Failed to connect for CVE lookup: {e}")
            return

        technologies = self._parse_server_tech(resp.headers)

        if not technologies:
            logger.info("No identifiable server technology found in HTTP headers.")
            self.results['cve_lookup'] = {
                'technologies': [],
                'cves': [],
                'raw_server': resp.headers.get('Server', 'Not disclosed'),
                'raw_powered_by': resp.headers.get('X-Powered-By', 'Not disclosed'),
            }
            return

        logger.info(f"Detected technologies: {', '.join(t['name'] + '/' + t['version'] for t in technologies)}")

        all_cves = []
        for tech in technologies:
            search_term = f"{tech['name']} {tech['version']}"
            logger.info(f"  Querying NVD for: {search_term}")
            nvd_cves = self._query_nvd_api(search_term)

            if nvd_cves:
                for cve in nvd_cves:
                    cve['technology'] = tech['name']
                all_cves.extend(nvd_cves)
            else:
                logger.info(f"  Using fallback CVE database for {tech['key']}")
                fallback = KNOWN_CVES.get(tech['key'], [])
                for cve in fallback:
                    cve_copy = dict(cve)
                    cve_copy['technology'] = tech['name']
                    cve_copy['source'] = 'fallback_db'
                    all_cves.append(cve_copy)

        all_cves.sort(key=lambda x: x.get('severity', 0), reverse=True)

        self.results['cve_lookup'] = {
            'technologies': technologies,
            'cves': all_cves,
            'raw_server': resp.headers.get('Server', 'Not disclosed'),
            'raw_powered_by': resp.headers.get('X-Powered-By', 'Not disclosed'),
        }

        logger.info(f"CVE lookup complete. {len(all_cves)} potential CVEs found.")

    def run_scan(self, modules: Optional[str] = None):
        all_modules = {
            'headers':  ('Security Headers',       self.check_security_headers),
            'files':    ('Common Sensitive Files',  self.check_common_files),
            'forms':    ('Form Analysis',           self.check_forms),
            'ssl':      ('SSL/TLS Check',           self.check_ssl_certificate),
            'dirs':     ('Directory Bruteforce',    self.dir_bruteforce),
            'subs':     ('Subdomain Discovery',     self.discover_subdomains),
            'js':       ('JS Endpoint Discovery',   self.discover_js_endpoints),
            'cookies':  ('Cookie & CORS Audit',     self.audit_cookies_cors),
            'cve':      ('CVE Lookup',              self.lookup_cves),
        }

        if modules:
            selected = [m.strip().lower() for m in modules.split(',')]
            invalid = [m for m in selected if m not in all_modules]
            if invalid:
                logger.warning(f"Unknown modules: {', '.join(invalid)}")
                logger.info(f"Available modules: {', '.join(all_modules.keys())}")
        else:
            selected = list(all_modules.keys())

        print(f"\n{'='*60}")
        print(f"  SECURITY SCANNER — Target: {self.target_url}")
        print(f"  Modules: {', '.join(selected)}")
        print(f"{'='*60}\n")

        for key in selected:
            if key in all_modules:
                name, func = all_modules[key]
                print(f"\n{'─'*50}")
                print(f"  ▶ Running: {name}")
                print(f"{'─'*50}")
                try:
                    func()
                except Exception as e:
                    logger.error(f"Module '{name}' failed: {e}")

        self.print_report()
        self.save_log()

    def _build_report_text(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append(f"  SECURITY SCAN REPORT: {self.target_url}")
        lines.append(f"  Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)

        missing = self.results.get('missing_headers', [])
        lines.append(f"\n[!] Missing Security Headers: {len(missing)}")
        for h in missing:
            lines.append(f"    X {h}")

        exposed = self.results.get('exposed_files', [])
        lines.append(f"\n[!] Exposed Sensitive Files: {len(exposed)}")
        for f in exposed:
            lines.append(f"    X {f}")

        forms = self.results.get('forms', [])
        lines.append(f"\n[!] Forms Found: {len(forms)}")
        for form in forms:
            lines.append(f"    - Action: {form['action']}, Method: {form['method']}, Inputs: {form['inputs']}")

        ssl_info = self.results.get('ssl_info', 'N/A')
        lines.append(f"\n[!] SSL Status: {ssl_info}")

        dirs = self.results.get('dir_bruteforce')
        if dirs:
            total_dirs = sum(len(v) for v in dirs.values())
            lines.append(f"\n{'─'*50}")
            lines.append(f"[!] Directory Bruteforce Results: {total_dirs} paths found")
            if dirs['200']:
                lines.append(f"\n    Accessible (200):")
                for d in dirs['200']:
                    lines.append(f"      {d['url']} ({d['size']} bytes)")
            if dirs['301_302']:
                lines.append(f"\n    Redirects (301/302):")
                for d in dirs['301_302']:
                    lines.append(f"      {d['url']} -> {d['redirect']}")
            if dirs['403']:
                lines.append(f"\n    Forbidden (403):")
                for d in dirs['403']:
                    lines.append(f"      {d['url']}")

        subs = self.results.get('subdomains')
        if subs is not None:
            lines.append(f"\n{'─'*50}")
            lines.append(f"[!] Subdomain Discovery: {len(subs)} found")
            for s in subs:
                status = f"HTTP {s['http_status']}" if s['http_status'] else "No HTTP"
                lines.append(f"    - {s['subdomain']} -> {', '.join(s['ips'])} ({status})")

        js = self.results.get('js_endpoints')
        if js:
            lines.append(f"\n{'─'*50}")
            lines.append(f"[!] JS Endpoint Discovery ({js['js_files_analyzed']} scripts analyzed)")

            if js['api_endpoints']:
                lines.append(f"\n    API Endpoints ({len(js['api_endpoints'])}):")
                for ep in js['api_endpoints']:
                    lines.append(f"      - {ep}")

            if js['urls']:
                lines.append(f"\n    URLs ({len(js['urls'])}):")
                for url in js['urls']:
                    lines.append(f"      - {url}")

            if js['paths']:
                lines.append(f"\n    Paths ({len(js['paths'])}):")
                for p in js['paths']:
                    lines.append(f"      - {p}")

            if js['potential_secrets']:
                lines.append(f"\n    Potential Secrets ({len(js['potential_secrets'])}):")
                for secret in js['potential_secrets']:
                    lines.append(f"      [!] [{secret['source']}] {secret['context']}")

        cookies = self.results.get('cookie_audit')
        if cookies is not None:
            lines.append(f"\n{'─'*50}")
            lines.append(f"[!] Cookie Audit: {len(cookies)} cookies with issues")
            for c in cookies:
                lines.append(f"    X {c['name']} ({c['domain']})")
                for issue in c['issues']:
                    lines.append(f"        - {issue}")

        cors = self.results.get('cors_audit')
        if cors is not None:
            lines.append(f"\n{'─'*50}")
            lines.append(f"[!] CORS Audit: {len(cors)} potential issues")
            for c in cors:
                lines.append(f"    [{c['severity']}] {c['finding']}")
                lines.append(f"        Origin: {c['test_origin']} -> ACAO: {c['acao']}, Credentials: {c['credentials']}")

        cve_data = self.results.get('cve_lookup')
        if cve_data:
            lines.append(f"\n{'─'*50}")
            lines.append(f"[!] CVE Lookup")
            lines.append(f"    Server: {cve_data['raw_server']}")
            lines.append(f"    X-Powered-By: {cve_data['raw_powered_by']}")

            if cve_data['technologies']:
                lines.append(f"\n    Detected Technologies:")
                for tech in cve_data['technologies']:
                    lines.append(f"      - {tech['name']}/{tech['version']} (from: {tech['raw_header']})")

            cves = cve_data['cves']
            if cves:
                lines.append(f"\n    Potential CVEs ({len(cves)}):")
                for cve in cves:
                    score = cve.get('severity', 0)
                    if score >= 9.0:
                        level = 'CRITICAL'
                    elif score >= 7.0:
                        level = 'HIGH'
                    elif score >= 4.0:
                        level = 'MEDIUM'
                    else:
                        level = 'LOW'
                    source = ' (fallback DB)' if cve.get('source') == 'fallback_db' else ''
                    lines.append(f"      {level} [{cve['id']}] CVSS {score} - {cve['desc']}{source}")
            else:
                lines.append(f"\n    No known CVEs found for detected technologies.")

        lines.append(f"\n{'='*60}")
        lines.append(f"  Scan Complete")
        lines.append(f"{'='*60}")

        return '\n'.join(lines)

    def save_log(self):
        logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        os.makedirs(logs_dir, exist_ok=True)

        safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', self.hostname)
        site_dir = os.path.join(logs_dir, safe_name)
        os.makedirs(site_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        txt_filename = f"scan_{timestamp}.txt"
        json_filename = f"scan_{timestamp}.json"

        report_text = self._build_report_text()
        txt_path = os.path.join(site_dir, txt_filename)
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(report_text)

        json_results = {}
        json_results['target'] = self.target_url
        json_results['hostname'] = self.hostname
        json_results['scan_time'] = datetime.now().isoformat()

        for key, value in self.results.items():
            try:
                json.dumps(value)
                json_results[key] = value
            except (TypeError, ValueError):
                json_results[key] = str(value)

        json_path = os.path.join(site_dir, json_filename)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Log saved: {txt_path}")
        logger.info(f"Log saved: {json_path}")
        print(f"\n  Log files saved to: {site_dir}")
        print(f"    - {txt_filename}")
        print(f"    - {json_filename}")

    def print_report(self):
        print("\n" + "=" * 60)
        print(f"  SECURITY SCAN REPORT: {self.target_url}")
        print("=" * 60)

        missing = self.results.get('missing_headers', [])
        print(f"\n[!] Missing Security Headers: {len(missing)}")
        for h in missing:
            print(f"    ✗ {h}")

        exposed = self.results.get('exposed_files', [])
        print(f"\n[!] Exposed Sensitive Files: {len(exposed)}")
        for f in exposed:
            print(f"    ✗ {f}")

        forms = self.results.get('forms', [])
        print(f"\n[!] Forms Found: {len(forms)}")
        for form in forms:
            print(f"    • Action: {form['action']}, Method: {form['method']}, Inputs: {form['inputs']}")

        ssl_info = self.results.get('ssl_info', 'N/A')
        print(f"\n[!] SSL Status: {ssl_info}")

        dirs = self.results.get('dir_bruteforce')
        if dirs:
            total_dirs = sum(len(v) for v in dirs.values())
            print(f"\n{'─'*50}")
            print(f"[!] Directory Bruteforce Results: {total_dirs} paths found")
            if dirs['200']:
                print(f"\n    ✓ Accessible (200):")
                for d in dirs['200']:
                    print(f"      {d['url']} ({d['size']} bytes)")
            if dirs['301_302']:
                print(f"\n    → Redirects (301/302):")
                for d in dirs['301_302']:
                    print(f"      {d['url']} -> {d['redirect']}")
            if dirs['403']:
                print(f"\n    ✗ Forbidden (403):")
                for d in dirs['403']:
                    print(f"      {d['url']}")

        subs = self.results.get('subdomains')
        if subs is not None:
            print(f"\n{'─'*50}")
            print(f"[!] Subdomain Discovery: {len(subs)} found")
            for s in subs:
                status = f"HTTP {s['http_status']}" if s['http_status'] else "No HTTP"
                print(f"    • {s['subdomain']} -> {', '.join(s['ips'])} ({status})")

        js = self.results.get('js_endpoints')
        if js:
            print(f"\n{'─'*50}")
            print(f"[!] JS Endpoint Discovery ({js['js_files_analyzed']} scripts analyzed)")

            if js['api_endpoints']:
                print(f"\n    API Endpoints ({len(js['api_endpoints'])}):")
                for ep in js['api_endpoints'][:30]:
                    print(f"      • {ep}")
                if len(js['api_endpoints']) > 30:
                    print(f"      ... and {len(js['api_endpoints']) - 30} more")

            if js['urls']:
                print(f"\n    URLs ({len(js['urls'])}):")
                for url in js['urls'][:20]:
                    print(f"      • {url}")
                if len(js['urls']) > 20:
                    print(f"      ... and {len(js['urls']) - 20} more")

            if js['paths']:
                print(f"\n    Paths ({len(js['paths'])}):")
                for p in js['paths'][:20]:
                    print(f"      • {p}")
                if len(js['paths']) > 20:
                    print(f"      ... and {len(js['paths']) - 20} more")

            if js['potential_secrets']:
                print(f"\n    ⚠ Potential Secrets ({len(js['potential_secrets'])}):")
                for secret in js['potential_secrets'][:10]:
                    print(f"      ⚠ [{secret['source']}] {secret['context']}")

        cookies = self.results.get('cookie_audit')
        if cookies is not None:
            print(f"\n{'─'*50}")
            print(f"[!] Cookie Audit: {len(cookies)} cookies with issues")
            for c in cookies:
                print(f"    ✗ {c['name']} ({c['domain']})")
                for issue in c['issues']:
                    print(f"        - {issue}")

        cors = self.results.get('cors_audit')
        if cors is not None:
            print(f"\n{'─'*50}")
            print(f"[!] CORS Audit: {len(cors)} potential issues")
            for c in cors:
                severity_icon = {'LOW': 'ℹ', 'MEDIUM': '⚠', 'HIGH': '✗', 'CRITICAL': '🔴'}.get(c['severity'], '•')
                print(f"    {severity_icon} [{c['severity']}] {c['finding']}")
                print(f"        Origin: {c['test_origin']} → ACAO: {c['acao']}, Credentials: {c['credentials']}")

        cve_data = self.results.get('cve_lookup')
        if cve_data:
            print(f"\n{'─'*50}")
            print(f"[!] CVE Lookup")
            print(f"    Server: {cve_data['raw_server']}")
            print(f"    X-Powered-By: {cve_data['raw_powered_by']}")

            if cve_data['technologies']:
                print(f"\n    Detected Technologies:")
                for tech in cve_data['technologies']:
                    print(f"      • {tech['name']}/{tech['version']} (from: {tech['raw_header']})")

            cves = cve_data['cves']
            if cves:
                print(f"\n    Potential CVEs ({len(cves)}):")
                for cve in cves[:20]:
                    score = cve.get('severity', 0)
                    if score >= 9.0:
                        level = '🔴 CRITICAL'
                    elif score >= 7.0:
                        level = '🟠 HIGH'
                    elif score >= 4.0:
                        level = '🟡 MEDIUM'
                    else:
                        level = '🟢 LOW'
                    source = ' (fallback DB)' if cve.get('source') == 'fallback_db' else ''
                    print(f"      {level} [{cve['id']}] CVSS {score} — {cve['desc']}{source}")
                if len(cves) > 20:
                    print(f"      ... and {len(cves) - 20} more")
            else:
                print(f"\n    ✓ No known CVEs found for detected technologies.")

        print(f"\n{'='*60}")
        print(f"  Scan Complete")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Advanced Web Security Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python vul.py https://example.com
  python vul.py https://example.com --modules headers,dirs,cve
  python vul.py https://example.com --wordlist custom.txt --extensions .php,.bak
  python vul.py https://example.com --modules subs --sub-wordlist subdomains.txt --threads 20

Available modules:
  headers  — Check missing security headers
  files    — Scan for exposed sensitive files
  forms    — Analyze HTML forms for injection points
  ssl      — Verify SSL/TLS certificate
  dirs     — Directory bruteforce
  subs     — Subdomain discovery
  js       — JS endpoint & secret discovery
  cookies  — Cookie & CORS security audit
  cve      — CVE lookup for detected technologies
        """
    )
    parser.add_argument("url", help="Target URL to scan")
    parser.add_argument("--wordlist", help="Custom wordlist file for directory bruteforce")
    parser.add_argument("--extensions", help="File extensions to append (comma-separated, e.g. .php,.html,.bak)")
    parser.add_argument("--sub-wordlist", help="Custom wordlist file for subdomain discovery")
    parser.add_argument("--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("--timeout", type=int, default=5, help="Request timeout in seconds (default: 5)")
    parser.add_argument("--modules", help="Comma-separated list of modules to run (default: all)")
    args = parser.parse_args()

    scanner = SecurityScanner(
        target_url=args.url,
        timeout=args.timeout,
        wordlist=args.wordlist,
        extensions=args.extensions,
        sub_wordlist=args.sub_wordlist,
        threads=args.threads,
    )
    scanner.run_scan(modules=args.modules)