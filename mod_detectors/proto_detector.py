import logging

class proto_detector(object):
	main_cfg = None
	def __init__(self,cfg):
		self.main_cfg = cfg
	def get(self, img):
		"""
		gets a PIL Image
		returns detected tags with areas and probs
		returns None on any error or if nothing was detected
		"""
		pass
