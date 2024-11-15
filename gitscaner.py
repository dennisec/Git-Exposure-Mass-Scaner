import requests
from multiprocessing.pool import ThreadPool

def banner():
    print(r"""
 ____  _____ _   _ _   _ ___ ____   ___ ____     ____ _ _
|  _ \| ____| \ | | \ | |_ _| ___| |_ _|  _ \   / ___(_) |_
| | | |  _| |  \| |  \| || ||___ \  | || | | | | |  _| | __|
| |_| | |___| |\  | |\  || | ___) | | || |_| | | |_| | | |_
|____/|_____|_| \_|_| \_|___|____(_)___|____/   \____|_|\__|
| ____|_  ___ __   ___  ___ _   _ _ __ ___
|  _| \ \/ / '_ \ / _ \/ __| | | | '__/ _ \
| |___ >  <| |_) | (_) \__ \ |_| | | |  __/
|_____/_/\_\ .__/ \___/|___/\__,_|_|  \___|
           |_|
          """)

def add_http(lists):
    try:
        for i in range(len(lists)):
            if not lists[i].startswith("http"):
                lists[i] = "http://" + lists[i]
    except KeyboardInterrupt:
        print("\033[95m[-] Canceled !.\033[0m")
        exit()
    return lists

try:
    banner()
    urls = input("\033[93m[+] Target : \033[0m")
    power = int(input("\033[93m[+] Thread : \033[0m"))
except KeyboardInterrupt:
    print("\n\033[95m[-] Canceled !.\033[0m")
    exit()

try:
    with open(urls, "r") as file:
        lists = file.read().splitlines()
except FileNotFoundError:
    print("\033[91mList Not Found !.\033[0m")
    exit()
except KeyboardInterrupt:
    print("\n\033[95m[-] Canceled !.\033[0m")
    exit()

webs = add_http(lists)

def send_request(url):
    try:
        response = requests.get(url, timeout=3)
        return response
    except requests.exceptions.RequestException:
        return None

git_files = [
    "/.git/config",
    ".gitignore",
    ".git/COMMIT_EDITMSG",
    ".git/description",
    ".git/hooks/applypatch-msg.sample",
    ".git/hooks/commit-msg.sample",
    ".git/hooks/post-commit.sample",
    ".git/hooks/post-receive.sample",
    ".git/hooks/post-update.sample",
    ".git/hooks/pre-applypatch.sample",
    ".git/hooks/pre-commit.sample",
    ".git/hooks/pre-push.sample",
    ".git/hooks/pre-rebase.sample",
    ".git/hooks/pre-receive.sample",
    ".git/hooks/prepare-commit-msg.sample",
    ".git/hooks/update.sample",
    ".git/index",
    ".git/info/exclude",
    ".git/objects/info/packs",
]

vuln_content = [
    "[core]",
    "repositoryformatversion = 0",
    "filemode = true",
    "bare = false",
    "logallrefupdates = true",
    "[remote \"origin\"]",
]

def check_vulnerabilities(target, file):
    try:
        response = send_request(target + file)
        if response:
            if response.status_code == 200:
                if all(line in response.text for line in vuln_content):
                    print(f"\033[92m[+] {target + file} -> Vulnerable (File Accessible)\033[0m")
                    with open("vulnerable_gits.txt", 'a') as inl:
                        inl.write(target + file + "\n")
                else:
                    print(f"\033[91m[-] {target + file} -> NOT VULNERABLE\033[0m")
            else:
                print(f"\033[91m[-] {target + file} -> NOT FOUND or REDIRECTED (Status Code: {response.status_code})\033[0m")
        else:
            print(f"\033[91m[-] {target + file} -> NOT FOUND\033[0m")

        if file == "/.git/":
            directory_response = send_request(target + "/.git/")
            if directory_response and directory_response.status_code == 200:
                if "Index of /.git" in directory_response.text:
                    print(f"\033[92m[+] {target}/.git/ -> Vulnerable (Directory Index Accessible)\033[0m")
                    with open("vulnerable_gits.txt", 'a') as inl:
                        inl.write(target + "/.git/\n")
                else:
                    print(f"\033[91m[-] {target}/.git/ -> NOT VULNERABLE (Directory not indexed)\033[0m")

    except KeyboardInterrupt:
        print("\n\033[95m[-] Canceled !.\033[0m")
        exit()

with ThreadPool(power) as pool:
    results = [(target, file) for target in webs for file in git_files]
    for result in pool.starmap(check_vulnerabilities, results):
        try:
            print(result)
        except Exception as e:
            print(e)

print("\033[92mRESULT SAVED AS TXT FILE\033[0m")