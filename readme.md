GOMstreamer Readme
==================

**GOMstreamer is now inactive. I have written a [post on my website](http://sjp.co.nz/posts/retiring-gomstreamer/) explaining why.**

Introduction
------------
GOMstreamer is a Python utility allowing OSX and other Unix based OS users to watch GOMtv GSL streams.

Requirements
------------
- Python 2.7.x
  with following libraries:
  - urllib2
  - cookielib
  - urllib
  - re
  - os
  - optparse
  - datetime
  - time
- VLC
- wget (for Linux users) or curl (for OSX users)

Usage
-----

### Standard Usage ###
If you are an OSX user, browse the `mac` folder and enter your GOMtv email and password into the `play.command` script, then execute it by double-clicking it. In order to schedule playback of a stream at a specific time, edit `scheduled-play.command` and enter in your user credentials. On top of this you must enter a **Korean** time (24h format) at which to save the stream, by default this is set to 18:00.

For Windows users, the same instructions as above apply. The only differences being that the files are located in the `win` folder, and they have a `cmd` file extension.

For Linux users, edit the files located in the `linux` directory: `play.sh` and `scheduled-play.sh`. Execute the appropriate script via the terminal.

### GOMstreamer parameters ###
    -h, --help            show this help message and exit
    -p PASSWORD, --password=PASSWORD
                          Password to your GOMtv account
    -e EMAIL, --email=EMAIL
                          Email your GOMtv account uses
    -m MODE, --mode=MODE  Mode of use: "play" or "scheduled-play".
                          Default is "play". This parameter is case sensitive.
    -q QUALITY, --quality=QUALITY
                          Stream quality to use: "HQ", "SQ" or "SQTest". Default
                          is "SQTest". This parameter is case sensitive.
    -t KT, --time=KT      If the "scheduled-play" mode is used, this option
                          holds the value of the *Korean* time to record at in
                          HH:MM format. (Default = "18:00")
    -v VLCCMD, -c VLCCMD, --vlccmd=VLCCMD, --command=VLCCMD
                          Custom command for playing stream from stdout
    -w WEBCMD, --webcmd=WEBCMD
                          Custom command for producing stream on stdout
    -d CACHE, --buffer-time=CACHE
                          VLC cache size in [ms]

### Usage with VLC player ###
GOMstreamer uses VLC player by default. In OSX, it requires VLC to be located in the `/Applications` folder while on other Unix based systems it requires it to be in your shell path (try to type `vlc --version` in terminal). If a user decides to use the default configuration, all they need to do is specify email and password via GOMstreamer parameters and the application should take care of the rest.

Security
--------
GOMstreamer requires one's login information in order to retrieve the stream url. This information is sent to the GOMtv website over the secure HTTPS protocol, just like it would be if you logged in via a browser to start up the GOM Player. Therefore the security risk is exactly the same as if one used the 'official' method to start up the stream. The password and login information are ONLY sent to the GOMtv site and are never stored outside the script.

The only other network communication that this application does is contact my server to grab a couple of text files. This is so that the tool can check for updates and (as a last resort) also to grab the latest GSL season's live URL. No user information is sent to the server.
