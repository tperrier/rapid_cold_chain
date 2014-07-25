#!/usr/bin/python
import re,code
from .. import utils
from ..utils import _

class sl(utils.Keyword):
	
	def parse(self,msg,pos=0):
		pos += len(self.kw)
		return self.__class__.parse_stock(msg,pos)
	
	@classmethod
	def parse_stock(cls,stock,pos=0):
		args = {}
		while utils.Tokens.singleletter(stock,pos):
			label = stock[pos]
			pos += 1 #jump over stock label 
			m,pos = utils.gobble('\d+',stock,pos)
			if not m:
				raise utils.InvalidStockError(stock[pos])
			else:
				args[label] = m.group(0)
		return args,pos
				
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	test_messages = [
		'slp50',
		'slp50q50',
		'slp{0',
	]
	
	parser = sl()

	print 'Start: ',parser.name,parser.kw
	for m in test_messages:
		try:
			print m,parser.parse(m,0)
		except utils.ParseError as e:
			print e
