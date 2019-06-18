import logging

class proto_filter(object):
	main_cfg = None
	def __init__(self,cfg):
		self.main_cfg = cfg
	def get(self,tags,confidences,boxes,parameters = None):
		""" 
		gets tags,confidences,boxes
		returns filtered tags,confidences,boxes
		"""
		pass
