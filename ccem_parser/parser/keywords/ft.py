#!/usr/bin/python
import re,code
from .. import utils
from ..utils import _

fridge = utils.gobbler(r'[a-z]\d{1,2}')

class ft(utils.Keyword):
	
	def parse(self,msg,pos=0):
		self.reset(pos=pos+len(self.kw))
		if len(msg) == self.pos:
			raise utils.ParseError(_('No Alarms Found'))
		if not utils.Tokens.singleletter(msg,self.pos): #single fridge with no letter
			self.parse_alarms(msg)
		else: #fridge with letter
			while utils.Tokens.singleletter(msg,self.pos): 
				self.label = msg[self.pos]
				self.pos += 1
				self.parse_alarms(msg)
		if len(self.args) == 0:
			raise utils.ParseError(_('No Alarms Found'))
		return self.args,self.pos
				
	def parse_alarms(self,string):
		alarms,self.pos = utils.gobble('\d{1,2}',string,self.pos) #gobble 1 or 2 digits
		if not alarms:
			raise utils.InvalidAlarmsError(string[self.pos])
		alarm_string = alarms.group(0)
		if len(alarm_string) == 1:
			alarms = (alarm_string[0],alarm_string[0])
		else:
			alarms = (alarm_string[0],alarm_string[1])
		self.args[self.label] = alarms
		
	def reset(self,pos=0):
		self.pos = pos
		self.args = {}
		self.label = None
		
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	test_messages = [
		'FT0',
		'FT00',
		'FTa0b00',
		'FT',
		'FTa0bb',
	]
	
	parser = ft()

	print 'Start: ',parser.name,parser.kw
	for m in test_messages:
		try:
			print m,parser.parse(m,0)
		except utils.ParseError as e:
			print e
		
	code.interact(local=locals())
