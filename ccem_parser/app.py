#!/usr/bin/python
import logging
from rapidsms.apps.base import AppBase
from parser import default_parser as parser

logger = logging.getLogger(__name__)

class CCEIParser(AppBase):
	
	def handle(self,msg):
		logger.debug('CCEIParser: %s',msg.raw_text)
		parsed = parser.parse(msg.text)
		if 'NO_KEYWORD_FOUND' in parsed.errors:
			return False
		msg.respond(str(parsed.commands))
		return True
		
