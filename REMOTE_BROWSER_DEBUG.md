# A-Telecom capture: diagnosis and recovery

The 2026-10-11 log shows a successful Firefox WebDriver session (`POST /session` returned 200), followed by a navigation timeout on the Zhigansk embed. A bounded browser probe returned an all-white image. The Flussonic `preview.jpg` endpoint returned real JPEG frames for all five A-Telecom sources and changed between two requests from the local workstation. The deployed `mod_simpledownloader` probe hung, so verify the preview endpoint inside the container before changing production config. Keep all five chain entries enabled.

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

The old simple downloader has no request timeout. Stop a hanging probe with Ctrl-C and use this bounded, unbuffered check before editing the host config:

```sh
docker exec wcw_bot-wcw_bot-1 timeout 20s python3 -u -c "import urllib.request; print('opening', flush=True); r=urllib.request.urlopen('https://cam.a-telecom.ru/Zhigansk/preview.jpg', timeout=8); print('status=', r.status, 'length=', r.headers.get('Content-Length'), flush=True); print('bytes=', len(r.read()), flush=True)"
```

This uses the deployed Python network path. A successful result is HTTP 200 and roughly 50–60 KB read. If only `opening` appears or the command exits 124, inspect container DNS/network behavior before changing the chain. The repair branch now sets a default 20-second timeout for direct image requests, but that code is not in the running container.

## 3. Update the host config

After the bounded check succeeds, in the host's existing `config.yaml`, change only the `url` values for these source definitions:

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

This preserves the deployed image, Compose file, channels, and all five camera entries. Other HTML screenshot sources still benefit from the repair branch.

The browser-only image built successfully on the host and returned an all-white Zhigansk screenshot. The direct JPEG URLs returned 640×360 images from all five cameras during local checking.
