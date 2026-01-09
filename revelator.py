import re
import json
import argparse
import requests
import sys
from urllib.parse import urlparse, urljoin
from datetime import datetime

# -------------------------------------------------------------------------
# Tool: Revelator
# Version: 2.0 (The Auto-Hunter)
# Author: R00t3dbyFa17h/NicholasMullenski
# Verse: "Search me, God, and know my heart..." (Psalm 139:23)
# -------------------------------------------------------------------------

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
    ____  _______    ____________    ___  __________  ____ 
   / __ \/ ____/ |  / / ____/ /   /   |/_  __/ __ \/ __ \
  / /_/ / __/  | | / / __/ / /   / /| | / / / / / / /_/ /
 / _, _/ /___  | |/ / /___/ /___/ ___ |/ / / /_/ / _, _/ 
/_/ |_/_____/  |___/_____/_____/_/  |_/_/  \____/_/ |_|  
                                            v2.0 (AUTO-HUNTER)
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
            # Handle relative URLs (e.g., /assets/main.js -> https://site.com/assets/main.js)
            full_url = urljoin(url, link)
            
            # Filter: Must be a .js file, not a tracker, not google analytics
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
    # Floodlight Regex: Grab anything that looks like a path inside quotes
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
    filename = "revelator_report.html"
    
    # Calculate totals
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
            .badge {{ background: #1f6feb; color: #fff; padding: 2px 8px; border-radius: 10px; font-size: 0.8em; }}
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
            continue # Skip empty files to keep report clean
            
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
    print(Colors.GREEN + f" [+] Report Generated: {filename}" + Colors.ENDC)

def main():
    parser = argparse.ArgumentParser()
    # v2.0 ARGUMENT: Just the domain!
    parser.add_argument("-d", "--domain", help="Target Domain (e.g., https://tesla.com)", required=True)
    args = parser.parse_args()
    banner()

    target = args.domain if args.domain.startswith("http") else "https://" + args.domain
    
    # 1. CRAWL
    js_files = get_js_links(target)
    
    if not js_files:
        print(Colors.FAIL + " [!] No JS files found. Try a different domain or check your connection." + Colors.ENDC)
        sys.exit()

    print(Colors.BLUE + f" [*] Found {len(js_files)} JS files. Beginning deep scan..." + Colors.ENDC)
    
    scan_results = []
    
    # 2. SCAN LOOP
    for js_url in js_files:
        print(f"   -> Scanning {js_url[:60]}...", end='\r')
        content = fetch_js_content(js_url)
        if content:
            endpoints = extract_endpoints(content)
            secrets = scan_secrets(content)
            scan_results.append({
                "url": js_url,
                "endpoints": endpoints,
                "secrets": secrets
            })
    
    print("\n" + Colors.GREEN + " [!] Scan Complete." + Colors.ENDC)
    
    # 3. REPORT
    generate_report(scan_results, target)

if __name__ == "__main__":
    main()
