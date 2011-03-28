#!/bin/sh
cd "`dirname \"$0\"`"
EMAIL='youremail@example.com'
PASSWORD='PASSWORD'
QUALITY='SQ'
MODE='delayed-save'
KST='18:00'
DUMPFILE='dump.ogm'
python ./gomstreamer.py -e $EMAIL -p $PASSWORD -q $QUALITY -m $MODE -t $KST -o $DUMPFILE
