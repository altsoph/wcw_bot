import logging
import cv2
import numpy as np
from proto_detector import * 

class instance(proto_detector):
    classes = None
    net = None
    def __init__(self,cfg):
        with open('yolov3.txt', 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.net = cv2.dnn.readNet('yolov3.weights', 'yolov3.cfg')
        super().__init__(cfg)

    # def _load_image_into_numpy_array(self,image):
    #     (im_width, im_height) = image.size
    #     return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)

    def _get_output_layers(self):
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
        return output_layers

    def get(self, image_np):
        logging.debug('Module "%s" activated.', __name__)
        conf_threshold = 1e-8 # no filtering here
        scale = 0.00392 # some hardcoded magic constant, just as in yolo example

        # Width, Height = img.size
        # image_np = self._load_image_into_numpy_array(img)
        # print(image_np.shape)
        Height, Width, _ = image_np.shape
        blob = cv2.dnn.blobFromImage(image_np, scale, (416,416), (0,0,0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self._get_output_layers())

        class_ids, confidences, boxes, tags  = [], [], [], []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence >= conf_threshold:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    x2 = x+w
                    y2 = y+h
                    x = max(x,0)
                    y = max(y,0)
                    x2 = min(x2,Width)
                    y2 = min(y2,Height)
                    w = x2-x
                    h = y2-y
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])
                    tags.append( str(self.classes[class_id]) )
        logging.info('Module "%s": found tags %s, %s, %s.', __name__, str(tags), str(confidences), str(boxes))
        return tags,confidences,boxes
