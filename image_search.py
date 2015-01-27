import json, urllib2, random

def get_google_search(query):
    return json.loads(urllib2.urlopen('http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=' + query).read())

def get_random_url(output):
    results = output['responseData']['results']
    if (results != []):
        return results[random.randint(0, len(results) - 1)]['unescapedUrl']
    return None
