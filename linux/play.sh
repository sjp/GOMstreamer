#!/bin/sh
####################
# If you're comfortable with your password being viewable in plaintext, you may
# create a PASSWORD variable with your password in it. By default, the script
# will prompt you for your password at runtime.
EMAIL='youremail@example.com'
QUALITY='SQTest'
STREAM='both'
####################

PARENT_DIR="$(dirname "$( cd "$( dirname "$0" )" && pwd )")"

# If password not set in variable, get password from user at runtime.
if [[ "$PASSWORD" = "" ]];
then
  # Turn off echo so password doesn't show up when typing.
	stty -echo
	read -p "GomTV.net Password: " PASSWORD
  # Turn echo back on
	stty echo
	echo ""
fi

python "$PARENT_DIR/gomstreamer.py" -e $EMAIL -p $PASSWORD -q $QUALITY -s $STREAM $*
