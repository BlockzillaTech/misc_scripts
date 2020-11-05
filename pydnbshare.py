#!/usr/bin/python
# -*- coding: utf-8 -*-	import math
import sys
import os.path
import urllib
import httplib
import re
import urllib2
from xml.dom.minidom import parse

# script to download releases from the dnbshare feed

# TODO: 
# what happens if the script dies? loses connection? whatever?
# Docker file
# Cron to automate daily sync

URL="http://www.dnbshare.com/feed"


fd = urllib2.urlopen(URL)

xml = parse(fd)

links = xml.getElementsByTagName('link')[1:]

for link in links:
    url = link.firstChild.data
    mp3 = url.replace('.html', '')
    rslash = mp3.rfind('/') + 1

    if os.path.exists(mp3[rslash:]):
        continue

    print url
    pg = urllib2.urlopen(url).read()

    payload = re.search('name="dlform-payload" value="([^"]*)', pg).group(1)

    data = urllib.urlencode({'file': mp3[rslash:], 'payload': payload})

    headers = {"Content-type": "application/x-www-form-urlencoded", 'Referer': url}

    conn = httplib.HTTPSConnection("dnbshare.com")

    conn.request('POST', url.replace(
        'https://dnbshare.com', ''), data, headers)
    resp = conn.getresponse()

    mp3url = resp.getheader('Location')

    conn.close()

    out = open(mp3[rslash:], 'w+')
    mp3f = urllib2.urlopen(mp3url)
    osize = float(mp3f.info().getheader('Content-Length'))

    #print "Size: %10s", mp3f.info().getheader('Content-Length')

    amountread = float(0)
    #print "  0%"
    while mp3f:
        data = mp3f.read(4096)
        if len(data) == 0:
            break
        amountread += len(data)
        pct = amountread / osize * 100
        sys.stdout.write("\r[T:%10d][R:%10d] %8d%%" % (osize, amountread, pct))
        sys.stdout.flush()
        out.write(data)

    print "\n"
    out.close()
