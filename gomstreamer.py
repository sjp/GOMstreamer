#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
Copyright 2010 Simon Potter, Tomáš Heřman
Copyright 2011 Simon Potter
Copyright 2011 Fj (fj.mail@gmail.com)

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
from urlparse import urljoin
import StringIO
import re
import os
from os import path as os_path
import sys
import datetime
import time
from optparse import OptionParser
from string import Template

debug = True
debug = False  # Comment this line to print debugging information

VERSION = "0.7.3"

def main():
    curlCmd = 'curl -A KPeerClient "$url" -o "$output"'
    wgetCmd = 'wget -U KPeerClient --tries 1 "$url" -O "$output"'

    # Application locations and parameters for different operating systems.
    if os.name == 'posix' and os.uname()[0] == 'Darwin':
        # OSX
        vlcPath = '/Applications/VLC.app/Contents/MacOS/VLC'
        webCmdDefault = curlCmd
    elif os.name == 'posix':
        # Linux
        vlcPath = 'vlc'
        webCmdDefault = wgetCmd
    elif os.name == 'nt':
        def find_vlc():
            vlc_subpath = r'VideoLAN\VLC\vlc.exe'
            prog_files = os.environ.get('ProgramFiles')
            prog_files86 = os.environ.get('ProgramFiles(x86)')
            # 32bit Python on x64 Windows would see both as mapping to the x86
            # folder, but that's OK since there's no official 64bit vlc for
            # Windows yet.
            vlc_path = os_path.join(prog_files, vlc_subpath) if prog_files else None
            if vlc_path and os_path.exists(vlc_path):
                return vlc_path
            vlc_path = os_path.join(prog_files86, vlc_subpath) if prog_files86 else None
            if vlc_path and os_path.exists(vlc_path):
                return vlc_path
            return 'vlc' # maybe it's in PATH

        vlcPath = '"' + find_vlc() + '"'
        webCmdDefault = curlCmd
    else:
        print 'Unrecognized OS'
        sys.exit(1)
    vlcCmdDefault = vlcPath + ' --file-caching $cache $debug - vlc://quit'

    # Collecting options parsed in from the command line
    parser = OptionParser()
    parser.add_option("-p", "--password", dest = "password", help = "Password to your GOMtv account")
    parser.add_option("-e", "--email", dest = "email", help = "Email your GOMtv account uses")
    parser.add_option("-m", "--mode", dest = "mode",
            help = "Mode of use: 'play', 'save' or 'delayed-save'. Default is 'play'. This parameter is case sensitive.",
            choices=['play', 'save', 'delayed-save'])
    parser.add_option("-q", "--quality", dest = "quality", help = "Stream quality to use: 'HQ', 'SQ' or 'SQTest'. Default is 'SQTest'. This parameter is case sensitive.")
    parser.add_option("-o", "--output", dest = "outputFile", help = "File to save stream to (Default = dump.ogm)")
    parser.add_option("-t", "--time", dest = "kt", help = "If the 'delayed-save' mode is used, this option holds the value of the *Korean* time to record at in HH:MM format. (Default = '18:00')")
    parser.add_option("-v", "--vlccmd", "-c", "--command", dest = "vlcCmd", help = "Custom command for playing stream from stdout")
    parser.add_option("-w", "--webcmd", dest = "webCmd", help = "Custom command for producing stream on stdout")
    parser.add_option("-d", "--buffer-time", dest = "cache", help = "VLC cache size in [ms]")

    parser.set_defaults(vlcCmd = vlcCmdDefault)
    parser.set_defaults(webCmd = webCmdDefault)

    parser.set_defaults(quality = "SQTest")  # Setting default stream quality to 'SQTest'
    parser.set_defaults(outputFile = "dump.ogm")  # Save to dump.ogm by default
    parser.set_defaults(mode = "play")  # Want to play the stream by default
    parser.set_defaults(kt = "18:00")  # If we are scheduling a recording, do it at 18:00 KST by default
    parser.set_defaults(cache = 30000)  # Caching 30s by default
    options, args = parser.parse_args()

    # Printing out parameters
    if debug:
        print "Email: ", options.email
        print "Password: ", options.password
        print "Mode: ", options.mode
        print "Quality: ", options.quality
        print "Output: ", options.outputFile
        print "VlcCmd: ", options.vlcCmd
        print "WebCmd: ", options.webCmd

    # additional sanity checks
    if len(args):
        parser.error('Extra arguments specified: ' + repr(args))
    if not options.email:
        parser.error('--email must be specified')
    if not options.password:
        parser.error('--password must be specified')

    # Stopping if email and password are defaults found in *.sh/command/cmd
    if options.email == "youremail@example.com" and options.password == "PASSWORD":
        print "Enter your GOMtv email and password into your *.sh, *.command, or *.cmd file."
        print "This script will not work correctly without a valid account."
        sys.exit(1)

    # Seeing if we're running the latest version of GOMstreamer
    checkForUpdate()

    if options.mode == "delayed-save":
        # Delaying execution until necessary
        delay(options.kt)

    gomtvURL = 'http://www.gomtv.net'
    gomtvSignInURL = 'https://ssl.gomtv.net/userinfo/loginProcess.gom'
    values = {
             'cmd': 'login',
             'rememberme': '1',
             'mb_username': options.email,
             'mb_password': options.password
             }
    # Now expects to log in only via the website. Thanks chrippa.
    headers = {'Referer': 'http://www.gomtv.net/'}

    data = urllib.urlencode(values)
    cookiejar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

    # Signing into GOMTV
    print "Signing in."
    request = urllib2.Request(gomtvSignInURL, data, headers)
    urllib2.install_opener(opener)
    response = urllib2.urlopen(request)

    if len(cookiejar) == 0:
        print "Error: Authentification failed. Please check your login and password."
        sys.exit(1)

    # Collecting data on the Live streaming page
    print 'Getting season url...'
    gomtvLiveURL = getLivePageURL(gomtvURL)
    print 'Grabbing the \'Live\' page (%s).' % gomtvLiveURL
    request = urllib2.Request(gomtvLiveURL)
    response = urllib2.urlopen(request)
    response = response.read()

    # If a special event occurs, we know that the live page response
    # will just be some JavaScript that redirects the browser to the
    # real live page. We assume that the entireity of this JavaScript
    # is less than 200 characters long, and that real live pages are
    # more than that.
    if len(response) < 200:
        # Grabbing the real live page URL
        gomtvLiveURL = getEventLivePageURL(gomtvLiveURL, response)
        print "Redirecting to the Event\'s 'Live' page (%s)." % gomtvLiveURL
        request = urllib2.Request(gomtvLiveURL)
        response = urllib2.urlopen(request)
        response = response.read()
        # Most events are free and have both HQ and SQ streams, but
        # not SQTest. As a result, assume we really want SQ after asking
        # for SQTest, makes it more seamless between events and GSL.
        if options.quality == "SQTest":
            options.quality = "SQ"

    print "Parsing the 'Live' page for the GOX XML link."
    url = parseHTML(response, options.quality)

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

    # Put variables into VLC command
    vlcCmd = Template(options.vlcCmd).substitute(
            {'cache': options.cache, 
             'debug' : ('', '--verbose=2')[debug]})

    # Put variables into wget/curl command
    outputFile = '-' if options.mode == "play" else options.outputFile
    webCmd = Template(options.webCmd).substitute(
            {'url' : url, 'output' : outputFile})

    # Add verbose output for VLC if we are debugging
    if debug:
        webCmd = webCmd + " -v"

    # If playing pipe wget/curl into VLC, else save stream to file
    # We have already substituted $output with correct target.
    if options.mode == "play":
        cmd = webCmd + " | " + vlcCmd
    else:
        cmd = webCmd

    print ""
    print "Stream URL:", url
    print ""
    print "Command:", cmd
    print ""

    if options.mode == "play":
        print 'Playing stream...'
    else:
        print 'Saving stream as "' + outputFile + '" ...'

    # Executing command
    try:
        os.system(cmd)
    except KeyboardInterrupt:
        # Swallow it, we are terminating anyway and don't want a stack trace.
        pass

def checkForUpdate():
    print 'Checking for update...',
    try:
        # Grabbing txt file containing version string of latest version
        updateURL = "http://sjp.co.nz/projects/gomstreamer/version.txt"
        request = urllib2.Request(updateURL)
        response = urllib2.urlopen(request)
        latestVersion = response.read().strip()

        if VERSION < latestVersion:
            print
            print "================================================================================"
            print
            print " NOTE: Your version of GOMstreamer is " + VERSION + "."
            print "       The latest version is " + latestVersion + "."
            print "       Download the latest version from http://sjp.co.nz/projects/gomstreamer/"
            print ""
            print "================================================================================"
            print
        else:
            print 'have the latest version'
    except Exception as exc:
        print 'Failed to check version:', exc

def delay(kt):
    KST = kt.split(":")
    korean_hours, korean_minutes = map(int, KST)

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
    record_delta = (target_korean_time - current_korean_time).total_seconds()
    minutes, seconds = divmod(record_delta, 60)
    hours, minutes = divmod(minutes, 60)
    nice_record_delta = '%dh %dm %ds' % (hours, minutes, seconds)

    print "Waiting until", kt, "KST."
    print "This will occur after waiting " + nice_record_delta + "."
    print ""
    time.sleep(record_delta)  # Delaying further execution until target Korean time

def getLivePageURL(gomtvURL, method = "url"):
    if method == "url":
        seasonURL = "/main/goLive.gom"
    elif method == "html":
        try:
            seasonURL = getSeasonURL_gom(gomtvURL)
        except Exception as exc:
            print 'Failed to get season url from gomtv.net: ', exc
            print 'Getting season url from sjp.co.nz...'
            seasonURL = getSeasonURL_sjp()
    else:
        seasonURL = getSeasonURL_sjp()
    return urljoin(gomtvURL, seasonURL)

def getEventLivePageURL(gomtvLiveURL, response):
    match = re.search(' \"(.*)\";', response)
    assert match, 'Event Live Page URL not found'
    return urljoin(gomtvLiveURL, match.group(1))

def getSeasonURL_sjp():
    # Grabbing txt file containing URL string of latest season
    seasonURL = "http://sjp.co.nz/projects/gomstreamer/season.txt"
    request = urllib2.Request(seasonURL)
    response = urllib2.urlopen(request)
    latestSeason = response.read().strip()
    return latestSeason

def getSeasonURL_gom(gomtvURL):
    # Getting season url from the 'Go Live!' button on the main page. 
    request = urllib2.Request(gomtvURL)
    response = urllib2.urlopen(request)
    match = re.search('.*liveicon"><a href="([^"]*)"', response.read())
    assert match, 'golive_btn href not found'
    return match.group(1)

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

    print "Stream found, cleaning up URL."
    regexResult = urllib.unquote(regexResult)
    regexResult = re.sub(r'&amp;', '&', regexResult)
    # SQ and SQTest streams can be gomp2p links, with actual stream address passed as a parameter.
    if regexResult.startswith('gomp2p://'):
        print 'Extracting stream URL from gomp2p link.'
        regexResult, n = re.subn(r'^.*LiveAddr=', '', regexResult)
        if not n:
            print 'Warning: failed to extract stream URL from %r' % regexResult
    # Cosmetics, getting rid of the HTML entity, we don't
    # need either of the " character or &quot;
    regexResult = regexResult.replace('&quot;', '')
    return regexResult

# Actually run the script
if __name__ == "__main__":
    main()
