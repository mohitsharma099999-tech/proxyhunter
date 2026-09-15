# 🕵️ ProxyHunter

### ⚡ Terminal-Based Proxy Discovery, Organization & Export Tool

**ProxyHunter** is a lightweight Python command-line tool for fetching, organizing, analyzing, and exporting proxy lists from GitHub-hosted datasets.

It provides a convenient terminal interface for working with **HTTP, HTTPS, SOCKS4, and SOCKS5** proxies while supporting filtering by country, protocol-based organization, statistics, manual proxy entry, file-based loading, and JSON/TXT exports.

> Built for developers, security researchers, network engineers, automation workflows, and authorized security testing.

---

## ✨ Features

* 🌍 Load proxies by country
* 🌐 Load proxies by protocol
* 🔀 Load multiple countries simultaneously
* 📦 Load all available countries
* 🔌 Support for HTTP, HTTPS, SOCKS4 and SOCKS5
* 📊 Proxy statistics and distribution analysis
* 🗂️ Group proxies by country
* 🔗 Group proxies by protocol
* 📄 Import proxies from local files
* ✍️ Manually enter proxy addresses
* 📤 Export proxy data to JSON
* 📤 Export proxy data to TXT
* 🖥️ Interactive terminal mode
* 🎨 Colorized terminal output
* 📋 Display country and protocol lists
* ⚡ Lightweight dependency footprint
* 🔑 No API key required
* 🚫 No GitHub API calls required

The current implementation retrieves proxy-list data from raw GitHub-hosted files rather than using the GitHub API.

---

## 🧠 How It Works

ProxyHunter follows a simple data-processing pipeline:

```text
             ┌──────────────────────┐
             │   GitHub Proxy Data  │
             └──────────┬───────────┘
                        │
                        ▼
             ┌──────────────────────┐
             │    ProxyHunter       │
             │       Loader         │
             └──────────┬───────────┘
                        │
             ┌──────────┴───────────┐
             │                      │
             ▼                      ▼
       Country Filter          Protocol Filter
             │                      │
             └──────────┬───────────┘
                        ▼
             ┌──────────────────────┐
             │ Proxy Organization   │
             │ & Metadata Parsing   │
             └──────────┬───────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
       Display       Statistics    Export
                                    │
                              ┌─────┴─────┐
                              ▼           ▼
                            JSON         TXT
```

The tool maintains metadata such as:

* IP address
* Port
* Protocol
* Country
* Anonymity information
* Original proxy representation

It can then group and display the loaded dataset in different ways.

---

## 🛠️ Tech Stack

| Technology        | Purpose                   |
| ----------------- | ------------------------- |
| 🐍 Python 3.7+    | Core application          |
| `requests`        | HTTP data retrieval       |
| `argparse`        | CLI argument parsing      |
| `json`            | JSON processing/export    |
| `re`              | Data parsing              |
| `collections`     | Proxy grouping/statistics |
| ANSI escape codes | Terminal styling          |

The project currently requires Python 3.7+ and `requests>=2.28.0`; the remaining listed modules are from Python's standard library.

---

# 🚀 Installation

## 1. Clone the repository

```bash
git clone https://github.com/mohitsharma099999-tech/proxyhunter.git
cd proxyhunter
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or:

```bash
pip3 install -r requirements.txt
```

## 3. Run ProxyHunter

```bash
python3 proxyhunter.py
```

Running the script without arguments launches the interactive mode.

---

# 🖥️ Interactive Mode

Start:

```bash
python3 proxyhunter.py -i
```

The interactive interface provides options such as:

```text
============================================================
 PROXYHUNTER - Interactive Mode
============================================================

 1. Load by Country
 2. Load by Protocol
 3. Load Multiple Countries
 4. Load All Countries
 5. Load All Protocols
 6. Manual Proxy Entry
 7. Load from File
 8. Show Statistics
 9. Display by Country
10. Display by Protocol
11. Display Simple List
12. Export to JSONhttps://github.com/mohitsharma099999-tech/proxyhunter
13. Export to TXT
14. Clear Loaded Proxies
15. List Countries
16. List Protocols
17. Change Display Mode / Show Limit

 0. Exit
============================================================
```

The interactive implementation currently exposes these 17 operations.

---

# 🌍 Country-Based Proxy Loading

Load proxies from a specific country:

```bash
python3 proxyhunter.py --country US
```

Examples:

```bash
python3 proxyhunter.py --country IN
```

```bash
python3 proxyhunter.py --country GB
```

```bash
python3 proxyhunter.py --country DE
```

### Multiple countries

```bash
python3 proxyhunter.py --countries US,GB,DE,IN
```

You can see the supported country codes with:

```bash
python3 proxyhunter.py --list-countries
```

---

# 🔌 Protocol Filtering

ProxyHunter supports:

```text
HTTP
HTTPS
SOCKS4
SOCKS5
```

List supported protocols:

```bash
python3 proxyhunter.py --list-protocols
```

Load SOCKS5 proxies:

```bash
python3 proxyhunter.py --protocol socks5
```

Load SOCKS4:

```bash
python3 proxyhunter.py --protocol socks4
```

Load HTTP:

```bash
python3 proxyhunter.py --protocol http
```

Load HTTPS:

```bash
python3 proxyhunter.py --protocol https
```

These are the four protocol types defined by the current implementation.

---

# 📊 Proxy Statistics

Display statistics:

```bash
python3 proxyhunter.py --country US --stats
```

Statistics include:

* Total proxies
* Unique countries
* Unique IP addresses
* Protocol distribution
* Anonymity distribution
* Top countries

Example:

```text
============================================================
PROXY STATISTICS
============================================================

Total Proxies: 1250
Unique Countries: 42
Unique IPs: 1198

Protocol Distribution:

HTTP        620  (49.6%)
HTTPS       280  (22.4%)
SOCKS4      190  (15.2%)
SOCKS5      160  (12.8%)

Anonymity Distribution:

elite         700
anonymous     350
transparent   200
```

The statistics engine calculates protocol, country, anonymity, and unique-IP distributions.

---

# 📋 Display Modes

## Group by Country

```bash
python3 proxyhunter.py --country US --by-country
```

## Group by Protocol

```bash
python3 proxyhunter.py --protocol socks5 --by-protocol
```

## Simple List

```bash
python3 proxyhunter.py --country US --list
```

## Limit displayed proxies

```bash
python3 proxyhunter.py --country US --by-country --show-limit 20
```

The default display limit is **10 proxies per group**.

---

# 📤 Export Proxy Data

## Export to JSON

```bash
python3 proxyhunter.py \
    --country US \
    --export-json us_proxies.json
```

The resulting JSON contains enriched proxy information.

Example structure:

```json
[
  {
    "ip": "192.0.2.10",
    "port": 8080,
    "protocol": "http",
    "country": "US",
    "anonymity": "elite",
    "original": "192.0.2.10:8080"
  }
]
```

---

## Export to TXT

```bash
python3 proxyhunter.py \
    --country US \
    --export-txt us_proxies.txt
```

### Group by country

```bash
python3 proxyhunter.py \
    --countries US,GB,DE \
    --export-txt proxies.txt \
    --group-export country
```

### Group by protocol

```bash
python3 proxyhunter.py \
    --countries US,GB,DE \
    --export-txt proxies.txt \
    --group-export protocol
```

Supported export grouping:

```text
country
protocol
none
```

TXT and JSON export functionality is implemented directly in `proxyhunter.py`.

---

# 📁 Load Proxies From a File

ProxyHunter can also process a local proxy file.

```bash
python3 proxyhunter.py --file proxies.txt
```

Example `proxies.txt`:

```text
192.168.1.10:8080
192.168.1.20:3128
10.10.10.5:1080
```

You can then display, analyze, or export the loaded data.

---

# ✍️ Manual Proxy Entry

Start manual entry mode:

```bash
python3 proxyhunter.py --manual
```

This is useful when you already have a small collection of proxy endpoints and want to analyze or export them without downloading another dataset.

---

# 🌐 Load Everything

### All protocols

```bash
python3 proxyhunter.py --all-protocols
```

### All countries

```bash
python3 proxyhunter.py --all-countries
```

> ⚠️ Loading all countries can generate many network requests and may take significantly longer than loading a single country.

The application itself labels the all-country operation as potentially slow.

---

# ⚙️ CLI Reference

| Argument              | Description                  |
| --------------------- | ---------------------------- |
| `-i`, `--interactive` | Launch interactive mode      |
| `--country CODE`      | Load proxies for one country |
| `--countries CODES`   | Load multiple countries      |
| `--protocol PROTOCOL` | Load a specific protocol     |
| `--all-countries`     | Load all countries           |
| `--all-protocols`     | Load all protocols           |
| `--manual`            | Manual proxy input           |
| `--file FILE`         | Load proxies from a file     |
| `--by-country`        | Group output by country      |
| `--by-protocol`       | Group output by protocol     |
| `--list`              | Display a simple proxy list  |
| `--stats`             | Display statistics           |
| `--export-json FILE`  | Export to JSON               |
| `--export-txt FILE`   | Export to TXT                |
| `--group-export TYPE` | Group TXT output             |
| `--show-limit N`      | Number shown per group       |
| `--list-countries`    | Display country codes        |
| `--list-protocols`    | Display supported protocols  |

These options correspond to the current `argparse` interface in the project.

---

# 🔥 Usage Examples

### Find US proxies

```bash
python3 proxyhunter.py --country US
```

### Find Indian proxies

```bash
python3 proxyhunter.py --country IN
```

### Find SOCKS5 proxies

```bash
python3 proxyhunter.py --protocol socks5
```

### Analyze US proxies

```bash
python3 proxyhunter.py --country US --stats
```

### Export US proxies

```bash
python3 proxyhunter.py \
    --country US \
    --export-json us.json
```

### Export SOCKS5 proxies

```bash
python3 proxyhunter.py \
    --protocol socks5 \
    --export-txt socks5.txt
```

### Multiple countries

```bash
python3 proxyhunter.py \
    --countries US,IN,GB,DE \
    --by-country
```

### Interactive workflow

```bash
python3 proxyhunter.py -i
```

---

# 🏗️ Project Structure

```text
proxyhunter/
│
├── proxyhunter.py       # Main CLI application
├── requirements.txt     # Python dependencies
└── README.md            # Documentation
```

The current repository contains the main Python implementation and `requirements.txt`.

---

# 🔐 Security & Privacy Considerations

Proxy lists obtained from public sources should **not automatically be considered trusted**.

Public proxies may:

* Log traffic
* Modify HTTP requests
* Inject content
* Monitor connections
* Become unavailable without warning
* Be operated by unknown parties
* Expose credentials if used incorrectly

### Recommended practice

Do **not** send:

```text
Passwords
API keys
Authentication cookies
Private tokens
Sensitive personal information
```

through an untrusted proxy.

For security research, use infrastructure that you own or have explicit authorization to test.

---

# ⚠️ Legal & Ethical Use

ProxyHunter is intended for:

* Educational purposes
* Network research
* Development/testing
* Authorized security testing
* Proxy-list analysis
* Automation experiments

You are responsible for ensuring that your use of the software complies with applicable laws, network policies, and terms of service.

**Do not use this project to scan, access, or interfere with systems without authorization.**

---

# 🚧 Limitations

ProxyHunter is primarily a **proxy-list retrieval and organization tool**.

It does not guarantee that every retrieved proxy is:

* Online
* Fast
* Anonymous
* Secure
* Suitable for sensitive traffic

A proxy can become unavailable or change behavior after it has been collected.

For production applications, proxies should be independently validated before use.

---

# 🧪 Recommended Workflow

For security research or development:

```text
1. Select Country / Protocol
            ↓
2. Load Proxy Dataset
            ↓
3. Inspect Statistics
            ↓
4. Filter / Organize
            ↓
5. Validate Proxies
            ↓
6. Export Results
            ↓
7. Use Only Authorized Targets
```

---

# 🚀 Future Improvements

Potential improvements for future versions include:

* [ ] Async proxy validation
* [ ] Proxy health checking
* [ ] Response-time benchmarking
* [ ] Concurrent downloads
* [ ] Proxy deduplication
* [ ] Automatic dead-proxy removal
* [ ] Country filtering improvements
* [ ] ASN/ISP information
* [ ] Proxy anonymity verification
* [ ] JSON/CSV output improvements
* [ ] Configuration file support
* [ ] Rich terminal UI
* [ ] SQLite proxy database
* [ ] Proxy scoring/ranking
* [ ] Scheduled proxy refresh
* [ ] Docker support
* [ ] GitHub Actions automation

---

# 🤝 Contributing

Contributions are welcome.

### Fork the project

```bash
git clone https://github.com/mohitsharma099999-tech/proxyhunter.git
cd proxyhunter
```

Create a branch:

```bash
git checkout -b feature/improvement
```

Make your changes, then:

```bash
git add .
git commit -m "Add improvement"
git push origin feature/improvement
```

Open a Pull Request on GitHub.

---

# 🐛 Issues & Feature Requests

Found a bug or have an idea?

Open an issue in the repository:

[ProxyHunter Issues](https://github.com/mohitsharma099999-tech/proxyhunter/issues?utm_source=chatgpt.com)

Please include:

* Operating system
* Python version
* Command used
* Error message
* Expected behavior
* Actual behavior

---

# 👨‍💻 Author

**Mohit Sharma**

Software Engineer | Cybersecurity | Python | Networking | Open Source

GitHub:

[@mohitsharma099999-tech](https://github.com/mohitsharma099999-tech?utm_source=chatgpt.com)

Repository:

[ProxyHunter](https://github.com/mohitsharma099999-tech/proxyhunter?utm_source=chatgpt.com)

---

# ⭐ Support the Project

If ProxyHunter is useful for your development, networking, or security research:

* ⭐ Star the repository
* 🍴 Fork the project
* 🐛 Report bugs
* 💡 Suggest improvements
* 🔧 Submit pull requests

---

# 📜 License

This project currently does not specify a license in the repository.

If you intend to make the project broadly open source, consider adding an appropriate license such as **MIT** after deciding on the terms under which others may use, modify, and distribute the software.

---

<div align="center">

### 🕵️ ProxyHunter

**Discover • Organize • Analyze • Export**

Built with 🐍 Python

⭐ Star the repository if you find it useful!

</div>
