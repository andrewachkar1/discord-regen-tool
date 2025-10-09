import requests, time, os, platform, sys, json, ctypes, random
from datetime import datetime, timezone
from keyauth import api
from keyauth import getchecksum
from colorama import Fore
from pystyle import Colorate, Colors, Center

def timestamp():
    return time.strftime("%H:%M:%S", time.localtime())

def load_config():
    with open("config.json", "r", encoding="utf-8") as f:
        return json.load(f)
config = load_config()

TOKEN = config.get("TOKEN")

if platform.system() == "Windows":
    os.system("cls")
else:
    os.system("clear")

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

def ensure_directories():
    paths = [
        "output/Single Link Regenerator/links.txt",
        "output/Single Link Regenerator/full_links.txt",
        "output/Link Fetcher/links.txt",
        "output/Link Fetcher/full_links.txt",
        "output/Generated Links/links.txt",
        "output/Generated Links/full_links.txt",
        "input/proxies.txt"
    ]
    for path in paths:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").close()

def safe_write(file_path, content):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(content)

def normalize_code(line):
    line = line.strip()
    if line.startswith("https://discord.gift/"):
        return line.split("/")[-1]
    elif line.startswith("discord.gift/"):
        return line.split("/")[-1]
    return line

def load_proxies():
    try:
        with open("input/proxies.txt", "r", encoding="utf-8") as f:
            proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        proxies = []
    
    # Be resilient to both keys in config
    proxyless = config.get("proxyless", config.get("PROXYLESS", True))
    if not proxies and not proxyless:
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET}){Fore.YELLOW} No proxies found — switching to proxyless mode...{Fore.RESET}")
    return proxies

proxies_list = load_proxies()

def get_proxy():
    proxyless = config.get("proxyless", config.get("PROXYLESS", True))
    if proxyless or not proxies_list:
        return None
    proxy_str = random.choice(proxies_list)
    return {
        "http": f"http://{proxy_str}",
        "https": f"http://{proxy_str}"
    }

# -------------------------
# Unified 429-aware requester
# -------------------------
def request_with_retry(method, url, headers=None, json=None, proxies=None, max_retries=6, base_backoff=1.0):
    """
    Sends a request and transparently retries on HTTP 429 using server-provided retry_after when available.
    Also retries on transient RequestExceptions with exponential backoff.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            resp = requests.request(method=method, url=url, headers=headers, json=json, proxies=proxies if proxies else None)
        except requests.RequestException as e:
            # Transient network error retry with exponential backoff
            if attempt >= max_retries:
                print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Request failed permanently: {e}{Fore.RESET}")
                raise
            sleep_s = min(30, base_backoff * (2 ** (attempt - 1)))
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET}){Fore.YELLOW} Network issue, retrying in {sleep_s:.1f}s...{Fore.RESET}")
            time.sleep(sleep_s)
            continue

        if resp.status_code == 429:
            # Honor server backoff if provided
            retry_after = 1
            try:
                data = resp.json()
                retry_after = float(data.get('retry_after', retry_after))
            except Exception:
                pass
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET}){Fore.YELLOW} We are being rate-limited! Waiting for {retry_after}s before continuing...{Fore.RESET}")
            if attempt >= max_retries:
                # After last attempt, still return resp so caller can handle
                return resp
            time.sleep(retry_after)
            continue

        return resp

def mass_regen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    infos()
    print("\n")
    url1 = "https://discord.com/api/v9/users/@me/entitlements/gifts"
    proxy = get_proxy()

    resp1 = request_with_retry("GET", url1, headers=HEADERS, proxies=proxy)
    if resp1.status_code != 200:
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Failed to fetch gifts: {resp1.status_code} - {resp1.text}{Fore.RESET}")
        return []
    gifts = resp1.json()
    if not gifts:
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} No gifts found or failed to fetch.{Fore.RESET}")
        time.sleep(3)
        main()

    for gift in gifts:
        time.sleep(1)
        sku = gift.get("sku", {})
        sku_id = sku.get("id")
        name = sku.get("name")
        gift_style = gift.get("gift_style")
        url2 = f"https://discord.com/api/v9/users/@me/entitlements/gift-codes?sku_id={sku_id}"

        resp2 = request_with_retry("GET", url2, headers=HEADERS, proxies=proxy)
        if resp2.status_code != 200:
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Failed to fetch gift codes for SKU {sku_id}: {resp2.status_code} - {resp2.text}{Fore.RESET}")
            return []
        gift_codes = resp2.json()
        if not gift_codes:
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} No gifts found.{Fore.RESET}")
            continue

        for code in gift_codes:
            code_str = code.get("code")
            url3 = f"https://discord.com/api/v9/users/@me/entitlements/gift-codes/{code_str}"

            resp3 = request_with_retry("DELETE", url3, headers=HEADERS, proxies=proxy)
            if resp3.status_code not in (200, 201, 204):
                print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Failed to delete gift code {code_str}: {resp3.status_code} - {resp3.text}{Fore.RESET}")

            url4 = f"https://discord.com/api/v9/users/@me/entitlements/gift-codes"
            payload = {
                "sku_id": str(sku_id),
                "subscription_plan_id": None,
                "gift_style": gift_style
            }
            resp4 = request_with_retry("POST", url4, headers=HEADERS, json=payload, proxies=proxy)
            if resp4.status_code not in (200, 201, 204):
                print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Failed to create new link for gift {code_str}: {resp4.status_code} - {resp4.text}{Fore.RESET}")
                continue

            new_code_json = resp4.json()
            new_code = new_code_json.get("code")
            expires_at = datetime.fromisoformat(new_code_json["expires_at"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            time_left = expires_at - now

            if time_left.total_seconds() > 0:
                days = time_left.days
                hours, remainder = divmod(time_left.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_left = f"{days}d {hours}h {minutes}m {seconds}s"
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.GREEN}+{Fore.RESET}){Fore.GREEN} Regenerated Code: https://discord.gift/{new_code[:5]}*** | Name: {name} | Expires in: {time_left}{Fore.RESET}")
    print(f"\n{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET}){Fore.LIGHTCYAN_EX} All active links have been regenerated!")
    input(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET}){Fore.LIGHTCYAN_EX} Press enter to exit. ")
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    sys.exit()

def handle_rate_limit(response):
    if response.status_code == 429:
        retry_after = response.json().get("retry_after", 2)
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET}){Fore.YELLOW} We are being rate-limited! Waiting for {retry_after:.2f}s...{Fore.RESET}")
        time.sleep(retry_after)
        return True
    return False

def generate_new():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    infos()
    print("\n")
    print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET})"
          f"{Fore.LIGHTCYAN_EX} Checking for ungenerated gifts...{Fore.RESET}")

    url_entitlements = "https://discord.com/api/v9/users/@me/entitlements/gifts"
    proxy = get_proxy()
    resp_entitlements = request_with_retry("GET", url_entitlements, headers=HEADERS, proxies=proxy)
    if resp_entitlements.status_code == 429:
        retry_after = resp_entitlements.json().get("retry_after", 2)
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET}){Fore.YELLOW} We are being rate-limited! Waiting for {retry_after:.2f}s...{Fore.RESET}")
        time.sleep(retry_after)
    if resp_entitlements.status_code != 200:
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET})"
              f"{Fore.RED} Failed to fetch gifts: {resp_entitlements.status_code} - {resp_entitlements.text}{Fore.RESET}")
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Exiting in 5 seconds...{Fore.RESET}")
        time.sleep(5)
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        sys.exit()
    
    all_gifts = resp_entitlements.json()
    if not all_gifts:
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET})"
              f"{Fore.YELLOW} No gift entitlements found.{Fore.RESET}")
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Exiting in 5 seconds...{Fore.RESET}")
        time.sleep(5)
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        sys.exit()

    # Group entitlements by SKU
    entitlements_by_sku = {}
    for gift in all_gifts:
        sku = gift.get("sku", {})
        sku_id = sku.get("id")
        name = sku.get("name")
        gift_style = gift.get("gift_style")
        if not sku_id:
            continue
        if sku_id not in entitlements_by_sku:
            entitlements_by_sku[sku_id] = {
                "count": 0,
                "name": name,
                "gift_style": gift_style
            }
        entitlements_by_sku[sku_id]["count"] += 1

    generatable_gifts = []
    for sku_id, data in entitlements_by_sku.items():
        time.sleep(1.5)
        proxy = get_proxy()
        url_codes = f"https://discord.com/api/v9/users/@me/entitlements/gift-codes?sku_id={sku_id}"
        resp_codes = request_with_retry("GET", url_codes, headers=HEADERS, proxies=proxy)
        if resp_codes.status_code == 429:
            retry_after = resp_codes.json().get("retry_after", 2)
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET}){Fore.YELLOW} We are being rate-limited! Waiting for {retry_after:.2f}s...{Fore.RESET}")
            time.sleep(retry_after)
        if resp_codes.status_code != 200:
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET})"
                  f"{Fore.YELLOW} Could not check codes for {data['name']}, skipping.{Fore.RESET}")
            continue
        
        num_existing = len(resp_codes.json())
        num_available = data['count'] - num_existing

        if num_available > 0:
            for _ in range(num_available):
                generatable_gifts.append({
                    "sku_id": sku_id,
                    "name": data["name"],
                    "gift_style": data["gift_style"]
                })

    if not generatable_gifts:
        print(f"\n{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET})"
              f"{Fore.YELLOW} No new links can be generated. All gifts already have links.{Fore.RESET}")
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Exiting in 5 seconds...{Fore.RESET}")
        time.sleep(5)
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        sys.exit()

    total_available = len(generatable_gifts)
    print(f"\n{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET})"
          f"{Fore.LIGHTCYAN_EX} You have a total of {Fore.YELLOW}{total_available}{Fore.LIGHTCYAN_EX} ungenerated gift(s).{Fore.RESET}")

    while True:
        try:
            amount_to_gen = int(input(
                f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}?{Fore.RESET})"
                f"{Fore.LIGHTCYAN_EX} How many would you like to generate? (Max: {total_available}, 0 to exit) > "))
            if 0 <= amount_to_gen <= total_available:
                break
            else:
                print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET})"
                      f"{Fore.RED} Invalid number. Please enter between 0 and {total_available}.{Fore.RESET}")
        except ValueError:
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET})"
                  f"{Fore.RED} Invalid input. Please enter a number.{Fore.RESET}")

    if amount_to_gen == 0:
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Exiting in 5 seconds...{Fore.RESET}")
        time.sleep(5)
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        sys.exit()

    gifts_to_generate_now = generatable_gifts[:amount_to_gen]
    total_generated_count = 0

    for i, gift_data in enumerate(gifts_to_generate_now):
        payload = {
            "sku_id": str(gift_data['sku_id']),
            "subscription_plan_id": None,
            "gift_style": gift_data['gift_style']
        }
        proxy = get_proxy()
        url_create = "https://discord.com/api/v9/users/@me/entitlements/gift-codes"
        resp_create = request_with_retry("POST", url_create, headers=HEADERS, json=payload, proxies=proxy)
        if resp_create.status_code == 429:
            retry_after = resp_create.json().get("retry_after", 2)
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.YELLOW}!{Fore.RESET}){Fore.YELLOW} We are being rate-limited! Waiting for {retry_after:.2f}s...{Fore.RESET}")
            time.sleep(retry_after)
        if resp_create.status_code in (200, 201, 204):
            new_code_json = resp_create.json()
            new_code = new_code_json.get("code")
            safe_write("output/Generated Links/links.txt", f"https://discord.gift/{new_code}\n")
            safe_write("output/Generated Links/full_links.txt", f"https://discord.gift/{new_code} | Name: {gift_data['name']}\n")
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.GREEN}+{Fore.RESET})"
              f"{Fore.GREEN} Generated link ({i+1}/{amount_to_gen}): https://discord.gift/{new_code[:5]}*** | Name: {gift_data['name']}{Fore.RESET}")
            total_generated_count += 1
        else:
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET})"
                  f"{Fore.RED} Failed to create new link: {resp_create.status_code} - {resp_create.text}{Fore.RESET}")
        time.sleep(8)

    print(f"\n{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.GREEN}+{Fore.RESET})"
          f"{Fore.GREEN} Finished! Successfully generated {total_generated_count}/{amount_to_gen} link(s).{Fore.RESET}")
    input(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET})"
          f"{Fore.LIGHTCYAN_EX} Press enter to exit. ")
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    sys.exit()

def regen(code):
    proxy = get_proxy()
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    infos()
    print("\n")

    url1 = f"https://discord.com/api/v10/entitlements/gift-codes/{code}?with_application=false"
    resp1 = request_with_retry("GET", url1, proxies=proxy)
    if resp1.status_code != 200:
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Failed to fetch gift code information: {resp1.status_code} - {resp1.text}{Fore.RESET}")
        return

    url3 = f"https://discord.com/api/v9/users/@me/entitlements/gift-codes/{code}"
    resp3 = request_with_retry("DELETE", url3, headers=HEADERS, proxies=proxy)
    if resp3.status_code not in (200, 201, 204):
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Failed to delete gift code {code}: {resp3.status_code} - {resp3.text}{Fore.RESET}")

    check = resp1.json()

    url4 = f"https://discord.com/api/v9/users/@me/entitlements/gift-codes"
    payload = {
        "sku_id": str(check.get("sku_id")),
        "subscription_plan_id": None,
        "gift_style": check.get("gift_style")
    }
    resp4 = request_with_retry("POST", url4, headers=HEADERS, json=payload, proxies=proxy)
    if resp4.status_code not in (200, 201, 204):
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Failed to create new link for {code}: {resp4.status_code} - {resp4.text}{Fore.RESET}")
        return

    new_code_json = resp4.json()
    new_code = new_code_json.get("code")
    expires_at = datetime.fromisoformat(new_code_json["expires_at"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    time_left = expires_at - now

    name = check.get("store_listing", {}).get("sku", {}).get("name")

    if time_left.total_seconds() > 0:
        days = time_left.days
        hours, remainder = divmod(time_left.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_left = f"{days}d {hours}h {minutes}m {seconds}s"
    print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.GREEN}+{Fore.RESET}){Fore.GREEN} Regenerated Code: https://discord.gift/{new_code[:5]}*** | Name: {name}{Fore.RESET}")
    safe_write("output/Single Link Regenerator/links.txt", f"https://discord.gift/{new_code}\n")
    safe_write("output/Single Link Regenerator/full_links.txt", f"Code: https://discord.gift/{new_code} | Name: {name}\n")
    print(f"\n{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET}){Fore.LIGHTCYAN_EX} The gift link has been regenerated!")
    enter = input(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET}){Fore.LIGHTCYAN_EX} Press enter to exit. ")
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    sys.exit()

def fetcher():
    proxy = get_proxy()

    # Clear terminal & print banner
    os.system("cls" if platform.system() == "Windows" else "clear")
    infos()
    print("\n")

    # Load existing codes from file (just the actual gift codes)
    existing_codes = set()
    try:
        with open("output/Link Fetcher/links.txt", "r", encoding="utf-8") as f:
            existing_codes = {line.strip().split("/")[-1] for line in f if line.strip()}
    except FileNotFoundError:
        pass

    processed_codes = set()  # track codes processed in *this* run

    url1 = "https://discord.com/api/v9/users/@me/entitlements/gifts"
    resp1 = request_with_retry("GET", url1, headers=HEADERS, proxies=proxy)
    if resp1.status_code != 200:
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET})"
            f"{Fore.RED} Failed to fetch gifts: {resp1.status_code} - {resp1.text}{Fore.RESET}")
        return

    gifts = resp1.json()
    if not gifts:
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET})"
            f"{Fore.RED} No gifts found or failed to fetch.{Fore.RESET}")
        time.sleep(3)
        main()

    for gift in gifts:
        time.sleep(1)
        sku_id = gift.get("sku", {}).get("id")
        name = gift.get("sku", {}).get("name", "Unknown")

        if not sku_id:
            continue

        url2 = f"https://discord.com/api/v9/users/@me/entitlements/gift-codes?sku_id={sku_id}"
        resp2 = request_with_retry("GET", url2, headers=HEADERS, proxies=proxy)
        if resp2.status_code != 200:
            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET})"
                f"{Fore.RED} Failed to fetch gift codes for SKU {sku_id}: {resp2.status_code} - {resp2.text}{Fore.RESET}")
            continue

        gift_codes = resp2.json()
        if not gift_codes:
            continue

        for code_data in gift_codes:
            code_str = code_data.get("code")
            if not code_str:
                continue

            # Skip if code already saved before or already processed this run
            if code_str in existing_codes or code_str in processed_codes:
                continue

            expires_at = datetime.fromisoformat(code_data["expires_at"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            time_left_delta = expires_at - now
            if time_left_delta.total_seconds() > 0:
                days = time_left_delta.days
                hours, remainder = divmod(time_left_delta.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_left = f"{days}d {hours}h {minutes}m {seconds}s"
            else:
                time_left = "Expired"

            short_code_url = f"https://discord.gift/{code_str}"
            full_code_line = f"Code: {short_code_url} | Name: {name} | Expires in: {time_left}"

            # Save to files
            safe_write("output/Link Fetcher/links.txt", short_code_url + "\n")
            safe_write("output/Link Fetcher/full_links.txt", full_code_line + "\n")

            # Add to tracking sets
            existing_codes.add(code_str)
            processed_codes.add(code_str)

            print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.GREEN}+{Fore.RESET})"
                f"{Fore.GREEN} Code: {short_code_url[:24]}*** | Name: {name} | Expires in: {time_left}{Fore.RESET}")

    print(f"\n{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET})"
        f"{Fore.LIGHTCYAN_EX} All active links have been checked!")

    input(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET})"
        f"{Fore.LIGHTCYAN_EX} Press enter to exit. ")

    os.system("cls" if platform.system() == "Windows" else "clear")
    sys.exit()

def infos():
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter(r"""
 _   _ _ _                       ______                         ______                      
| \ | (_) |               ___    |  _  \                        | ___ \                     
|  \| |_| |_ _ __ ___    ( _ )   | | | |___  ___ ___  _ __ ___  | |_/ /___  __ _  ___ _ __  
| . ` | | __| '__/ _ \   / _ \/\ | | | / _ \/ __/ _ \| '__/ __| |    // _ \/ _` |/ _ \ '_ \ 
| |\  | | |_| | | (_) | | (_>  < | |/ /  __/ (_| (_) | |  \__ \ | |\ \  __/ (_| |  __/ | | |
\_| \_/_|\__|_|  \___/   \___/\/ |___/ \___|\___\___/|_|  |___/ \_| \_\___|\__, |\___|_| |_|
                                                                            __/ |           
                                                                           |___/            
""")))
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("\nmade by @imlittledoo_ - V1.0 - https://discord.gg/R6qPEHrj")))

def main():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")
    ensure_directories()
    infos()
    print(Colorate.Horizontal(Colors.blue_to_cyan, Center.XCenter("""\n
[1] - Link Fetcher
[2] - Generate New Links
[3] - Mass Link Regeneration
[4] - Single Link Regeneration
[5] - Exit""")))
    opt = input(f"\n{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET}){Fore.LIGHTCYAN_EX} Which function do you want to use? ")
    if opt == "1":
        fetcher()
    if opt == "2":
        generate_new()
    if opt == "3":
        mass_regen()
    if opt == "4":
        code = input(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET}){Fore.LIGHTCYAN_EX} Which gift link do you want to regenerate? ")
        ncode = normalize_code(code)
        regen(ncode)
    if opt == "5":
        print(f"{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.LIGHTCYAN_EX}•{Fore.RESET}){Fore.LIGHTCYAN_EX} Exiting in 3 seconds... Goodbye!{Fore.RESET}")
        time.sleep(3)
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")
        sys.exit()
    else:
        main()
        print(f"\n{Fore.RESET}{Fore.MAGENTA}[{timestamp()}]{Fore.RESET}({Fore.RED}-{Fore.RESET}){Fore.RED} Choose a valid option from the available menu above!")

if __name__ == "__main__":
    main()
