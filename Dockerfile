FROM gaiar/docker-python3-opencv:jammy-4.8.1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# The base image can contain an older geckodriver and a nonworking Firefox
# launcher. Selenium Manager downloads and caches a compatible browser and
# driver, as it already did in the running deployment.
ENV SE_SKIP_BROWSER_IN_PATH=true
RUN if [ -x /usr/local/bin/geckodriver ]; then mv /usr/local/bin/geckodriver /usr/local/bin/geckodriver.base; fi \
    && python3 -c "from selenium.webdriver.common.selenium_manager import SeleniumManager; SeleniumManager().binary_paths(['--browser', 'firefox'])"

COPY . /app
ARG YOLO_MODEL=yolov3
RUN sh download_yolo.sh "$YOLO_MODEL"

CMD ["python3", "camera_bot.py"]
