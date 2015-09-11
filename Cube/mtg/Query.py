try:
    from mtg import SEARCH_URL
    from mtg.Card import Card
except ImportError:
    from __init__ import SEARCH_URL
    from Card import Card
    

#fields
#name, description, flavor, color, manacost, convertedmanacost, type, subtype, power, toughness, loyalty, rarity, artist, setId

#comparitors
#m : contains, eq : equal to, not : not equal, gt : greater than, gte : greater than or equal to, lt : less than, lte : less than or equal to

class Query(object):
    """description of class"""
    pass

def test():
    try:
        from urllib2 import urlopen, quote
    except ImportError:
        from urllib.request import urlopen, quote
    from json import loads

    url = SEARCH_URL + 'color not black AND color not green AND type m Legendary'
    url_data = urlopen(url).read()
    url_data = loads(url_data)

    x = [ Card(d) for d in url_data ]
    print(x)

if __name__ == "__main__":
    try:
        from urllib2 import urlopen, quote
    except ImportError:
        from urllib.request import urlopen, quote
    from json import loads

    url = SEARCH_URL + "color m red AND color m white AND color m black"
    print(url)
    url_data = urlopen(url).read()
    url_data = loads(url_data)

    x = [ Card(d) for d in url_data ]
    print(x)
    