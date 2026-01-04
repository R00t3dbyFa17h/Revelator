# Revelator
### The JavaScript Reconnaissance Framework
**"He reveals deep and hidden things..." (Daniel 2:22)**

Revelator is an advanced pentesting tool that reconstructs hidden API specifications from minified JavaScript and hunts for hardcoded secrets.

### Features
- **API Map Reconstruction:** Turns messy JS into clean Swagger/OpenAPI documentation.
- **Secret Hunter:** Detects AWS keys, API tokens, and Bearer auth.
- **Pro Reporting:** Generates a full HTML dashboard of findings.

### Usage
```bash
python revelator.py -u <JS_URL> -t <TARGET_URL> --html
```
