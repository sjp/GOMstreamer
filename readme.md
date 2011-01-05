GOMstreamer Readme
=================

Introduction
------------
GOMstreamer is a Python utility allowing OSX and other Unix based OS users to watch GOMtv GSL streams. GOMsaver is a tool derived from GOMstreamer that allows you to save GSL streams to watch at a later time. Note, you are able to watch the streams in VLC as they are downloading, though this may require another instance of VLC to be loaded.

Requirements
------------
- Python 2.x.x
  with following librarires:
  - urllib2
  - cookielib
  - urllib
  - re
  - os
  - optparse
- Media player capable of playing HTTP stream whose URL is passed through command line. (For example VLC player, MPlayer)

Usage
-----

### Standard Usage ###
Enter your GOMtv email and password into the `run.sh` script, then execute it. For GOMsaver, do the same but for the `save.sh` script. To play the stream that GOMsaver dumped, open the file (default = `dump.ogm`) in any decent media player, like VLC.

### GOMstreamer parameters ###
    -h, --help            show this help message and exit
    -p PASSWORD, --password=PASSWORD
                          Password to your GOMtv account
    -e EMAIL, --email=EMAIL
                          Email your GOMtv account uses
    -q QUALITY, --quality=QUALITY
                          Stream quality to use: 'HQ', 'SQ' or 'SQTest'. Default
                          is 'SQTest'. This parameter is case sensitive.
    -c COMMAND, --command=COMMAND
                          Custom command to run
    -d CACHE, --buffer-time=CACHE
                          Cache size in [ms]

### GOMsaver parameters ###
    -h, --help            show this help message and exit
    -p PASSWORD, --password=PASSWORD
                          Password to your GOMtv account
    -e EMAIL, --email=EMAIL
                          Email your GOMtv account uses
    -q QUALITY, --quality=QUALITY
                          Stream quality to use: 'HQ', 'SQ' or 'SQTest'. Default
                          is 'SQTest'. This parameter is case sensitive.
    -c COMMAND, --command=COMMAND
                          Custom command to run
    -d CACHE, --buffer-time=CACHE
                          Cache size in [ms]
    -o OUTPUTFILE, --output=OUTPUTFILE
                          File to save stream to (Default = dump.ogm)

### Usage with VLC player ###
GOMstreamer uses VLC player by default. In OSX, it requires VLC to be located in the `/Applications` folder while on other Unix based systems it requires it to be in your shell path (try to type `vlc --version` in terminal). If one decides to use default configuration, all one needs to do is specify email and password via GOMstreamer parameters and the system should take care of the rest. The cache length can be specified by the `-b` parameter.

### Advanced usage with custom commands ###
Once can also define a specific command he wants GOMstreamer to run. There are variables which will be filled in by the GOMstreamer one can utilize in his command. The variables are:

- `$url` = url of the stream retrieved by GOMstreamer
- `$cache` = cache size requested by the user to be used by media player

For example, the default VLC command used by GOMstreamer is:
`vlc "--http-caching=$cache" "$url"`  

Security
--------
GOMstreamer requires one's login information in order to retrieve the stream url. This information is sent to the GOMtv website over the insecure HTTP protocol, just like it would be if one used browser to start up the GOM Player. Therefore the security risk is exactly the same as if one used the 'official' method to start up the stream. The password and login information are ONLY sent to the GOMtv site and are never stored by the script.

TODO
----
- Fix Autoplay in OSX
