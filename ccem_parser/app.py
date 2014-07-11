#!/usr/bin/python
import logging, code
from rapidsms.apps.base import AppBase
from parser import default_parser as parser
import messagelog as mlog 
import django_ccem.models as ccem

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
		
		#create CCEM Message and append to msg
		msg.ccem = ccem.Message.from_msg(msg,parsed)
		
		if 'NO_KEYWORD_FOUND' in parsed.errors: #ERROR CODE
			return False
		
		#The message looks like a report submission. So generate report.
		report = ccem.Report.from_ccem(msg.ccem,parsed)
		if not parsed.errors: #Not other errors
			response = msg.respond(str(parsed.commands))
		else: #there were errors
			response = msg.respond(str(parsed.errors))
		return True
		
	def outgoing(self, msg):
		#tnp: Moved from rapidsms.contrib.messaglog.app
		msg.logger_msg = mlog.app.MessageLogApp._log(mlog.models.Message.OUTGOING, msg)
		
		#create CCEM Report
		msg.ccem = ccem.Report.add_latest_response(msg)
		print 'OUTGOING'
