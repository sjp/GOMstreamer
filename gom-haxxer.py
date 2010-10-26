import urllib2
import cookielib
import urllib
import StringIO
import re
import os
from optparse import OptionParser
from string import Template
# set up variables and constants
def main():

	defaultOSXcommandVLC = '/Applications/VLC.app/Contents/MacOS/VLC "--http-caching=$cache" "$url"'
	defaultLinuxVLC = 'vlc "--http-caching=$cache" "$url"'

	parser = OptionParser()
	parser.add_option("-p","--password",dest="password")
	parser.add_option("-e","--email",dest="email")
	parser.add_option("-b",action="store_true",dest="hq")
	parser.add_option("-l",action="store_false",dest="hq")
	parser.add_option("-c","--command",dest="command")
	parser.add_option("-d","--buffer-time",dest="cache")

	parser.set_defaults(hq=True)
	if os.uname()[0] == 'Darwin':
		parser.set_defaults(command=defaultOSXcommandVLC)
	else:
		parser.set_defaults(command=defaultLinuxVLC)
	parser.set_defaults(cache=1)
	(options,args) = parser.parse_args()

	gomtvURL = "http://www.gomtv.net"
	gomtvLiveURL= gomtvURL + "/2010gslopens2/live/"
	gomtvSignInURL= gomtvURL + "/user/loginCheck.php"
	values = {'cmd' : 'login',
			  'returl' : '%2F',
			  'mb_username' : options.email,
			   'mb_password': options.password,
			  }
	data = urllib.urlencode(values)
	virtualFile = StringIO.StringIO("")
	cookiejar = cookielib.LWPCookieJar()

	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))

	request = urllib2.Request(gomtvSignInURL,data)
	urllib2.install_opener(opener)
	response = urllib2.urlopen(request)

	request = urllib2.Request(gomtvLiveURL)
	response= urllib2.urlopen(request)
	urls = parseURLs(response.read())
	if(options.hq == True):
		url = parseHQStreamURL(urls)
	else:
		url = parseLQStreamURL(urls)
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	url = parseStreamURL(response.read())
	command = Template(options.command)
	commandArgs = {
					'cache':options.cache,
	                'url':url
			       }
	cmd = command.substitute(commandArgs)
	print(cmd)
	os.system(cmd)
def parseURLs(response):
	patternGOMCMD = r"gomcmd://[^;]+;"
	commands = re.findall(patternGOMCMD,response)
	return map(parseHTTPofCmd,commands)
def parseHTTPofCmd(item):
	patternHTTP = r"(http://[^;]+)';"
	return re.search(patternHTTP,item).group(1)
def parseHQStreamURL(urls):
	hqStreamPattern = r".*HQ.*"
	return parseStreamFileURL(urls,hqStreamPattern)
def parseLQStreamURL(urls):
	lqStreamPattern = r".*SQ.*"
	return parseStreamFileURL(urls,lqStreamPattern)
def parseStreamFileURL(urls,pattern):
	for url in urls:
		if re.match(pattern,url):
			return url
def parseStreamURL(response):
	streamPattern = r'<REF href= "([^"]*)"/>'
	return re.search(streamPattern,response).group(1)
if __name__=="__main__":
	main()

