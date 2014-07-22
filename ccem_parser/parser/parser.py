#!/usr/bin/python
import re,code
import utils
from utils import _

#Regular Expression of characters to be removed when cleaning messages
MSG_REMOVE_CHARS = r'[\s]'

class Parser:
	
	remove_chars = re.compile(MSG_REMOVE_CHARS)
	
	def __init__(self,*args):
		'''
		Set the list of keywords based on keyword argument if present
		or _auto_discovery() if not
		'''
		if len(args) == 0:
			self.keywords = _auto_discovery()
		else:
			self.keywords = args
	
	def __call__(self,msg,pos=0):
		'''
		Make the parser object callable so my_parser() is equivalent to my_parser.parse()
		''' 
		self.parse(msg,pos)
	
	def parse(self,msg,pos=0):
		'''
		The main parsing function: Raises ParseError if an error was found
		'''
		# Clean Message and create report object
		msg = self.clean(msg)
		msg_report = utils.ParseResult(msg)
		while True:
			#Attempt to parse message keywords at currrent possition 
			#kw = returned keyword
			#args = dict of args for keyword
			#pos = new position = old position + length parsed string
			kw,args,pos = self._parse(msg,pos)
			if kw is not None:
				if kw.name != 'short':  #the short kw is a special case and returns both an ft and sl.
							#this can probably be made more elegant
					msg_report.add(kw,args)
				else:
					msg_report.add('ft',args[0])
					msg_report.add('sl',args[1])
			else:
				break
		if pos == 0: #no keyword found
			raise utils.NoKeywordError()
		elif pos < len(msg): # The are unparsed characters left on the message string
			raise utils.ParseError(_('Unexpected Character %s')%(msg[pos],))
		return msg_report
		
	def _parse(self,s,pos):
		'''
		Loop through all keywords in parser and test if they match the current position
		If a match is found use that keywords parse method at the current postion
		'''
		for kw in self.keywords:
			 if kw.test(s,pos):
				 args,pos = kw.parse(s,pos)
				 return kw,args,pos
		return None,None,pos
				 
	def clean(self,s):
		s = s.lower()
		return self.remove_chars.sub('',s)
		
def _auto_discovery():
	'''
	Attempts to load a keyword array from classes in keywords.KEYWORDS
	'''
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
		try:
			print m,parser.parse(m)
		except utils.ParseError as e:
			print e
		
	code.interact(local=locals())
