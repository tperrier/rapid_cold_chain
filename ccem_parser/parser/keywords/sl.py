#!/usr/bin/python
import re,code
from .. import utils
from ..utils import _

class sl(utils.Keyword):
	
	def parse(self,msg,pos=0):
		self.reset(pos=pos+len(self.kw))
		while utils.Tokens.singleletter(msg,self.pos): 
				self.label = msg[self.pos]
				self.pos += 1
				self.parse_stock(msg)
		return self.args,self.pos
		
	def parse_stock(self,msg):
		
		m,self.pos = utils.gobble('\d+',msg,self.pos)
		if not m:
			raise utils.InvalidStockError(msg[self.pos])
		else:
			self.args[self.label] = m.group(0)
			
	def reset(self,pos=0):
		self.pos = pos
		self.args = {}
		self.label = None
		
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	test_messages = [
		'slp50',
		'slp50q50',
		'slpp0',
	]
	
	parser = sl()

	print 'Start: ',parser.name,parser.kw
	for m in test_messages:
		try:
			print m,parser.parse(m,0)
		except utils.ParseError as e:
			print e
