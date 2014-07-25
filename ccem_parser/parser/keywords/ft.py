#!/usr/bin/python
import re,code
from .. import utils
from ..utils import _

fridge = utils.gobbler(r'[a-z]\d{1,2}')

class ft(utils.Keyword):
	
	def parse(self,msg,pos=0):
		pos += len(self.kw)
		
		if len(msg) == pos:
			raise utils.ParseError(_('No Alarms Found'))
		
		if not utils.Tokens.singleletter(msg,pos): #single fridge with no letter
			alarms,pos = self.__class__.parse_alarms(msg,pos)
			args = {None:alarms}
		else: #fridge with letter
			args,pos = self.__class__.parse_multiple_alarms(msg,pos)
		return args,pos
		
	@classmethod
	def parse_alarms(cls,alarms,pos=0):
		match,pos = utils.gobble('\d{1,2}',alarms,pos) #gobble 1 or 2 digits
		if not match:
			raise utils.InvalidAlarmsError(alarms[pos])
		alarms = match.group(0)
		high = alarms[0]
		try:
			low = alarms[1]
		except IndexError as e:
			low = high
		return (high,low),pos
		
	@classmethod
	def parse_multiple_alarms(cls,alarms,pos=0):
		args = {}
		while utils.Tokens.singleletter(alarms,pos):
			label = alarms[pos]
			pos += 1
			args[label],pos = cls.parse_alarms(alarms,pos)
		
		if len(args) == 0:
			raise utils.ParseError(_('No Alarms Found'))
		
		return args,pos
		
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	test_messages = [
		'ft0',
		'ft00',
		'fta0b00',
		'fta0bb',
		'ft',
		'ft*',
	]
	
	parser = ft()

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
		
