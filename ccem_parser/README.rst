# CCEM Parser
The CCEM Parser is responsible for parsing incoming messages based on the CCEM SMS Reporting syntax. 
* The Parser is initialized with a list of classes inheriting from util.Keyword
* Calling parser(msg,pos) will attempt to parse a message starting at position.
