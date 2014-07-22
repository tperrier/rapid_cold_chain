#!/usr/bin/python
import re, code
from .. import utils

class short(utils.Keyword):
	
	kw = '^(\d{1,2}$)|^(\d{1,2})?(sl)?([a-z]\d+)+'
	name = 'short'
	parser = re.compile('^(\d)?(\d)?(sl)?(.*)')
	
	'''
	Currently the short keyword does not parse multiple fridges withouth the ft keyword.
	This code might be helpful in fixing that.  The short keyword should basically be
	our current parser but return the apporperiate data structure.
	#hack for O -> 0 if at begining
		if msg.startswith('O'):
			msg = '0'+msg[1:]
		
		self.fridges = {}
		self.vaccines = {}
		self.pos = pos
		self.label = None
		
		if msg[0].isdigit(): #assume single fridge
			self.parser_alarms(msg)
		else: #assume multiple fridges
			while fridge.test(msg,self.pos): 
				self.label = msg[self.pos]
				self.pos += 1
				self.parse_alarms(msg)
				if self.error is not None: #Found an error with alarms
					return self.args,self.error,self.pos
			if self.pos != len(msg): #next token should be sl
				if msg[self.pos:self.pos+1] != 'sl':
					self.error = 'EXPECTED_SL'
					return self.args,self.error,self.pos
				else:
					self.pos += 2 #jump over sl
	'''
	
	def parse(self,msg,pos=0):
		match = self.parser.match(msg)
		high,low,sl,stock = match.groups()
		ft = {None:(high,low)}
		sl = self.parse_stock(stock)
		return (ft,sl),match.end()
		
	def parse_stock(self,stock):
		pos = 0
		args = {}
		error = None
		while utils.Tokens.singleletter(stock,pos):
			label = stock[pos]
			pos += 1
			m,pos = utils.gobble('\d+',stock,pos)
			if not m:
				error = 'INVALID_STOCK'
			else:
				args[label] = m.group(0)
			if error is not None:
				break
		return args,error
	
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	
	test_messages = [
		'0',
		'00',
		'00slp0',
		'1slp1000',
		'0slp11d22',
		'0slp11d22a',
	]
	
	
	parser = short()
	
	for m in test_messages:
		print m,
		print parser.parse(m)
		
	
	code.interact(local=locals())
