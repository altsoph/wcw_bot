"""Inspect a YouTube wrapper player without running the bot or Telegram pipeline."""

import argparse
import json
import re
import time
from pathlib import Path

from selenium import webdriver


PLAYER_STATE = """
const player = window.player;
let state = null;
let title = '';
if (player && typeof player.getPlayerState === 'function') {
  try {
    state = player.getPlayerState();
    title = player.getVideoData()?.title || '';
  } catch (error) { state = String(error); }
}
return {
  readyState: document.readyState,
  iframeApi: typeof window.YT !== 'undefined',
  playerCreated: !!player,
  playerState: state,
  title: title,
  iframeCount: document.querySelectorAll('iframe').length,
  visibleText: document.body?.innerText?.slice(0, 300) || ''
};
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video_id')
    parser.add_argument('--wait', type=int, default=20)
    parser.add_argument('--output', type=Path, default=Path('/app/dbg_detected/youtube_probe.png'))
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', args.video_id):
        parser.error('video_id must be an 11-character YouTube ID')

    url = ('https://jeffreyca.github.io/yt-embed-wrapper/embed.html?v='
           + args.video_id + '&autoplay=1&mute=1&controls=0')
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    options.page_load_strategy = 'none'
    options.set_preference('media.autoplay.default', 0)
    options.set_preference('media.volume_scale', '0.0')
    print('Opening:', url, flush=True)
    with webdriver.Firefox(options=options) as driver:
        driver.set_window_size(1920, 1080)
        driver.set_page_load_timeout(20)
        driver.get(url)
        deadline = time.monotonic() + args.wait
        previous = None
        while time.monotonic() < deadline:
            try:
                status = driver.execute_script(PLAYER_STATE)
            except Exception as error:
                status = {'scriptError': str(error)}
            if status != previous:
                print('Player:', json.dumps(status, ensure_ascii=False), flush=True)
                previous = status
            if status.get('playerState') == 1:  # YouTube PLAYING
                break
            time.sleep(2)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(args.output))
        print('Screenshot:', args.output, flush=True)


if __name__ == '__main__':
    main()
