import logging
import string
import io
import random
import urllib.request
from PIL import Image
from proto_downloader import * 

class instance(proto_downloader):
    def get(self, source, parameters=None):
        """ 
        just fetch the image from the url and convert it to the PIL Image
        """
        hdr = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        'Connection' : 'close',
        'Cache-Control' : 'max-age=0',
        'Upgrade-Insecure-Requests' : '0',
        'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding' : 'gzip, deflate',
        'Accept-Language' : 'en-US;q=0.9,en;q=0.7'
        }

        random_len = source.get('random_len',13)
        random_part = ''.join(random.choice(string.digits) for _ in range(random_len))
        url = source['url'].replace('#random#',random_part)

        logging.debug('Module "%s" activated.', __name__)
        req = urllib.request.Request(url, headers=hdr)
        # response = urllib.request.urlopen(source['url'])
        try:
              response = urllib.request.urlopen(req)
              data = response.read()  
              image = Image.open(io.BytesIO(data))
              return image
        except:
            logging.warning('Module "%s": connection error to url %s.', __name__,url)
            return None
