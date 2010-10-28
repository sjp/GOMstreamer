Gom-Haxxer Readme
=================

Introduction
------------
Gom-Haxxer is a python utility allowing OS X and other Unix based OS users to watch GomTV GSL streams.

Requirements
------------
- Python 2.X.X
  with following librarires:
  - urllib2
  - cookielib
  - urllib
  - re
  - os
  - optparse
- Media player capable of playing http stream whose url is passed through command line. (For example VLC player, MPlayer)

Usage
-----

###Gom-Haxxer parameters###
	-h, --help        show the help message and exit
	-p PASSWORD, --password=PASSWORD
                      Password to your GomTV account.
	-e EMAIL, --email=EMAIL
                      Email your GomTV account uses.
	-b                    Use better quality stream. (Default)
	-l                    Use lower quality stream
	-c COMMAND, --command=COMMAND
                      Customg command to run.
	-d CACHE, --buffer-time=CACHE
                      Cache size in [ms]
###Usage with VLC player###
Gom-Haxxer uses VLC player by default. In OS X, it requires vlc to be located in /Applications folder while on other Unix based systems it requires it to be in your shell path (try to type `vlc --version` in terminal). If one decides to use default configuration, all one needs to do is specify email and password via Gom-Haxxer parameters and the system should take care of the rest. Once can also specify the cache length via `-b` parameter.

###Advanced usage with custom commands###
Once can also define a specific command he wants Gom-Haxxer to run. There are variables which will be filled in by the Gom-Haxxer one can utilize in his command. The variables are:
- `$url` = url of the stream retrieved by Gom-Haxxer
- `$cache` = cache size requested by the user to be used by media player

For example, the default VLC command used by Gom-Haxxer is:
`vlc "--http-caching=$cache" "$url"`  

Security
--------
Gom-Haxxer requires ones login information in order to retrieve stream url. These information are sent to the GomTV website over the insecure http protocol, just like it would if one used browser to start up the GomPlayer. Therefore the security risk is exactly the same as i one used the 'official' method to start up the stream. The password and login information are ONLY sent to the GomTV site and are never stored by the script.

TODO
----
- add error checking
- fix autoplay in os x