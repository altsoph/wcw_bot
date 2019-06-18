import logging
from proto_sender import * 
import time
import datetime
import io
import numpy as np
from PIL import Image

class instance(proto_sender):
    def get(self, img, annot, target, parameters=None):
        logging.debug('Module "%s" activated.', __name__)
        img = Image.fromarray(img)
        ts_dump = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
        r_dump = str(np.random.randint(0,999)).zfill(3)
        save_fn = '%s/%s_%s%s.png' % (target['path'],ts_dump,r_dump,target['suffix'])
        img.save(save_fn)
        if parameters and 'orig_pic' in parameters:
        	img = Image.fromarray(parameters['orig_pic'])
	        save_fn = '%s/%s_%s%s.png' % (target['path'],ts_dump,r_dump,'_raw')
	        img.save(save_fn)
        logging.debug('Module "%s": File "%s" saved.', __name__, save_fn)
