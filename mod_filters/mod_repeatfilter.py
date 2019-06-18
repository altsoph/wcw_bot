import logging
import time
from proto_filter import * 
from collections import defaultdict

class instance(proto_filter):
    storages = None
    def __init__(self,cfg):
        self.storages = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        super().__init__(cfg)
    def get(self,tags,confidences,boxes,source_cfg=None,parameters = None):
        """ 
        gets tags,confidences,boxes
        returns filtered tags,confidences,boxes
        """
        if not parameters or 'storage' not in parameters or 'suppress_period' not in parameters or not source_cfg or 'id' not in source_cfg:
            logging.debug('Module "%s" aborted: not enough parameters.', __name__)
        logging.debug('Module "%s" activated.', __name__)

        res = []
        remember_tags = set()
        for tag,conf,box in zip(tags,confidences,boxes):
            last_seen = self.storages[parameters['storage']][source_cfg['id']][tag]
            if ( time.time() - last_seen ) < parameters['suppress_period']:
                logging.debug('Module "%s": Tag "%s" suppressed for %d seconds more.', __name__, tag, int(parameters['suppress_period'] - ( time.time() - last_seen )))
                # print('Module "%s": Tag "%s" suppressed for %d seconds more.' %  (__name__, tag, int(parameters['suppress_period'] - ( time.time() - last_seen ))))
                continue
            remember_tags.add(tag)
            res.append( [tag,conf,box] )
        for tag in remember_tags:
            self.storages[parameters['storage']][source_cfg['id']][tag] = time.time()
        res = list(zip(*res))
        logging.info('Module "%s": found tags %s.', __name__, str(res))
        return res

