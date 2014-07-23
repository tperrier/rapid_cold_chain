#!/usr/bin/python
import logging, code
from rapidsms.apps.base import AppBase
from parser import default_parser as parser, utils
import messagelog as mlog 
import django_ccem.models as ccem

logger = logging.getLogger(__name__)

class CCEIParser(AppBase):
	
	def filter(self, msg):
		#tnp: Moved from rapidsms.contrib.messaglog.app
		# annotate the message as we log them in case any other apps
		# want a handle to them
		
		msg.logger_msg =  mlog.app.MessageLogApp._log(mlog.models.Message.INCOMING, msg)
	
	def parse(self,msg):
		'''
		The RapidSMS parse phase: pass the message through the ccem_parser
		Attach result as ccem_parsed
		'''
		logger.debug('CCEIParser: %s',msg.raw_text)
		try:
			msg.ccem_parsed = parser.parse(msg.text)
		except utils.ParseError as e:
			msg.ccem_error =  e
			msg.ccem_parsed = parser.parse(msg.text,fake=True)
		else:
			msg.ccem_error = False
		
	
	def handle(self,msg):
		
		#create CCEM Message and append to msg
		msg.ccem = ccem.Message.from_msg(msg)
		
		if isinstance(msg.ccem_error,utils.NoKeywordError):
			return False
		
		#The message looks like a report submission. So generate report.
		report = ccem.Report.from_msg(msg)
		if not msg.ccem_error: #No other errors
			response = msg.respond(str(msg.ccem_parsed.commands))
		else: #there were errors
			response = msg.respond(str(msg.ccem_error))
		return True
		
	def outgoing(self, msg):
		#tnp: Moved from rapidsms.contrib.messaglog.app
		msg.logger_msg = mlog.app.MessageLogApp._log(mlog.models.Message.OUTGOING, msg)
		
		#create CCEM Report
		msg.ccem = ccem.Report.add_latest_response(msg)
		
		logger.debug('CCEI Outgoing: %s',msg.raw_text)
