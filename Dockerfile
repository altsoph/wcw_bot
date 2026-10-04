FROM gaiar/docker-python3-opencv:jammy-4.8.1

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# Ubuntu Jammy distributes Firefox as a snap. Use Mozilla's signed deb repo
# so headless Firefox works inside the container.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates wget gnupg \
    && install -d -m 0755 /etc/apt/keyrings \
    && wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O /etc/apt/keyrings/packages.mozilla.org.asc \
    && printf 'deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main\n' > /etc/apt/sources.list.d/mozilla.list \
    && printf 'Package: firefox\nPin: origin packages.mozilla.org\nPin-Priority: 1000\n' > /etc/apt/preferences.d/mozilla \
    && apt-get update \
    && apt-get install -y --no-install-recommends firefox \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Download geckodriver during the build, rather than on first capture.
RUN python3 -c "from selenium.webdriver.common.selenium_manager import SeleniumManager; SeleniumManager().binary_paths(['--browser', 'firefox'])"

COPY . /app
ARG YOLO_MODEL=yolov3
RUN sh download_yolo.sh "$YOLO_MODEL"

CMD ["python3", "camera_bot.py"]
