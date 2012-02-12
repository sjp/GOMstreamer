#!/bin/sh
####################
EMAIL='youremail@example.com'
PASSWORD='PASSWORD'
QUALITY='SQTest'
MODE='scheduled-play'
KST='18:00'
STREAM='both'
####################
PARENT_DIR="$(dirname "$( cd "$( dirname "$0" )" && pwd )")"
python "$PARENT_DIR/gomstreamer.py" -e $EMAIL -p $PASSWORD -q $QUALITY -m $MODE -t $KST -s $STREAM $*
