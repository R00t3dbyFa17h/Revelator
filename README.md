# 👁️ REVELATOR
### The JavaScript Reconnaissance Framework

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20MacOS-lightgrey.svg)]()

> *"He reveals deep and hidden things; he knows what lies in darkness, and light dwells with him."*
> — **Daniel 2:22**

---

## 💀 What is Revelator?

**Revelator** is an advanced reconnaissance framework designed to resurrect hidden API structures from the chaos of minified JavaScript.

Unlike standard link scrapers, Revelator **v2.0 (The Auto-Hunter)** automates the entire process. It crawls a target domain, identifies all unique JavaScript bundles, and parses them to:

* 🕷️ **Crawl & Collect:** Automatically finds all `.js` files on a target domain.
* 🗺️ **Map:** Reconstructs hidden API endpoints (GET/POST/PUT) from the code.
* 🗝️ **Hunt:** Detects hardcoded secrets (API Keys, AWS Tokens, Bearer Auth).
* 📊 **Report:** Generates a visual HTML dashboard for client reporting.

---

## ⚡ Features

| Feature | Description |
| :--- | :--- |
| **🤖 Auto-Discovery** | No need to hunt for JS files manually. Give it a domain (`-d`), and it crawls them all. |
| **🔎 API Resurrection** | Scrapes minified code to find endpoints and rebuilds the API map. |
| **🗝️ Secret Hunter** | Uses regex signatures to find AWS Keys, Google API tokens, and Auth headers. |
| **📊 Visual Reporting** | Generates a professional, dark-mode HTML report (`revelator_report.html`). |
| **🧠 Smart Filtering** | Automatically ignores Google Analytics, Facebook trackers, and 3rd party noise. |

---

## 🛠️ Installation

### 1. Clone the Repository

`git clone [https://github.com/R00t3dbyFa17h/Revelator.git](https://github.com/R00t3dbyFa17h/Revelator.git)
cd Revelator`

### 2. Install Dependencies

`pip install -r requirements.txt`

**(Note: Requires Python 3.x)**
## 🚀 Usage

**Revelator v2.0 is designed for speed. You only need one argument: the target domain.**

### The Auto-Hunter Scan


`python revelator.py -d example.com`

**This command will:**

  - Craw https://example.com

  - Find all hosted JavaScript files.

  - Scan each file for secrets and endpoints.

  - Generate an HTML report automatically.

### Arguments

Argument	Description	Required

`-d, --domain`	The target domain to crawl (e.g., example.com or https://example.com).
✅ Yes
📸 Output

**1. The Terminal Output**

Revelator provides a clean, color-coded CLI output identifying endpoints and secrets in real-time as it crawls.

**2. The HTML Report**

A dark-themed dashboard (revelator_report.html) listing all discovered "secrets" and a complete map of the API methods found.

---

# 🔥 REVELATOR v3.0 (REVELATION)

> *"He reveals deep and hidden things; he knows what lies in darkness, and light dwells with him."*
> — **Daniel 2:22**

**v3.0 is a strictly ADDITIVE upgrade.** Everything from v2.0 works exactly as before when run the same way — the `-d`/`-p` flags, the ASCII banner, the HTML report and the Postman export keep their original filenames and behavior. Every new capability below is **opt-in** via a new flag, so your existing workflows never change.

```
python revelator.py -d example.com          # classic scan — identical to v2.0
python revelator.py -d example.com -p        # classic scan + Postman — identical to v2.0
```

## ✨ What's New in v3.0

### 🕸️ 1. Deeper Crawl (`--deep`)
* Parses **inline `<script>...</script>` blocks** in the HTML, not just `src=` files.
* Discovers and recursively fetches **webpack / lazy-loaded JS chunks** (`import()`, chunk maps, hashed `*.chunk.js`).
* Parses **`.map` source maps** (`//# sourceMappingURL=`) to recover original source paths and embedded code/strings.
* De-duplicates every discovered JS source.
* **`--crawl-depth N`** follows same-host HTML pages (up to `--max-pages`, default 50) to find even more scripts.
* **`--wayback`** pulls historical `.js` URLs from the Wayback Machine (archive.org) CDX API (`--wayback-limit`, default 1000) — an OSINT archive lookup, never a scan of your target.

### 🎯 2. Smarter Endpoint Extraction
* The original extractor is **unchanged and still the default** (nothing is lost).
* **`--strict`** applies a refined filter that cuts the usual false positives (regex-looking junk, escaped fragments, image/static paths).
* **`--linkfinder`** folds in a high-recall, LinkFinder-grade regex (full URLs, REST routes, files with common extensions).
* **HTTP method detection** — endpoints are labelled `GET/POST/PUT/DELETE/PATCH` by parsing `fetch()`, `axios`, `XMLHttpRequest`, and `$.ajax` call patterns.
* **`-r, --match REGEX`** filters reported endpoints (e.g. `-r '^/api/'`).

### 🗝️ 3. Expanded Secret Engine
* Keeps the **3 original signatures** (AWS, Google, Generic Token) exactly.
* Adds **20+ new signatures**: JWTs, Bearer tokens, GitHub (`ghp_/gho_/ghs_/github_pat_`), Stripe (`sk_live/pk_live/rk_live`), Slack (`xox[baprs]-` + webhooks), Twilio (`SK…`/`AC…`), Google OAuth (`GOCSPX-`), SendGrid, Mailgun, Square, npm, GitLab, OpenAI, Hugging Face, Shopify, Discord, Telegram, Mailchimp, Firebase, PayPal/Braintree, New Relic, Postman, Notion, Cloudinary, Basic-Auth-in-URL, and **PEM private keys** (`-----BEGIN ... PRIVATE KEY-----`).
* **`--entropy`** enables Shannon high-entropy string detection with a tunable **`--entropy-threshold`** (bits/char, default `4.0`).
* Every hit includes a **severity** (critical/high/medium/low) and a **context snippet**.
* 🚫 **Detection only** — Revelator never sends validation requests to third parties.

### 🧭 Extra Intelligence (additive)
* **`--dom-sinks`** flags dangerous DOM-XSS sinks (`innerHTML`, `eval`, `document.write`, `insertAdjacentHTML`, `dangerouslySetInnerHTML`, …).
* **GraphQL** endpoints and operation names (`query`/`mutation`/`subscription`) are detected automatically.
* Referenced **hosts/subdomains** and **cloud storage buckets** (S3, GCS, Azure Blob, DigitalOcean Spaces, Firebase) are collected as recon pivots.
* **`--wordlist FILE`** writes a fuzzing wordlist (parameter names + path segments).

### ⚡ 4. Performance & Input
* **`--threads N`** — concurrent JS fetching/analysis via `ThreadPoolExecutor` (default `1` = classic sequential).
* **Retries with exponential backoff** (`--retries`, default 2), **`--timeout`** (default 10s).
* Rate limiting via **`--delay SECS`** or **`--rate-limit RPS`**.
* **`-l, --list FILE`** — scan many domains from a file (one per line, `#` for comments).
* **`--proxy URL`** — route through Burp etc. (e.g. `http://127.0.0.1:8080`), with **`--insecure`** to toggle TLS verification.
* **`-H/--header 'Name: Value'`** (repeatable) and **`--cookie 'a=1; b=2'`** for authenticated scans.
* **`--user-agent UA`** to override the User-Agent.
* **`--output-dir DIR`** to collect all output files in one place.
* **`--max-js N`** safety cap on JS sources fetched (default 300).

### 📊 5. Output
* **KEEPS** the original HTML report and Postman JSON (same filenames, same behavior).
* **`--postman-v2`** — a corrected, **import-ready Postman v2.1** collection (detected methods, a `{{baseUrl}}` collection variable, path arrays, query params split out) written to a **new file** so the original is untouched.
* **`--json`** — a machine-readable results file (endpoints, methods, secrets, GraphQL, hosts, buckets, parameters).
* **`--rich-html`** — an enriched dark-mode HTML report (summary counts, per-secret severity, collapsible per-file sections, client-side search) written to a **new file**; the original dark-mode report is never changed.
* **`--csv`** — export all secret findings to CSV.

### 🧰 6. UX / Robustness
* **`--version`**, **`-q/--quiet`**, **`-v/--verbose`**, graceful error handling (Ctrl-C safe), and all the original colored output preserved.

## 🧪 Full-Power Example

```
python revelator.py -d example.com \
    --deep --strict --linkfinder --entropy --dom-sinks \
    --threads 10 --timeout 15 --retries 3 \
    --proxy http://127.0.0.1:8080 --insecure \
    -H 'Authorization: Bearer <token>' --cookie 'session=abc' \
    --json --rich-html --postman-v2 --csv \
    --wordlist params.txt --save-js discovered_js.txt \
    --output-dir ./loot
```

## 📋 v3.0 Arguments

| Flag | Description |
| :--- | :--- |
| `-d, --domain` | Target domain *(unchanged from v2.0)* |
| `-p, --postman` | Original Postman export *(unchanged from v2.0)* |
| `-l, --list FILE` | Scan multiple domains from a file |
| `--deep` | Inline scripts, webpack chunks, source maps |
| `--crawl-depth N` / `--max-pages N` | Follow same-host HTML pages |
| `--wayback` / `--wayback-limit N` | Discover archived `.js` via archive.org |
| `--strict` | Refined endpoint extractor (fewer false positives) |
| `--linkfinder` | High-recall LinkFinder-style extractor |
| `-r, --match REGEX` | Filter reported endpoints |
| `--entropy` / `--entropy-threshold BITS` | Shannon high-entropy secret detection |
| `--dom-sinks` | Flag dangerous DOM-XSS sinks |
| `--threads N` | Concurrent workers (default 1) |
| `--timeout SECS` / `--retries N` | Request timeout / retry count |
| `--delay SECS` / `--rate-limit RPS` | Rate limiting |
| `--proxy URL` / `--insecure` | Proxy routing / TLS verify toggle |
| `-H, --header` / `--cookie` | Custom headers / cookies |
| `--user-agent UA` | Override User-Agent |
| `--max-js N` | Cap on JS sources fetched |
| `--output-dir DIR` | Output directory |
| `--json` / `--rich-html` / `--postman-v2` / `--csv` | Additional output formats |
| `--wordlist FILE` / `--save-js FILE` | Fuzzing wordlist / discovered-JS list |
| `--version` / `-q, --quiet` / `-v, --verbose` | UX flags |

## ⚠️ Disclaimer

**This tool is for educational purposes and authorized testing only. Using this tool against systems you do not have permission to test is illegal.**

 - **The author (R00t3dbyFa17h) is not responsible for any misuse.**

 **Built with 💻 and ✝️ by R00t3dbyFa17h / K70n0s510**

> **K70n0s510** — HackTheBox, Bugcrowd, Microsoft, Intigriti & Google bug bounty handle.

### Rooted by Authority. Faith by Design. STAY R00t3d In Fa17h!!
