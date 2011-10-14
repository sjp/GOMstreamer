@set EMAIL="youremail@example.com"
@set PASSWORD="PASSWORD"
@set QUALITY="SQTest"
@set KST="18:00"
@set DUMPFILE="dump.ogm"
python ..\gomstreamer.py -m scheduled-save -e %EMAIL% -p %PASSWORD% -q %QUALITY% -o %DUMPFILE% -t %KST%
