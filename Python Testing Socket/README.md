# Old version
Old script of the project that can still be useful in the future.

## What's in it ?

### FakeSerial.py
Old version of the ```FakeSerial_V2.py``` where instructions other than ping have been developped in the write() function.
This script fake the Serialport and is called by the Nanomodem.

### sim1.groovy
First version of the .groovy simulation with ```GenericMessage```.

### test1.py
First version of the .py simulation with ```GenericMessage```.
That's where we encountered the issue of the GenericMessage that need to be sended twice.
The first GenericMessage will not be recognised by UnetStack. We still don't know why.
