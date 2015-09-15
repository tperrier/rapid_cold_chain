# CCEM Parser
The CCEM Parser is responsible for parsing incoming messages based on the CCEM SMS Reporting syntax. 
* The Parser is initialized with a list of classes inheriting from util.Keyword
* Calling parser(msg,pos) will attempt to parse a message starting at position.

## SMS Parser Specification

### General Specification
+ Messages are a concatenation of OPCODE/Argument pairs
+ For some OPCODES multiple OPCODES can appear in the same message
+ Some OPCODES cannot be in the same message with others
+ An OPCODE must be followed by at least one argument
+ All capitalization is ignored
+ A configurable list of characters should also be ignored
    + This defaults to [\s;,;+-] (Whitespace plus a few special chars)

### Symbols
The following is a definition of symbols in the grammar and their equivalent regular expressions

+ *label*: [a-z]
+ *integer*: \d+
+ *opcode*: [a-z]{2}
+ *alarms*:  \d\d | 0
+ *fridge*: label  alarms
+ *stock*: label integer

### Laos CCEI Message Syntax
There are five groups of messages.  Multiple opcodes can appear in the same message only if the are from the same group. However, the *All* group can be in a message with any other opcode.  Each opcode in the in the *Periodic Reports* and *Information* groups may only occur once e.g. *ft a 11 ft b 22* is an invalid message.

#### Periodic Reports
These OPCODES are for monthly reporting

* Fridge Tag
    - opcode: *ft*
    - arguments: *alarms* | *fridge*+
* Stock Level
    - opcode: *sl*
    - arguments: *stock*+

#### Spontaneous Reports
These OPCODES are for reporting the occurrence of events

* Stock Out
    - opcode: *so*
    - arguments: *label* 
* Fridge Failure
    - opcode: *nf*
    - arguments: *label*
* Fridge Repair
    - opcode: *wo*
    - arguments: *label*

#### Administration and Management
These OPCODES are for basic administration

* Registrar
    - opcode: *rg*
    - arguments: *\d[8]* | *\d[4]-\d[4]* | *\+\d[13]*  (Phone Number)
* Preferred Language
    - opcode: *pl*
    - arguments: *\d*  (1: English, 2: Karoake, 3: Lao)

#### Information
* Help 
    - opcode: *he*
    - arguments: *opcode*

#### All
* Facility Code
    - opcode: *fc*
    - arguments: \d* (facility_code)

### Currently Supported
Our initial roll out only had monthly alarms and stock reporting so the ft and sl opcodes were removed. For backwards compatibility in the Laos deployment we are supporting special edge cases where no opcode appears at the front of a message.

We also have only implemented the ft and sl opcodes. Here is a list of the current grammar:

+ ft *alarms* | *fridge+* sl *stock+*
+ *alarms* sl? *stock+*
+ *fridge+* sl *stock+*

Notes: 

+ Currently ft must be followed by sl. We should parse messages with sl preceded by ft.
+ If a message does not start with ft and there is a single fridge the sl opcode is optional
+ If a message starts with ft - even if there is a single fridge - the sl opcode is required

