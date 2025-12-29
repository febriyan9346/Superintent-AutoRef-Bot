import requests
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_utils import to_checksum_address
from datetime import datetime, timezone
import time
import random
import os
import pytz
from colorama import Fore, Style, init
from urllib.parse import quote

init(autoreset=True)

def get_wib_time():
    wib = pytz.timezone('Asia/Jakarta')
    return datetime.now(wib).strftime('%H:%M:%S')

def log(message, level="INFO"):
    time_str = get_wib_time()
    
    if level == "INFO":
        color = Fore.CYAN
        symbol = "[INFO]"
    elif level == "SUCCESS":
        color = Fore.GREEN
        symbol = "[SUCCESS]"
    elif level == "ERROR":
        color = Fore.RED
        symbol = "[ERROR]"
    elif level == "WARNING":
        color = Fore.YELLOW
        symbol = "[WARNING]"
    elif level == "CYCLE":
        color = Fore.MAGENTA
        symbol = "[CYCLE]"
    else:
        color = Fore.WHITE
        symbol = "[LOG]"
    
    print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")

def parse_proxy(proxy_string):
    if not proxy_string:
        return None
    
    try:
        proxy_string = proxy_string.strip()
        
        if proxy_string.startswith(('http://', 'https://', 'socks5://')) and '@' in proxy_string:
            try:
                protocol, rest = proxy_string.split('://', 1)
                auth, host = rest.rsplit('@', 1)
                
                if ':' in auth:
                    user, password = auth.split(':', 1)
                    user_encoded = quote(user, safe='')
                    password_encoded = quote(password, safe='')
                    return f"{protocol}://{user_encoded}:{password_encoded}@{host}"
                return proxy_string 
            except:
                return proxy_string

        if '://' not in proxy_string and proxy_string.count(':') >= 3:
            parts = proxy_string.split(':')
            if len(parts) >= 4:
                ip = parts[0]
                port = parts[1]
                user = parts[2]
                password = ":".join(parts[3:])
                
                user_encoded = quote(user, safe='')
                password_encoded = quote(password, safe='')
                return f"http://{user_encoded}:{password_encoded}@{ip}:{port}"

        elif '@' in proxy_string and '://' not in proxy_string:
            try:
                auth, host = proxy_string.rsplit('@', 1)
                if ':' in auth:
                    user, password = auth.split(':', 1)
                    user_encoded = quote(user, safe='')
                    password_encoded = quote(password, safe='')
                    return f"http://{user_encoded}:{password_encoded}@{host}"
            except:
                pass
            return f"http://{proxy_string}"

        elif '://' not in proxy_string and proxy_string.count(':') == 1:
            return f"http://{proxy_string}"
        
        return proxy_string
        
    except Exception as e:
        log(f"Error parsing proxy '{proxy_string}': {str(e)}", "ERROR")
        return None

def get_nonce(session, base_url):
    try:
        url = f"{base_url}/v1/auth/nonce"
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('nonce')
    except Exception as e:
        log(f"Get nonce error: {str(e)}", "ERROR")
        return None

def sign_message(account, address, nonce):
    try:
        issued_at = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        message = (
            f"mission.superintent.ai wants you to sign in with your Ethereum account:\n"
            f"{address}\n\n"
            f"To securely sign in, please sign this message to verify you're the owner of this wallet.\n\n"
            f"URI: https://mission.superintent.ai\n"
            f"Version: 1\n"
            f"Chain ID: 1\n"
            f"Nonce: {nonce}\n"
            f"Issued At: {issued_at}"
        )
        
        message_hash = encode_defunct(text=message)
        signed_message = account.sign_message(message_hash)
        signature = '0x' + signed_message.signature.hex() if not signed_message.signature.hex().startswith('0x') else signed_message.signature.hex()
        
        return message, signature
    except Exception as e:
        log(f"Sign message error: {str(e)}", "ERROR")
        return None, None

def login(private_key, proxy=None):
    try:
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        
        account = Account.from_key(private_key)
        address = to_checksum_address(account.address)
        
        base_url = "https://bff-root.superintent.ai"
        origin = "https://mission.superintent.ai"
        
        session = requests.Session()
        
        if proxy:
            parsed_proxy = parse_proxy(proxy)
            if parsed_proxy:
                session.proxies.update({
                    'http': parsed_proxy,
                    'https': parsed_proxy
                })
            else:
                log("Invalid proxy format, continuing without proxy...", "WARNING")

        session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/json',
            'origin': origin,
            'referer': f'{origin}/',
            'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
        })
        
        nonce = get_nonce(session, base_url)
        if not nonce:
            return False, None, None, None
        
        message, signature = sign_message(account, address, nonce)
        if not message or not signature:
            return False, None, None, None
        
        url = f"{base_url}/v1/auth/siwe"
        payload = {
            "message": message,
            "signature": signature
        }
        
        response = session.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        return True, session, address, private_key
        
    except Exception as e:
        log(f"Login error: {str(e)}", "ERROR")
        return False, None, None, None

def validate_referral(session, referral_code, base_url):
    try:
        url = f"{base_url}/v1/me/referral/validate"
        payload = {"referralCode": referral_code}
        response = session.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('success', False)
    except Exception as e:
        log(f"Validate referral error: {str(e)}", "ERROR")
        return False

def bind_referral(session, referral_code, base_url):
    try:
        url = f"{base_url}/v1/me/referral/bind"
        payload = {"referralCode": referral_code}
        response = session.post(url, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('success', False)
    except Exception as e:
        log(f"Bind referral error: {str(e)}", "ERROR")
        return False

def get_check_in_status(session, base_url):
    try:
        url = f"{base_url}/v1/check-in/status"
        response = session.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get('hasCheckedInToday', False)
    except Exception as e:
        log(f"Check status error: {str(e)}", "ERROR")
        return False

def perform_check_in(session, base_url):
    try:
        url = f"{base_url}/v1/check-in"
        response = session.post(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log(f"Perform check-in error: {str(e)}", "ERROR")
        return None

def get_user_stats(session, base_url):
    try:
        url = f"{base_url}/v1/me/stats"
        response = session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log(f"Get stats error: {str(e)}", "ERROR")
        return None

def generate_random_wallet():
    account = Account.create()
    private_key = account.key.hex()
    address = to_checksum_address(account.address)
    return private_key, address

def read_file(filename):
    try:
        if not os.path.exists(filename):
            return []
        with open(filename, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        log(f"Error reading {filename}: {str(e)}", "ERROR")
        return []

def format_proxy_display(proxy):
    if not proxy:
        return "No Proxy"
    try:
        if '@' in proxy:
            return proxy.split('@')[1]
        if proxy.count(':') >= 3:
            parts = proxy.split(':')
            return f"{parts[0]}:{parts[1]}"
        return proxy
    except:
        return proxy

def auto_referral(referral_code, num_accounts=1, proxies_list=None):
    base_url = "https://bff-root.superintent.ai"
    successful = 0
    failed = 0
    created_accounts = []
    
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
    log(f"Referral Code: {referral_code}", "INFO")
    log(f"Target Referrals: {num_accounts}", "INFO")
    log(f"Proxy Mode: {'Enabled' if proxies_list else 'Disabled'}", "INFO")
    if proxies_list:
        log(f"Total Proxies: {len(proxies_list)}", "INFO")
    
    print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
    
    for i in range(num_accounts):
        log(f"Account #{i+1}/{num_accounts}", "CYCLE")
        print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
        
        proxy = None
        if proxies_list and len(proxies_list) > 0:
            proxy = proxies_list[i % len(proxies_list)]
            log(f"Proxy: {format_proxy_display(proxy)}", "INFO")
        else:
            log("Proxy: No Proxy", "INFO")
        
        private_key, address = generate_random_wallet()
        log(f"{address[:6]}...{address[-4:]}", "INFO")
        
        time.sleep(random.uniform(1, 3))
        
        log("Processing: Login", "INFO")
        success, session, addr, pk = login(private_key, proxy)
        
        if not success:
            log("Login failed!", "ERROR")
            failed += 1
            continue
        
        log("Login successful!", "SUCCESS")
        time.sleep(random.uniform(1, 2))
        
        log("Processing: Validate referral", "INFO")
        if not validate_referral(session, referral_code, base_url):
            log("Referral validation failed!", "ERROR")
            failed += 1
            continue
        log("Referral validated!", "SUCCESS")
        
        time.sleep(random.uniform(1, 2))
        
        log("Processing: Bind referral", "INFO")
        if not bind_referral(session, referral_code, base_url):
            log("Referral binding failed!", "ERROR")
            failed += 1
            continue
        log("Referral bound successfully!", "SUCCESS")
        
        time.sleep(random.uniform(1, 2))

        log("Processing: Check daily status", "INFO")
        has_checked_in = get_check_in_status(session, base_url)
        
        if not has_checked_in:
            log("Processing: Daily check-in", "INFO")
            check_in_res = perform_check_in(session, base_url)
            
            if check_in_res and check_in_res.get('success'):
                points = check_in_res.get('pointsGranted', 0)
                log(f"Check-in Success! Reward: +{points} Points", "SUCCESS")
            else:
                log("Check-in failed!", "ERROR")
        else:
            log("Already checked in today", "INFO")
            
        time.sleep(random.uniform(1, 2))

        log("Processing: Fetch stats", "INFO")
        stats = get_user_stats(session, base_url)
        if stats:
            total_points = stats.get('totalPoints', 0)
            log(f"Total Points: {total_points}", "SUCCESS")
        else:
            log("Failed to fetch stats", "ERROR")

        successful += 1
        created_accounts.append({
            'address': address,
            'private_key': private_key,
            'proxy': proxy
        })
        
        log(f"Account #{i+1} completed!", "SUCCESS")
        
        if i < num_accounts - 1:
            print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
            time.sleep(random.uniform(5, 10))
    
    print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
    log(f"Process Complete | Success: {successful}/{num_accounts}", "CYCLE")
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
    
    if created_accounts:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log("Saving accounts...", "INFO")
        
        with open('referral_accounts.txt', 'a') as f:
            f.write(f"\nCreated on {timestamp} | Referral: {referral_code}\n")
            for acc in created_accounts:
                f.write(f"{acc['private_key']}\n")
        
        log("Saved to 'referral_accounts.txt'", "SUCCESS")
        
        with open('referral_accounts_details.txt', 'a') as f:
            f.write(f"\n{'='*60}\nCreated: {timestamp}\nReferral: {referral_code}\n{'='*60}\n\n")
            for idx, acc in enumerate(created_accounts, 1):
                f.write(f"Account #{idx}\nAddress: {acc['address']}\nPrivate Key: {acc['private_key']}\n")
                if acc['proxy']:
                    f.write(f"Proxy: {format_proxy_display(acc['proxy'])}\n")
                f.write(f"{'-'*60}\n")
        
        log("Saved details to 'referral_accounts_details.txt'", "SUCCESS")
    
    return successful, failed, created_accounts


def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    
    print(f"{Fore.CYAN}SUPERINTENT.AI AUTO REFERRAL BOT{Style.RESET_ALL}")
    print(f"{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}")
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
    
    referral_code = input(f"Enter your referral code: ").strip()
    
    if not referral_code:
        log("Referral code cannot be empty!", "ERROR")
        return
    
    while True:
        try:
            num_accounts = int(input(f"Enter number of referrals to create: ").strip())
            if num_accounts > 0: 
                break
            else: 
                log("Please enter a positive number!", "ERROR")
        except ValueError:
            log("Please enter a valid number!", "ERROR")
    
    print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Select Mode:{Style.RESET_ALL}")
    print(f"{Fore.GREEN}1. Run with proxy")
    print(f"2. Run without proxy{Style.RESET_ALL}")
    print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
    
    use_proxy = input(f"Enter your choice (1/2): ").strip()
    
    proxies_list = None
    if use_proxy == '1':
        proxies_list = read_file('proxy.txt')
        if not proxies_list:
            log("No proxies in proxy.txt, running without proxy...", "WARNING")
        else:
            log(f"Loaded {len(proxies_list)} proxies", "SUCCESS")
    
    log("Starting process...", "INFO")
    time.sleep(1)
    
    try:
        auto_referral(referral_code, num_accounts, proxies_list)
    except KeyboardInterrupt:
        log("Interrupted by user!", "ERROR")
    except Exception as e:
        log(f"Error: {str(e)}", "ERROR")

if __name__ == "__main__":
    main()
