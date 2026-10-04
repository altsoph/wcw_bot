"""Capture a frame from an HLS stream rendered by the local player page."""

import random
import string
from pathlib import Path
from urllib.parse import quote

from browser_capture import capture_page
from proto_downloader import proto_downloader


class instance(proto_downloader):
    def get(self, source, parameters=None):
        parameters = parameters or {}
        random_part = ''.join(random.choices(string.digits, k=source.get('random_len', 13)))
        stream_url = source['url'].replace('#random#', random_part)
        player_url = (Path(__file__).resolve().parent.parent / 'm3u8player.html').as_uri()
        player_url += '?c=' + quote(stream_url, safe='')
        return capture_page(
            player_url,
            wait_seconds=parameters.get('waiting_time', source.get('waiting_time', 7)),
            page_load_timeout=parameters.get('page_load_timeout', source.get('page_load_timeout', 30)),
            wait_for_video=True,
        )
