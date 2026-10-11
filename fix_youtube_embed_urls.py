"""Repair malformed YouTube wrapper URLs in a YAML config without reformatting it."""

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml


PREFIX = b'https://jeffreyca.github.io/yt-embed-wrapper/embed.html?v='
MALFORMED = re.compile(
    rb'(?m)^([ \t]*url:[ \t]*' + re.escape(PREFIX) + rb'[A-Za-z0-9_-]{11})[?]autoplay='
)


def repair(data):
    return MALFORMED.subn(lambda match: match.group(1) + b'&autoplay=', data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--apply', action='store_true', help='write the repair and make a backup')
    args = parser.parse_args()

    original = args.config.read_bytes()
    repaired, count = repair(original)
    before = yaml.safe_load(original)
    after = yaml.safe_load(repaired)
    changed = [source_id for source_id, source in before['sources'].items()
               if source.get('url') != after['sources'][source_id].get('url')]
    if count != len(changed):
        raise RuntimeError('Refusing to write: URL replacement count differs from changed sources')

    print('Malformed wrapper URLs:', count)
    print('Sources:', ', '.join(changed) if changed else '(none)')
    if not args.apply or not count:
        return

    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    backup = args.config.with_name(args.config.name + '.' + timestamp + '.bak')
    backup.write_bytes(original)
    args.config.write_bytes(repaired)
    print('Backup:', backup)
    print('Updated:', args.config)


if __name__ == '__main__':
    main()
