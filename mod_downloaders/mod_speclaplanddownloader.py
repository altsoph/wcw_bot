import logging
import string
import io
import random
import json
import urllib.request
from PIL import Image
from proto_downloader import * 

class instance(proto_downloader):
    def __init__(self,cfg):
        self.last_id = None
        super().__init__(cfg)
    def get(self, source, parameters=None):
        """ 
        just fetch the image from the url and convert it to the PIL Image
        """

        logging.debug('Module "%s" activated.', __name__)

        hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Connection' : 'close',
        'Accept' : 'application/json, text/plain, */*',
        'Referer' : 'https://webcams.lightsoverlapland.com/viewer?camera=1&theme=theme-green'
        }

        url = "https://webcams.lightsoverlapland.com/api/photos/1?#last#domain=https:%2F%2Flightsoverlapland.com%2Faurora-webcam%2F"
        last_replacer = ""

#         try:
        if self.last_id is not None:
            last_replacer = "last=%d&" %(self.last_id-1)
        url = url.replace("#last#", last_replacer)

        req = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(req)
        data = response.read()  
        data = json.loads(data)
        last_item = data['data'][0]

        self.last_id = last_item['id']
        url = last_item['large_url']
        del(hdr['Accept'])
        req = urllib.request.Request(url, headers=hdr)
        response = urllib.request.urlopen(req)
        data = response.read()
        image = Image.open(io.BytesIO(data))
        return image

#         except:
#             logging.warning('Module "%s": some error.', __name__)
#             return None


