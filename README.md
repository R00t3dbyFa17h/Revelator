# 👁️ REVELATOR
### The JavaScript Reconnaissance Framework

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux%20|%20Windows-grey?style=for-the-badge)
![Purpose](https://img.shields.io/badge/Purpose-Bug%20Bounty%20|%20Pentesting-red?style=for-the-badge)

> *"He reveals deep and hidden things; he knows what lies in darkness, and light dwells with him."* > — **Daniel 2:22**

---

## 💀 What is Revelator?

**Revelator** is not just a link scraper. It is an advanced reconnaissance framework designed to **resurrect hidden API structures** from the chaos of minified JavaScript. 

Modern Single Page Applications (SPAs) hide their logic in `main.js` files. Revelator parses this logic to:
1.  **Reconstruct** a valid OpenAPI (Swagger) specification.
2.  **Hunt** for hardcoded secrets (API Keys, AWS Tokens).
3.  **Generate** a visual HTML dashboard for client reporting.

---

## ⚡ Features

| Feature | Description |
| :--- | :--- |
| **🔎 API Resurrection** | Scrapes JS files to find `GET`, `POST`, `PUT` requests and rebuilds the API map. |
| **🗝️ Secret Hunter** | Uses regex signatures to find AWS Keys, Google API tokens, and Bearer Auth headers. |
| **📊 Visual Reporting** | Generates a professional, dark-mode HTML report (`revelator_report.html`). |
| **📝 Swagger Export** | Exports findings to `swagger.json` for immediate import into **Postman** or **Burp Suite**. |
| **🧠 Parameter Detection** | intelligently identifies query parameters (e.g., `?id=123`) in code. |

---

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/R00t3dbyFa17h/Revelator.git](https://github.com/R00t3dbyFa17h/Revelator.git)
cd Revelator

2. Install Dependencies
Bash

pip install -r requirements.txt

(Note: Requires Python 3.x)
🚀 Usage
Basic Scan (Output to JSON)
Bash

python revelator.py -u [https://target.com/assets/main.js](https://target.com/assets/main.js) -t [https://api.target.com](https://api.target.com)

Full Recon (HTML Report + JSON)
Bash

python revelator.py -u [https://target.com/assets/main.js](https://target.com/assets/main.js) -t [https://api.target.com](https://api.target.com) --html

Argument	Description	Required
-u, --url	The URL of the JavaScript file to analyze.	✅
-t, --target	The base URL of the API (e.g., https://api.example.com).	✅
-o, --output	Custom name for the JSON output (Default: swagger.json).	❌
--html	Generate a visual HTML report.	❌
📸 Output Examples

1. The Terminal Output:

    Revelator provides a clean, color-coded CLI output identifying endpoints and secrets in real-time.

2. The HTML Report:

    A dark-themed dashboard listing all discovered "secrets" and a complete map of the API methods found.

⚠️ Disclaimer

This tool is for educational purposes and authorized testing only. Using this tool against systems you do not have permission to test is illegal. The author (R00t3dbyFa17h) is not responsible for any misuse.

Built with 💻 and ✝️ by R00t3dbyFa17h