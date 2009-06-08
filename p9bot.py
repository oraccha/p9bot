#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import urllib
import urllib2
import urlparse
import time
import feedparser
import yaml

LASTFILE = './p9bot.timestamp'
CONFFILE = './p9bot.yaml'

TWITTER_REALM = 'Twitter API'
TWITTER_URL = 'http://twitter.com/statuses/update.xml'

class TwitterBot:
    now = last = 0.0

    def __init__(self):
        self.read_last()
        self.now = time.mktime(time.gmtime())

        y = yaml.load(open(CONFFILE))
        self.target = y['feed']
        self.config = y['twitter']
        user = self.config['username']
        passwd = self.config['password']
        parsed_url = urlparse.urlparse(TWITTER_URL)
        handler = urllib2.HTTPBasicAuthHandler()
        handler.add_password(TWITTER_REALM, parsed_url.hostname, user, passwd)

        self.opener = urllib2.build_opener(handler)

    def read_last(self):
        try:
            f = open(LASTFILE, 'r')
            try:
                for line in f:
                    self.last = float(line)
            finally:
                f.close()
        except IOError:
            pass

    def update_last(self):
        try:
            f = open(LASTFILE, 'w')
            try:
                f.write(str(self.now))
            finally:
                f.close()
        except IOError:
            pass

    def open(self, url):
        self.feed = feedparser.parse(url)
        return self.feed['feed'].get('title', '-'), \
            self.feed['feed'].get('author', '-'), \
            self.feed['feed'].get('link', '-')

    def fetch(self, max=None):
        for e in self.feed['entries'][:max]:
            title = link = ''

            try:
                date = time.mktime(e['updated_parsed'])
                if self.last > date:
                    break

                link = e['link']
                title = e['title']
            except (AttributeError, KeyError), e:
                pass

            yield date, title, link

    def submit(self, post):
        data = urllib.urlencode({'status': post.encode('utf-8')})
        self.opener.open(TWITTER_URL, data)

def main():
    limit = 10
    if len(sys.argv) == 2:
	limit = int(sys.argv[1])

    entries = []
    p9bot = TwitterBot()

    for target in p9bot.target:
        if target[0] == '#':
            continue

        title, author, url = p9bot.open(target)
        for date, etitle, link in p9bot.fetch():
            fdate = time.strftime("%b %d, %H:%M:%S", time.localtime(date))
            msg = "%s (%s), %s, %s" % (etitle, title, fdate, link)
            entries.append({'date' : date, 'msg' : msg})
            entries.sort(key=lambda h : h['date'], reverse=False)

    elen = len(entries)
    for i in range(max(0, elen - limit), elen):
        post = entries[i]['msg']
        p9bot.submit(post)
        print "posted", post.encode('utf-8')

    p9bot.update_last()

if __name__ == '__main__':
    main()
