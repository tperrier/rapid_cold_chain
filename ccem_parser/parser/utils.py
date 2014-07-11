import re

class Tokens:
	'''
	Regular expression tokens available for easy accesss
	'''
	integer = re.compile("\d+").match
	whitespace = re.compile("\s+").match
	singleletter = re.compile("[a-z]").match
	singledigit = re.compile("\d").match
	variable = re.compile("[a-z]+").match

	
class Keyword(object):
	'''
	All parser keywords should inherit from the utils.Keyword class	
	'''

	def __init__(self):
		#If the subclass has not set a kw property set one based on the class name
		if not hasattr(self,'kw'):
			self.kw = self.__class__.__name__
		#If the subclass has not set a name property set one based on the class name
		if not hasattr(self,'name'):
			self.name = self.__class__.__name__
		#create a regular expression object from the kw property
		self.reg = re.compile(self.kw)
		
	def parse():
		'''
		Subclasses shouls implement a custom version of parse
		parse(msg,pos=0)
			msg: The message string to parse
			pos: The possition in the string to start parsing
		return:
			args: dictionary of arguments found while parsing
			erros: list of errors found while parsing
			pos: the new position based on the end of parsing	
		'''
		pass
		
	def test(self,s,pos=0):
		return self.reg.match(s,pos)
		
class ParseResult(dict):
	
	def __init__(self,cleaned='',commands=None,errors=None):
		if commands is None:
			commands = {}
		if errors is None:
			errors = []
		self.cleaned = cleaned
		self['commands'] = commands
		self['errors'] = errors
		
	@property
	def commands(self):
		return self['commands']
		
	@property
	def errors(self):
		return self['errors']
		
	@property
	def has_error():
		return len(self['errors']) > 0
		
	def add(self,kw,args,error):
		self.arg(kw,args)
		self.error(error)
		
	def arg(self,kw,args):
		if not isinstance(kw,basestring):
			kw = kw.name #passed a keyword object in
		if kw not in self['commands']:
			self.commands[kw] = args
		else:
			self.errors.append('MULTIPLE_KEYWORD')
		
	def error(self,error):
		if error:
			self.errors.append(error)

class gobbler(object):
	
	def __init__(self,regx):
		self.regx = re.compile(regx)
		
	def gobble(self,s,pos):
		m = self.regx.match(s,pos)
		if not m:
			return m,pos
		return m,m.end()+pos
		
	def test(self,s,pos):
		return self.regx.match(s,pos)

def gobble(reg,s,pos):
	m = re.match(reg,s[pos:])
	if not m:
		return m,pos
	return m,m.end()+pos
