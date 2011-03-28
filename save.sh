#!/bin/sh
EMAIL='youremail@example.com'
PASSWORD='PASSWORD'
QUALITY='SQ'
MODE='save'
DUMPFILE='dump.ogm'
python ./gomstreamer.py -e $EMAIL -p $PASSWORD -q $QUALITY -m $MODE -o $DUMPFILE
