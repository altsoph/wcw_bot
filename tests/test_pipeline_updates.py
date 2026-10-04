"""Focused regression checks for optional modules and browser capture."""

import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlsplit

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
for directory in ('mod_downloaders', 'mod_detectors', 'mod_filters'):
    sys.path.insert(0, str(ROOT / directory))

import browser_capture
import mod_conffilter
import mod_m3u8screenshotdownloader
import mod_yolo4detector
from module_loader import load_modules


class ModuleLoadingTests(unittest.TestCase):
    def test_unused_module_is_not_imported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            (folder / 'mod_test_active.py').write_text(
                'class instance:\n    def __init__(self, cfg): self.cfg = cfg\n',
                encoding='utf-8',
            )
            (folder / 'mod_test_unused.py').write_text(
                'raise RuntimeError("unused module was imported")\n',
                encoding='utf-8',
            )
            cfg = {
                'general': {'modules_dir': {name: temp_dir for name in (
                    'downloader', 'detector', 'filter', 'annotator', 'enhancer', 'sender'
                )}},
                'chains': {'test': {
                    'sources': [{'module': 'mod_test_active'}],
                    'detector': 'mod_test_active',
                    'filters': [{'module': 'mod_test_active'}],
                    'enhancers': [{'module': 'mod_test_active'}],
                    'senders': [{'sender_module': 'mod_test_active',
                                 'annotator_module': 'mod_test_active'}],
                }},
            }
            try:
                loaded = load_modules(cfg)
                self.assertEqual(len(loaded), 6)
                self.assertNotIn('mod_test_unused', sys.modules)
            finally:
                sys.modules.pop('mod_test_active', None)


class OpenCvCompatibilityTests(unittest.TestCase):
    def test_nms_accepts_flat_nested_and_empty_indexes(self):
        cfg = {'general': {'filtering': {'min_confidence': 0.5, 'nms_threshold': 0.4}}}
        detector_filter = mod_conffilter.instance(cfg)
        args = (['boat', 'bird'], [0.9, 0.8], [[0, 0, 10, 10], [20, 20, 10, 10]])
        for indexes in (np.array([1]), np.array([[1]]), [1], [[1]]):
            with self.subTest(indexes=indexes):
                with mock.patch('cv2.dnn.NMSBoxes', return_value=indexes):
                    self.assertEqual(detector_filter.get(*args)[0], ('bird',))
        for indexes in (None, np.array([])):
            with self.subTest(indexes=indexes):
                with mock.patch('cv2.dnn.NMSBoxes', return_value=indexes):
                    self.assertEqual(detector_filter.get(*args), ([], [], []))

    def test_yolo4_accepts_flat_and_nested_output_layers(self):
        detector = object.__new__(mod_yolo4detector.instance)
        detector.net = mock.Mock()
        detector.net.getLayerNames.return_value = ['first', 'second']
        for indexes in (np.array([2]), np.array([[2]])):
            with self.subTest(indexes=indexes):
                detector.net.getUnconnectedOutLayers.return_value = indexes
                self.assertEqual(detector._get_output_layers(), ['second'])


class BrowserCaptureTests(unittest.TestCase):
    def test_capture_converts_screenshot_to_rgb(self):
        screenshot = io.BytesIO()
        Image.new('RGBA', (2, 2), (10, 20, 30, 255)).save(screenshot, 'PNG')
        driver = mock.MagicMock()
        driver.__enter__.return_value = driver
        driver.get_screenshot_as_png.return_value = screenshot.getvalue()
        with mock.patch('selenium.webdriver.Firefox', return_value=driver), \
             mock.patch('selenium.webdriver.FirefoxOptions'), \
             mock.patch('browser_capture.time.sleep'):
            image = browser_capture.capture_page('https://example.com', wait_seconds=0)
        self.assertEqual(image.mode, 'RGB')
        self.assertEqual(image.getpixel((0, 0)), (10, 20, 30))
        driver.get.assert_called_once_with('https://example.com')

    def test_hls_stream_url_is_encoded_in_player_query(self):
        source = {'url': 'https://example.com/live.m3u8?token=a&quality=high'}
        with mock.patch.object(mod_m3u8screenshotdownloader, 'capture_page') as capture:
            mod_m3u8screenshotdownloader.instance({}).get(source)
        player_url = capture.call_args.args[0]
        self.assertEqual(parse_qs(urlsplit(player_url).query)['c'], [source['url']])
        self.assertTrue(capture.call_args.kwargs['wait_for_video'])

    def test_hls_capture_waits_for_decoded_video(self):
        screenshot = io.BytesIO()
        Image.new('RGB', (1, 1)).save(screenshot, 'PNG')
        driver = mock.MagicMock()
        driver.__enter__.return_value = driver
        driver.execute_script.return_value = True
        driver.get_screenshot_as_png.return_value = screenshot.getvalue()
        with mock.patch('selenium.webdriver.Firefox', return_value=driver), \
             mock.patch('selenium.webdriver.FirefoxOptions'), \
             mock.patch('selenium.webdriver.support.ui.WebDriverWait') as wait:
            wait.return_value.until.side_effect = lambda condition: condition(driver)
            image = browser_capture.capture_page('file:///player.html', wait_for_video=True)
        self.assertEqual(image.mode, 'RGB')
        driver.execute_script.assert_called_once()


if __name__ == '__main__':
    unittest.main()
