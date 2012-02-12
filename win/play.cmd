@set EMAIL="youremail@example.com"
@set PASSWORD="PASSWORD"
@set QUALITY="SQTest"
@set STREAM="both"
python ..\gomstreamer.py -e %EMAIL% -p %PASSWORD% -q %QUALITY% -s %STREAM% %*
