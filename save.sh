#!/bin/sh
EMAIL='youremail@example.com'
PASSWORD='PASSWORD'
QUALITY='SQTest'
DUMPFILE='dump.ogm'
python ./gomsaver.py -e $EMAIL -p $PASSWORD -q $QUALITY -o $DUMPFILE
