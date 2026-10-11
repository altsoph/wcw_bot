"""Check public HTTP CONNECT proxies against YouTube over verified TLS."""

import argparse
import concurrent.futures
import random
import urllib.request


LISTS = (
    'https://raw.githubusercontent.com/Moleway/Free-Proxy-List/main/http.txt',
    'https://raw.githubusercontent.com/litportnet/free-proxy-list/live/proxies/http.txt',
)
TEST_URL = 'https://www.youtube.com/robots.txt'


def check(proxy):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({
        'http': 'http://' + proxy,
        'https': 'http://' + proxy,
    }))
    try:
        with opener.open(TEST_URL, timeout=5) as response:
            content = response.read(1024)
            if response.status == 200 and b'User-agent:' in content:
                return proxy
    except Exception:
        pass
    return None


class QuietLogger:
    def debug(self, message):
        pass

    def warning(self, message):
        pass

    def error(self, message):
        pass


def check_video(proxy):
    import yt_dlp

    try:
        with yt_dlp.YoutubeDL({
            'quiet': True,
            'no_warnings': True,
            'logger': QuietLogger(),
            'noplaylist': True,
            'format': 'bestvideo[protocol^=m3u8]/bestvideo',
            'proxy': 'http://' + proxy,
            'socket_timeout': 8,
            'extractor_retries': 0,
            'retries': 0,
        }) as youtube:
            info = youtube.extract_info('https://www.youtube.com/watch?v=i12eS_2YV-s',
                                        download=False)
        if info and info.get('live_status') == 'is_live' and info.get('url'):
            return proxy
    except Exception:
        pass
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int, default=200)
    parser.add_argument('--video', action='store_true', help='also test live stream extraction')
    args = parser.parse_args()
    proxies = set()
    direct = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for url in LISTS:
        with direct.open(url, timeout=15) as response:
            proxies.update(line.strip() for line in response.read().decode().splitlines()
                           if ':' in line)
    proxies = list(proxies)
    random.Random(20261011).shuffle(proxies)
    proxies = proxies[:args.limit]
    print('Checking %d public proxies' % len(proxies), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        working = [proxy for proxy in executor.map(check, proxies) if proxy]
    print('HTTPS to YouTube:', len(working), flush=True)
    if args.video:
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            working = [proxy for proxy in executor.map(check_video, working) if proxy]
        print('Live extraction:', len(working), flush=True)
    for proxy in working:
        print(proxy, flush=True)


if __name__ == '__main__':
    main()
