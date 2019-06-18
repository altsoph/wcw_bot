import logging
from proto_filter import * 

class instance(proto_filter):
    def get(self,tags,confidences,boxes,source_cfg=None,parameters = None):
        """ 
        gets tags,confidences,boxes
        returns filtered tags,confidences,boxes
        """
        logging.debug('Module "%s" activated.', __name__)
        ignore_tags = set(self.main_cfg['general']['filtering']['ignore_tags'])
        if source_cfg and source_cfg.get('replace_ignore_tags'):
            ignore_tags = set(source_cfg.get('replace_ignore_tags'))
        elif source_cfg and source_cfg.get('add_ignore_tags'):
            ignore_tags |= set(source_cfg.get('add_ignore_tags'))
        if parameters and parameters.get('replace_ignore_tags'):
            ignore_tags = set(parameters.get('replace_ignore_tags'))
        elif parameters and parameters.get('add_ignore_tags'):
            ignore_tags |= set(parameters.get('add_ignore_tags'))
        res = []
        for tag,conf,box in zip(tags,confidences,boxes):
            if tag not in ignore_tags:
                res.append( [tag,conf,box] )
        res = list(zip(*res))
        logging.info('Module "%s": found tags %s.', __name__, str(res))
        return res

