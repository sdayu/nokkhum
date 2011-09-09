'''
Created on Sep 7, 2011

@author: boatkrap
'''

if __name__ == '__main__':
    import json, urllib, urllib2
    output = urllib2.urlopen('http://localhost:9000/AddValue', urllib.urlencode({'name': '143'}))
    print json.loads(output.read())
    
