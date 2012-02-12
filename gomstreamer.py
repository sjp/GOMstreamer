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

import cookielib
import datetime
import logging
import os
import re
import StringIO
import subprocess
import sys
import time
import urllib
import urllib2
from optparse import OptionParser
from os import path as os_path
from string import Template
from urlparse import urljoin

debug = True
debug = False  # Comment this line to print debugging information

# We only see log messages at the DEBUG level.
if debug:
    logging.basicConfig(level = logging.DEBUG,
                        format='%(levelname)s %(message)s')
else:
    logging.basicConfig(level = logging.WARNING,
                        format='%(levelname)s %(message)s')

VERSION = '0.10.0'

def main():
    curlCmd = 'curl -A KPeerClient "$url" -o "$output"'
    wgetCmd = 'wget -U KPeerClient --tries 1 "$url" -O "$output"'
    vlcPath, webCmdDefault = getDefaultLocations(curlCmd, wgetCmd)
    vlcCmdDefault = vlcPath + ' --file-caching $cache $debug - vlc://quit'
    options, args = parseOptions(vlcCmdDefault, webCmdDefault)

    # Printing out parameters
    logging.debug('Email: %s', options.email)
    logging.debug('Password: %s', options.password)
    logging.debug('Mode: %s', options.mode)
    logging.debug('Quality: %s', options.quality)
    logging.debug('VlcCmd: %s', options.vlcCmd)
    logging.debug('WebCmd: %s', options.webCmd)

    # Stopping if email and password are defaults found in *.sh/command/cmd
    if options.email == 'youremail@example.com' and options.password == 'PASSWORD':
        errMsg = 'Enter your GOMtv email and password into your *.sh, *.command, or *.cmd file.'
        errMsg = errMsg + '\nThis script will not work correctly without a valid account.'
        logging.error(errMsg)
        sys.exit(1)

    # Seeing if we're running the latest version of GOMstreamer
    checkForUpdate()

    if options.mode == 'scheduled-play':
        # Delaying execution until necessary
        delay(options.kt)

    # Attempt to grab a list of available streams
    numberOfStreams, urls = grabStreams(options)

    # Put variables into VLC command
    vlcCmd = Template(options.vlcCmd).substitute(
            {'cache': options.cache, 
             'debug' : ('', '--verbose=2')[debug]})

    # Create shell commands
    cmds = []
    for i in range(numberOfStreams):
        url = urls[i]

        webCmd = Template(options.webCmd).substitute(
                {'url' : url, 'output' : '-'})
    
        # Add verbose output for VLC if we are debugging
        if debug:
            webCmd = webCmd + ' -v'
    
        # When playing, pipe wget/curl into VLC
        # We have already substituted $output with correct target.
        cmds.append(webCmd + ' | ' + vlcCmd)

    if numberOfStreams > 1:
        logging.info('Stream URLs: %s' % urls)
        logging.info('Commands: %s' % cmds)
    else:
        logging.info('Stream URL: %s' % urls[0])
        logging.info('Command: %s' % cmds[0])

    if numberOfStreams > 1:
        print 'Playing streams...'
    else:
        print 'Playing stream...'

    # Executing command
    procs = []
    try:
        for i in range(numberOfStreams):
            procs.append(subprocess.Popen(cmds[i], shell = True))
        for i in range(numberOfStreams):
            procs[i].wait()
    except KeyboardInterrupt:
        # Swallow it, we are terminating anyway and don't want a stack trace.
        for i in range(numberOfStreams):
            procs[i].kill()
    except OSError:
        # If wget/curl fails to grab the stream, give up
        for i in range(numberOfStreams):
            procs[i].kill()
    finally:
        sys.exit(0)

def signIn(gomtvSignInURL, options):
    values = {
             'cmd': 'login',
             'rememberme': '1',
             'mb_username': options.email,
             'mb_password': options.password
             }
    data = urllib.urlencode(values)
    # Now expects to log in only via the website. Thanks chrippa.
    headers = {'Referer': 'http://www.gomtv.net/'}
    request = urllib2.Request(gomtvSignInURL, data, headers)
    response = urllib2.urlopen(request)
    # The real response that we want are the cookies, so returning None is fine.
    return

def grabLivePage(gomtvLiveURL, options):
    response = grabPage(gomtvLiveURL)
    # If a special event occurs, we know that the live page response
    # will just be some JavaScript that redirects the browser to the
    # real live page. We assume that the entireity of this JavaScript
    # is less than 200 characters long, and that real live pages are
    # more than that.
    if len(response) < 200:
        # Grabbing the real live page URL
        gomtvLiveURL = getEventLivePageURL(gomtvLiveURL, response)
        logging.info('Redirecting to the Event\'s \'Live\' page (%s).' % gomtvLiveURL)
        response = grabPage(gomtvLiveURL)
        # Most events are free and have both HQ and SQ streams, but
        # not SQTest. As a result, assume we really want SQ after asking
        # for SQTest, makes it more seamless between events and GSL.
        if options.quality == 'SQTest':
            options.quality = 'SQ'
    return response, options

def grabPage(url):
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return response.read()

def grabStreams(options):
    # Setting urllib2 up so that we can store cookies
    cookiejar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    urllib2.install_opener(opener)

    # Signing into GOMTV
    logging.info('Signing in.')
    signIn('https://ssl.gomtv.net/userinfo/loginProcess.gom', options)
    if len(cookiejar) == 0:
        logging.error('Authentification failed. Please check your login and password.')
        sys.exit(1)

    # Collecting data on the Live streaming page
    logging.info('Getting season url...')
    gomtvLiveURL = getLivePageURL('http://www.gomtv.net')
    logging.info('Grabbing the \'Live\' page (%s).' % gomtvLiveURL)
    response, options = grabLivePage(gomtvLiveURL, options)

    logging.info('Parsing the \'Live\' page for the GOX XML link.')
    goxFiles = []
    validGoxFound = False
    while (not validGoxFound):
        urls = parseHTML(response, options.quality)
        logging.debug('Printing URL(s) on Live page: %s' % urls)
    
        if len(urls) > 1:
            if options.streamChoice == 'first':
                urls = urls[:1]
            if options.streamChoice == 'alternate':
                urls = urls[1:2] # Assume second is alternate

        for i in range(len(urls)):
            url = urls[i]

            # Grab the response of the URL listed on the Live page for a stream
            logging.info('Grabbing the GOX XML file for the %s stream.' % options.quality)
            goxFile = grabPage(url)

            # It's possible to have a second stream available to premium viewers only
            if (goxFile == '1002' or goxFile == '') and options.quality == 'SQTest' and i > 0:
                logging.warning('Unable to use the alternate stream without premium membership.')
                logging.warning('Using only the first stream.')
                validGoxFound = True
                break

            # The response for the GOX XML if an incorrect stream quality is chosen is 1002.
            if (goxFile == '1002' or goxFile == ''):
                newQuality = 'SQ' if options.quality == 'HQ' else 'SQTest'
                logging.warning('Unable to use %s quality stream.', options.quality)
                logging.warning('Purchase a premium ticket for access to this stream quality.')
                logging.warning('Trying %s quality instead.', newQuality)
                options.quality = newQuality
                break
            else:
                goxFiles.append(goxFile)
                validGoxFound = True

    # Find out the URL found in the response
    logging.info('Parsing the GOX XML file(s) for the stream URL(s).')
    numberOfStreams = len(goxFiles)
    urls = []
    for i in range(numberOfStreams):
        urls.append(parseStreamURL(goxFiles[i]))
    return numberOfStreams, urls

def parseOptions(vlcCmdDefault, webCmdDefault):
    # Collecting options parsed in from the command line
    parser = OptionParser()
    parser.add_option('-p', '--password', dest = 'password', help = 'Password to your GOMtv account')
    parser.add_option('-e', '--email', dest = 'email', help = 'Email your GOMtv account uses')
    parser.add_option('-m', '--mode', dest = 'mode',
                      help = 'Mode of use: "play" or "scheduled-play". Default is "play". This parameter is case sensitive.',
                      choices = ['play', 'scheduled-play'])
    parser.add_option('-q', '--quality', dest = 'quality', help = 'Stream quality to use: "HQ", "SQ" or "SQTest". Default is "SQTest". This parameter is case sensitive.')
    parser.add_option('-s', '--stream', dest = 'streamChoice',
                      help = 'When more than one stream is available, this determines which stream to use. Possible choices are "first", "alternate" and "both". The default is "both". This parameter is case sensitive.',
                      choices = ['first', 'alternate', 'both'])
    parser.add_option('-t', '--time', dest = 'kt', help = 'If the "scheduled-play" mode is used, this option holds the value of the *Korean* time to record at in HH:MM format. (Default = "18:00")')
    parser.add_option('-v', '--vlccmd', '-c', '--command', dest = 'vlcCmd', help = 'Custom command for playing stream from stdout')
    parser.add_option('-w', '--webcmd', dest = 'webCmd', help = 'Custom command for producing stream on stdout')
    parser.add_option('-d', '--buffer-time', dest = 'cache', help = 'VLC cache size in [ms]')

    parser.set_defaults(vlcCmd = vlcCmdDefault)
    parser.set_defaults(webCmd = webCmdDefault)
    parser.set_defaults(quality = 'SQTest')  # Setting default stream quality to 'SQTest'
    parser.set_defaults(streamChoice = 'both')  # Use both streams by default
    parser.set_defaults(mode = 'play')  # Want to play the stream by default
    parser.set_defaults(kt = '18:00')  # If we are scheduling a recording, do it at 18:00 KST by default
    parser.set_defaults(cache = 30000)  # Caching 30s by default
    options, args = parser.parse_args()
    # additional sanity checks
    if len(args):
        parser.error('Extra arguments specified: ' + repr(args))
    if not options.email:
        parser.error('--email must be specified')
    if not options.password:
        parser.error('--password must be specified')
    return options, args

def getDefaultLocations(curlCmd, wgetCmd):
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
        logging.error('Unrecognized OS')
        sys.exit(1)
    return vlcPath, webCmdDefault

def checkForUpdate():
    logging.info('Checking for update...')
    try:
        # Grabbing txt file containing version string of latest version
        updateURL = 'http://sjp.co.nz/projects/gomstreamer/version.txt'
        request = urllib2.Request(updateURL)
        response = urllib2.urlopen(request)
        latestVersion = response.read().strip()

        versionParts = map(int, VERSION.split('.'))
        latestParts = map(int, latestVersion.split('.'))

        needsUpdate = False
        for i in range(len(versionParts)):
            # Have a newer version than what's available, no need for an update
            if versionParts[i] > latestParts[i]:
                break
            if versionParts[i] < latestParts[i]:
                needsUpdate = True
                break

        if needsUpdate:
            logging.warning('========================================================================')
            logging.warning('')
            logging.warning('Your version of GOMstreamer is ' + VERSION + '.')
            logging.warning('The latest version is ' + latestVersion + '.')
            logging.warning('Download the latest version from http://sjp.co.nz/projects/gomstreamer/')
            logging.warning('')
            logging.warning('========================================================================')
        else:
            logging.info('You are using the latest version.')
    except Exception as exc:
        logging.error('Failed to check version: %s', exc)

def delay(kt):
    KST = kt.split(':')
    korean_hours, korean_minutes = map(int, KST)

    # Checking to see whether we have valid times
    if korean_hours < 0 or korean_hours > 23 or \
       korean_minutes < 0 or korean_minutes > 59:
        logging.error('Enter in a valid time in the format HH:MM. HH = hours [0-23], MM = minutes [0-59].')

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

    print 'Waiting until', kt, 'KST.'
    print 'This will occur after waiting ' + nice_record_delta + '.'
    print ''
    try:
        time.sleep(record_delta)  # Delaying further execution until target Korean time
    except KeyboardInterrupt:
        print ''
        print 'Scheduling has been cancelled.'
        sys.exit(0)

def getLivePageURL(gomtvURL, method = 'url'):
    if method == 'url':
        seasonURL = '/main/goLive.gom'
    elif method == 'html':
        try:
            seasonURL = getSeasonURL_gom(gomtvURL)
        except Exception as exc:
            logging.error('Failed to get season url from gomtv.net: ', exc)
            logging.info('Getting season url from sjp.co.nz...')
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
    seasonURL = 'http://sjp.co.nz/projects/gomstreamer/season.txt'
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
    logging.debug('Response: %s', response)

    # Parsing through the live page for a link to the gox XML file.
    # Quality is simply passed as a URL parameter e.g. HQ, SQ, SQTest
    try:
        patternHTML = r'[^/]+var.+(http://www.gomtv.net/gox[^;]+;)'
        urlFromHTML = re.search(patternHTML, response).group(1)
        urlFromHTML = re.sub(r'\" \+ playType \+ \"', quality, urlFromHTML)
    except AttributeError:
        logging.error('Unable to find the majority of the GOMtv XML URL on the Live page.')
        sys.exit(0)

    # Finding the title of the stream, probably not necessary but
    # done for completeness
    try:
        patternTitle = r'this\.title[^;]+;'
        titleFromHTML = re.search(patternTitle, response).group(0)
        titleFromHTML = re.search(r'\"(.*)\"', titleFromHTML).group(0)
        titleFromHTML = re.sub(r'"', '', titleFromHTML)
        urlFromHTML = re.sub(r'"\+ tmpThis.title[^;]+;', titleFromHTML, urlFromHTML)
    except AttributeError:
        logging.error('Unable to find the stream title on the Live page.')
        sys.exit(0)

    # Check for multiple streams going at the same time, and extract the conid and the title
    # Those streams have the class "live_now"
    patternLive = r'<a\shref=\"/live/index.gom\?conid=(?P<conid>\d+)\"\sclass=\"live_now\"\stitle=\"(?P<title>[^\"]+)'
    live_streams = re.findall(patternLive, response)

    if len(live_streams) > 1:
        liveUrls = []
        options = range(len(live_streams))
        for i in options:
            # Modify the urlFromHTML according to the user
            singleUrlFromHTML = re.sub(r'conid=\d+', 'conid=' + live_streams[i][0], urlFromHTML)
            singleTitleHTML = '+'.join(live_streams[i][1].split(' '))
            singleUrlFromHTML = re.sub(r'title=[\w|.|+]*', 'title=' + singleTitleHTML, singleUrlFromHTML)
            liveUrls.append(singleUrlFromHTML)
        return liveUrls
    else:
        return [urlFromHTML]

def parseStreamURL(response):
    # Observing the GOX XML file containing the stream link
    logging.debug('GOX XML: %s', response)

    # Grabbing the gomcmd URL
    try:
        logging.info('Parsing for the HTTP stream.')
        streamPattern = r'<REF href="([^"]*)"\s*/>'
        regexResult = re.search(streamPattern, response).group(1)
    except AttributeError:
        logging.error('Unable to find the gomcmd URL in the GOX XML file.')
        sys.exit(0)

    logging.info('Stream found, cleaning up URL.')
    regexResult = urllib.unquote(regexResult)
    regexResult = re.sub(r'&amp;', '&', regexResult)
    # SQ and SQTest streams can be gomp2p links, with actual stream address passed as a parameter.
    if regexResult.startswith('gomp2p://'):
        logging.info('Extracting stream URL from gomp2p link.')
        regexResult, n = re.subn(r'^.*LiveAddr=', '', regexResult)
        if not n:
            logging.warning('Failed to extract stream URL from %r', regexResult)
    # Cosmetics, getting rid of the HTML entity, we don't
    # need either of the " character or &quot;
    regexResult = regexResult.replace('&quot;', '')
    return regexResult

# Actually run the script
if __name__ == '__main__':
    main()
