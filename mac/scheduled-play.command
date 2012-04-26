#!/bin/sh
############################################################################
# If you're comfortable with your login credentials being viewable in plain
# text, you may uncomment the EMAIL and PASSWORD variables and place your
# GOMtv.net credentials inside them. The script will simply ask you for 
# your login information at runtime if not provided here.
############################################################################

###############################
# Your preferences here!
###############################
#EMAIL='youremail@example.com'
#PASSWORD='yourpassword'
QUALITY='SQTest'
MODE='scheduled-play'
KST='18:00'
STREAM='both'
####################

###############################
# Don't edit beyond this point
###############################

PARENT_DIR="$(dirname "$( cd "$( dirname "$0" )" && pwd )")"

# If email not set in variable, get email from user at runtime.
if [[ "$EMAIL" = "" ]];
then
	read -p "GOMtv.net Email: " EMAIL
fi

# If password not set in variable, get password from user at runtime.
if [[ "$PASSWORD" = "" ]];
then
  # Turn off echo so password doesn't show up when typing.
	stty -echo
  read -p "GOMtv.net Password (text will not display): " PASSWORD
  # Turn echo back on
	stty echo
	echo ""
fi

python "$PARENT_DIR/gomstreamer.py" -e $EMAIL -p $PASSWORD -q $QUALITY -m $MODE -t $KST -s $STREAM $*

