#!/usr/bin/python
import logging, code
from rapidsms.apps.base import AppBase
from parser import default_parser as parser, utils
import django_ccem.models as ccem

logger = logging.getLogger(__name__)

class CCEIParser(AppBase):
	
	@classmethod
	def _log(cls,direction,msg):
		'''
		Return an unsaved Message object
		'''
		if not msg.connection:
			raise ValueError
		return ccem.Message(
			direction=direction,
			text=msg.raw_text,
			connection=msg.connection,
		)
	
	def filter(self, msg):
		#tnp: Moved from rapidsms.contrib.messaglog.app
		# annotate the message as we log them in case any other apps
		# want a handle to them
		
		msg.ccem_msg = self.__class__._log(ccem.Message.INCOMING,msg)
	
	def parse(self,msg):
		'''
		The RapidSMS parse phase: pass the message through the ccem_parser
		Attach result as ccem_parsed
		'''
		#logger.debug('CCEIParser: %s',msg.raw_text)
		try:
			msg.ccem_parsed = parser.parse(msg.text)
		except utils.ParseError as e:
			msg.ccem_error =  e
			msg.ccem_parsed = parser.parse(msg.text,fake=True)
		else:
			msg.ccem_error = None
			
		#save msg.ccem_msg with data from parsed message
		msg.ccem_msg.is_submission = False if isinstance(msg.ccem_error,utils.NoKeywordError) else True
		if msg.ccem_msg.is_submission:
			msg.ccem_msg.cleaned = msg.ccem_parsed.cleaned # only add cleaned if submission
		msg.ccem_msg.save()
		
	def handle(self,msg):
		
		#Do not handle if this is not a submission message
		if not msg.ccem_msg.is_submission:
			return False
		
		#The message looks like a report submission. So generate report.
		report = ccem.Report.from_msg(msg)
		if not msg.ccem_error: #No other errors
			response = msg.respond(str(msg.ccem_parsed)))
		else: #there were errors
			response = msg.respond(str(msg.ccem_error))
		return True
		
	def outgoing(self, msg):
		#tnp: Moved from rapidsms.contrib.messaglog.app
		msg.ccem_msg = self.__class__._log(ccem.Message.OUTGOING,msg)
		msg.ccem_msg.save()
		
		#add to correct CCEM Report if it exists
		msg.ccem_report = ccem.Report.add_latest_response(msg)
		
		#logger.debug('CCEI Outgoing: %s',msg.raw_text)
