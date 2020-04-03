# Old version
Old script of the project that can still be useful in the future.

## What's in it ?

### FakeSerial.py
Old version of the ```FakeSerial_V2.py``` where instructions other than ping have been developped in the write() function.
This script fake the Serialport and is called by the Nanomodem.

### main.py
Script to launch ```TestClass.py```

### TestClass.py
Class used to test the different function of the FakeModem. 
It is not used for now, but will help us to create the next UnitTest.

### test1.py
First version of the .py simulation with ```GenericMessage```.
That's where we encountered the issue of the GenericMessage that need to be sended twice.
The first ```GenericMessage``` will not be recognised by UnetStack. We still don't know why.
