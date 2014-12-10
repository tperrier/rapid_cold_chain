#!/usr/bin/python
import re,code
from .. import utils
from ..utils import _

facility_code = utils.gobbler(r'\d*')


class hc(utils.Keyword):
	
	def parse(self,msg,pos=0):
		pos += len(self.kw)
		
		if len(msg) == pos:
			raise utils.ParseError(_('No Health Facility Given'))
		
		hc_code,pos = facility_code.gobble(msg,pos)
		
		if not hc_code:
			raise utils.ParseError(_('Facility Code Is Numeric'))
			
		hc_code = hc_code.group(0)
		
		if len(hc_code) < 6:
			raise utils.ParseError(_('Facility Code To Short'))
		if len(hc_code) >6:
			raise utils.ParseError(_('Facility Code To Long'))
			
		return hc_code,pos
	
	@classmethod
	def get_msg(cls,args):
		out = _('Health Facility')
		return out+': '+str(args)
		
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	test_messages = [
		'hc010101',
		'hc020202',
		'hc030303',
		'hc01010',
		'hc0101010101',
		'hc',
		'hi',
	]
	
	parser = hc()

	print 'Start: ',parser.name,parser.kw
	for m in test_messages:
		if not parser.test(m):
			print m,'Does not match'
		else:
			try:
				args,pos = parser.parse(m)
			except utils.ParseError as e:
				print m,e
			else:
				print m,args,m[pos:]
		
