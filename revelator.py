# -*- coding: utf-8 -*-
import re
import json
import argparse
import requests
import sys
import os
import time
import math
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse, urljoin, urlsplit, parse_qsl
from datetime import datetime, timezone

# -------------------------------------------------------------------------
# Tool: Revelator
# Version: 3.0 (Revelation - The Deep Recon Engine)
# Author: R00t3dbyFa17h / NicholasMullenski / K70n0s510
#         (K70n0s510 = HackTheBox, Bugcrowd, Microsoft, Intigriti & Google bug bounty handle)
# Verse: "Search me, God, and know my heart..." (Psalm 139:23)
# -------------------------------------------------------------------------
#
# v3.0 is a strictly ADDITIVE upgrade. Every v2.0 function, class, CLI flag
# (-d, -p), the ASCII banner, the HTML report and the Postman export behave
# exactly as before when run the same way. All new power is opt-in via new
# flags (see --help) or purely additive enhancements that never remove the
# original output. See README.md for the full v3.0 feature list.
# -------------------------------------------------------------------------

VERSION = "3.0"

def _utcnow_iso():
    """Timezone-aware UTC timestamp as 'YYYY-MM-DDTHH:MM:SSZ'."""
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def banner():
    print(Colors.HEADER + r"""
██████╗ ███████╗██╗   ██╗███████╗██╗      █████╗ ████████╗ ██████╗ ██████╗
██╔══██╗██╔════╝██║   ██║██╔════╝██║     ██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
██████╔╝█████╗  ██║   ██║█████╗  ██║     ███████║   ██║   ██║   ██║██████╔╝
██╔══██╗██╔══╝  ╚██╗ ██╔╝██╔══╝  ██║     ██╔══██║   ██║   ██║   ██║██╔══██╗
██║  ██║███████╗ ╚████╔╝ ███████╗███████╗██║  ██║   ██║   ╚██████╔╝██║  ██║
╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
                     v3.0 (REVELATION) - The Deep Recon Engine
    """ + Colors.ENDC)

def get_js_links(url):
    print(Colors.BLUE + f" [*] Crawling {url} for JavaScript files..." + Colors.ENDC)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(Colors.FAIL + f" [!] Failed to connect to site: {response.status_code}" + Colors.ENDC)
            return []

        # Regex to find <script src="...">
        script_pattern = r'<script[^>]+src=["\'](.*?)["\']'
        links = re.findall(script_pattern, response.text)
        
        valid_js = []
        for link in links:
            # Handle relative URLs
            full_url = urljoin(url, link)
            
            # Filter: Must be a .js file, not a tracker
            if ".js" in full_url and "google" not in full_url and "facebook" not in full_url:
                valid_js.append(full_url)
        
        # Remove duplicates
        return list(set(valid_js))

    except Exception as e:
        print(Colors.FAIL + f" [!] Crawler Error: {e}" + Colors.ENDC)
        return []

def fetch_js_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Revelator-Scanner)'}
        response = requests.get(url, headers=headers, timeout=10)
        return response.text if response.status_code == 200 else None
    except:
        return None

def extract_endpoints(js_content):
    endpoints = set()
    # Floodlight Regex
    matches = re.findall(r"(['\"`])(.*?)\1", js_content)
    for quote, content in matches:
        if '/' in content and ' ' not in content and 4 < len(content) < 120:
             if not content.endswith(('.png', '.svg', '.css', '.js', '.ico', '.html')):
                if not content.startswith(('http', '//', 'www', '<', '>')):
                     if content.startswith('/') or 'api' in content or 'v1' in content:
                        endpoints.add(content)
    return list(endpoints)

def scan_secrets(content):
    signatures = {
        "AWS Key": r"AKIA[0-9A-Z]{16}",
        "Google Key": r"AIza[0-9A-Za-z\\-_]{35}",
        "Generic Token": r"(api_key|access_token)\s*[:=]\s*['\"`]([a-zA-Z0-9_\-]{10,})['\"`]"
    }
    found = []
    for name, pattern in signatures.items():
        for match in re.findall(pattern, content):
            val = match if isinstance(match, str) else match[1]
            found.append({"type": name, "value": val})
    return found

def generate_report(results, target_domain):
    parsed_domain = urlparse(target_domain).netloc or target_domain
    filename = f"revelator_report_{parsed_domain}.html"
    
    total_endpoints = sum(len(r['endpoints']) for r in results)
    total_secrets = sum(len(r['secrets']) for r in results)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Revelator Scan: {target_domain}</title>
        <style>
            body {{ background: #0d1117; color: #c9d1d9; font-family: sans-serif; padding: 20px; }}
            .header {{ border-bottom: 1px solid #30363d; padding-bottom: 20px; margin-bottom: 20px; }}
            h1 {{ color: #58a6ff; }}
            .file-block {{ background: #161b22; border: 1px solid #30363d; margin-bottom: 20px; border-radius: 6px; overflow: hidden; }}
            .file-title {{ background: #21262d; padding: 10px; font-weight: bold; color: #f0f6fc; border-bottom: 1px solid #30363d; }}
            .item {{ padding: 5px 15px; border-bottom: 1px solid #21262d; font-family: monospace; }}
            .secret {{ color: #ff7b72; font-weight: bold; }}
            .endpoint {{ color: #7ee787; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>REVELATOR REPORT</h1>
            <h3>Target: {target_domain}</h3>
            <p>Files Scanned: {len(results)} | Endpoints Found: {total_endpoints} | Secrets: {total_secrets}</p>
        </div>
    """
    
    for res in results:
        if not res['endpoints'] and not res['secrets']:
            continue
            
        html += f"""
        <div class="file-block">
            <div class="file-title">{res['url']}</div>
            {''.join([f'<div class="item secret">[SECRET] {s["type"]}: {s["value"]}</div>' for s in res['secrets']])}
            {''.join([f'<div class="item endpoint">[GET] {e}</div>' for e in res['endpoints']])}
        </div>
        """
        
    html += "</body></html>"
    
    with open(filename, "w") as f:
        f.write(html)
    print(Colors.GREEN + f" [+] HTML Report Generated: {filename}" + Colors.ENDC)

def generate_postman_collection(all_endpoints, target_domain):
    parsed_domain = urlparse(target_domain).netloc or target_domain
    collection_name = f"Revelator: {parsed_domain}"
    
    collection = {
        "info": {
            "name": collection_name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    for endpoint in all_endpoints:
        # Ensure endpoint starts with a slash for clean parsing
        clean_endpoint = endpoint if endpoint.startswith('/') else '/' + endpoint
        full_url = urljoin(target_domain, clean_endpoint)
        path_array = [p for p in clean_endpoint.split('/') if p]

        item = {
            "name": clean_endpoint,
            "request": {
                "method": "GET",
                "url": {
                    "raw": full_url,
                    "host": [target_domain],
                    "path": path_array
                }
            }
        }
        collection["item"].append(item)

    filename = f"revelator_postman_{parsed_domain}.json"
    with open(filename, "w") as f:
        json.dump(collection, f, indent=4)
        
    print(Colors.GREEN + f" [+] Postman Collection Generated: {filename}" + Colors.ENDC)

# =========================================================================
# v3.0 ADDITIONS BELOW  --  everything above is preserved from v2.0 as-is.
# All helpers below are new; none replace or alter v2.0 behavior.
# =========================================================================

# ---- Logging helpers (respect --quiet / --verbose; default = unchanged) --

_LOG = {"quiet": False, "verbose": False}

def log_info(msg):
    if not _LOG["quiet"]:
        print(msg)

def log_verbose(msg):
    if _LOG["verbose"] and not _LOG["quiet"]:
        print(Colors.BLUE + f"   [v] {msg}" + Colors.ENDC)

def log_warn(msg):
    if not _LOG["quiet"]:
        print(Colors.WARNING + msg + Colors.ENDC)

def log_err(msg):
    # Errors are always surfaced, even in quiet mode, on stderr.
    print(Colors.FAIL + msg + Colors.ENDC, file=sys.stderr)

# ---- HTTP session / fetch with retries, backoff, proxy, auth ------------

def build_session(args):
    """Build a configured requests.Session for the enhanced scan paths.

    Default values mirror v2.0 behavior (plain GET, verify on, no proxy).
    """
    session = requests.Session()
    default_ua = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    session.headers.update({'User-Agent': getattr(args, 'user_agent', None) or default_ua})

    # Custom headers (-H "Name: Value")
    for raw in (args.header or []):
        if ':' in raw:
            name, _, value = raw.partition(':')
            session.headers[name.strip()] = value.strip()
        else:
            log_warn(f" [-] Ignoring malformed header (expected 'Name: Value'): {raw}")

    # Cookies (--cookie "a=1; b=2")
    if args.cookie:
        for part in args.cookie.split(';'):
            if '=' in part:
                k, _, v = part.partition('=')
                session.cookies.set(k.strip(), v.strip())

    # Proxy (route through Burp etc.)
    if args.proxy:
        session.proxies.update({'http': args.proxy, 'https': args.proxy})

    # TLS verification toggle
    if args.insecure:
        session.verify = False
        try:
            import urllib3
            urllib3.disable_warnings()
        except Exception:
            pass

    return session

def fetch_text(session, url, args):
    """Fetch text content with retries + exponential backoff.

    Returns the response body on HTTP 200, else None. Never raises.
    """
    delay = _effective_delay(args)
    retries = max(0, args.retries)
    for attempt in range(retries + 1):
        try:
            if delay > 0:
                time.sleep(delay)
            resp = session.get(url, timeout=args.timeout)
            if resp.status_code == 200:
                return resp.text
            # Retry transient server/ratelimit responses.
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = min(2 ** attempt, 16)
                log_verbose(f"HTTP {resp.status_code} on {url}; backing off {wait}s")
                time.sleep(wait)
                continue
            log_verbose(f"HTTP {resp.status_code} on {url}")
            return None
        except requests.RequestException as e:
            if attempt < retries:
                wait = min(2 ** attempt, 16)
                log_verbose(f"Error on {url} ({e}); retry in {wait}s")
                time.sleep(wait)
                continue
            log_verbose(f"Giving up on {url}: {e}")
            return None
    return None

def _effective_delay(args):
    if args.rate_limit and args.rate_limit > 0:
        return 1.0 / args.rate_limit
    return max(0.0, args.delay)

# ---- Deeper crawl: inline scripts, chunks, source maps ------------------

def extract_inline_scripts(html):
    """Return a list of (pseudo-name, content) for inline <script> blocks
    (those WITHOUT a src attribute)."""
    results = []
    idx = 0
    for m in re.finditer(r"<script\b([^>]*)>(.*?)</script>", html, re.I | re.S):
        attrs, body = m.group(1), m.group(2)
        if re.search(r"\bsrc\s*=", attrs, re.I):
            continue  # external script handled elsewhere
        body = body.strip()
        if body:
            idx += 1
            results.append((f"inline-script-#{idx}", body))
    return results

def discover_chunk_urls(content, base_url, same_host_only=True):
    """Heuristically discover additional JS chunk URLs referenced in a page
    or a JS bundle (webpack lazy-loaded chunks, import() calls, static refs)."""
    found = set()
    base_host = urlparse(base_url).netloc

    patterns = [
        # Any quoted reference that ends in .js (chunks, vendors, runtime)
        r"""['"`]([A-Za-z0-9_./@\-]+?\.js)['"`]""",
        # dynamic import()
        r"""import\(\s*['"`]([^'"`]+?\.js)['"`]\s*\)""",
        # Next.js / webpack static chunk paths
        r"""['"`](/_next/static/[^'"`]+?\.js)['"`]""",
        r"""['"`]((?:/)?static/js/[^'"`]+?\.js)['"`]""",
        # hashed chunk filenames (e.g. 23.4a1b2c3d.chunk.js)
        r"""['"`]([A-Za-z0-9_./\-]+?\.[a-f0-9]{6,}\.(?:chunk\.)?js)['"`]""",
    ]
    for pat in patterns:
        for ref in re.findall(pat, content):
            ref = ref.strip()
            if not ref or ' ' in ref:
                continue
            full = urljoin(base_url, ref)
            if 'google' in full or 'facebook' in full:
                continue
            if same_host_only and urlparse(full).netloc and urlparse(full).netloc != base_host:
                continue
            if full.split('?')[0].endswith('.js'):
                found.add(full)
    return found

def find_source_map_url(content, js_url):
    """Return the sourceMappingURL for a JS file, if declared."""
    m = re.search(r"//[#@]\s*sourceMappingURL=([^\s'\"]+)", content)
    if m:
        ref = m.group(1).strip()
        if ref.startswith('data:'):
            return None  # inline data maps handled separately
        return urljoin(js_url, ref)
    return None

def parse_source_map(map_text):
    """Parse a .map file and recover original source paths and their
    embedded content (sourcesContent). Returns (sources, contents)."""
    sources, contents = [], []
    try:
        data = json.loads(map_text)
    except Exception:
        return sources, contents
    for s in (data.get("sources") or []):
        if isinstance(s, str):
            sources.append(s)
    for c in (data.get("sourcesContent") or []):
        if isinstance(c, str):
            contents.append(c)
    return sources, contents

# ---- Smarter endpoint extraction (opt-in --strict) + method detection ---

_STRICT_SKIP_EXT = (
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.css', '.js', '.ico', '.html',
    '.woff', '.woff2', '.ttf', '.eot', '.map', '.txt', '.xml', '.mp4', '.webp',
    '.scss', '.less', '.json', '.wasm', '.mp3', '.pdf', '.avif',
)

def extract_endpoints_strict(js_content):
    """A refined extractor that trims the false positives produced by the
    original (regex-looking junk, escaped fragments, image/static paths)
    while keeping genuine API-looking paths. Opt-in via --strict."""
    endpoints = set()
    for quote, content in re.findall(r"(['\"`])(.*?)\1", js_content):
        c = content.strip()
        if not c or ' ' in c or '\\' in c:
            continue
        if len(c) < 2 or len(c) > 120:
            continue
        if c.startswith(('http', '//', 'www', '<', '>', 'data:', 'mailto:', 'tel:')):
            continue
        if './' in c or '../' in c:
            continue
        # Cut regex-looking junk (metacharacters that never belong in a path).
        if re.search(r'[()\[\]|*+^$]', c):
            continue
        low = c.lower()
        if low.endswith(_STRICT_SKIP_EXT):
            continue
        # Must look like an API path or versioned route.
        looks_api = (
            c.startswith('/') or c.startswith('api/') or
            'api' in low or re.search(r'/v\d', low) or re.search(r'\bv\d/', low)
        )
        if not looks_api:
            continue
        # Final shape check: only path-safe characters.
        if not re.match(r'^/?[A-Za-z0-9_.\-/:{}?=&%]+$', c):
            continue
        endpoints.add(c)
    return list(endpoints)

def detect_endpoint_methods(js_content):
    """Detect HTTP methods for endpoints from fetch()/axios/XHR/$.ajax
    call patterns. Returns {endpoint: METHOD}. Best-effort/heuristic."""
    methods = {}

    def put(ep, m):
        ep = ep.strip()
        if ep:
            methods[ep] = m.upper()

    # fetch('url', { method: 'POST' })
    for m in re.finditer(
            r"""fetch\(\s*['"`]([^'"`]+)['"`]\s*,\s*\{[^{}]*?method\s*:\s*['"`](get|post|put|delete|patch)['"`]""",
            js_content, re.I | re.S):
        put(m.group(1), m.group(2))
    # fetch('url')  -> default GET (don't clobber an explicit method)
    for m in re.finditer(r"""fetch\(\s*['"`]([^'"`]+)['"`]""", js_content):
        methods.setdefault(m.group(1).strip(), 'GET')
    # axios.get('url'), axios.post('url'), ...
    for m in re.finditer(
            r"""axios\.(get|post|put|delete|patch)\(\s*['"`]([^'"`]+)['"`]""",
            js_content, re.I):
        put(m.group(2), m.group(1))
    # axios({ url: '...', method: '...' })  (order-independent)
    for m in re.finditer(r"""axios\(\s*\{([^{}]*?)\}""", js_content, re.I | re.S):
        blob = m.group(1)
        um = re.search(r"""url\s*:\s*['"`]([^'"`]+)['"`]""", blob)
        mm = re.search(r"""method\s*:\s*['"`](get|post|put|delete|patch)['"`]""", blob, re.I)
        if um:
            put(um.group(1), (mm.group(1) if mm else 'get'))
    # jQuery $.get / $.post
    for m in re.finditer(r"""\$\.(get|post)\(\s*['"`]([^'"`]+)['"`]""", js_content, re.I):
        put(m.group(2), m.group(1))
    # $.ajax({ url: '...', type/method: '...' })
    for m in re.finditer(r"""\$\.ajax\(\s*\{([^{}]*?)\}""", js_content, re.I | re.S):
        blob = m.group(1)
        um = re.search(r"""url\s*:\s*['"`]([^'"`]+)['"`]""", blob)
        mm = re.search(r"""(?:type|method)\s*:\s*['"`](get|post|put|delete|patch)['"`]""", blob, re.I)
        if um:
            put(um.group(1), (mm.group(1) if mm else 'get'))
    # XMLHttpRequest: xhr.open('POST', '/url')
    for m in re.finditer(
            r"""\.open\(\s*['"`](get|post|put|delete|patch)['"`]\s*,\s*['"`]([^'"`]+)['"`]""",
            js_content, re.I):
        put(m.group(2), m.group(1))
    # Generic http-client style: client.put('/url', ...), api.delete('/url')
    for m in re.finditer(
            r"""\b[\w$]+\.(get|post|put|delete|patch)\(\s*['"`](/[^'"`]+)['"`]""",
            js_content, re.I):
        methods.setdefault(m.group(2).strip(), m.group(1).upper())

    return methods

# ---- LinkFinder-grade endpoint extractor (high recall, opt-in merge) ----

# Faithful adaptation of GerbenJavado/LinkFinder's battle-tested regex:
# matches full URLs, absolute/relative paths, REST routes, and files with
# common extensions. Gives Revelator parity with the industry-standard tool.
_LINKFINDER_REGEX = re.compile(r"""
  (?:"|'|`)
  (
    ((?:[a-zA-Z]{1,10}://|//)[^"'`/]{1,}\.[a-zA-Z]{2,}[^"'`]{0,})
    |
    ((?:/|\.\./|\./)[^"'`><,;| *()(%$^/\\\[\]][^"'`><,;|()]{1,})
    |
    ([a-zA-Z0-9_\-/]{1,}/[a-zA-Z0-9_\-/.]{1,}\.(?:[a-zA-Z]{1,4}|action)(?:[\?|#][^"|'`]{0,}|))
    |
    ([a-zA-Z0-9_\-/]{1,}/[a-zA-Z0-9_\-/]{3,}(?:[\?|#][^"|'`]{0,}|))
    |
    ([a-zA-Z0-9_\-]{1,}\.(?:php|asp|aspx|jsp|json|action|html|js|txt|xml)(?:[\?|#][^"|'`]{0,}|))
  )
  (?:"|'|`)
""", re.VERBOSE)

_STATIC_ASSET_EXT = (
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.css', '.ico', '.woff', '.woff2',
    '.ttf', '.eot', '.webp', '.avif', '.mp4', '.mp3', '.wav', '.pdf', '.map',
    '.scss', '.less', '.wasm',
)

def _is_static_asset(path):
    low = path.split('?')[0].split('#')[0].lower()
    return low.endswith(_STATIC_ASSET_EXT)

def extract_endpoints_linkfinder(js_content):
    """High-recall endpoint discovery using the LinkFinder regex. Returns a
    de-duplicated list (order-stable). Use --match / -r to filter."""
    results = []
    seen = set()
    for m in _LINKFINDER_REGEX.finditer(js_content):
        val = m.group(1).strip()
        if not val or len(val) > 200:
            continue
        if val in seen:
            continue
        seen.add(val)
        results.append(val)
    return results

# ---- GraphQL / DOM-sink / host / bucket / parameter intelligence --------

def detect_graphql(content):
    """Detect GraphQL endpoints and operation names in a JS blob."""
    endpoints = set()
    for m in re.finditer(r"""['"`](/?[^'"`\s]*graphql[^'"`\s]*)['"`]""", content, re.I):
        ep = m.group(1)
        if len(ep) < 120:
            endpoints.add(ep)
    operations = []
    seen = set()
    for m in re.finditer(r"\b(query|mutation|subscription)\s+([A-Za-z_][A-Za-z0-9_]{1,60})\s*[\({]", content):
        key = (m.group(1).lower(), m.group(2))
        if key in seen:
            continue
        seen.add(key)
        operations.append({"type": m.group(1).lower(), "name": m.group(2)})
        if len(operations) >= 50:
            break
    return {"endpoints": sorted(endpoints), "operations": operations}

_DOM_SINKS = [
    ("innerHTML", r"\.innerHTML\s*="),
    ("outerHTML", r"\.outerHTML\s*="),
    ("document.write", r"document\.write(?:ln)?\s*\("),
    ("eval", r"\beval\s*\("),
    ("Function constructor", r"\bnew\s+Function\s*\("),
    ("setTimeout(string)", r"setTimeout\s*\(\s*['\"`]"),
    ("setInterval(string)", r"setInterval\s*\(\s*['\"`]"),
    ("insertAdjacentHTML", r"\.insertAdjacentHTML\s*\("),
    ("dangerouslySetInnerHTML", r"dangerouslySetInnerHTML"),
    ("location assignment", r"(?:window\.|document\.)?location(?:\.href)?\s*=\s*[^=]"),
    ("postMessage", r"\.postMessage\s*\("),
    ("jQuery .html()", r"\.html\s*\("),
    ("jQuery .append()", r"\.append\s*\("),
    ("srcdoc", r"\.srcdoc\s*="),
]

def detect_dom_sinks(content, per_sink_cap=5):
    """Flag potentially dangerous DOM XSS sinks (additive security intel)."""
    found = []
    for name, pat in _DOM_SINKS:
        count = 0
        for m in re.finditer(pat, content):
            found.append({"sink": name, "context": _context_snippet(content, m.start(), m.end())})
            count += 1
            if count >= per_sink_cap:
                break
    return found

def extract_hosts(content):
    """Collect referenced hostnames/domains from absolute URLs (recon pivot)."""
    hosts = set()
    for m in re.finditer(r"https?://([a-zA-Z0-9][a-zA-Z0-9.\-]{1,250}\.[a-zA-Z]{2,24})", content):
        host = m.group(1).lower().rstrip('.')
        if '.' in host and not host.endswith(_STATIC_ASSET_EXT):
            hosts.add(host)
    return sorted(hosts)

# NOTE: variable-length classes are bounded (DNS labels/hosts are <=253 chars)
# to keep matching linear and avoid ReDoS on large minified single-line bundles.
_BUCKET_PATTERNS = [
    ("AWS S3", r"[a-z0-9.\-]{1,63}\.s3[.\-][a-z0-9\-]{0,40}\.amazonaws\.com"),
    ("AWS S3 (path)", r"s3://[a-z0-9][a-z0-9.\-]{1,61}[a-z0-9]"),
    ("Google Cloud Storage", r"storage\.googleapis\.com/[a-zA-Z0-9._\-]{1,128}"),
    ("Google Cloud Storage (vhost)", r"[a-z0-9._\-]{1,63}\.storage\.googleapis\.com"),
    ("Azure Blob", r"[a-z0-9]{1,63}\.blob\.core\.windows\.net"),
    ("DigitalOcean Spaces", r"[a-z0-9.\-]{1,63}\.digitaloceanspaces\.com"),
    ("Firebase Storage", r"[a-z0-9.\-]{1,63}\.firebaseio\.com"),
    ("Firebase App", r"[a-z0-9.\-]{1,63}\.firebaseapp\.com"),
]

def extract_cloud_buckets(content):
    """Detect cloud storage buckets referenced in JS (common misconfig target)."""
    found = {}
    for name, pat in _BUCKET_PATTERNS:
        for m in re.finditer(pat, content, re.I):
            found.setdefault(name, set()).add(m.group(0))
    return {k: sorted(v) for k, v in found.items()}

def extract_parameters(content):
    """Extract candidate parameter names (for fuzzing wordlists)."""
    params = set()
    for m in re.finditer(r"[?&]([a-zA-Z_][a-zA-Z0-9_\-]{1,40})=", content):
        params.add(m.group(1))
    return sorted(params)

# ---- Expanded secret engine (keeps the original 3, adds many more) ------

# (name, pattern, severity, value_group)  value_group=0 -> whole match
_SECRET_SIGNATURES = [
    # --- original v2.0 signatures (preserved) ---
    ("AWS Key", r"AKIA[0-9A-Z]{16}", "critical", 0),
    ("Google Key", r"AIza[0-9A-Za-z\-_]{35}", "high", 0),
    ("Generic Token",
     r"(?:api_key|access_token|secret|client_secret|auth_token|token)\s*[:=]\s*['\"`]([a-zA-Z0-9_\-]{10,})['\"`]",
     "medium", 1),
    # --- v3.0 additions ---
    ("JWT", r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}", "high", 0),
    ("Bearer Token", r"[Bb]earer\s+[A-Za-z0-9\-._~+/]{20,}=*", "high", 0),
    ("GitHub Token", r"(?:ghp|gho|ghs|ghu|ghr)_[0-9A-Za-z]{36}", "critical", 0),
    ("GitHub Fine-Grained PAT", r"github_pat_[0-9A-Za-z_]{22,}", "critical", 0),
    ("Stripe Live Secret", r"(?:sk|rk)_live_[0-9A-Za-z]{10,}", "critical", 0),
    ("Stripe Live Publishable", r"pk_live_[0-9A-Za-z]{10,}", "high", 0),
    ("Slack Token", r"xox[baprs]-[0-9A-Za-z\-]{10,}", "critical", 0),
    ("Twilio SID", r"SK[0-9a-fA-F]{32}", "high", 0),
    ("Google OAuth Client Secret", r"GOCSPX-[0-9A-Za-z_\-]{20,}", "critical", 0),
    ("SendGrid Key", r"SG\.[0-9A-Za-z_\-]{20,}\.[0-9A-Za-z_\-]{30,}", "critical", 0),
    ("Mailgun Key", r"key-[0-9a-zA-Z]{32}", "high", 0),
    ("Square Access Token", r"sq0atp-[0-9A-Za-z\-_]{22}", "critical", 0),
    ("Square OAuth Secret", r"sq0csp-[0-9A-Za-z\-_]{43}", "critical", 0),
    ("npm Token", r"npm_[0-9A-Za-z]{36}", "critical", 0),
    ("PEM Private Key",
     r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----",
     "critical", 0),
    # --- v3.0 extended provider signatures (community pattern DBs) ---
    ("GitLab PAT", r"glpat-[0-9A-Za-z_\-]{20}", "critical", 0),
    ("OpenAI Key", r"sk-(?:proj-)?[A-Za-z0-9_\-]{20,}T3BlbkFJ[A-Za-z0-9_\-]{20,}", "critical", 0),
    ("Hugging Face Token", r"hf_[A-Za-z0-9]{34}", "high", 0),
    ("Shopify Token", r"shp(?:at|ca|pa|ss)_[a-fA-F0-9]{32}", "critical", 0),
    ("Discord Bot Token", r"[MNO][A-Za-z\d_\-]{23}\.[A-Za-z\d_\-]{6}\.[A-Za-z\d_\-]{27}", "high", 0),
    ("Discord Webhook", r"https://discord(?:app)?\.com/api/webhooks/[0-9]+/[A-Za-z0-9_\-]+", "high", 0),
    ("Slack Webhook", r"https://hooks\.slack\.com/services/T[A-Za-z0-9_]+/B[A-Za-z0-9_]+/[A-Za-z0-9_]+", "high", 0),
    ("Telegram Bot Token", r"[0-9]{8,10}:[A-Za-z0-9_\-]{35}", "high", 0),
    ("Twilio Account SID", r"AC[0-9a-fA-F]{32}", "high", 0),
    ("Mailchimp Key", r"[0-9a-f]{32}-us[0-9]{1,2}", "high", 0),
    ("Firebase Cloud Messaging Key", r"AAAA[A-Za-z0-9_\-]{7}:[A-Za-z0-9_\-]{140}", "high", 0),
    ("PayPal Braintree Token", r"access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}", "critical", 0),
    ("New Relic Key", r"NRAK-[A-Z0-9]{27}", "high", 0),
    ("Postman API Key", r"PMAK-[a-f0-9]{24}-[a-f0-9]{34}", "high", 0),
    ("Notion Token", r"secret_[A-Za-z0-9]{43}", "high", 0),
    ("Cloudinary URL", r"cloudinary://[0-9]{15}:[A-Za-z0-9_\-]+@[a-zA-Z0-9_\-]+", "high", 0),
    ("Google Service Account", r'"type"\s*:\s*"service_account"', "high", 0),
    ("Basic Auth Credentials in URL", r"[a-zA-Z]{2,10}://[^:@/\s'\"]{1,64}:[^:@/\s'\"]{1,64}@[^\s'\"/]{1,128}", "high", 0),
    ("Authorization Basic Header", r"[Bb]asic\s+[A-Za-z0-9+/]{12,}={0,2}", "medium", 0),
]

def shannon_entropy(data):
    """Shannon entropy (bits per char) of a string."""
    if not data:
        return 0.0
    freq = {}
    for ch in data:
        freq[ch] = freq.get(ch, 0) + 1
    entropy = 0.0
    length = len(data)
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy

def _context_snippet(content, start, end, radius=40):
    lo = max(0, start - radius)
    hi = min(len(content), end + radius)
    snippet = content[lo:hi]
    snippet = re.sub(r'\s+', ' ', snippet).strip()
    if len(snippet) > 140:
        snippet = snippet[:137] + '...'
    return snippet

def scan_secrets_v3(content, entropy=False, entropy_threshold=4.0):
    """Expanded secret scanner. Superset of scan_secrets(): it keeps the 3
    original signatures and adds many provider-specific ones, PEM keys,
    optional Shannon high-entropy detection, and a context snippet + severity
    for every hit. Purely detection — it never sends validation requests."""
    found = []
    seen = set()

    for name, pattern, severity, group in _SECRET_SIGNATURES:
        try:
            regex = re.compile(pattern)
        except re.error:
            continue
        for m in regex.finditer(content):
            try:
                value = m.group(group) if group else m.group(0)
            except (IndexError, re.error):
                value = m.group(0)
            if not value:
                continue
            key = (name, value)
            if key in seen:
                continue
            seen.add(key)
            found.append({
                "type": name,
                "value": value,
                "severity": severity,
                "context": _context_snippet(content, m.start(), m.end()),
            })

    if entropy:
        # Look at quoted string literals and assignment values for
        # high-entropy blobs (likely keys/tokens) not caught by signatures.
        for m in re.finditer(r"""['"`]([A-Za-z0-9_\-+/=]{20,})['"`]""", content):
            candidate = m.group(1)
            if len(candidate) > 200:
                continue
            ent = shannon_entropy(candidate)
            if ent >= entropy_threshold:
                key = ("High Entropy String", candidate)
                if key in seen:
                    continue
                seen.add(key)
                found.append({
                    "type": "High Entropy String",
                    "value": candidate,
                    "severity": "low",
                    "entropy": round(ent, 2),
                    "context": _context_snippet(content, m.start(), m.end()),
                })

    return found

# ---- Corrected, import-ready Postman v2.1 export (additional file) ------

def generate_postman_v21(results, target_domain, out_name=None):
    """Produce a corrected, import-ready Postman v2.1 collection with host as
    a parsed array, detected HTTP methods, a {{baseUrl}} collection variable,
    and query params split out. Written to a NEW file so the original
    generate_postman_collection() output is untouched."""
    split = urlsplit(target_domain)
    scheme = split.scheme or 'https'
    netloc = split.netloc or urlparse(target_domain).netloc or target_domain
    base_url = f"{scheme}://{netloc}"
    host_array = netloc.split('.') if netloc else [target_domain]
    parsed_domain = netloc or target_domain

    # Merge endpoint -> method across all scanned files.
    method_map = {}
    endpoints = set()
    for res in results:
        for ep in res.get('endpoints', []):
            endpoints.add(ep)
        for ep in res.get('endpoints_strict', []):
            endpoints.add(ep)
        for ep, meth in (res.get('methods') or {}).items():
            method_map[ep] = meth

    collection = {
        "info": {
            "name": f"Revelator v{VERSION}: {parsed_domain}",
            "description": "Import-ready collection generated by Revelator v3.0. "
                           "Set the {{baseUrl}} variable to point at your target.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "variable": [
            {"key": "baseUrl", "value": base_url, "type": "string"}
        ],
        "item": []
    }

    for endpoint in sorted(endpoints):
        raw_ep = endpoint if endpoint.startswith('/') else '/' + endpoint
        path_part, _, query_part = raw_ep.partition('?')
        path_array = [p for p in path_part.split('/') if p]
        query_items = []
        for k, v in parse_qsl(query_part, keep_blank_values=True):
            query_items.append({"key": k, "value": v})

        method = method_map.get(endpoint) or method_map.get(path_part) or "GET"

        url_obj = {
            "raw": "{{baseUrl}}" + raw_ep,
            "host": ["{{baseUrl}}"],
            "path": path_array,
        }
        if query_items:
            url_obj["query"] = query_items

        item = {
            "name": f"{method} {path_part}",
            "request": {
                "method": method,
                "header": [],
                "url": url_obj,
            }
        }
        collection["item"].append(item)

    filename = out_name or f"revelator_postman_{parsed_domain}_v2.1.json"
    with open(filename, "w") as f:
        json.dump(collection, f, indent=4)
    log_info(Colors.GREEN + f" [+] Postman v2.1 (import-ready) Generated: {filename}" + Colors.ENDC)
    # Also expose the parsed host array for reference without altering the host var.
    log_verbose(f"Parsed host array: {host_array}")
    return filename

# ---- Machine-readable JSON output ---------------------------------------

def generate_json_output(results, target_domain, meta, out_name=None):
    parsed_domain = urlparse(target_domain).netloc or target_domain
    payload = {
        "tool": "Revelator",
        "version": VERSION,
        "target": target_domain,
        "generated": _utcnow_iso(),
        "summary": meta,
        "files": [],
    }
    # Aggregate cross-file recon pivots.
    all_hosts, all_buckets = set(), {}
    for res in results:
        for h in res.get("hosts", []):
            all_hosts.add(h)
        for k, v in (res.get("buckets") or {}).items():
            all_buckets.setdefault(k, set()).update(v)
    payload["hosts"] = sorted(all_hosts)
    payload["buckets"] = {k: sorted(v) for k, v in all_buckets.items()}

    for res in results:
        payload["files"].append({
            "url": res.get("url"),
            "endpoints": res.get("endpoints", []),
            "endpoints_strict": res.get("endpoints_strict", []),
            "endpoints_linkfinder": res.get("endpoints_linkfinder", []),
            "methods": res.get("methods", {}),
            "secrets": res.get("secrets", []),
            "secrets_v3": res.get("secrets_v3", []),
            "graphql": res.get("graphql", {}),
            "dom_sinks": res.get("dom_sinks", []),
            "hosts": res.get("hosts", []),
            "buckets": res.get("buckets", {}),
            "parameters": res.get("parameters", []),
        })
    filename = out_name or f"revelator_results_{parsed_domain}.json"
    with open(filename, "w") as f:
        json.dump(payload, f, indent=2)
    log_info(Colors.GREEN + f" [+] JSON Results Generated: {filename}" + Colors.ENDC)
    return filename

# ---- Extra exports: wordlist / discovered-JS list / CSV secrets ---------

def generate_wordlist(results, out_name):
    """Write a fuzzing wordlist of discovered parameter names and path
    segments (xnLinkFinder-style)."""
    words = set()
    for res in results:
        for p in res.get("parameters", []):
            words.add(p)
        for ep in res.get("endpoints", []) + res.get("endpoints_linkfinder", []):
            for seg in re.split(r'[/?=&#.]', ep):
                seg = seg.strip()
                if 2 <= len(seg) <= 40 and re.match(r'^[A-Za-z0-9_\-]+$', seg):
                    words.add(seg)
    with open(out_name, "w") as f:
        f.write("\n".join(sorted(words)) + ("\n" if words else ""))
    log_info(Colors.GREEN + f" [+] Wordlist Generated: {out_name} ({len(words)} words)" + Colors.ENDC)
    return out_name

def save_js_list(content_map, extra_sources, out_name):
    """Persist the de-duplicated list of discovered JS sources."""
    lines = sorted(content_map.keys()) + [n for n, _ in extra_sources]
    with open(out_name, "w") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))
    log_info(Colors.GREEN + f" [+] Discovered JS list saved: {out_name} ({len(lines)} entries)" + Colors.ENDC)
    return out_name

def generate_csv(results, out_name):
    """Write all secret findings to a CSV file."""
    import csv
    rows = 0
    with open(out_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file", "type", "severity", "value", "context"])
        for res in results:
            for s in (res.get("secrets_v3") or res.get("secrets") or []):
                writer.writerow([
                    res.get("url", ""), s.get("type", ""), s.get("severity", ""),
                    s.get("value", ""), s.get("context", ""),
                ])
                rows += 1
    log_info(Colors.GREEN + f" [+] CSV Secrets Export Generated: {out_name} ({rows} rows)" + Colors.ENDC)
    return out_name

# ---- Enriched HTML report (opt-in --rich-html; dark-mode preserved) -----

_SEVERITY_COLORS = {
    "critical": "#ff7b72",
    "high": "#f0883e",
    "medium": "#d29922",
    "low": "#58a6ff",
}

def _html_escape(text):
    return (str(text)
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))

def generate_enriched_report(results, target_domain, meta, out_name=None):
    """Enriched dark-mode HTML report: summary counts, per-secret severity,
    collapsible per-file sections, and client-side search. Written to a NEW
    file so the original generate_report() output is untouched."""
    parsed_domain = urlparse(target_domain).netloc or target_domain
    filename = out_name or f"revelator_report_{parsed_domain}_v3.html"

    total_endpoints = sum(len(r.get('endpoints', [])) for r in results)
    total_strict = sum(len(r.get('endpoints_strict', [])) for r in results)
    all_secrets = [s for r in results for s in r.get('secrets_v3', []) or r.get('secrets', [])]
    total_secrets = len(all_secrets)
    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for s in all_secrets:
        sev_counts[s.get("severity", "medium")] = sev_counts.get(s.get("severity", "medium"), 0) + 1

    def chip(label, value, color):
        return (f'<span class="chip" style="border-color:{color};color:{color}">'
                f'{label}: <b>{value}</b></span>')

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Revelator v{VERSION} Scan: {_html_escape(target_domain)}</title>
<style>
    body {{ background: #0d1117; color: #c9d1d9; font-family: sans-serif; padding: 20px; }}
    .header {{ border-bottom: 1px solid #30363d; padding-bottom: 20px; margin-bottom: 20px; }}
    h1 {{ color: #58a6ff; margin-bottom: 4px; }}
    h3 {{ margin: 6px 0; color: #8b949e; font-weight: normal; }}
    .chips {{ margin: 14px 0; }}
    .chip {{ display:inline-block; border:1px solid #30363d; border-radius: 16px;
             padding: 4px 12px; margin: 4px 6px 4px 0; font-size: 13px; background:#161b22; }}
    #search {{ width: 100%; max-width: 480px; padding: 10px 12px; margin: 10px 0 20px;
               background:#161b22; border:1px solid #30363d; border-radius:6px; color:#c9d1d9;
               font-family: monospace; }}
    .file-block {{ background: #161b22; border: 1px solid #30363d; margin-bottom: 16px;
                   border-radius: 6px; overflow: hidden; }}
    details > summary {{ background: #21262d; padding: 10px; font-weight: bold; color: #f0f6fc;
                         border-bottom: 1px solid #30363d; cursor: pointer; list-style: none; }}
    details > summary::-webkit-details-marker {{ display:none; }}
    details > summary::before {{ content: "\\25B6  "; color:#8b949e; }}
    details[open] > summary::before {{ content: "\\25BC  "; }}
    .item {{ padding: 6px 15px; border-bottom: 1px solid #21262d; font-family: monospace;
             font-size: 13px; word-break: break-all; }}
    .secret {{ color: #ff7b72; font-weight: bold; }}
    .endpoint {{ color: #7ee787; }}
    .method {{ display:inline-block; min-width:52px; color:#0d1117; background:#7ee787;
               border-radius:4px; padding:0 6px; margin-right:8px; font-weight:bold; text-align:center; }}
    .sev {{ display:inline-block; border-radius:4px; padding:0 6px; margin-right:8px;
            font-size:11px; font-weight:bold; text-transform:uppercase; }}
    .context {{ color:#8b949e; font-size: 11px; margin-top: 2px; }}
    footer {{ margin-top: 30px; color:#8b949e; font-size:12px; border-top:1px solid #30363d; padding-top:14px; }}
</style>
</head>
<body>
    <div class="header">
        <h1>&#128065; REVELATOR REPORT <span style="font-size:14px;color:#8b949e;">v{VERSION}</span></h1>
        <h3>Target: {_html_escape(target_domain)}</h3>
        <h3>Generated: {_utcnow_iso()}</h3>
        <div class="chips">
            {chip("Files", len(results), "#58a6ff")}
            {chip("Endpoints", total_endpoints, "#7ee787")}
            {chip("Strict Endpoints", total_strict, "#7ee787")}
            {chip("Secrets", total_secrets, "#ff7b72")}
            {chip("Critical", sev_counts.get("critical",0), _SEVERITY_COLORS["critical"])}
            {chip("High", sev_counts.get("high",0), _SEVERITY_COLORS["high"])}
            {chip("Medium", sev_counts.get("medium",0), _SEVERITY_COLORS["medium"])}
            {chip("Low", sev_counts.get("low",0), _SEVERITY_COLORS["low"])}
        </div>
    </div>
    <input id="search" type="text" placeholder="&#128269; Filter endpoints / secrets / files..." onkeyup="revFilter()">
    <div id="results">
"""

    for res in results:
        secrets = res.get('secrets_v3') or res.get('secrets') or []
        endpoints = res.get('endpoints', [])
        strict = res.get('endpoints_strict', [])
        methods = res.get('methods', {}) or {}
        gql_any = (res.get('graphql') or {})
        if (not endpoints and not strict and not secrets and not res.get('dom_sinks')
                and not gql_any.get('operations') and not gql_any.get('endpoints')
                and not res.get('buckets')):
            continue

        shown_eps = strict if strict else endpoints
        rows = []
        for s in secrets:
            sev = s.get("severity", "medium")
            color = _SEVERITY_COLORS.get(sev, "#d29922")
            ctx = s.get("context", "")
            ctx_html = f'<div class="context">&#8627; {_html_escape(ctx)}</div>' if ctx else ''
            rows.append(
                f'<div class="item secret"><span class="sev" style="background:{color};color:#0d1117">{_html_escape(sev)}</span>'
                f'[SECRET] {_html_escape(s.get("type"))}: {_html_escape(s.get("value"))}{ctx_html}</div>'
            )
        for e in shown_eps:
            path_only = e.split('?')[0]
            method = methods.get(e) or methods.get(path_only) or 'GET'
            rows.append(
                f'<div class="item endpoint"><span class="method">{_html_escape(method)}</span>{_html_escape(e)}</div>'
            )
        gql = res.get('graphql') or {}
        for op in gql.get('operations', []):
            rows.append(
                f'<div class="item" style="color:#d2a8ff"><span class="method" style="background:#d2a8ff">GQL</span>'
                f'{_html_escape(op.get("type"))} {_html_escape(op.get("name"))}</div>'
            )
        for ep in gql.get('endpoints', []):
            rows.append(f'<div class="item" style="color:#d2a8ff">[GRAPHQL] {_html_escape(ep)}</div>')
        for ds in res.get('dom_sinks', []):
            rows.append(
                f'<div class="item" style="color:#ffa657">[DOM SINK] {_html_escape(ds.get("sink"))}'
                f'<div class="context">&#8627; {_html_escape(ds.get("context"))}</div></div>'
            )
        for name, vals in (res.get('buckets') or {}).items():
            for v in vals:
                rows.append(f'<div class="item" style="color:#79c0ff">[BUCKET {_html_escape(name)}] {_html_escape(v)}</div>')

        html += f"""    <div class="file-block">
        <details open>
            <summary>{_html_escape(res['url'])} &nbsp; <span style="color:#8b949e;font-weight:normal;">({len(secrets)} secrets, {len(shown_eps)} endpoints)</span></summary>
            {''.join(rows)}
        </details>
    </div>
"""

    # Aggregate recon pivots (hosts + buckets) across all files (inside #results).
    agg_hosts, agg_buckets = set(), {}
    for res in results:
        for h in res.get('hosts', []):
            agg_hosts.add(h)
        for k, v in (res.get('buckets') or {}).items():
            agg_buckets.setdefault(k, set()).update(v)
    if agg_hosts or agg_buckets:
        html += '    <div class="file-block"><details><summary>Recon Pivots &mdash; Hosts &amp; Buckets</summary>\n'
        for h in sorted(agg_hosts):
            html += f'        <div class="item" style="color:#8b949e">[HOST] {_html_escape(h)}</div>\n'
        for name, vals in agg_buckets.items():
            for v in sorted(vals):
                html += f'        <div class="item" style="color:#79c0ff">[BUCKET {_html_escape(name)}] {_html_escape(v)}</div>\n'
        html += '    </details></div>\n'

    html += """    </div>
    <footer>
        Built with &#128187; and &#10013; by R00t3dbyFa17h / K70n0s510 &mdash; Revelator v""" + VERSION + """.<br>
        For authorized testing and educational use only.
    </footer>
<script>
function revFilter() {
    var q = document.getElementById('search').value.toLowerCase();
    var blocks = document.querySelectorAll('.file-block');
    blocks.forEach(function(block) {
        var items = block.querySelectorAll('.item');
        var anyVisible = false;
        var titleText = block.querySelector('summary') ? block.querySelector('summary').textContent.toLowerCase() : '';
        items.forEach(function(it) {
            var match = it.textContent.toLowerCase().indexOf(q) !== -1;
            it.style.display = (q === '' || match) ? '' : 'none';
            if (match) anyVisible = true;
        });
        var titleMatch = titleText.indexOf(q) !== -1;
        block.style.display = (q === '' || anyVisible || titleMatch) ? '' : 'none';
        if (titleMatch && q !== '') {
            items.forEach(function(it){ it.style.display=''; });
        }
    });
}
</script>
</body>
</html>"""

    with open(filename, "w") as f:
        f.write(html)
    log_info(Colors.GREEN + f" [+] Enriched HTML Report Generated: {filename}" + Colors.ENDC)
    return filename

# ---- Orchestration helpers for the enhanced scan ------------------------

def fetch_wayback_js(session, target, args):
    """Discover historical .js URLs for the target domain from the Wayback
    Machine CDX API (OSINT archive lookup, opt-in via --wayback). This queries
    archive.org only — it never scans the target itself."""
    netloc = urlparse(target).netloc or target
    cdx = (f"https://web.archive.org/cdx/search/cdx?url={netloc}/*"
           f"&output=text&fl=original&collapse=urlkey&limit={args.wayback_limit}")
    log_info(Colors.BLUE + f" [*] Querying Wayback Machine archive for {netloc}..." + Colors.ENDC)
    text = fetch_text(session, cdx, args)
    urls = set()
    if text:
        for line in text.splitlines():
            line = line.strip()
            base = line.split('?')[0]
            if base.endswith('.js') and 'google' not in line and 'facebook' not in line:
                urls.add(line)
    log_verbose(f"Wayback returned {len(urls)} archived .js URL(s)")
    return urls

def _collect_scripts_from_html(html, page_url, deep):
    """Return (js_urls set, inline list, same-host page links set) for one page."""
    js_urls = set()
    inline = []
    page_links = set()
    base_host = urlparse(page_url).netloc
    for link in re.findall(r'<script[^>]+src=["\'](.*?)["\']', html):
        full_url = urljoin(page_url, link)
        if ".js" in full_url and "google" not in full_url and "facebook" not in full_url:
            js_urls.add(full_url)
    if deep:
        inline = extract_inline_scripts(html)
        js_urls |= discover_chunk_urls(html, page_url)
    for href in re.findall(r'<a[^>]+href=["\'](.*?)["\']', html, re.I):
        full = urljoin(page_url, href.split('#')[0])
        if urlparse(full).netloc == base_host and full.startswith(('http://', 'https://')):
            page_links.add(full)
    return js_urls, inline, page_links

def collect_js_sources(session, target, args):
    """Enhanced crawl. Returns:
       content_map : {url: js_text}
       extra_sources : list of (pseudo_name, text)  -> inline scripts + source-map originals
    Falls back gracefully; only runs the deep bits when --deep is set.
    Follows same-host HTML pages up to --crawl-depth, and folds in Wayback
    archive results when --wayback is set."""
    content_map = {}
    extra_sources = []
    max_js = args.max_js

    log_info(Colors.BLUE + f" [*] Crawling {target} for JavaScript files..." + Colors.ENDC)
    html = fetch_text(session, target, args)
    js_urls = set()

    if html:
        found_js, inline, page_links = _collect_scripts_from_html(html, target, args.deep)
        js_urls |= found_js
        if inline:
            log_verbose(f"Found {len(inline)} inline <script> block(s)")
            extra_sources.extend(inline)
        if args.deep and found_js:
            log_verbose(f"Discovered {len(found_js)} script/chunk reference(s) in HTML")

        # Follow same-host HTML pages up to --crawl-depth for more scripts.
        if args.crawl_depth and args.crawl_depth > 0:
            visited_pages = {target}
            frontier = list(page_links)[:args.max_pages]
            depth = 1
            while frontier and depth <= args.crawl_depth and len(visited_pages) < args.max_pages:
                next_frontier = []
                page_batch = _fetch_many(session, [p for p in frontier if p not in visited_pages], args)
                for purl, ptext in page_batch.items():
                    visited_pages.add(purl)
                    if not ptext:
                        continue
                    pjs, pinline, plinks = _collect_scripts_from_html(ptext, purl, args.deep)
                    js_urls |= pjs
                    if pinline:
                        extra_sources.extend(pinline)
                    for pl in plinks:
                        if pl not in visited_pages and len(visited_pages) + len(next_frontier) < args.max_pages:
                            next_frontier.append(pl)
                frontier = next_frontier
                depth += 1
            log_verbose(f"Crawl-depth visited {len(visited_pages)} page(s)")
    else:
        log_warn(f" [!] Could not fetch page body for {target}")

    if args.wayback:
        js_urls |= fetch_wayback_js(session, target, args)

    # BFS fetch of JS (and recursive chunk discovery when --deep).
    queue = list(js_urls)
    visited = set()
    while queue and len(content_map) < max_js:
        batch = []
        while queue and len(batch) < max(1, args.threads):
            u = queue.pop(0)
            if u in visited:
                continue
            visited.add(u)
            batch.append(u)
        if not batch:
            break

        fetched = _fetch_many(session, batch, args)
        for u, text in fetched.items():
            if text is None:
                continue
            content_map[u] = text
            if args.deep:
                # Recursively discover further chunks.
                for new_url in discover_chunk_urls(text, u):
                    if new_url not in visited and len(content_map) + len(queue) < max_js:
                        queue.append(new_url)
                # Source maps -> recover original sources/strings.
                map_url = find_source_map_url(text, u)
                if map_url:
                    log_verbose(f"Fetching source map: {map_url}")
                    map_text = fetch_text(session, map_url, args)
                    if map_text:
                        srcs, contents = parse_source_map(map_text)
                        log_verbose(f"Source map recovered {len(srcs)} sources")
                        for name, body in zip(srcs, contents):
                            if body:
                                extra_sources.append((f"[sourcemap] {name}", body))

    return content_map, extra_sources

def _fetch_many(session, urls, args):
    """Fetch a batch of URLs, concurrently when --threads > 1."""
    results = {}
    if args.threads <= 1:
        for u in urls:
            results[u] = fetch_text(session, u, args)
        return results
    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        future_map = {pool.submit(fetch_text, session, u, args): u for u in urls}
        for fut in as_completed(future_map):
            u = future_map[fut]
            try:
                results[u] = fut.result()
            except Exception as e:
                log_verbose(f"Fetch failed for {u}: {e}")
                results[u] = None
    return results

def analyze_content(name, content, args):
    """Run endpoint + secret + method analysis on one JS blob and return a
    result dict compatible with the original report (keys url/endpoints/
    secrets preserved) plus additive keys."""
    endpoints_default = extract_endpoints(content)
    endpoints_strict = extract_endpoints_strict(content)
    endpoints_linkfinder = extract_endpoints_linkfinder(content)
    secrets_orig = scan_secrets(content)
    secrets_deep = scan_secrets_v3(content, entropy=args.entropy,
                                   entropy_threshold=args.entropy_threshold)
    methods = detect_endpoint_methods(content)
    graphql = detect_graphql(content)
    dom_sinks = detect_dom_sinks(content) if args.dom_sinks else []
    hosts = extract_hosts(content)
    buckets = extract_cloud_buckets(content)
    params = extract_parameters(content)

    # Active endpoints feed the original report; --strict trims them,
    # --linkfinder / --deep fold in the high-recall LinkFinder results.
    active = endpoints_strict if args.strict else endpoints_default
    if args.linkfinder or args.deep:
        merged = list(active)
        seen = set(active)
        for ep in endpoints_linkfinder:
            if ep in seen or _is_static_asset(ep):
                continue
            seen.add(ep)
            merged.append(ep)
        active = merged

    # Optional user-supplied endpoint filter (LinkFinder-style -r).
    if args.match:
        try:
            rx = re.compile(args.match)
            active = [e for e in active if rx.search(e)]
        except re.error as e:
            log_verbose(f"Invalid --match regex ({e}); ignoring filter")

    return {
        "url": name,
        "endpoints": active,
        "endpoints_strict": endpoints_strict,
        "endpoints_default": endpoints_default,
        "endpoints_linkfinder": endpoints_linkfinder,
        "secrets": secrets_orig,
        "secrets_v3": secrets_deep,
        "methods": methods,
        "graphql": graphql,
        "dom_sinks": dom_sinks,
        "hosts": hosts,
        "buckets": buckets,
        "parameters": params,
    }

def needs_enhanced(args):
    """Decide whether any enhanced behavior is requested. When False we take
    the exact v2.0 code path so default runs are byte-for-byte compatible."""
    return any([
        args.list, args.proxy, args.insecure, args.header, args.cookie,
        args.deep, args.strict, args.entropy, args.json, args.rich_html,
        args.postman_v2, args.threads and args.threads > 1,
        args.timeout != 10, args.delay and args.delay > 0,
        args.rate_limit and args.rate_limit > 0, args.output_dir,
        args.retries != 2, args.linkfinder, args.wayback, args.match,
        args.dom_sinks, args.wordlist, args.save_js, args.csv,
        args.crawl_depth and args.crawl_depth > 0, args.user_agent,
    ])

def run_legacy_scan(target, args):
    """The original v2.0 flow, preserved exactly for default invocations."""
    js_files = get_js_links(target)

    if not js_files:
        print(Colors.FAIL + " [!] No JS files found. Try a different domain or check your connection." + Colors.ENDC)
        return False

    print(Colors.BLUE + f" [*] Found {len(js_files)} JS files. Beginning deep scan..." + Colors.ENDC)

    scan_results = []
    global_endpoints = set()

    for js_url in js_files:
        print(f"   -> Scanning {js_url[:60]}...", end='\r')
        content = fetch_js_content(js_url)
        if content:
            endpoints = extract_endpoints(content)
            secrets = scan_secrets(content)
            if endpoints:
                global_endpoints.update(endpoints)
            scan_results.append({
                "url": js_url,
                "endpoints": endpoints,
                "secrets": secrets
            })

    print("\n" + Colors.GREEN + " [!] Scan Complete." + Colors.ENDC)

    generate_report(scan_results, target)

    if args.postman:
        if global_endpoints:
            generate_postman_collection(global_endpoints, target)
        else:
            print(Colors.WARNING + " [-] No endpoints found to generate Postman collection." + Colors.ENDC)
    return True

def run_enhanced_scan(target, args):
    """The v3.0 flow. Produces the original HTML report + Postman (unchanged
    filenames/behavior) plus any requested additive outputs."""
    session = build_session(args)
    content_map, extra_sources = collect_js_sources(session, target, args)

    total_sources = len(content_map) + len(extra_sources)
    if total_sources == 0:
        log_err(" [!] No JS sources found. Try a different domain or check your connection.")
        return False

    log_info(Colors.BLUE + f" [*] Collected {len(content_map)} JS file(s)"
             + (f" + {len(extra_sources)} inline/source-map blob(s)" if extra_sources else "")
             + ". Beginning deep scan..." + Colors.ENDC)

    scan_results = []
    global_endpoints = set()

    # Analyze fetched JS files (concurrently when threads > 1).
    items = list(content_map.items()) + extra_sources
    if args.threads > 1:
        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            futures = {pool.submit(analyze_content, name, content, args): name
                       for name, content in items}
            ordered = {}
            for fut in as_completed(futures):
                name = futures[fut]
                try:
                    ordered[name] = fut.result()
                except Exception as e:
                    log_verbose(f"Analysis failed for {name}: {e}")
            # Preserve input order for stable output.
            for name, _ in items:
                if name in ordered:
                    scan_results.append(ordered[name])
    else:
        for name, content in items:
            log_info(f"   -> Scanning {name[:60]}...")
            scan_results.append(analyze_content(name, content, args))

    for res in scan_results:
        global_endpoints.update(res.get("endpoints", []))

    log_info("\n" + Colors.GREEN + " [!] Scan Complete." + Colors.ENDC)

    # Move into output dir if requested (keeps original relative filenames).
    original_cwd = os.getcwd()
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        os.chdir(args.output_dir)
        log_verbose(f"Writing outputs to {os.path.abspath(args.output_dir)}")

    try:
        # --- Original outputs (preserved) ---
        generate_report(scan_results, target)
        if args.postman:
            if global_endpoints:
                generate_postman_collection(global_endpoints, target)
            else:
                log_warn(" [-] No endpoints found to generate Postman collection.")

        # --- Additive outputs (opt-in) ---
        total_secrets = sum(len(r.get('secrets_v3', []) or r.get('secrets', [])) for r in scan_results)
        meta = {
            "files_scanned": len(scan_results),
            "endpoints": len(global_endpoints),
            "secrets": total_secrets,
        }
        if args.rich_html:
            generate_enriched_report(scan_results, target, meta)
        if args.postman_v2:
            generate_postman_v21(scan_results, target)
        if args.json:
            generate_json_output(scan_results, target, meta)
        if args.wordlist:
            generate_wordlist(scan_results, args.wordlist)
        if args.save_js:
            save_js_list(content_map, extra_sources, args.save_js)
        if args.csv:
            parsed_domain = urlparse(target).netloc or target
            generate_csv(scan_results, args.csv if isinstance(args.csv, str) else f"revelator_secrets_{parsed_domain}.csv")
    finally:
        if args.output_dir:
            os.chdir(original_cwd)

    return True

def load_targets(args):
    """Resolve the list of targets from -d and/or -l."""
    targets = []
    if args.list:
        try:
            with open(args.list, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        targets.append(line)
        except OSError as e:
            log_err(f" [!] Could not read list file '{args.list}': {e}")
    if args.domain:
        targets.append(args.domain)
    # De-duplicate while preserving order.
    seen = set()
    ordered = []
    for t in targets:
        if t not in seen:
            seen.add(t)
            ordered.append(t)
    return ordered

def main():
    parser = argparse.ArgumentParser(
        description=f"Revelator v{VERSION} - The Deep Recon Engine (ADDITIVE upgrade of v2.0)",
        epilog="Run 'python3 revelator.py -d example.com' for the classic scan, "
               "or add --deep --strict --rich-html --json --postman-v2 for the full v3.0 experience.",
    )
    # --- Original v2.0 flags (unchanged) ---
    parser.add_argument("-d", "--domain", help="Target Domain (e.g., tesla.com)")
    parser.add_argument("-p", "--postman", action="store_true",
                        help="Export found endpoints to a Postman JSON collection")

    # --- v3.0 additive flags ---
    parser.add_argument("--version", action="version",
                        version=f"Revelator v{VERSION} (Revelation) - R00t3dbyFa17h / K70n0s510")
    parser.add_argument("-l", "--list", metavar="FILE",
                        help="Read a file of target domains (one per line, # for comments)")
    parser.add_argument("--deep", action="store_true",
                        help="Deeper crawl: inline <script> blocks, webpack/lazy JS chunks, and .map source maps")
    parser.add_argument("--strict", action="store_true",
                        help="Apply the refined endpoint extractor (cuts false positives). Default keeps v2.0 behavior")
    parser.add_argument("--linkfinder", action="store_true",
                        help="Fold in high-recall LinkFinder-style endpoint discovery")
    parser.add_argument("-r", "--match", metavar="REGEX",
                        help="Only report endpoints matching this regex (LinkFinder-style filter)")
    parser.add_argument("--wayback", action="store_true",
                        help="Also discover archived .js URLs via the Wayback Machine (archive.org) and scan them")
    parser.add_argument("--wayback-limit", type=int, default=1000, metavar="N",
                        help="Max archived URLs to pull from Wayback (default: 1000)")
    parser.add_argument("--crawl-depth", type=int, default=0, metavar="N",
                        help="Follow same-host HTML pages to depth N for more JS (default: 0 = root page only)")
    parser.add_argument("--max-pages", type=int, default=50, metavar="N",
                        help="Safety cap on HTML pages visited during --crawl-depth (default: 50)")
    parser.add_argument("--dom-sinks", action="store_true",
                        help="Flag dangerous DOM XSS sinks (innerHTML, eval, document.write, ...)")
    parser.add_argument("--wordlist", metavar="FILE",
                        help="Write a fuzzing wordlist (parameters + path segments) to FILE")
    parser.add_argument("--save-js", metavar="FILE",
                        help="Save the de-duplicated list of discovered JS sources to FILE")
    parser.add_argument("--csv", action="store_true",
                        help="Also export all secret findings to a CSV file")
    parser.add_argument("--user-agent", metavar="UA",
                        help="Override the HTTP User-Agent string")
    parser.add_argument("--entropy", action="store_true",
                        help="Enable Shannon high-entropy string detection for secrets")
    parser.add_argument("--entropy-threshold", type=float, default=4.0, metavar="BITS",
                        help="Entropy threshold (bits/char) for --entropy (default: 4.0)")
    parser.add_argument("--threads", type=int, default=1, metavar="N",
                        help="Concurrent JS fetch/analysis workers (default: 1 = classic sequential)")
    parser.add_argument("--timeout", type=int, default=10, metavar="SECS",
                        help="Per-request timeout in seconds (default: 10)")
    parser.add_argument("--retries", type=int, default=2, metavar="N",
                        help="Retry count with exponential backoff (default: 2)")
    parser.add_argument("--delay", type=float, default=0.0, metavar="SECS",
                        help="Delay between requests in seconds (simple rate limiting)")
    parser.add_argument("--rate-limit", type=float, default=0.0, metavar="RPS",
                        help="Max requests per second (overrides --delay when set)")
    parser.add_argument("--max-js", type=int, default=300, metavar="N",
                        help="Safety cap on number of JS sources fetched (default: 300)")
    parser.add_argument("--proxy", metavar="URL",
                        help="Route traffic through a proxy, e.g. http://127.0.0.1:8080 (Burp)")
    parser.add_argument("--insecure", action="store_true",
                        help="Disable TLS certificate verification (use with --proxy/Burp)")
    parser.add_argument("-H", "--header", action="append", metavar="'Name: Value'",
                        help="Add a custom request header (repeatable) for authenticated scans")
    parser.add_argument("--cookie", metavar="'a=1; b=2'",
                        help="Send a Cookie header for authenticated scans")
    parser.add_argument("--output-dir", metavar="DIR",
                        help="Directory to write all output files into (created if missing)")
    parser.add_argument("--json", action="store_true",
                        help="Also write a machine-readable JSON results file")
    parser.add_argument("--rich-html", action="store_true",
                        help="Also write an enriched HTML report (severity, collapsible, search)")
    parser.add_argument("--postman-v2", action="store_true",
                        help="Also write a corrected, import-ready Postman v2.1 collection (new file)")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="Suppress non-essential output")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output for debugging/visibility")

    args = parser.parse_args()

    _LOG["quiet"] = args.quiet
    _LOG["verbose"] = args.verbose

    if not args.quiet:
        banner()

    if not args.domain and not args.list:
        parser.error("one of the arguments -d/--domain or -l/--list is required")

    targets = load_targets(args)
    if not targets:
        log_err(" [!] No valid targets to scan.")
        sys.exit(1)

    enhanced = needs_enhanced(args)
    multi = len(targets) > 1

    try:
        for raw_target in targets:
            target = raw_target if raw_target.startswith("http") else "https://" + raw_target
            if multi:
                log_info(Colors.HEADER + f"\n============ TARGET: {target} ============" + Colors.ENDC)
            if enhanced:
                run_enhanced_scan(target, args)
            else:
                run_legacy_scan(target, args)
    except KeyboardInterrupt:
        log_err("\n [!] Interrupted by user. Exiting.")
        sys.exit(130)
    except Exception as e:
        log_err(f" [!] Unexpected error: {e}")
        if args.verbose:
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()
