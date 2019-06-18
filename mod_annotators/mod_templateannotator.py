import logging
from proto_annotator import * 

class instance(proto_annotator):
    def get(self,img,items,source_cfg=None,sender_cfg=None,parameters = None):
        """ 
        gets img, items, pars
        returns text annotation based on template
        """
        logging.debug('Module "%s" activated.', __name__)
        template = self.main_cfg['general']['annotation']['template']
        if source_cfg and source_cfg.get('template'):
            template = source_cfg.get('template')
        if sender_cfg and sender_cfg.get('template'):
            template = sender_cfg.get('template')
        if parameters and parameters.get('template'):
            template = parameters.get('template')

        substitutions = set()
        if source_cfg and 'substitutions' in source_cfg:
            substitutions |= set(source_cfg['substitutions'].keys())
        if sender_cfg and 'substitutions' in sender_cfg:
            substitutions |= set(sender_cfg['substitutions'].keys())
        if parameters and 'substitutions' in parameters:
            substitutions |= set(parameters['substitutions'].keys())

        for skey in substitutions:
            sval = None
            if source_cfg and 'substitutions' in source_cfg and skey in source_cfg['substitutions']: sval = source_cfg['substitutions'][skey]
            if sender_cfg and 'substitutions' in sender_cfg and skey in sender_cfg['substitutions']: sval = sender_cfg['substitutions'][skey]
            if parameters and 'substitutions' in parameters and skey in parameters['substitutions']: sval = parameters['substitutions'][skey]
            if sval:
                template = template.replace("%"+skey+"%",sval)

        # also replace TAGS
        tags,confs,boxes = items
        if len(tags) == 1: 
            tags = '"%s"' % tags[0]
        else:
            tags = str(list(set(tags)))
        template = template.replace("%TAGS%",tags)
        return template
