#!/bin/sh
####################
EMAIL='youremail@example.com'
PASSWORD='PASSWORD'
QUALITY='SQTest'
####################
PARENT_DIR="$(dirname "$( cd "$( dirname "$0" )" && pwd )")"
python "$PARENT_DIR/gomstreamer.py" -e $EMAIL -p $PASSWORD -q $QUALITY $*
