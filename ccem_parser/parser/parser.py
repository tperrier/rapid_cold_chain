#!/usr/bin/python
import abc,re,code
from . import utils

MSG_REMOVE_CHARS = r'[\s]'

class Parser:
	
	remove_chars = re.compile(MSG_REMOVE_CHARS)
	
	def __init__(self,*args):
		if len(args) == 0:
			self.keywords = _auto_discovery()
		else:
			self.keywords = args
	
	def __call__(self,msg,pos=0):
		self.parse(msg,pos)
	
	def parse(self,msg,pos=0):
		msg = self.clean(msg)
		msg_report = utils.ParseResult(msg)
		while True:
			kw,args,errors,pos = self._parse(msg,pos)
			if kw is not None:
				if kw.name != 'short':
					msg_report.add(kw,args,errors)
				else:
					msg_report.add('ft',args[0],None)
					msg_report.add('sl',args[1],errors)
				if errors:
					self.pos = len(msg) #finish parsing
					break
			else:
				break
		if pos == 0: #no keyword found
			msg_report.error('NO_KEYWORD_FOUND')
		elif pos < len(msg):
			msg_report.error('INVALID_NEXT_KEYWORD')
		return msg_report
		
	def _parse(self,s,pos):
		for kw in self.keywords:
			 if kw.test(s,pos):
				 args,errors,pos = kw.parse(s,pos)
				 return kw,args,errors,pos
		return None,None,None,pos
				 
	def clean(self,s):
		s = s.lower()
		return self.remove_chars.sub('',s)
		
def _auto_discovery():
	from keywords import KEYWORDS
	return [kw() for kw in KEYWORDS]
		
		
if __name__ == '__main__':
	'''
	Basic Testing
	'''
	
	test_messages = [
		'FT a0 0 b00 sl p 1000d500',
		'fta000slp1000',
		'00slp111d222',
		'00slp111d222a',
		'ft   a00b11slp111d222',
		'hello how are you?',
	]
	parser = Parser()
	
	for m in test_messages:
		print m,parser.parse(m)
		
	code.interact(local=locals())
