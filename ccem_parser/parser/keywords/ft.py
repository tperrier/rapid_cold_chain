#!/usr/bin/python
import re,code
from .. import utils
from ..utils import _

fridge = utils.gobbler(r'[a-z]\d{1,2}')

def parse_alarms(alarms,pos=0):
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
	
def parse_multiple_alarms(alarms,pos=0):
	args = {}
	while utils.Tokens.singleletter(alarms,pos):
		label = alarms[pos]
		pos += 1
		args[label],pos = parse_alarms(alarms,pos)
	
	if len(args) == 0:
		raise utils.ParseError(_('No Alarms Found'))
	
	return args,pos

class ft(utils.Keyword):
	
	def parse(self,msg,pos=0):
		pos += len(self.kw)
		
		if len(msg) == pos:
			raise utils.ParseError(_('No Alarms Found'))
		
		if not utils.Tokens.singleletter(msg,pos): #single fridge with no letter
			alarms,pos = parse_alarms(msg,pos)
			args = {None:alarms}
		else: #fridge with letter
			args,pos = parse_multiple_alarms(msg,pos)
		return args,pos
	
	@classmethod
	def get_msg(cls,args):
		out = u' %s [ '%_('Fridge')
		for label,alarms in args.iteritems():
			out += '( %s%s%s ) '%(label if label is not None else '',alarms[0],alarms[1])
		return out + ']'
		
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
		
