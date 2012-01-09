@set EMAIL="youremail@example.com"
@set PASSWORD="PASSWORD"
@set QUALITY="SQTest"
python ..\gomstreamer.py -e %EMAIL% -p %PASSWORD% -q %QUALITY% %*
