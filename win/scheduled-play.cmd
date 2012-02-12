@set EMAIL="youremail@example.com"
@set PASSWORD="PASSWORD"
@set QUALITY="SQTest"
@set KST="18:00"
@set STREAM="both"
python ..\gomstreamer.py -m scheduled-play -e %EMAIL% -p %PASSWORD% -q %QUALITY% -s %STREAM% -t %KST% %*
