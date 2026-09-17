#!/usr/bin/env python3


import requests
import re
import sys
import json
import os
from collections import defaultdict
import argparse
from typing import Dict, List, Optional, Tuple

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA = '\033[35m'
    WHITE = '\033[37m'

# Base URLs for GitHub raw content
COUNTRY_BASE = "https://raw.githubusercontent.com/mohitsharma099999-tech/free-proxy-list/main/proxies/countries"
PROTOCOL_BASE = "https://raw.githubusercontent.com/mohitsharma099999-tech/free-proxy-list/main/proxies/protocols"

# Available country codes
COUNTRY_CODES = [
    "AE","AF","AL","AM","AO","AR","AT","AU","AZ","BB","BD","BE","BG","BO","BR","BS","BW","BY",
    "CA","CG","CH","CI","CL","CN","CO","CR","CY","CZ","DE","DK","DM","DO","EC","EE","EG","ES",
    "FI","FR","GB","GE","GH","GN","GR","GT","HK","HN","HR","HU","ID","IE","IL","IN","IQ","IR",
    "IT","JM","JP","KE","KG","KH","KR","KZ","LA","LB","LK","LS","LT","LU","LV","LY","MD","ME",
    "MM","MN","MO","MU","MW","MX","MY","NA","NG","NL","NO","NP","NZ","PA","PE","PH","PK","PL",
    "PS","PT","PY","QA","RE","RO","RS","RU","RW","SA","SC","SE","SG","SI","SK","SL","SN","SV",
    "SY","TC","TG","TH","TJ","TR","TT","TW","TZ","UA","UG","US","UY","UZ","VE","VG","VN","WS",
    "XK","YE","YT","ZA","ZM","ZW","ZZ"
]

# Available protocols
PROTOCOLS = ["http", "https", "socks4", "socks5"]

# Country code to name mapping
COUNTRY_NAMES = {
    "AE": "United Arab Emirates", "AF": "Afghanistan", "AL": "Albania", "AM": "Armenia",
    "AR": "Argentina", "AT": "Austria", "AU": "Australia", "AZ": "Azerbaijan",
    "BD": "Bangladesh", "BE": "Belgium", "BG": "Bulgaria", "BR": "Brazil",
    "CA": "Canada", "CH": "Switzerland", "CL": "Chile", "CN": "China",
    "CO": "Colombia", "CZ": "Czech Republic", "DE": "Germany", "DK": "Denmark",
    "EG": "Egypt", "ES": "Spain", "FI": "Finland", "FR": "France",
    "GB": "United Kingdom", "GR": "Greece", "HK": "Hong Kong", "HU": "Hungary",
    "ID": "Indonesia", "IE": "Ireland", "IL": "Israel", "IN": "India",
    "IR": "Iran", "IT": "Italy", "JP": "Japan", "KR": "South Korea",
    "KZ": "Kazakhstan", "MX": "Mexico", "MY": "Malaysia", "NG": "Nigeria",
    "NL": "Netherlands", "NO": "Norway", "NP": "Nepal", "NZ": "New Zealand",
    "PH": "Philippines", "PK": "Pakistan", "PL": "Poland", "PT": "Portugal",
    "RO": "Romania", "RU": "Russia", "SA": "Saudi Arabia", "SE": "Sweden",
    "SG": "Singapore", "TH": "Thailand", "TR": "Turkey", "TW": "Taiwan",
    "UA": "Ukraine", "US": "United States", "VN": "Vietnam", "ZA": "South Africa",
    "ZZ": "Unknown"
}

class ProxyHunter:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.cache = {}
    
    def fetch_json(self, url: str) -> Optional[List[Dict]]:
        """Fetch and parse a JSON file from GitHub with caching"""
        if url in self.cache:
            return self.cache[url]
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            self.cache[url] = data
            return data
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            print(f"{Colors.RED}[-] HTTP error: {e}{Colors.ENDC}")
            return None
        except Exception as e:
            print(f"{Colors.RED}[-] Error fetching: {e}{Colors.ENDC}")
            return None
    
    def parse_manual_proxy(self, proxy_str: str) -> Optional[Dict]:
        """Parse a manually entered proxy string"""
        proxy_str = proxy_str.strip()
        if not proxy_str:
            return None
        
        pattern = r'(socks5|socks4|https?|http)://([0-9.]+):(\d+)'
        match = re.match(pattern, proxy_str)
        
        if match:
            protocol = match.group(1)
            ip = match.group(2)
            port = match.group(3)
        else:
            pattern2 = r'^([0-9.]+):(\d+)$'
            match2 = re.match(pattern2, proxy_str)
            if match2:
                protocol = 'http'
                ip = match2.group(1)
                port = match2.group(2)
            else:
                return None
        
        return {
            'original': f"{protocol}://{ip}:{port}",
            'protocol': protocol,
            'ip': ip,
            'port': port,
            'country': 'MANUAL',
            'city': 'Manual Entry',
            'anonymity': 'unknown',
            'score': 0
        }
    
    def get_manual_proxies(self) -> List[Dict]:
        """Interactive manual proxy entry"""
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}MANUAL PROXY ENTRY{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Enter proxies one per line. Format: protocol://ip:port{Colors.ENDC}")
        print(f"{Colors.YELLOW}Examples:{Colors.ENDC}")
        print(f"  socks5://192.168.1.1:1080")
        print(f"  http://10.0.0.1:8080")
        print(f"  192.168.1.1:3128  (defaults to http)")
        print(f"{Colors.CYAN}Enter empty line to finish, or 'file' to load from file{Colors.ENDC}\n")
        
        proxies = []
        line_num = 0
        
        while True:
            line_num += 1
            try:
                user_input = input(f"{Colors.GREEN}[{line_num}]{Colors.ENDC} ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            
            if not user_input:
                break
            
            if user_input.lower() == 'file':
                filename = input(f"{Colors.CYAN}Enter file path: {Colors.ENDC}").strip()
                file_proxies = self.load_from_file(filename)
                proxies.extend(file_proxies)
                print(f"{Colors.GREEN}[+] Loaded {len(file_proxies)} proxies from file{Colors.ENDC}")
                continue
            
            parsed = self.parse_manual_proxy(user_input)
            if parsed:
                proxies.append(parsed)
                print(f"{Colors.GREEN}  ✓ Added: {parsed['protocol']}://{parsed['ip']}:{parsed['port']}{Colors.ENDC}")
            else:
                print(f"{Colors.RED}  ✗ Invalid format: {user_input}{Colors.ENDC}")
        
        if proxies:
            print(f"\n{Colors.GREEN}[+] Total manual proxies: {len(proxies)}{Colors.ENDC}")
        
        return proxies
    
    def load_from_file(self, filename: str) -> List[Dict]:
        """Load proxies from a text file"""
        proxies = []
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parsed = self.parse_manual_proxy(line)
                        if parsed:
                            proxies.append(parsed)
        except Exception as e:
            print(f"{Colors.RED}[-] Error reading file: {e}{Colors.ENDC}")
        
        return proxies
    
    def load_country(self, country_code: str) -> List[Dict]:
        """Load proxies for a specific country"""
        country_code = country_code.upper()
        url = f"{COUNTRY_BASE}/{country_code}/data.json"
        
        data = self.fetch_json(url)
        if data is None:
            print(f"{Colors.YELLOW}[!] No data found for country: {country_code}{Colors.ENDC}")
            return []
        
        proxies = []
        for item in data:
            geo = item.get('geolocation', {})
            proxies.append({
                'original': item.get('proxy', ''),
                'protocol': item.get('protocol', 'unknown'),
                'ip': item.get('ip', ''),
                'port': str(item.get('port', '')),
                'country': geo.get('country', country_code),
                'city': geo.get('city', 'Unknown'),
                'anonymity': item.get('anonymity', 'unknown'),
                'score': item.get('score', 0)
            })
        
        print(f"{Colors.GREEN}[+] Loaded {len(proxies)} proxies from {country_code} ({COUNTRY_NAMES.get(country_code, country_code)}){Colors.ENDC}")
        return proxies
    
    def load_protocol(self, protocol: str) -> List[Dict]:
        """Load proxies for a specific protocol"""
        protocol = protocol.lower()
        url = f"{PROTOCOL_BASE}/{protocol}/data.json"
        
        data = self.fetch_json(url)
        if data is None:
            print(f"{Colors.YELLOW}[!] No data found for protocol: {protocol}{Colors.ENDC}")
            return []
        
        proxies = []
        for item in data:
            geo = item.get('geolocation', {})
            proxies.append({
                'original': item.get('proxy', ''),
                'protocol': item.get('protocol', protocol),
                'ip': item.get('ip', ''),
                'port': str(item.get('port', '')),
                'country': geo.get('country', 'ZZ'),
                'city': geo.get('city', 'Unknown'),
                'anonymity': item.get('anonymity', 'unknown'),
                'score': item.get('score', 0)
            })
        
        print(f"{Colors.GREEN}[+] Loaded {len(proxies)} proxies for {protocol}{Colors.ENDC}")
        return proxies
    
    def load_multiple_countries(self, country_codes: List[str]) -> List[Dict]:
        """Load multiple countries"""
        all_proxies = []
        total = len(country_codes)
        
        for i, code in enumerate(country_codes, 1):
            code = code.strip().upper()
            if code in COUNTRY_CODES:
                print(f"\r{Colors.CYAN}[*] Loading {i}/{total}: {code}...{Colors.ENDC}", end='')
                proxies = self.load_country(code)
                all_proxies.extend(proxies)
            else:
                print(f"\n{Colors.YELLOW}[!] Skipping unknown country: {code}{Colors.ENDC}")
        
        print()
        print(f"{Colors.GREEN}[+] Total loaded: {len(all_proxies)} proxies from {total} countries{Colors.ENDC}")
        return all_proxies
    
    def load_all_countries(self) -> List[Dict]:
        """Load all countries (slow)"""
        print(f"{Colors.CYAN}[*] Loading all {len(COUNTRY_CODES)} countries...{Colors.ENDC}")
        print(f"{Colors.YELLOW}[!] This will make {len(COUNTRY_CODES)} requests and may take a while{Colors.ENDC}")
        
        return self.load_multiple_countries(COUNTRY_CODES)
    
    def load_all_protocols(self) -> List[Dict]:
        """Load all protocols"""
        print(f"{Colors.CYAN}[*] Loading all protocols...{Colors.ENDC}")
        all_proxies = []
        for protocol in PROTOCOLS:
            all_proxies.extend(self.load_protocol(protocol))
        print(f"{Colors.GREEN}[+] Total loaded: {len(all_proxies)} proxies{Colors.ENDC}")
        return all_proxies
    
    def display_by_country(self, proxies: List[Dict], country_filter: str = None, 
                           show_limit: int = 10):
        """Display proxies grouped by country"""
        country_groups = defaultdict(list)
        
        for proxy in proxies:
            country = proxy['country']
            if country_filter and country_filter.upper() != country.upper():
                continue
            country_groups[country].append(proxy)
        
        if not country_groups:
            print(f"{Colors.YELLOW}[!] No proxies found{Colors.ENDC}")
            return
        
        sorted_countries = sorted(country_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}PROXIES GROUPED BY COUNTRY{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
        
        for country, country_proxies in sorted_countries:
            country_name = COUNTRY_NAMES.get(country, country)
            print(f"{Colors.GREEN}{Colors.BOLD}📍 {country} - {country_name} ({len(country_proxies)} proxies){Colors.ENDC}")
            print(f"{Colors.CYAN}{'-'*60}{Colors.ENDC}")
            
            protocol_groups = defaultdict(list)
            for p in country_proxies:
                protocol_groups[p['protocol']].append(p)
            
            for protocol, prot_proxies in sorted(protocol_groups.items()):
                print(f"  {Colors.YELLOW}▸ {protocol.upper()}: {len(prot_proxies)}{Colors.ENDC}")
                for p in prot_proxies[:show_limit]:
                    anon_color = Colors.GREEN if p['anonymity'] == 'elite' else Colors.YELLOW
                    print(f"    • {p['ip']}:{p['port']}  {anon_color}[{p['anonymity']}]{Colors.ENDC}")
                
                if len(prot_proxies) > show_limit:
                    print(f"    {Colors.MAGENTA}... and {len(prot_proxies) - show_limit} more{Colors.ENDC}")
            
            print()
    
    def display_by_protocol(self, proxies: List[Dict], protocol_filter: str = None,
                            show_limit: int = 5):
        """Display proxies grouped by protocol"""
        protocol_groups = defaultdict(list)
        
        for proxy in proxies:
            protocol = proxy['protocol']
            if protocol_filter and protocol_filter.lower() != protocol.lower():
                continue
            protocol_groups[protocol].append(proxy)
        
        if not protocol_groups:
            print(f"{Colors.YELLOW}[!] No proxies found{Colors.ENDC}")
            return
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}PROXIES GROUPED BY PROTOCOL{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
        
        for protocol, prot_proxies in sorted(protocol_groups.items()):
            print(f"{Colors.GREEN}{Colors.BOLD}🔌 {protocol.upper()} ({len(prot_proxies)} proxies){Colors.ENDC}")
            print(f"{Colors.CYAN}{'-'*60}{Colors.ENDC}")
            
            country_groups = defaultdict(list)
            for p in prot_proxies:
                country_groups[p['country']].append(p)
            
            for country, country_proxies in sorted(country_groups.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
                country_name = COUNTRY_NAMES.get(country, country)
                print(f"  {Colors.YELLOW}▸ {country} - {country_name}: {len(country_proxies)}{Colors.ENDC}")
                for p in country_proxies[:show_limit]:
                    anon_color = Colors.GREEN if p['anonymity'] == 'elite' else Colors.YELLOW
                    print(f"    • {p['ip']}:{p['port']}  {anon_color}[{p['anonymity']}]{Colors.ENDC}")
                
                if len(country_proxies) > show_limit:
                    print(f"    {Colors.MAGENTA}... and {len(country_proxies) - show_limit} more{Colors.ENDC}")
            
            print()
    
    def display_simple_list(self, proxies: List[Dict], show_limit: int = 50):
        """Display simple list of proxies"""
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}PROXY LIST ({len(proxies)} total){Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
        
        for i, p in enumerate(proxies[:show_limit], 1):
            country_name = COUNTRY_NAMES.get(p['country'], p['country'])
            print(f"  {i:>4}. {p['original']:<45} {Colors.CYAN}[{p['country']}]{Colors.ENDC} {p['anonymity']}")
        
        if len(proxies) > show_limit:
            print(f"\n  {Colors.MAGENTA}... and {len(proxies) - show_limit} more proxies{Colors.ENDC}")
        print()
    
    def export_to_json(self, proxies: List[Dict], filename: str = "proxies.json"):
        """Export enriched proxy list to JSON"""
        try:
            with open(filename, 'w') as f:
                json.dump(proxies, f, indent=2)
            print(f"{Colors.GREEN}[+] Exported {len(proxies)} proxies to {filename}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}[-] Error exporting to JSON: {e}{Colors.ENDC}")
    
    def export_to_txt(self, proxies: List[Dict], filename: str = "proxies.txt", 
                      group_by: str = "none"):
        """Export enriched proxy list to text file"""
        try:
            with open(filename, 'w') as f:
                if group_by == "country":
                    groups = defaultdict(list)
                    for p in proxies:
                        groups[p['country']].append(p)
                    
                    for group, group_proxies in sorted(groups.items()):
                        country_name = COUNTRY_NAMES.get(group, group)
                        f.write(f"# {group} - {country_name} ({len(group_proxies)} proxies)\n")
                        for p in group_proxies:
                            f.write(f"{p['original']}\n")
                        f.write("\n")
                
                elif group_by == "protocol":
                    groups = defaultdict(list)
                    for p in proxies:
                        groups[p['protocol']].append(p)
                    
                    for group, group_proxies in sorted(groups.items()):
                        f.write(f"# {group} ({len(group_proxies)} proxies)\n")
                        for p in group_proxies:
                            f.write(f"{p['original']}\n")
                        f.write("\n")
                
                else:
                    for p in proxies:
                        f.write(f"{p['original']}\n")
            
            print(f"{Colors.GREEN}[+] Exported {len(proxies)} proxies to {filename}{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.RED}[-] Error exporting to TXT: {e}{Colors.ENDC}")
    
    def show_statistics(self, proxies: List[Dict]):
        """Show statistics about the proxy list"""
        if not proxies:
            print(f"{Colors.YELLOW}[!] No proxies to analyze{Colors.ENDC}")
            return
        
        protocol_counts = defaultdict(int)
        country_counts = defaultdict(int)
        anonymity_counts = defaultdict(int)
        
        for p in proxies:
            protocol_counts[p['protocol']] += 1
            country_counts[p['country']] += 1
            anonymity_counts[p['anonymity']] += 1
        
        print(f"\n{Colors.HEADER}{'='*80}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}PROXY STATISTICS{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*80}{Colors.ENDC}\n")
        
        print(f"{Colors.GREEN}Total Proxies: {len(proxies)}{Colors.ENDC}")
        print(f"{Colors.GREEN}Unique Countries: {len(country_counts)}{Colors.ENDC}")
        print(f"{Colors.GREEN}Unique IPs: {len(set(p['ip'] for p in proxies))}{Colors.ENDC}\n")
        
        print(f"{Colors.YELLOW}Protocol Distribution:{Colors.ENDC}")
        for protocol, count in sorted(protocol_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(proxies)) * 100
            bar = '█' * int(percentage / 2)
            print(f"  {protocol.upper():<10} {count:>6} ({percentage:>5.1f}%) {Colors.CYAN}{bar}{Colors.ENDC}")
        
        print(f"\n{Colors.YELLOW}Anonymity Distribution:{Colors.ENDC}")
        for anon, count in sorted(anonymity_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(proxies)) * 100
            bar = '█' * int(percentage / 2)
            color = Colors.GREEN if anon == 'elite' else Colors.YELLOW
            print(f"  {anon:<15} {count:>6} ({percentage:>5.1f}%) {color}{bar}{Colors.ENDC}")
        
        print(f"\n{Colors.YELLOW}Top 15 Countries:{Colors.ENDC}")
        for country, count in sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
            percentage = (count / len(proxies)) * 100
            bar = '█' * int(percentage / 2)
            country_name = COUNTRY_NAMES.get(country, country)
            print(f"  {country:<5} {country_name:<20} {count:>6} ({percentage:>5.1f}%) {Colors.GREEN}{bar}{Colors.ENDC}")
        
        print()
    
    def list_countries(self):
        """List all available country codes"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}Available Country Codes:{Colors.ENDC}\n")
        cols = 8
        for i in range(0, len(COUNTRY_CODES), cols):
            row = COUNTRY_CODES[i:i+cols]
            line = "  "
            for c in row:
                name = COUNTRY_NAMES.get(c, "")
                line += f"{Colors.GREEN}{c}{Colors.ENDC} ({name[:12]:<12}) "
            print(line)
        print()
    
    def list_protocols(self):
        """List all available protocols"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}Available Protocols:{Colors.ENDC}\n")
        for p in PROTOCOLS:
            print(f"  {Colors.GREEN}•{Colors.ENDC} {p}")
        print()

def interactive_mode():
    """Interactive menu-driven mode"""
    hunter = ProxyHunter()
    proxies = []
    
    # Display settings
    show_limit = 10
    display_mode = "by_country"  # options: by_country, by_protocol, list, stats, none
    
    def auto_display():
        """Automatically display loaded proxies based on current display mode"""
        if not proxies:
            return
        print(f"\n{Colors.CYAN}[*] Auto-displaying {len(proxies)} proxies in '{display_mode}' mode...{Colors.ENDC}")
        if display_mode == "by_country":
            hunter.display_by_country(proxies, None, show_limit)
        elif display_mode == "by_protocol":
            hunter.display_by_protocol(proxies, None, show_limit)
        elif display_mode == "list":
            hunter.display_simple_list(proxies, show_limit * 5)
        elif display_mode == "stats":
            hunter.show_statistics(proxies)
        # "none" = do nothing
    
    while True:
        print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}  PROXYHUNTER - Interactive Mode{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        print(f"  {Colors.GREEN}1.{Colors.ENDC} Load by Country")
        print(f"  {Colors.GREEN}2.{Colors.ENDC} Load by Protocol")
        print(f"  {Colors.GREEN}3.{Colors.ENDC} Load Multiple Countries")
        print(f"  {Colors.GREEN}4.{Colors.ENDC} Load All Countries {Colors.YELLOW}(slow){Colors.ENDC}")
        print(f"  {Colors.GREEN}5.{Colors.ENDC} Load All Protocols")
        print(f"  {Colors.GREEN}6.{Colors.ENDC} Manual Proxy Entry")
        print(f"  {Colors.GREEN}7.{Colors.ENDC} Load from File")
        print(f"  {Colors.GREEN}8.{Colors.ENDC} Show Statistics")
        print(f"  {Colors.GREEN}9.{Colors.ENDC} Display by Country")
        print(f"  {Colors.GREEN}10.{Colors.ENDC} Display by Protocol")
        print(f"  {Colors.GREEN}11.{Colors.ENDC} Display Simple List")
        print(f"  {Colors.GREEN}12.{Colors.ENDC} Export to JSON")
        print(f"  {Colors.GREEN}13.{Colors.ENDC} Export to TXT")
        print(f"  {Colors.GREEN}14.{Colors.ENDC} Clear Loaded Proxies")
        print(f"  {Colors.GREEN}15.{Colors.ENDC} List Countries")
        print(f"  {Colors.GREEN}16.{Colors.ENDC} List Protocols")
        print(f"  {Colors.GREEN}17.{Colors.ENDC} Change Display Mode / Show Limit")
        print(f"  {Colors.RED}0.{Colors.ENDC}  Exit")
        print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
        
        if proxies:
            print(f"  {Colors.CYAN}Currently loaded: {len(proxies)} proxies{Colors.ENDC}")
            print(f"  {Colors.CYAN}Auto-display: {display_mode} (show_limit={show_limit}){Colors.ENDC}")
        else:
            print(f"  {Colors.YELLOW}No proxies loaded yet.{Colors.ENDC}")
        
        try:
            choice = input(f"\n{Colors.BOLD}Enter choice: {Colors.ENDC}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        
        if choice == '0':
            print(f"{Colors.GREEN}Goodbye!{Colors.ENDC}")
            break
        
        elif choice == '1':
            code = input(f"{Colors.CYAN}Enter country code (e.g., US, GB): {Colors.ENDC}").strip().upper()
            if code in COUNTRY_CODES:
                proxies = hunter.load_country(code)
                auto_display()
            else:
                print(f"{Colors.RED}[-] Invalid country code. Use option 15 to list countries.{Colors.ENDC}")
        
        elif choice == '2':
            print(f"{Colors.CYAN}Available protocols: {', '.join(PROTOCOLS)}{Colors.ENDC}")
            proto = input(f"{Colors.CYAN}Enter protocol: {Colors.ENDC}").strip().lower()
            if proto in PROTOCOLS:
                proxies = hunter.load_protocol(proto)
                auto_display()
            else:
                print(f"{Colors.RED}[-] Invalid protocol.{Colors.ENDC}")
        
        elif choice == '3':
            codes_input = input(f"{Colors.CYAN}Enter country codes (comma-separated, e.g., US,GB,DE): {Colors.ENDC}").strip()
            codes = [c.strip().upper() for c in codes_input.split(',') if c.strip()]
            if codes:
                proxies = hunter.load_multiple_countries(codes)
                auto_display()
            else:
                print(f"{Colors.RED}[-] No codes entered.{Colors.ENDC}")
        
        elif choice == '4':
            confirm = input(f"{Colors.YELLOW}This will load all {len(COUNTRY_CODES)} countries. Continue? (y/n): {Colors.ENDC}").strip().lower()
            if confirm == 'y':
                proxies = hunter.load_all_countries()
                auto_display()
        
        elif choice == '5':
            proxies = hunter.load_all_protocols()
            auto_display()
        
        elif choice == '6':
            manual = hunter.get_manual_proxies()
            if manual:
                if proxies:
                    action = input(f"{Colors.CYAN}Replace existing ({len(proxies)})? (y=replace, n=append): {Colors.ENDC}").strip().lower()
                    if action == 'n':
                        proxies.extend(manual)
                        print(f"{Colors.GREEN}[+] Appended. Total: {len(proxies)} proxies{Colors.ENDC}")
                    else:
                        proxies = manual
                        print(f"{Colors.GREEN}[+] Replaced. Total: {len(proxies)} proxies{Colors.ENDC}")
                else:
                    proxies = manual
                auto_display()
        
        elif choice == '7':
            filename = input(f"{Colors.CYAN}Enter file path: {Colors.ENDC}").strip()
            if os.path.exists(filename):
                file_proxies = hunter.load_from_file(filename)
                if file_proxies:
                    if proxies:
                        action = input(f"{Colors.CYAN}Replace existing ({len(proxies)})? (y=replace, n=append): {Colors.ENDC}").strip().lower()
                        if action == 'n':
                            proxies.extend(file_proxies)
                            print(f"{Colors.GREEN}[+] Appended. Total: {len(proxies)} proxies{Colors.ENDC}")
                        else:
                            proxies = file_proxies
                            print(f"{Colors.GREEN}[+] Replaced. Total: {len(proxies)} proxies{Colors.ENDC}")
                    else:
                        proxies = file_proxies
                        print(f"{Colors.GREEN}[+] Loaded {len(file_proxies)} proxies from file{Colors.ENDC}")
                    auto_display()
            else:
                print(f"{Colors.RED}[-] File not found: {filename}{Colors.ENDC}")
        
        elif choice == '8':
            if proxies:
                hunter.show_statistics(proxies)
            else:
                print(f"{Colors.YELLOW}[!] No proxies loaded. Load some first.{Colors.ENDC}")
        
        elif choice == '9':
            if proxies:
                hunter.display_by_country(proxies, None, show_limit)
            else:
                print(f"{Colors.YELLOW}[!] No proxies loaded. Load some first.{Colors.ENDC}")
        
        elif choice == '10':
            if proxies:
                hunter.display_by_protocol(proxies, None, show_limit)
            else:
                print(f"{Colors.YELLOW}[!] No proxies loaded. Load some first.{Colors.ENDC}")
        
        elif choice == '11':
            if proxies:
                hunter.display_simple_list(proxies, show_limit * 5)
            else:
                print(f"{Colors.YELLOW}[!] No proxies loaded. Load some first.{Colors.ENDC}")
        
        elif choice == '12':
            if proxies:
                filename = input(f"{Colors.CYAN}Output filename (default: proxies.json): {Colors.ENDC}").strip() or "proxies.json"
                hunter.export_to_json(proxies, filename)
            else:
                print(f"{Colors.YELLOW}[!] No proxies loaded. Load some first.{Colors.ENDC}")
        
        elif choice == '13':
            if proxies:
                filename = input(f"{Colors.CYAN}Output filename (default: proxies.txt): {Colors.ENDC}").strip() or "proxies.txt"
                print(f"{Colors.CYAN}Group by: 1=country, 2=protocol, 3=none{Colors.ENDC}")
                grp = input(f"{Colors.CYAN}Choice (default: 3): {Colors.ENDC}").strip() or "3"
                group_map = {'1': 'country', '2': 'protocol', '3': 'none'}
                hunter.export_to_txt(proxies, filename, group_map.get(grp, 'none'))
            else:
                print(f"{Colors.YELLOW}[!] No proxies loaded. Load some first.{Colors.ENDC}")
        
        elif choice == '14':
            proxies = []
            print(f"{Colors.GREEN}[+] Cleared loaded proxies{Colors.ENDC}")
        
        elif choice == '15':
            hunter.list_countries()
        
        elif choice == '16':
            hunter.list_protocols()
        
        elif choice == '17':
            print(f"\n{Colors.CYAN}Display modes:{Colors.ENDC}")
            print(f"  1 = by_country  (group by country, then protocol)")
            print(f"  2 = by_protocol (group by protocol, then country)")
            print(f"  3 = list        (flat numbered list)")
            print(f"  4 = stats       (statistics with bars)")
            print(f"  5 = none        (don't auto-display)")
            dm = input(f"{Colors.CYAN}Choice (default: 1): {Colors.ENDC}").strip() or "1"
            mode_map = {'1': 'by_country', '2': 'by_protocol', '3': 'list', '4': 'stats', '5': 'none'}
            display_mode = mode_map.get(dm, 'by_country')
            
            sl = input(f"{Colors.CYAN}Show limit per group (default: 10): {Colors.ENDC}").strip()
            if sl.isdigit():
                show_limit = int(sl)
            print(f"{Colors.GREEN}[+] Display mode: {display_mode}, show_limit={show_limit}{Colors.ENDC}")
        
        else:
            print(f"{Colors.RED}[-] Invalid choice{Colors.ENDC}")

def main():
    parser = argparse.ArgumentParser(
        description='ProxyHunter - Fetch, organize and display proxy lists from GitHub (no API calls)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -i                               # Interactive mode
  %(prog)s --list-countries                 # Show all available country codes
  %(prog)s --list-protocols                 # Show all available protocols
  %(prog)s --country US                     # Load US proxies only
  %(prog)s --country US --by-country        # Display US proxies grouped by country
  %(prog)s --country US --by-protocol       # Display US proxies grouped by protocol
  %(prog)s --protocol socks5                # Load socks5 proxies only
  %(prog)s --protocol socks5 --by-country   # Display socks5 proxies grouped by country
  %(prog)s --all-countries --by-country     # Load ALL countries (slow)
  %(prog)s --all-protocols --by-protocol    # Load all protocols
  %(prog)s --country US --stats             # Show statistics for US proxies
  %(prog)s --country US --export-json us.json
  %(prog)s --country US --export-txt us.txt --group-export protocol
  %(prog)s --manual                         # Manual proxy entry
  %(prog)s --file proxies.txt               # Load from file
        """
    )
    
    parser.add_argument('-i', '--interactive', action='store_true',
                       help='Interactive menu mode')
    parser.add_argument('--country', type=str,
                       help='Country code to load (e.g., US, GB, DE)')
    parser.add_argument('--countries', type=str,
                       help='Multiple country codes (comma-separated, e.g., US,GB,DE)')
    parser.add_argument('--protocol', type=str, choices=PROTOCOLS,
                       help='Protocol to load (http, https, socks4, socks5)')
    parser.add_argument('--all-countries', action='store_true',
                       help='Load all countries (slow - many requests)')
    parser.add_argument('--all-protocols', action='store_true',
                       help='Load all protocols')
    parser.add_argument('--manual', action='store_true',
                       help='Manual proxy entry mode')
    parser.add_argument('--file', type=str, metavar='FILE',
                       help='Load proxies from a text file')
    parser.add_argument('--by-country', action='store_true',
                       help='Display proxies grouped by country')
    parser.add_argument('--by-protocol', action='store_true',
                       help='Display proxies grouped by protocol')
    parser.add_argument('--list', action='store_true',
                       help='Display simple list of proxies')
    parser.add_argument('--stats', action='store_true',
                       help='Show statistics only')
    parser.add_argument('--export-json', type=str, metavar='FILE',
                       help='Export proxy list to JSON file')
    parser.add_argument('--export-txt', type=str, metavar='FILE',
                       help='Export proxy list to text file')
    parser.add_argument('--group-export', type=str, choices=['country', 'protocol', 'none'],
                       default='none', help='Group export by country, protocol, or none')
    parser.add_argument('--show-limit', type=int, default=10,
                       help='Number of proxies to show per group (default: 10)')
    parser.add_argument('--list-countries', action='store_true',
                       help='List all available country codes')
    parser.add_argument('--list-protocols', action='store_true',
                       help='List all available protocols')
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive or len(sys.argv) == 1:
        interactive_mode()
        return
    
    # Handle list commands
    if args.list_countries:
        hunter = ProxyHunter()
        hunter.list_countries()
        return
    
    if args.list_protocols:
        hunter = ProxyHunter()
        hunter.list_protocols()
        return
    
    hunter = ProxyHunter()
    proxies = []
    
    # Load data based on arguments
    if args.manual:
        proxies = hunter.get_manual_proxies()
    
    elif args.file:
        print(f"{Colors.CYAN}[*] Loading from file: {args.file}{Colors.ENDC}")
        proxies = hunter.load_from_file(args.file)
        if proxies:
            print(f"{Colors.GREEN}[+] Loaded {len(proxies)} proxies from file{Colors.ENDC}")
    
    elif args.countries:
        codes = [c.strip().upper() for c in args.countries.split(',') if c.strip()]
        if codes:
            proxies = hunter.load_multiple_countries(codes)
    
    elif args.country:
        proxies = hunter.load_country(args.country)
    
    elif args.protocol:
        proxies = hunter.load_protocol(args.protocol)
    
    elif args.all_countries:
        proxies = hunter.load_all_countries()
    
    elif args.all_protocols:
        proxies = hunter.load_all_protocols()
    
    else:
        print(f"{Colors.YELLOW}[!] No data source specified.{Colors.ENDC}")
        print(f"{Colors.CYAN}[*] Use --country, --protocol, --manual, --file, --all-countries, --all-protocols{Colors.ENDC}")
        print(f"{Colors.CYAN}[*] Or use -i for interactive mode{Colors.ENDC}")
        print(f"{Colors.CYAN}[*] Use --list-countries or --list-protocols to see available options{Colors.ENDC}")
        sys.exit(1)
    
    if not proxies:
        print(f"{Colors.RED}[-] No proxies loaded. Exiting.{Colors.ENDC}")
        sys.exit(1)
    
    # Display or export based on arguments
    if args.stats:
        hunter.show_statistics(proxies)
    
    elif args.export_json:
        hunter.export_to_json(proxies, args.export_json)
    
    elif args.export_txt:
        hunter.export_to_txt(proxies, args.export_txt, args.group_export)
    
    elif args.by_country:
        hunter.display_by_country(proxies, args.country, args.show_limit)
    
    elif args.by_protocol:
        hunter.display_by_protocol(proxies, args.protocol, args.show_limit)
    
    elif args.list:
        hunter.display_simple_list(proxies)
    
    else:
        # Default: show statistics and display
        hunter.show_statistics(proxies)
        if args.country or args.countries:
            hunter.display_by_country(proxies, None, args.show_limit)
        elif args.protocol:
            hunter.display_by_protocol(proxies, args.protocol, args.show_limit)
        else:
            hunter.display_by_country(proxies, None, args.show_limit)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Interrupted by user{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[-] Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
