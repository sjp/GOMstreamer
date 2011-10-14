#!/bin/sh
cd "`dirname \"$0\"`"
EMAIL='youremail@example.com'
PASSWORD='PASSWORD'
QUALITY='SQTest'
MODE='save'
DUMPFILE='dump.ogm'
python ../gomstreamer.py -e $EMAIL -p $PASSWORD -q $QUALITY -m $MODE -o $DUMPFILE
