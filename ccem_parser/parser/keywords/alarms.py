#!/usr/bin/python
import re,code
from .. import utils
from ..utils import _

fridge = utils.gobbler(r'[a-z]\d{1,2}')
'''
Fridge Tag Related Keywords:
	ft: monthly fridge tag report 
	uh: unresoved hot alarm
	uc: unresoved cold alarm
	rt: replace fridge tag
'''

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
	'''
	Fridge Tag Alarm Keyword Class.
	Valid Format: ft \d\d  or ft ([a-z]\d\d)*
	'''
	
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
		out = _('Fridge')
		for label,alarms in args.iteritems():
			out += u' %s: (%s %s %s %s)'%(label if label is not None else '',alarms[0],_('high'),alarms[1],_('low'))
		return out+'\n'
		
class keyword_fridge(utils.Keyword):
	'''
	Unresoved Hot or Cold Alarms Keyword Class
	Valid Formats: kw or kw [a-z]
	'''
	
	def parse(self,msg,pos=0):
		pos += len(self.kw)

		letter = utils.Tokens.singleletter(msg,pos)
		
		if not letter:
			return None,pos
			
		fridge_letter = letter.group(0)
		return fridge_letter,pos+len(fridge_letter)
		
class uh(keyword_fridge):
	'''
	Unresolved Hot Alarms
	'''
	@classmethod
	def get_msg(cls,args):
		out = _('Hot Alarm')
		return out + ': %s'%args
	
class uc(keyword_fridge):
	'''
	Unresolved Cold Alarms
	'''
	@classmethod
	def get_msg(cls,args):
		out = _('Cold Alarm')
		return out + ': %s'%args
	
class rt(keyword_fridge):
	'''
	Replace Tag: fridge tag needs to be replaced 
	'''
	@classmethod
	def get_msg(cls,args):
		out = _('Replace')
		return out + ': %s'%args
	
class nf(keyword_fridge):
	'''
	Equipment Not Functioning
	'''
	@classmethod
	def get_msg(cls,args):
		out = _('Not Functioning')
		return out + ': %s'%args
	
class ok(keyword_fridge):
	'''
	Equipment OK
	'''
	@classmethod
	def get_msg(cls,args):
		out = _('OK')
		return out + ': %s'%args
		
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	
	'''
	test_messages = [
		'ft0',
		'ft00',
		'fta0b00',
		'fta0bb',
		'ft',
		'ft*',
	]
	'''
	
	test_messages = [
		'uh',
		'uha',
		'uhb',
		'uhuf',
	]
	
	parser = uh()

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
		
