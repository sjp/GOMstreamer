@set EMAIL="youremail@example.com"
@set PASSWORD="PASSWORD"
@set QUALITY="SQ"
@set KST="18:00"
@set DUMPFILE="dump.ogm"
python gomstreamer.py -m delayed-save -e %EMAIL% -p %PASSWORD% -q %QUALITY% -o %DUMPFILE% -t %KST%
