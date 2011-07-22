GOMstreamer Readme
==================

Introduction
------------
GOMstreamer is a Python utility allowing OSX and other Unix based OS users to watch and save GOMtv GSL streams. Note, you are able to watch the streams in VLC as they are downloading, though this will require another instance of VLC to be loaded.

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
If you are an OSX user, enter your GOMtv email and password into the `play.command` script, then execute it by double-clicking it. To save a stream, do the same but for the `save.command` script. In order to record a stream at a specific time, edit `delayed-save.command` and as was the case with previous scripts, enter in your user credentials. On top of this you must enter a **Korean** time (24h format) at which to save the stream, by default this is set to 18:00.

For Linux users, edit `play.sh`, `save.sh` and `delayed-save.sh` instead and execute the appropriate script via the terminal. To play the stream that GOMstreamer dumped, open the file (default = `dump.ogm`) in any decent media player, like VLC.

### GOMstreamer parameters ###
    -h, --help            show this help message and exit
    -p PASSWORD, --password=PASSWORD
                          Password to your GOMtv account
    -e EMAIL, --email=EMAIL
                          Email your GOMtv account uses
    -m MODE, --mode=MODE  Mode of use: 'play', 'save' or 'delayed-save'. Default
                          is 'play'. This parameter is case sensitive.
    -q QUALITY, --quality=QUALITY
                          Stream quality to use: 'HQ', 'SQ' or 'SQTest'. Default
                          is 'SQTest'. This parameter is case sensitive.
    -o OUTPUTFILE, --output=OUTPUTFILE
                          File to save stream to (Default = dump.ogm)
    -t KT, --time=KT      If the 'delayed-save' mode is used, this option holds
                          the value of the *Korean* time to record at in HH:MM
                          format. (Default = '18:00')
    -c COMMAND, --command=COMMAND
                          Custom command to run
    -w WEBCMD, --webcmd=WEBCMD
                          wget/curl command to run
    -d CACHE, --buffer-time=CACHE
                          Cache size in [ms]

### Usage with VLC player ###
GOMstreamer uses VLC player by default. In OSX, it requires VLC to be located in the `/Applications` folder while on other Unix based systems it requires it to be in your shell path (try to type `vlc --version` in terminal). If the user decides to use the default configuration, all they need to do is specify email and password via GOMstreamer parameters and the application should take care of the rest.

Security
--------
GOMstreamer requires one's login information in order to retrieve the stream url. This information is sent to the GOMtv website over the insecure HTTP protocol, just like it would be if you logged in via a browser to start up the GOM Player. Therefore the security risk is exactly the same as if one used the 'official' method to start up the stream. The password and login information are ONLY sent to the GOMtv site and are never stored by the script.

The only other network communication that this application does is contact my server to grab a couple of text files. This is so that the tool can check for updates and also to grab the latest GSL season's live URL. This avoids the need to update GOMstreamer each season just to get the correct URL. No user information is sent to the server.
