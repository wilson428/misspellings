#!/usr/bin/env python

import os
import json
import re
import oauth2 as oauth
from datetime import datetime
from collections import defaultdict
import argparse

try:
    keys = json.load(open(os.getcwd() + '/scripts/keys.json', 'r'))
except:
    keys = {
        "CONSUMER_KEY": "",
        "CONSUMER_SECRET": "",
        "ACCESS_TOKEN": "",
        "ACCESS_TOKEN_SECRET": ""
    }   
    
print keys
    
# Create your consumer with the proper key/secret.
consumer = oauth.Consumer(key=keys["CONSUMER_KEY"], secret=keys["CONSUMER_SECRET"])
token = oauth.Token(keys["ACCESS_TOKEN"],keys["ACCESS_TOKEN_SECRET"])

# Create our client.
client = oauth.Client(consumer, token)    
query = "Obama"

#max_id_str

def prep(first, last, which, max_depth = 100):
    output = {
        'first': first,
        'last': last,
        'matches': [],
        'misspelled': defaultdict(int)
    }
    
    if which == 'first':
        options = {
            'query': last,
            'regex': r"\b(" + first[0] + "[a-z']+)\s" + last,
            'correct': [first],
            'max_depth': max_depth
        }
    else:
        options = {
            'query': first,
            'regex': first + "\s(" + last[0] + "[a-z']+)",
            'correct': [last, last + "'s"],
            'max_depth': max_depth
        }
    search(options, output)        

    if which == 'first':
        f = open(os.getcwd() + "/data/matches-%s-%s.json" % (output['first'], datetime.now().strftime("%Y-%m-%d-%H-%M-%S")), 'w')
        f.write(json.dumps(output, indent=2))
        f.close()
    else:
        f = open(os.getcwd() + "/data/matches-%s-%s.json" % (output['last'], datetime.now().strftime("%Y-%m-%d-%H-%M-%S")), 'w')
        f.write(json.dumps(output, indent=2))
        f.close()

def search(options, output, maxid="", depth = 1, strikes = 0):
    if depth > options['max_depth']:
        return
    url="http://search.twitter.com/search.json?q=%s&max_id=%s&rpp=100&include_entities=true&result_type=mixed" % (options['query'].replace(" ", "%20"), maxid)
    try:
        resp, content = client.request(url)
        results = json.loads(content)
    except:
        print "Error retrieving results at", url        
        print json.dumps(results, indent=2)
        if strikes > 3:
            return
        search(options, output, maxid, depth, strikes + 1)
        return
        
    if 'results' not in results:
        print "No results at", url        
        print json.dumps(results, indent=2)
        if strikes > 3:
            return
        search(options, output, maxid, depth, strikes + 1)
        return
    for result in results['results']:
        name = re.search(options['regex'], result['text'].encode('utf-8'))
        if name and name.group(1) not in options['correct'] and result['iso_language_code'] == "en":
            print name.group(0), result['iso_language_code']
            output['misspelled'][name.group(1)] += 1
            output['matches'].append({
                'name': name.group(0),
                'misspelled': name.group(1),
                'language': result['iso_language_code'],
                'tweet': result
            })            
    try:
        last_id = results['results'][-1]['id_str']
    except:
        return    
    
    search(options, output, last_id, depth + 1, strikes)    

def main():
    parser = argparse.ArgumentParser(description="Search TWitter for common misspellings of a name")
    parser.add_argument("-n", "--name", metavar="STRING", dest="name", type=str, default=None,
                        help="a first and last name (or any two-word phrase")
    parser.add_argument("-m", "--max", metavar="INTEGER", dest="max", type=int, default=100,
                        help="a first and last name (or any two-word phrase")
                        
    args = parser.parse_args()    
    if len(args.name.split('+')) != 2:
        parser.error("I need a two-word name -- thanks.")        
    else:
        first, last = args.name.split('+')
        prep(first, last, 'first', args.max)
        prep(first, last, 'last', args.max)

if __name__ == "__main__":
    main()