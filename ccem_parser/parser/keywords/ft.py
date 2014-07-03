#!/usr/bin/python
import re,code
from .. import utils

fridge = utils.gobbler(r'[a-z]\d{1,2}')

class ft(utils.Keyword):
	
	def parse(self,msg,pos=0):
		self.reset(pos=pos+len(self.kw))
		if not utils.Tokens.singleletter(msg,self.pos): #single fridge with no letter
			self.parse_alarms(msg)
		else: #fridge with letter
			while fridge.test(msg,self.pos): 
				self.label = msg[self.pos]
				self.pos += 1
				self.parse_alarms(msg)
				if self.error is not None:
					return self.args,self.error,self.pos
		if len(self.args) == 0:
			self.error = 'NO_ALARMS'
		return self.args,self.error,self.pos
				
	def parse_alarms(self,string):
		m,self.pos = utils.gobble('\d{1,2}',string,self.pos) #gobble 1 or 2 diggits
		if not m:
			self.error = 'INVALID_ALARMS'
		else:
			alarm_string = m.group(0)
			if len(alarm_string) == 1:
				alarms = (alarm_string[0],alarm_string[0])
			else:
				alarms = (alarm_string[0],alarm_string[1])
			self.args[self.label] = alarms
			
	def reset(self,pos=0):
		self.pos = pos
		self.args = {}
		self.error = None
		self.label = None
		
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	test_messages = [
		'FT0',
		'FT00',
		'FTa0b00',
		'FTaa0',
		'FTa000b00',
	]
	
	parser = ft()

	print 'Start: ',parser.name,parser.kw
	for m in test_messages:
		print m,parser.parse(m,0)
		
	code.interact(local=locals())
