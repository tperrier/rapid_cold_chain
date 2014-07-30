#!/usr/bin/python
import re, code
from .. import utils
import ft,sl


class short(utils.Keyword):
	
	'''
	The short keyword is a hack for accepting messages of the following format
		- fridge_alarms
		- fridge_alarms stock+
		- stock+
	'''
	
	kw = '^\d{1,2}|^\d{0,2}([a-z]\d+)+'
	name = 'short'
	multiple = True
	parser = re.compile('(\d)?(\d)?(([a-z]\d+)*)')
	
	def parse(self,msg,pos=0):
		match = self.parser.match(msg)
		high,low,stock,last = match.groups()
		args = {}
		if stock and not high:
			#no alarms so stock is really multiple fridge alarms
			args['ft'],pos = ft.parse_multiple_alarms(stock)
		elif stock:
			stock,pos = sl.parse_stock(stock)
			if stock:
				args['sl'] = stock
		if high:
			pos += 1
			if not low:
				low = high
			else:
				pos += 1
			args['ft'] = {None:(high,low)}
		return args,pos
		
	
	
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	
	test_messages = [
		'0',
		'02',
		'03p100',
		'02b100p100',
		'20slp0',
		'1slp1000',
		'2slp11d22',
		'3slp11d22',
		'p11d22',
		'a11b22slp1000',
		'slp11d22a',
		'ft3slp11d22a',
		'ft3slp11d22aa',
		'*0',
		'0p10O0',
		'0p!0O0',
	]
	
	
	parser = short()
	
	print 'Start: ',parser.name,parser.kw
	for m in test_messages:
		if not parser.test(m):
			print m,'Does not match'
		else:
			args,pos = parser.parse(m)
			print m,args,m[pos:]
