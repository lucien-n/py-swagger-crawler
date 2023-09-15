import requests
import sys
import json
import time
import threading

time_between_requests_ms = 800
max_threads = 8
threads: list[threading.Thread] = []


def crawl_host(host: str, endpoints: list[str]):
    last_request_at = time.time()
    for endpoint in endpoints:
        if last_request_at + time_between_requests_ms > time.time():
            time.sleep(
                (last_request_at + time_between_requests_ms - time.time()) / 1000
            )
        url = f"{host}/{endpoint}"
        res = requests.get(url)
        if res.status_code == 404:
            print(
                f"\033[1;37;41m {res.status_code} \033[0m {host}/\033[1m{endpoint}\033[0;0m"
            )
        elif res.status_code == 200:
            try:
                data = res.json()
                with open(f"./results/{url}.json", "w+") as f:
                    json.dump(data, f)
                print(
                    f"\033[1;37;42m {res.status_code} \033[0m {host}/\033[1m{endpoint}\033[0;0m",
                    res,
                )
            except json.JSONDecodeError:
                print(
                    f"\033[1;37;43m {res.status_code} \033[0m {host}/\033[1m{endpoint} \033[1;31mFailed to parse response\033[0;0m",
                    res,
                )


def get_endpoints(path: str):
    endpoints = []
    with open(path, "r") as f:
        data = f.read()
        endpoints = data.split("\n")
    return endpoints


def get_hosts(path: str):
    hosts = []
    with open(path, "r") as f:
        data = f.read()
        hosts = data.split("\n")
    return hosts


def main():
    host = None
    if len(sys.argv) > 1:
        host = sys.argv[1]

    endpoints = get_endpoints("./endpoints.txt")

    if not host:
        print("Getting hosts from './hosts.txt' as you did not provide an host")
        print(f"Crawling at a max of {max_threads} parallels crawlers")
        hosts = get_hosts("./hosts.txt")

        for host in hosts:
            if len(threads) >= max_threads:
                threads[0].join()
                threads.pop(0)

            thread = threading.Thread(target=crawl_host, args=(host, endpoints))
            thread.start()
            threads.append(thread)
            print(f"Crawling '{host}'")

    if not host.startswith("https://"):
        host = "https://" + host
        print(f"Crawling '{host}'")
        crawl_host(host, endpoints)


if __name__ == "__main__":
    main()
