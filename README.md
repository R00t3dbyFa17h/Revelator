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

2. Install Dependencies

`pip install -r requirements.txt`

(Note: Requires Python 3.x)
🚀 Usage

Revelator v2.0 is designed for speed. You only need one argument: the target domain.
The Auto-Hunter Scan


`python revelator.py -d example.com`

This command will:

  - Craw https://example.com

  - Find all hosted JavaScript files.

  - Scan each file for secrets and endpoints.

  - Generate an HTML report automatically.

Arguments
Argument	Description	Required
`-d, --domain`	The target domain to crawl (e.g., example.com or https://example.com).	✅ Yes
📸 Output
1. The Terminal Output

Revelator provides a clean, color-coded CLI output identifying endpoints and secrets in real-time as it crawls.
2. The HTML Report

A dark-themed dashboard (revelator_report.html) listing all discovered "secrets" and a complete map of the API methods found.
⚠️ Disclaimer

This tool is for educational purposes and authorized testing only. Using this tool against systems you do not have permission to test is illegal. The author (R00t3dbyFa17h) is not responsible for any misuse.

Built with 💻 and ✝️ by R00t3dbyFa17h
