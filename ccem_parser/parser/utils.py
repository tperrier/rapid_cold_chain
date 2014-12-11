import re,sys

try: #try to set up django translation if available
	from django.conf import settings
	from django.core.exceptions import ImproperlyConfigured
	settings.USE_I18N
	from django.utils.translation import  ugettext_lazy as _
except (ImportError, ImproperlyConfigured):
	#otherwise define our own fake i18n translation
	def _(s):
		return s

class Tokens:
	'''
	Regular expression tokens available for easy accesss
	'''
	integer = re.compile("\d+").match
	whitespace = re.compile("\s+").match
	singleletter = re.compile("[a-z](?:[^a-z]|$)").match
	startsletter = re.compile("[a-z]").match
	singledigit = re.compile("\d").match
	variable = re.compile("[a-z]+").match

	
class Keyword(object):
	'''
	All parser keywords should inherit from the utils.Keyword class	
	'''
	
	'''
	By default a keyword only return args for one keyword
	Set multiple to True if multiple keywords will be returned
	Formate:
	 {keyword1:[*args],
	  keyword2: [*args]
	  }
	'''
	multiple = False
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
		'''
		Given the args for this keyword return a response message
		'''
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
		'''
		Returns a lazzy i18n object that can be compiled in the users language.
		'''
		if len(self.commands) == 0:
			return _('No commands found')+'\n'
		msg = _('Thanks. Message successfully submitted.')+'\n'
		
		for kw,args in self.commands.iteritems():
			msg += self.__class__.get_kw_msg(kw,args)+''
			
		return msg

	@classmethod
	def get_kw_msg(cls,kw,args):
		'''
		Keyword Models should declare a get_msg function that takes parsed arguments
		and returns a lazzy i18n object.
		'''
		from keywords import KEYWORDS
		try:
			kw_cls = [k for k in KEYWORDS if k.__name__ == kw][0]
		except IndexError as e:
			#Translators: keyword is our name for ft or sl ect.
			return _('Keyword %s'%kw)
		else:
			return kw_cls.get_msg(args)
			

class ParseError(Exception):
	
	#Translators: This is the default error message
	message = _('There was an error in report format. Please Try again.')
	
	def __init__(self,message=None):
		if message:
			self.message = message
			
	def __str__(self):
		return unicode(self.message)
	
class SingleArgParseError(ParseError):
	
	def __init__(self,arg,template=None):
		self.arg = arg
		if template:
			self.template = template
		
	@property
	def message(self):
		return self.template % (self.arg,)

class NoKeywordError(ParseError):
	message = _('Sorry, we did not find a keyword in your message. A moderator is reviewing it.')
	
class NoVaccineFoundError(ParseError):
	message = _('No vaccine lable found')
	
class UnexpectedCharError(SingleArgParseError):
	template = _('Unexpected Character %s')
	
class MultipleKeyWordError(SingleArgParseError):
	template = _('Duplicate Keyword: %s already present')

class InvalidAlarmsError(SingleArgParseError):
	template = _('Invalid alarm value \'%s\'. Must be a digit')
	
class NoStockFoundError(SingleArgParseError):
	template = _('No Value For Stock %s Found')

class InvalidStockError(SingleArgParseError):
	template = _('Invalid Stock value \'%s\', must be a digit')

class gobbler(object):
	'''
	Class that compares a regx to the given string and advances the match position
	forward if a match is found.
	'''
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
