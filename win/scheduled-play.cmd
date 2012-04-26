:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
:: If you're comfortable with your login credentials being viewable in plain
:: text, you may uncomment the EMAIL and PASSWORD variables and place your
:: GOMtv.net credentials inside them. The script will simply ask you for 
:: your login information at runtime if not provided here.
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::
:: Your preferences here!
:::::::::::::::::::::::::::::::
::@set EMAIL="youremail@example.com"
::@set PASSWORD="PASSWORD"
@set QUALITY="SQTest"
@set KST="18:00"
@set STREAM="both"

::::::::::::::::::::::::::::::::
:: Don't edit beyond this point
::::::::::::::::::::::::::::::::
@echo off
if not defined EMAIL (
    @set /p EMAIL=GOMtv.net Email: 
)
if not defined PASSWORD (
    echo Before entering your password, make sure no-one is looking!
    @set /p PASSWORD=GOMtv.net Password: 
)

python ..\gomstreamer.py -m scheduled-play -e %EMAIL% -p %PASSWORD% -q %QUALITY% -s %STREAM% -t %KST% %*
