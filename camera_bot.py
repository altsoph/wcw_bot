import sys
import importlib
import yaml
import logging
import time
import numpy as np

from glob import glob
from collections import defaultdict

# loggin 

# logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', datefmt='%Y%m%d_%H%M%S', handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)
logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', datefmt='%Y%m%d_%H%M%S', filename='debug.log', level=logging.DEBUG)
logging.debug('Logging started')


# load config

cfg = yaml.load(open('config.yaml', encoding='utf-8')) # , Loader=yaml.FullLoader)
cfg['secrets'] = yaml.load(open('secrets.yaml', encoding='utf-8')) #, Loader=yaml.FullLoader)
logging.debug('Config loaded')

# discover and install available modules

modules = defaultdict(dict)
for mod_type in ('downloader','detector','filter','annotator','enhancer','sender'):
    sys.path.append(cfg['general']['modules_dir'][mod_type])
    for module in glob(cfg['general']['modules_dir'][mod_type]+'mod_*'):
        module_fn = module.replace('\\','/').split('/')[-1].replace('.py','')
        modules[mod_type][module_fn] = importlib.import_module(module_fn).instance(cfg)
logging.debug('Modules loaded')

def _load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)


sources_cache = dict()
source_chain_check_ts = dict()
# process chains
while True:
    logging.info('Another iteration:')
    for chain, chain_cfg in cfg['chains'].items():
        logging.info('Processing chain "%s"', chain)
        fetched_pics = []
        for source_cfg in chain_cfg['sources']:
            check_period = cfg['general']['check_period']
            if 'parameters' in source_cfg and source_cfg['parameters'].get('check_period',0): check_period = source_cfg['parameters']['check_period']
            if (time.time()-source_chain_check_ts.get( (chain,source_cfg['source']), 0 ))<check_period: 
                # print(source_cfg['source'],chain,check_period, check_period-(time.time()-source_chain_check_ts.get( (chain,source_cfg['source']), 0 )))
                logging.info('Skip the source %s in the chain %s since a check_period is not completed.',source_cfg['source'],chain)
                continue
            source_chain_check_ts[ (chain,source_cfg['source']) ] = time.time()
              # in source_chain_check_ts and 
            cache_timeout = cfg['sources'][source_cfg['source']].get('cache_time',cfg['general']['cache_time'])
            if source_cfg['source'] in sources_cache and (time.time()-sources_cache[source_cfg['source']][0])<cache_timeout:
                logging.debug('Got a cached pic for source "%s". Timeout in %d.',source_cfg['source'],cache_timeout-int(sources_cache[source_cfg['source']][0]-time.time()))
                pic = sources_cache[source_cfg['source']][1]
            else:
                pic = modules['downloader'][source_cfg['module']].get(cfg['sources'][source_cfg['source']],parameters=source_cfg.get('parameters',None))
                sources_cache[source_cfg['source']] = (time.time(), pic)
                logging.debug('Caching a pic for source "%s". Timeout in %d.',source_cfg['source'],cache_timeout)
            if pic: fetched_pics.append( (_load_image_into_numpy_array(pic),source_cfg['source']) )
        logging.info('Fetched total %d pics.',len(fetched_pics))

        tagged_pics = []
        for pic, src in fetched_pics:
            tags = modules['detector'][chain_cfg['detector']].get(pic)
            if len(tags[0])>0:
                tagged_pics.append( (pic,src,tags) )
        logging.info('Tagged total %d pics.',len(tagged_pics))

        filtered_pics = []
        for pic, src, tags in tagged_pics:
            for flt_mod in chain_cfg['filters']:
                tags = modules['filter'][flt_mod['module']].get(*tags,cfg['sources'][src],parameters=flt_mod.get('parameters',None))
                if not tags: break
            if tags and len(tags[0])>0:
                filtered_pics.append( (pic,src,tags) )
        logging.info('Filtered total %d pics.',len(filtered_pics))

        enhanced_pics = []
        for orig_pic, src, tags in filtered_pics:
            pic = orig_pic.copy()
            for enh_mod in chain_cfg['enhancers']:
                pic = modules['enhancer'][enh_mod['module']].get(pic,tags,cfg['sources'][src],parameters=enh_mod.get('parameters',None))
                if not pic.any(): break
            if pic.any():
                enhanced_pics.append( (pic,src,tags,orig_pic) )
        logging.info('Enhanced total %d pics.',len(enhanced_pics))

        for pic, src, tags, orig_pic in enhanced_pics:
            for sender in chain_cfg['senders']:
                parameters = sender.get('parameters',dict())
                parameters['orig_pic'] = orig_pic
                annotation = modules['annotator'][sender['annotator_module']].get(pic,tags,cfg['sources'][src],cfg['targets'][sender['target']],parameters=parameters)
                if annotation:
                    modules['sender'][sender['sender_module']].get(pic,annotation,cfg['targets'][sender['target']],parameters=parameters)
    logging.info('Iteration done.')
    time.sleep(cfg['general'].get('iteration_time',60*5))

exit()

