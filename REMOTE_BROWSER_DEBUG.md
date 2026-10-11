# A-Telecom capture: diagnosis and recovery

The 2026-10-11 log shows a successful Firefox WebDriver session (`POST /session` returned 200), followed by a navigation timeout on the Zhigansk embed. A bounded browser probe returned an all-white image. The Flussonic `preview.jpg` endpoint returned real JPEG frames for all five A-Telecom sources and changed between two requests. Use those direct images with the existing `mod_simpledownloader`; a new image build is not required for these five sources. Keep all five chain entries enabled.

Run these commands on the Docker host from the current Compose directory. They do not use the Telegram token or post to a channel.

## 1. Confirm what is inside the running container

```sh
docker exec wcw_bot-wcw_bot-1 python3 -c "from pathlib import Path; p=Path('/app/mod_downloaders/mod_htmlscreenshotdownloader.py'); print('new_capture_code=', 'from browser_capture import capture_page' in p.read_text())"
docker exec wcw_bot-wcw_bot-1 python3 -c "import selenium; print('selenium=', selenium.__version__)"
```

`new_capture_code=False` confirms the deployed image has the old downloader shown in the log.

Check whether the Zhigansk HTML endpoint responds from the container:

```sh
docker exec wcw_bot-wcw_bot-1 python3 -c "import urllib.request; r=urllib.request.urlopen('https://cam.a-telecom.ru/Zhigansk/embed.html?autoplay=true', timeout=15); print('HTTP', r.status, 'content-type', r.headers.get('Content-Type'))"
```

An HTTP failure or timeout here points to source availability or container networking. An HTTP success does not prove that the live video plays.

## 2. Check direct image capture in the deployed container

Run this read-only check before editing the host config:

```sh
docker exec wcw_bot-wcw_bot-1 python3 -c "import sys; sys.path.insert(0,'/app/mod_downloaders'); from mod_simpledownloader import instance; im=instance({}).get({'url':'https://cam.a-telecom.ru/Zhigansk/preview.jpg'}); print('image_size=', im.size if im else None)"
```

This uses the deployed downloader and network path. A valid result is `image_size= (640, 360)`. If it returns `None`, collect the warning and inspect container network/certificate behavior before changing the chain.

## 3. Update the host config

In the host's existing `config.yaml`, change only the `url` values for these source definitions:

| Source | New `url` |
| --- | --- |
| `boat_dk_202610_1` | `https://cam.a-telecom.ru/Zhigansk/preview.jpg` |
| `boat_dk_202610_2` | `https://cam.a-telecom.ru/Sangary_Yug/preview.jpg` |
| `boat_dk_202610_3` | `https://cam.a-telecom.ru/Pokrovsk_Naberejnaya/preview.jpg` |
| `boat_dk_202610_4` | `https://cam.a-telecom.ru/Bestyah/preview.jpg` |
| `boat_dk_202610_5` | `https://cam.a-telecom.ru/Lensk2/preview.jpg` |

Under `chains.boatbot.sources`, change the `module` of those same five items from `mod_htmlscreenshotdownloader` to `mod_simpledownloader`. Keep their `source` IDs and `check_period` values. Leave the `browser_url` links pointed at the original embed pages. Do not replace the host's full config.

From the original Compose directory, restart the current service and watch its logs:

```sh
docker compose restart wcw_bot
docker logs --since 5m wcw_bot-wcw_bot-1
```

This preserves the deployed image, Compose file, channels, and all five camera entries. Other HTML screenshot sources still benefit from the repair branch, but this A-Telecom fix needs only config changes.

The browser-only image built successfully on the host and returned an all-white Zhigansk screenshot. The direct JPEG URLs returned 640×360 images from all five cameras during local checking.
