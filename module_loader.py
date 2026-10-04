"""Load only pipeline modules referenced by active chains."""

import importlib
import sys
from collections import defaultdict
from pathlib import Path


MODULE_TYPES = ('downloader', 'detector', 'filter', 'annotator', 'enhancer', 'sender')


def load_modules(cfg):
    required = defaultdict(set)
    for chain in cfg['chains'].values():
        required['detector'].add(chain['detector'])
        for source in chain['sources']:
            required['downloader'].add(source['module'])
        for filter_cfg in chain['filters']:
            required['filter'].add(filter_cfg['module'])
        for enhancer_cfg in chain['enhancers']:
            required['enhancer'].add(enhancer_cfg['module'])
        for sender_cfg in chain['senders']:
            required['annotator'].add(sender_cfg['annotator_module'])
            required['sender'].add(sender_cfg['sender_module'])

    modules = defaultdict(dict)
    for module_type in MODULE_TYPES:
        module_dir = Path(cfg['general']['modules_dir'][module_type])
        sys.path.append(str(module_dir.resolve()))
        for name in sorted(required[module_type]):
            if not (module_dir / (name + '.py')).is_file():
                raise FileNotFoundError('Missing %s module: %s' % (module_type, name))
            modules[module_type][name] = importlib.import_module(name).instance(cfg)
    return modules
