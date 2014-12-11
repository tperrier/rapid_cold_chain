#!/usr/bin/python
import re,code
from .. import utils
from ..utils import _

vaccine_map = {
	'p':'PCV',
	'd':'Penta',
}

def parse_stock(stock,pos=0):
		args = {}
		while utils.Tokens.singleletter(stock,pos):
			label = stock[pos]
			pos += 1 #jump over stock label 
			m,pos = utils.gobble('\d+',stock,pos)
			if not m:
				try:
					raise utils.InvalidStockError(stock[pos])
				except IndexError as e:
					raise utils.NoStockFoundError(label)
			else:
				args[label] = m.group(0)
		return args,pos

class sl(utils.Keyword):
	'''
	Stock Level Report sl (vaccine_label stock)+
	'''
	
	def parse(self,msg,pos=0):
		pos += len(self.kw)
		if pos == len(msg):
			raise utils.NoVaccineFoundError()
		return parse_stock(msg,pos)
	
	@classmethod
	def get_msg(cls,args):
		out = _('Stock')
		for label,count in args.iteritems():
			if label in vaccine_map:
				label = vaccine_map[label]
			out += u' %s (%s)'%(label,count)
		return out+'\n'

class so(utils.Keyword):
	'''
	Stock Out Event: so [a-z]
	'''
	
	def parse(self,msg,pos=0):
		pos += len(self.kw)
		
		letter = utils.Tokens.startsletter(msg,pos)
		
		if not letter:
			raise utils.ParseError(_('Stock Out Error: No Vaccine Label'))
			
		letter = letter.group(0)
		return letter,pos+1
	
	@classmethod
	def get_msg(cls,args):
		out = _('Stock Out')
		args = vaccine_map[args] if args in vaccine_map else args
		return out + ': %s'%args
		
		
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
