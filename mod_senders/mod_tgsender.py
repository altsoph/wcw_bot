import logging
from proto_sender import * 
import time
import io
from PIL import Image
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

class instance(proto_sender):
    updater = None
    retries_num = None
    retries_pause = None
    def __init__(self,cfg):
        # print(cfg['secrets']['tgsender']['BOT_KEY'])
        self.updater = Updater(cfg['secrets']['tgsender']['BOT_KEY'])
        # print(updater)
        self.retries_num = cfg['general']['sender']['retries_num']
        self.retries_pause = cfg['general']['sender']['retries_pause']
        super().__init__(cfg)

    def get(self, img, annot, target, parameters=None):
        logging.debug('Module "%s" activated.', __name__)
        img = Image.fromarray(img)
        pic_out = io.BytesIO()
        pic_out.name = 'image.jpeg'
        img.save(pic_out, 'JPEG')
        # print(pic_out)
        pic_out.seek(0)
        # print(pic_out)
        retries_num = self.retries_num
        retries_pause = self.retries_pause
        if target and 'retries_num' in target: retries_num = target['retries_num']
        if target and 'retries_pause' in target: retries_pause = target['retries_pause']

        for attempt in range(retries_num):
            try:
                self.updater.bot.send_photo(target['id'], photo=pic_out, caption=annot, parse_mode='Markdown')
                break
            except:
                logging.warning('Module "%s": tg connection error, retry.', __name__)
                time.sleep(retries_pause)
