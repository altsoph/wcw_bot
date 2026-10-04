"""Capture a rendered web page as a webcam image."""

import random
import string

from browser_capture import capture_page
from proto_downloader import proto_downloader


class instance(proto_downloader):
    def get(self, source, parameters=None):
        parameters = parameters or {}
        random_part = ''.join(random.choices(string.digits, k=source.get('random_len', 13)))
        url = source['url'].replace('#random#', random_part)
        return capture_page(
            url,
            wait_seconds=parameters.get('waiting_time', source.get('waiting_time', 7)),
            page_load_timeout=parameters.get('page_load_timeout', source.get('page_load_timeout', 30)),
        )
