@set EMAIL="youremail@example.com"
@set PASSWORD="PASSWORD"
@set QUALITY="SQTest"
@set DUMPFILE="dump.ogm"
python ..\gomstreamer.py -m save -e %EMAIL% -p %PASSWORD% -q %QUALITY% -o %DUMPFILE%
