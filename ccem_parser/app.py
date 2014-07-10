#!/usr/bin/python
import logging
from rapidsms.apps.base import AppBase
from parser import default_parser as parser
import messagelog as mlog 

logger = logging.getLogger(__name__)

class CCEIParser(AppBase):
	
	def filter(self, msg):
		#tnp: Moved from rapidsms.contrib.messaglog.app
		# annotate the message as we log them in case any other apps
		# want a handle to them
		
		msg.logger_msg =  mlog.app.MessageLogApp._log(mlog.models.Message.INCOMING, msg)
	
	def handle(self,msg):
		logger.debug('CCEIParser: %s',msg.raw_text)
		parsed = parser.parse(msg.text)
		if 'NO_KEYWORD_FOUND' in parsed.errors:
			return False
		if not parsed.errors: #Not other errors
			msg.respond(str(parsed.commands))
		else: #there were errors
			msg.respond(str(parsed.errors))
		return True
		
	def outgoing(self, msg):
		#tnp: Moved from rapidsms.contrib.messaglog.app
		msg.logger_msg = mlog.app.MessageLogApp._log(mlog.models.Message.OUTGOING, msg)
