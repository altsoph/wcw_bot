import logging
import cv2
from proto_filter import * 

class instance(proto_filter):
    def get(self,tags,confidences,boxes,source_cfg=None,parameters = None):
        """ 
        gets tags,confidences,boxes
        returns filtered tags,confidences,boxes
        """
        logging.debug('Module "%s" activated.', __name__)
        min_confidence = self.main_cfg['general']['filtering']['min_confidence']
        nms_threshold = self.main_cfg['general']['filtering']['nms_threshold']

        if source_cfg and source_cfg.get('min_confidence'): min_confidence = source_cfg.get('min_confidence')
        if source_cfg and source_cfg.get('nms_threshold'):  nms_threshold = source_cfg.get('nms_threshold')

        if parameters and parameters.get('min_confidence'): min_confidence = parameters.get('min_confidence')
        if parameters and parameters.get('nms_threshold'):  nms_threshold = parameters.get('nms_threshold')

        indices = cv2.dnn.NMSBoxes(boxes, confidences, min_confidence, nms_threshold)
        res = []
        for idx in indices:
            idx = idx[0]
            res.append( [tags[idx],confidences[idx],boxes[idx]] )
        res = list(zip(*res))
        logging.info('Module "%s": found tags %s.', __name__, str(res))
        return res        
