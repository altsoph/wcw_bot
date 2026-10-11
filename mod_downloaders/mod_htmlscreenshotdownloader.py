"""Capture a rendered web page as a webcam image."""

import random
import string

from browser_capture import capture_page
from proto_downloader import proto_downloader
from youtube_capture import capture_youtube_wrapper, is_youtube_wrapper


class instance(proto_downloader):
    def get(self, source, parameters=None):
        parameters = parameters or {}
        random_part = ''.join(random.choices(string.digits, k=source.get('random_len', 13)))
        url = source['url'].replace('#random#', random_part)
        if is_youtube_wrapper(url):
            return capture_youtube_wrapper(
                url,
                timeout=parameters.get('capture_timeout', source.get('capture_timeout', 60)),
            )
        return capture_page(
            url,
            wait_seconds=parameters.get('waiting_time', source.get('waiting_time', 7)),
            page_load_timeout=parameters.get('page_load_timeout', source.get('page_load_timeout', 30)),
            page_load_strategy=parameters.get(
                'page_load_strategy', source.get('page_load_strategy', 'eager')
            ),
        )
