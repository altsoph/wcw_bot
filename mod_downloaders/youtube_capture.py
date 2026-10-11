"""Capture one frame from a YouTube live stream without using a browser."""

import io
import logging
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from PIL import Image


WRAPPER_HOST = 'jeffreyca.github.io'
WRAPPER_PATH = '/yt-embed-wrapper/embed.html'
VIDEO_ID = re.compile(r'^([A-Za-z0-9_-]{11})(?:$|[?&])')


def is_youtube_wrapper(url):
    parsed = urlsplit(url)
    return parsed.hostname == WRAPPER_HOST and parsed.path == WRAPPER_PATH


def get_video_id(url):
    if not is_youtube_wrapper(url):
        return None
    value = parse_qs(urlsplit(url).query).get('v', [''])[0]
    match = VIDEO_ID.match(value)
    return match.group(1) if match else None


def capture_youtube_wrapper(url, timeout=60):
    """Return an RGB frame, or None if extraction or decoding fails."""
    video_id = get_video_id(url)
    if video_id is None:
        logging.warning('YouTube wrapper URL has no valid video ID: %s', url)
        return None

    try:
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve()), video_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        if result.returncode != 0:
            logging.warning('YouTube frame capture failed for %s (exit %s)',
                            video_id, result.returncode)
            return None
        with Image.open(io.BytesIO(result.stdout)) as frame:
            return frame.convert('RGB')
    except subprocess.TimeoutExpired:
        logging.warning('YouTube frame capture timed out for %s after %ss', video_id, timeout)
    except Exception:
        logging.exception('YouTube frame capture failed for %s', video_id)
    return None


def _capture_frame(video_id):
    import cv2
    import yt_dlp

    page_url = 'https://www.youtube.com/watch?v=' + video_id
    with yt_dlp.YoutubeDL({
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'format': 'bestvideo[protocol^=m3u8]/bestvideo',
    }) as youtube:
        info = youtube.extract_info(page_url, download=False)
    if info.get('live_status') != 'is_live':
        raise RuntimeError('Video is not currently live')
    stream_url = info.get('url')
    if not stream_url:
        raise RuntimeError('No stream URL returned')

    capture = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
    try:
        if not capture.isOpened():
            raise RuntimeError('Could not open HLS stream')
        for _ in range(30):
            ok, frame = capture.read()
            if ok and frame is not None:
                encoded, jpeg = cv2.imencode('.jpg', frame)
                if not encoded:
                    raise RuntimeError('Could not encode frame')
                sys.stdout.buffer.write(jpeg.tobytes())
                return
        raise RuntimeError('HLS stream did not yield a frame')
    finally:
        capture.release()


if __name__ == '__main__':
    try:
        if len(sys.argv) != 2 or not re.fullmatch(r'[A-Za-z0-9_-]{11}', sys.argv[1]):
            raise ValueError('Invalid video ID')
        _capture_frame(sys.argv[1])
    except Exception as exc:
        # Never print a signed stream URL to logs.
        print('%s: %s' % (type(exc).__name__, str(exc).split('https://')[0][:200]), file=sys.stderr)
        raise SystemExit(1)
