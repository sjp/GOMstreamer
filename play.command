#!/bin/sh
cd "`dirname \"$0\"`"
EMAIL='youremail@example.com'
PASSWORD='PASSWORD'
QUALITY='SQ'
python ./gomstreamer.py -e $EMAIL -p $PASSWORD -q $QUALITY
