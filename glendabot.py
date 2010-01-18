#!/usr/bin/python

import os
import sys
import urllib
import urllib2
import json

rootdir = os.path.dirname(os.path.abspath(__file__))
CONFFILE = rootdir + '/config.json'

TWITTER_REALM = 'Twitter API'
SEARCH_URL = 'http://search.twitter.com/search.json'
RETWEET_URL = 'http://api.twitter.com/1/statuses/retweet/' # + 'id.json'

config = json.load(open(CONFFILE))

user = config['username']
passwd = config['password']
lastid = config['lastid']

url = SEARCH_URL + '?q=' + urllib.quote_plus(config['keyword'])
url += '+-from:' + urllib.quote_plus(user) # avoid self-retweet
for u in config['nguser']:
    url += '+-from:' + urllib.quote_plus(u)
f = urllib2.urlopen(url)

data = json.load(f, 'utf-8')
if 'results' in data:
    for x in reversed(data['results']):
        id = x['id']
        if id <= lastid: continue
        config['lastid'] = lastid = id

        text =  x['text']
        ng = False
        for w in config['ngword']:
            if text.find(w) != -1:
                ng = True
        if ng == True: continue

        url = RETWEET_URL + str(id) + '.json'
        handler = urllib2.HTTPBasicAuthHandler()
        handler.add_password(TWITTER_REALM, url, user, passwd)

        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        try:
            print('Reweeting ' + str(id) + '...')
            f = urllib2.urlopen(url, urllib.urlencode({'id' : str(id)}))
        except urllib2.HTTPError, msg:
            print(msg)
            break

json.dump(config, open(CONFFILE, 'w'))

