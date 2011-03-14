# -*- coding: utf-8 -*-

'''
Copyright 2010 Simon Potter, Tomáš Heřman
Copyright 2011 Simon Potter

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import urllib2
import cookielib
import urllib
import StringIO
import re
import os
import sys
import datetime
import time
from optparse import OptionParser
from string import Template

def main():

    global debug
    debug = False  # Set this to true to print debugging information

    global VERSION
    VERSION = "0.5.0"

    # Application locations and parameters for different operating systems.
    vlcOSX = '/Applications/VLC.app/Contents/MacOS/VLC "$url" "--http-caching=$cache"'
    vlcLinux = 'vlc "$url" "--http-caching=$cache"'

    # Collecting options parsed in from the command line
    parser = OptionParser()
    parser.add_option("-p", "--password", dest = "password", help = "Password to your GOMtv account")
    parser.add_option("-e", "--email", dest = "email", help = "Email your GOMtv account uses")
    parser.add_option("-m", "--mode", dest = "mode", help = "Mode of use: 'play', 'save' or 'delayed-save'. Default is 'play'. This parameter is case sensitive.")
    parser.add_option("-q", "--quality", dest = "quality", help = "Stream quality to use: 'HQ', 'SQ' or 'SQTest'. Default is 'SQTest'. This parameter is case sensitive.")
    parser.add_option("-o", "--output", dest = "outputFile", help = "File to save stream to (Default = dump.ogm)")
    parser.add_option("-t", "--time", dest = "kt", help = "If the 'delayed-save' mode is used, this option holds the value of the *Korean* time to record at in HH:MM format. (Default = '18:00')")
    parser.add_option("-c", "--command", dest = "command", help = "Custom command to run")
    parser.add_option("-d", "--buffer-time", dest = "cache", help = "Cache size in [ms]")

    # Determining which VLC command to use based on the OS that this script is being run on
    if os.name == 'posix' and os.uname()[0] == 'Darwin':
        parser.set_defaults(command = vlcOSX)
    else:
        parser.set_defaults(command = vlcLinux)  # On Windows, assuming VLC is in the PATH, this should work.

    parser.set_defaults(quality = "SQTest")  # Setting default stream quality to 'SQTest'
    parser.set_defaults(outputFile = "dump.ogm")  # Save to dump.ogm by default
    parser.set_defaults(mode = "play")  # Want to play the stream by default
    parser.set_defaults(kt = "18:00")  # If we are scheduling a recording, do it at 18:00 KST by default
    parser.set_defaults(cache = 30000)  # Caching 30s by default
    (options, args) = parser.parse_args()

    # Printing out parameters
    if debug:
        print "Email: ", options.email
        print "Password: ", options.password
        print "Mode: ", options.mode
        print "Quality: ", options.quality
        print "Output: ", options.outputFile

    # Stopping if email and password are defaults found in *.sh/command
    if options.email == "youremail@example.com" and options.password == "PASSWORD":
        print "Enter in your GOMtv email and password into your *.sh or *.command file."
        print "This script will not work correctly without a valid account."
        sys.exit(1)

    # Seeing if we're running the latest version of GOMstreamer
    checkForUpdate()

    if options.mode == "delayed-save":
        # Delaying execution until necessary
        delay(options.kt)

    gomtvURL = "http://www.gomtv.net"
    gomtvLiveURL = gomtvURL + getSeasonURL()
    gomtvSignInURL = gomtvURL + "/user/loginProcess.gom"
    values = {
             'cmd': 'login',
             'rememberme': '1',
             'mb_username': options.email,
             'mb_password': options.password
             }

    data = urllib.urlencode(values)
    cookiejar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

    # Signing into GOMTV
    print "Signing in."
    request = urllib2.Request(gomtvSignInURL, data)
    urllib2.install_opener(opener)
    response = urllib2.urlopen(request)

    if len(cookiejar) == 0:
        print "Error: Authentification failed. Please check your login and password."
        sys.exit(1)

    # Collecting data on the Live streaming page
    print "Grabbing the 'Live' page."
    request = urllib2.Request(gomtvLiveURL)
    response = urllib2.urlopen(request)
    print "Parsing the 'Live' page for the GOX XML link."
    url = parseHTML(response.read(), options.quality)

    if debug:
        print "Printing URL on Live page:"
        print url
        print ""

    # Grab the response of the URL listed on the Live page for a stream
    print "Grabbing the GOX XML file."
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    responseData = response.read()

    # Find out the URL found in the response
    print "Parsing the GOX XML file for the stream URL."
    url = parseStreamURL(responseData, options.quality)

    command = Template(options.command)
    commandArgs = {
                  'cache': options.cache,
                  'url': url
                  }
    cmd = command.substitute(commandArgs)

    # If we're dumping the stream, modify vlc args
    if options.mode != "play":
        cmd = cmd + " --demux=dump --demuxdump-file=\"" + options.outputFile + "\""

    # GOM are now blocking via UA strings, copying GOM Player's CDN UA
    cmd = cmd + " --http-user-agent KPeerClient"
    cmd = cmd + " vlc://quit"

    print ""
    print "Stream URL:", url
    print ""
    print "VLC command:", cmd
    print ""

    if options.mode == "play":
        print "Playing stream via VLC..."
    else:
        print "Dumping stream via VLC..."

    # Executing vlc
    os.system(cmd)

def checkForUpdate():
    # Grabbing txt file containing version string of latest version
    updateURL = "http://sjp.co.nz/projects/gomstreamer/version.txt"
    request = urllib2.Request(updateURL)
    response = urllib2.urlopen(request)
    latestVersion = response.read().strip()

    if VERSION < latestVersion:
        print "================================================================================"
        print ""
        print " NOTE: Your version of GOMstreamer is " + VERSION + "."
        print "       The latest version is " + latestVersion + "."
        print "       Download the latest version from http://sjp.co.nz/projects/gomstreamer/"
        print ""
        print "================================================================================"
        print ""

def delay(kt):
    KST = kt.split(":")
    korean_hours = int(KST[0])
    korean_minutes = int(KST[1])

    # Checking to see whether we have valid times
    if korean_hours < 0 or korean_hours > 23 or \
       korean_minutes < 0 or korean_minutes > 59:
        print "Error: Enter in a valid time in the format HH:MM."
        print "       HH = hours [0-23], MM = minutes [0-59]."

    current_utc_time = datetime.datetime.utcnow()
    # Korea is 9 hours ahead of UTC
    current_korean_time = current_utc_time + datetime.timedelta(hours = 9)
    target_korean_time = datetime.datetime(current_korean_time.year,
                                           current_korean_time.month,
                                           current_korean_time.day,
                                           korean_hours,
                                           korean_minutes)

    # If the current korean time is after our target time, we assume that
    # delayed recording is for the following evening
    if current_korean_time > target_korean_time:
        target_korean_time = target_korean_time + datetime.timedelta(days = 1)

    # Finding out the length of time to sleep for
    # and enabling nice printing of the time.
    record_delta = (target_korean_time - current_korean_time).seconds
    record_delta_h = divmod(record_delta, 3600)
    record_delta_m = divmod(record_delta_h[1], 60)
    record_delta_h = str(record_delta_h[0]) + "h"
    record_delta_m = str(record_delta_m[0]) + "m"
    record_delta_s = str(record_delta_m[1]) + "s"
    nice_record_delta = record_delta_h + " " + \
                        record_delta_m + " " + \
                        record_delta_s

    print "Waiting until", kt, "KST."
    print "This will occur after waiting " + nice_record_delta + "."
    print ""
    time.sleep(record_delta)  # Delaying further execution until target Korean time

def getSeasonURL():
    # Grabbing txt file containing URL string of latest season
    seasonURL = "http://sjp.co.nz/projects/gomstreamer/season.txt"
    request = urllib2.Request(seasonURL)
    response = urllib2.urlopen(request)
    latestSeason = response.read().strip()
    return latestSeason

def parseHTML(response, quality):
    # Seeing what we've received from GOMtv
    if debug:
        print "Response:"
        print response

    # Parsing through the live page for a link to the gox XML file.
    # Quality is simply passed as a URL parameter e.g. HQ, SQ, SQTest
    try:
        patternHTML = r"http://www.gomtv.net/gox[^;]+;"
        urlFromHTML = re.search(patternHTML, response).group(0)
        urlFromHTML = re.sub(r"\" \+ playType \+ \"", quality, urlFromHTML)
        urlFromHTML = re.sub(r"\"[^;]+;", "", urlFromHTML)
    except AttributeError:
        print "Error: Unable to find the majority of the GOMtv XML URL on the Live page."
        sys.exit(0)

    # Finding the title of the stream, probably not necessary but
    # done for completeness
    try:
        patternTitle = r"this\.title[^;]+;"
        titleFromHTML = re.search(patternTitle, response).group(0)
        titleFromHTML = re.search(r"\"(.*)\"", titleFromHTML).group(0)
        titleFromHTML = re.sub(r"\"", "", titleFromHTML)
    except AttributeError:
        print "Error: Unable to find the stream title on the Live page."
        sys.exit(0)

    return (urlFromHTML + titleFromHTML)

def parseStreamURL(response, quality):
    # Observing the GOX XML file containing the stream link
    if debug:
        print "GOX XML:"
        print response

    # The response for the GOX XML if an incorrect stream quality is chosen is 1002.
    if (response == "1002"):
        print "Error: A premium ticket is required to watch higher quality streams, please choose 'SQTest' instead."
        sys.exit(0)

    # Grabbing the gomcmd URL
    try:
        print "Parsing for the HTTP stream."
        streamPattern = r'<REF href="([^"]*)"/>'
        regexResult = re.search(streamPattern, response).group(1)
    except AttributeError:
        print "Error: Unable to find the gomcmd URL in the GOX XML file."
        sys.exit(0)

    # If we are using a premium ticket, we don't need to parse the URL further
    # we just need to clean it up a bit
    if quality == 'HQ' or quality == 'SQ':
        print "Stream found, cleaning up URL."
        regexResult = urllib.unquote(regexResult) # Unquoting URL entities
        regexResult = re.sub(r'&amp;', '&', regexResult) # Removing amp;
        return regexResult

    # Collected the gomcmd URL, now need to extract the correct HTTP URL
    # from the string, only for 'SQTest'
    try:
        print "Stream found, cleaning up URL."
        patternHTTP = r"(http%3[Aa].+)&quot;"
        regexResult = re.search(patternHTTP, regexResult).group(0)
        regexResult = urllib.unquote(regexResult) # Unquoting URL entities
        regexResult = re.sub(r'&amp;', '&', regexResult) # Removing amp;
        regexResult = re.sub(r'&quot;', '', regexResult) # Removing &quot;
    except AttributeError:
        print "Error: Unable to extract the HTTP stream from the gomcmd URL."
        sys.exit(0)

    return regexResult

# Actually run the script
if __name__ == "__main__":
    main()
