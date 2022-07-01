## Modbus Client programs using Python-3
* client.py

## Installation:
* sudo pip3 install modbus

## Usage Examples:

### Client:
* from modbus.client import *
* c = Modbus_Client() ...if host = 'localhost'
* c = Modbus_Client(host='HOSTNAME') ...Change HOSTNAME to Server IP address
* c.read() ...To read 10 Input Registers from Address 0
* c.read(FC=3, ADR=10, LEN=8) ...To read 8 Holding Registers from Address 10
* c.write(11,22,333,4444) ...To write Holding Registers from Address 0
* c.write(11,22,333,4444, ADR=10) ...To write Holding Registers from Address 10
* c.write(11,22, FC=15, ADR=10) ...To write Coils from Address 10
* fc() ...To get the supported Function Codes

### Supported Function Codes:
* 1 = Read Coils or Digital Outputs\n\
* 2 = Read Digital Inputs\n\
* 3 = Read Holding Registers\n\
* 4 = Read Input Registers\n\
* 5 = Write Single Coil\n\
* 6 = Write Single Register\n\
* 15 = Write Coils or Digital Outputs\n\
* 16 = Write Holding Registers")


