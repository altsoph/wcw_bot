# Remote Firefox capture: diagnosis and recovery

The 2026-10-11 log shows a successful Firefox WebDriver session (`POST /session` returned 200). The next `driver.get()` to the Zhigansk embed did not return; the Selenium HTTP client timed out after 120 seconds. Session teardown then waited again. The old downloader uses the default `normal` page load strategy and does not set a page load timeout. The geckodriver version warning is worth cleaning up, but it is not evidence that Firefox failed to start.

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

## 2. Restore progress while investigating

In the host `config.yaml`, comment out the `boat_dk_202610_1` item under `chains.boatbot.sources` (keep its definition in `sources`), then restart the service so it rereads the config:

```sh
docker compose -p wcw_bot restart wcw_bot
docker logs --since 5m wcw_bot-wcw_bot-1
```

If the other A-Telecom embeds stall in the same way, temporarily comment out their chain items too. This is a temporary operational step; it does not delete their source definitions.

## 3. Deploy the current code

Use a clean checkout of the `upstream/browser-yolo4-refresh` branch containing the browser fix. Preserve the host's current `config.yaml` and `secrets.yaml` by copying them into the new checkout, or keep equivalent bind mounts. Do not replace the host config with the repository's example config. In the checkout:

```sh
mkdir -p dbg_detected
docker compose -p wcw_bot build --build-arg YOLO_MODEL=yolov4 wcw_bot
docker compose -p wcw_bot up -d --no-deps --force-recreate wcw_bot
```

The project name `wcw_bot` matches the existing container name, so Compose recreates that service instead of running a second posting bot. The new Dockerfile installs Firefox and resolves geckodriver at build time. The new downloader uses `eager` page loading and a 30-second page timeout by default.

For A-Telecom sources that still hang, add these source-level settings to each of `boat_dk_202610_1` through `boat_dk_202610_5` in the host config, as shown in the local `config.v2.yaml`:

```yaml
    page_load_strategy: none
    page_load_timeout: 20
```

`none` tells WebDriver to return from navigation without waiting for the page's load event. The downloader then waits the configured `waiting_time` before taking a screenshot. Check the resulting image; a returned screenshot can still show a loading page rather than a video frame.

## 4. Test one source without running the bot pipeline

Run this in the new checkout before enabling the source in `chains.boatbot.sources` again:

```sh
docker compose -p wcw_bot run --rm --no-deps wcw_bot timeout 70s python3 -c "import sys,yaml; sys.path.insert(0,'/app/mod_downloaders'); from mod_htmlscreenshotdownloader import instance; s=yaml.safe_load(open('/app/config.yaml'))['sources']['boat_dk_202610_1']; im=instance({}).get(s); print('image_size=', im.size if im else None); im and im.save('/app/dbg_detected/zhigansk_probe.jpg')"
```

Open `dbg_detected/zhigansk_probe.jpg` on the host. If it shows real video and the command finishes promptly, re-enable the chain item and restart. If the command times out, leave that camera disabled and collect the full error plus the endpoint check result. If it saves a blank/loading screen, the page needs a video-readiness check or a direct stream URL instead of a timed page screenshot.

The local automated tests check the new page-load option and timeout wiring. A full Docker build and live Firefox capture could not be run in the local workspace because no Docker engine is available there.
