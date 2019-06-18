import logging
import cv2
import numpy as np
from proto_enhancer import * 

class instance(proto_enhancer):
    # def _load_image_into_numpy_array(self,image):
    #     (im_width, im_height) = image.size
    #     return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
    def _draw_prediction(self, img, tag, confidence, x, y, x_plus_w, y_plus_h, COLORS):
        # label = str(self.classes[class_id])
        color = COLORS.get(tag,(0,0,0)) if COLORS else (0,0,0)
        cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
        cv2.putText(img, tag, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def get(self, np_img, items, source_cfg, parameters=None):
        """ 
        decorate image with tags
        """
        logging.debug('Module "%s" activated.', __name__)
        # np_img = self._load_image_into_numpy_array(pil_img)
        use_colors = None
        if 'class_colors' in self.main_cfg['general']:
            use_colors = self.main_cfg['general']['class_colors']
        if source_cfg and source_cfg.get('class_colors'):
            for k,v in source_cfg.get('class_colors').items():
                use_colors[k] = v
        if parameters and parameters.get('class_colors'):
            for k,v in parameters.get('class_colors').items():
                use_colors[k] = v
        for tag,conf,box in zip(*items):
            x, y, w, h = box[:4]
            self._draw_prediction(np_img, tag, conf, round(x), round(y), round(x+w), round(y+h), use_colors)
        return np_img