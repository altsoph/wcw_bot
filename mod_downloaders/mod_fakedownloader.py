import logging
import io
from PIL import Image
from glob import glob
import random
from proto_downloader import * 

class instance(proto_downloader):
    options = []
    def __init__(self,cfg):
        self.options = list(glob('raw_tests/*.png'))
        self.options.extend( list(glob('raw_tests/*.jpg')) )
        super().__init__(cfg)
    def get(self, source, parameters=None):
        """ 
        just fetch a random image from folder and convert it to the PIL Image
        """
        random.seed()
        logging.debug('Module "%s" activated.', __name__)
        print(self.options)
        random_file = random.choice(self.options)
        print(random_file)
        logging.info('Module "%s": selected image %s.', __name__, random_file)
        return Image.open(io.BytesIO(open(random_file,'rb').read()))
