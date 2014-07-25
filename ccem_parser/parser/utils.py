import re,sys

#from django.utils.translation import ugettext_lazy as _

def _(s): #fake i18n translation
	return s

class Tokens:
	'''
	Regular expression tokens available for easy accesss
	'''
	integer = re.compile("\d+").match
	whitespace = re.compile("\s+").match
	singleletter = re.compile("[a-z][^a-z]").match
	singledigit = re.compile("\d").match
	variable = re.compile("[a-z]+").match

	
class Keyword(object):
	'''
	All parser keywords should inherit from the utils.Keyword class	
	'''
	
	multiple = False #by default a keyword only return args for one keyword
	repeat = False #by default a keyword can not repeat

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
			pos: the new position based on the end of parsing	
		'''
		raise NotImplementedError('Keyword subclass should override keyword.parse')
		
	def test(self,s,pos=0):
		return self.reg.match(s,pos)
		
	@classmethod
	def get_msg(cls,args):
		return '%s: %s'%(cls.__name__,str(args))
		
class ParseResult(object):
	
	def __init__(self,cleaned='',commands=None):
		if commands is None:
			commands = {}
		self.cleaned = cleaned
		self.commands = commands
		
	def add(self,kw,args):
		if not isinstance(kw,basestring):
			kw = kw.name #passed a keyword object in
		if kw not in self.commands:
			self.commands[kw] = args
		else:
			raise MultipleKeywordError(kw)
			
	def __repr__(self):
		return repr(self.commands)
		
	def __str__(self):
		if len(self.commands) == 0:
			return _('No commands found')
		msg = _('Message successfully parsed: Found:')
		
		for kw,args in self.commands.iteritems():
			msg += self.__class__.get_kw_msg(kw,args)
			
		return msg

	@classmethod
	def get_kw_msg(cls,kw,args):
		module = 'ccem_parser.parser.keywords.%s'%kw
		print module
		try:
			__import__(module)
		except ImportError:
			return _('Keyword %s'%kw)
		else:
			kw_cls = sys.modules[module]
			return getattr(kw_cls,kw).get_msg(args)
			

class ParseError(Exception):
	
	message = _('There was an error in report format. Please Try again.')
	
	def __init__(self,message=None):
		if message:
			self.message = message
			
	def __str__(self):
		return self.message
	
class SingleArgParseError(ParseError):
	
	def __init__(self,arg,message=None):
		self.arg = arg
		if message:
			self.message = message
		
	@property
	def message(self):
		return self.template % (self.arg,)

class NoKeywordError(ParseError):
	message = _('No Keyword Found')
	
class MultipleKeyWordError(SingleArgParseError):
	template = _('Keyword %s already present')

class InvalidAlarmsError(SingleArgParseError):
	template = _('Invalid alarm value \'%s\'. Must be a digit')

class InvalidStockError(SingleArgParseError):
	template = _('Invalid Stock value \'%s\', must be a digit')

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
