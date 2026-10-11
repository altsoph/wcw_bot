"""Probe a YouTube live stream without a browser, then save one decoded frame."""

import argparse
import os
import re
import time
from pathlib import Path

import cv2
import yt_dlp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('video_id')
    parser.add_argument('--output', type=Path, default=Path('/app/dbg_detected/youtube_stream_probe.jpg'))
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]{11}', args.video_id):
        parser.error('video_id must be an 11-character YouTube ID')

    page_url = 'https://www.youtube.com/watch?v=' + args.video_id
    print('Extracting:', page_url, flush=True)
    started = time.monotonic()
    options = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'format': 'bestvideo[protocol^=m3u8]/bestvideo',
    }
    cookiefile = os.environ.get('WCW_YOUTUBE_COOKIES')
    if cookiefile:
        if not Path(cookiefile).is_file():
            raise FileNotFoundError('WCW_YOUTUBE_COOKIES file does not exist')
        options['cookiefile'] = cookiefile
        print('Cookie file: configured', flush=True)
    with yt_dlp.YoutubeDL(options) as youtube:
        info = youtube.extract_info(page_url, download=False)
    print('Video:', info.get('title'), flush=True)
    print('Status:', info.get('live_status'), flush=True)
    print('Format:', info.get('format_id'), info.get('protocol'), flush=True)
    print('Extracted in %.1fs' % (time.monotonic() - started), flush=True)

    stream_url = info.get('url')
    if not stream_url:
        raise RuntimeError('Extractor did not return a stream URL')
    # Do not print the temporary stream URL: it may contain signed parameters.
    capture = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
    try:
        if not capture.isOpened():
            raise RuntimeError('OpenCV could not open the stream')
        for attempt in range(30):
            ok, frame = capture.read()
            if ok and frame is not None:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                if not cv2.imwrite(str(args.output), frame):
                    raise RuntimeError('Could not save frame')
                print('Frame:', frame.shape[1], 'x', frame.shape[0], flush=True)
                print('Saved:', args.output, flush=True)
                return
        raise RuntimeError('Stream opened but did not yield a video frame')
    finally:
        capture.release()


if __name__ == '__main__':
    main()
