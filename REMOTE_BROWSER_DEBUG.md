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

## 2. Build an isolated probe image

The deployed host has a custom Compose file using `gaiar/wcw_bot`, a local port mapping, and its own mounts. Leave it and the running container untouched while testing. From the host's current Git checkout, fetch the repair branch into a separate worktree:

```sh
git fetch https://github.com/altsoph/wcw_bot.git upstream/browser-yolo4-refresh
git worktree add ../wcw_bot-browser-fix FETCH_HEAD
cd ../wcw_bot-browser-fix
mkdir -p dbg_detected
docker build --progress=plain -t wcw-bot-browser-probe --build-arg YOLO_MODEL=none .
```

The build alone does not replace the running bot. The Dockerfile uses Selenium Manager to cache Firefox and resolve geckodriver at build time, without an additional apt repository. The new downloader uses `eager` page loading and a 30-second page timeout by default.

For A-Telecom sources, the separate `config.probe.yaml` already includes these settings:

```yaml
    page_load_strategy: none
    page_load_timeout: 20
```

`none` tells WebDriver to return from navigation without waiting for the page's load event. The downloader then waits the configured `waiting_time` before taking a screenshot. Check the resulting image; a returned screenshot can still show a loading page rather than a video frame.

## 3. Test one source without running the bot pipeline

Run this in the new checkout before replacing the running bot. It invokes one downloader, without reading the production config or running the Telegram pipeline:

```sh
docker run --rm -v "$PWD/dbg_detected:/app/dbg_detected" wcw-bot-browser-probe timeout 70s python3 -c "import sys,yaml; sys.path.insert(0,'/app/mod_downloaders'); from mod_htmlscreenshotdownloader import instance; s=yaml.safe_load(open('/app/config.probe.yaml'))['sources']['boat_dk_202610_1']; im=instance({}).get(s); print('image_size=', im.size if im else None); im and im.save('/app/dbg_detected/zhigansk_probe.jpg')"
```

Open `dbg_detected/zhigansk_probe.jpg` on the host. If it saves a blank/loading screen, the page needs a video-readiness check or a direct stream URL instead of a timed page screenshot. Deployment should preserve the host's custom Compose file and current `config.yaml`.

The local automated tests check the new page-load option and timeout wiring. A full Docker build and live Firefox capture could not be run in the local workspace because no Docker engine is available there.
