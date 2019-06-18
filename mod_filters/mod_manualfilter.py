import logging
from collections import defaultdict
from proto_filter import * 

class instance(proto_filter):
    def get(self,tags,confidences,boxes,source_cfg=None,parameters = None):
        """ 
        gets tags,confidences,boxes
        returns filtered tags,confidences,boxes
        """
        logging.debug('Module "%s" activated.', __name__)
        # print(source_cfg)
        filters = defaultdict(list)
        for item in parameters.get("suppress_list",[]):
            filters[item[0]].append((item[1],item[2]))
        # print(filters)
        res = []
        for tag,conf,box in zip(tags,confidences,boxes):
            skip = False
            for item in filters[source_cfg['id']]:
                if tag in item[1] and max(box[0],0)>=item[0][0] and max(box[1],0)>=item[0][1] and max(box[0],0)+box[2]<=item[0][2] and max(box[1],0)+box[3]<=item[0][3]:
                    skip = True
#            print(tag,box,skip)
            if not skip:
                res.append( [tag,conf,box] )
        res = list(zip(*res))
        logging.info('Module "%s": found tags %s.', __name__, str(res))
        return res

